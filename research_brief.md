# Research Brief: Shopping List & Personal Wallet Manager Architecture

**Author:** Nour, Principal Systems & API Researcher  
**Target:** LibanDev Engineering Team (Ziad & Maya)  
**Date:** March 2025  
**Document Status:** Approved & Finalized for Sprint Kickoff  

---

## 1. Executive Summary & Architectural Corrective

### 1.1 CEO Directive Reconciliation
A critical divergence occurred in team discussions between the Manager's proposed milestones and the CEO's directive. The CEO explicitly specified:
> *"The user is not required to create an account to login and out from... Just create a wallet that has a username and password for it and inside the wallet he can do all the other stuff... track expenses like rent, electricity, gas for the car, luxury activities."*

**Architectural Correction:** We are **not** building a multi-tenant OAuth/Firebase Auth user SaaS platform with bloated user profile tables and email verification workflows. Instead, the architecture centers on a **Wallet Identity Primitive**. A `Wallet` is the root security, sync, and transactional boundary. The `username` serves as the Wallet Identifier (`wallet_id`), and the `password` derives both the local data encryption key (via Argon2id / PBKDF2) and authentication credentials.

---

## 2. Tech Stack Selection & Compatibility Matrix

To meet the requirements of zero-friction wallet access, offline-first execution, cross-device real-time sync, and client-side encryption, the following minimal, bulletproof stack has been selected:

| Layer | Recommended Technology | Version | License | Justification & Compatibility Matrix |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Framework** | React + Vite | React `18.3.1`<br>Vite `5.2.x` | MIT | Fast HMR, lightweight bundle size (<45KB gzipped core runtime). Full PWA Service Worker support. |
| **Local Storage Engine** | Dexie.js (IndexedDB) | `4.0.1` | Apache-2.0 | Reactive IndexedDB wrapper with full offset/limit indexing, live queries, and transactional safety. |
| **State & Sync Engine** | TanStack Query (React Query) + RxDB / Custom CRDT | `5.28.x` | MIT | Optimistic updates, background revalidation, offline queue management, automatic refetch on network reconnect. |
| **Styling & UI Components**| Tailwind CSS + Lucide Icons | Tailwind `3.4.x`<br>Lucide `0.359.0` | MIT | Zero-runtime CSS extraction, mobile-first responsive layout, accessible UI components. |
| **Backend Runtime** | Node.js (LTS) + Express | Node `20.12.x` LTS<br>Express `4.19.2` | MIT | Ubiquitous runtime with native ES modules support, low memory footprint (~35MB baseline heap). |
| **Realtime Gateway** | Socket.IO | `4.7.5` | MIT | Fallback transport (WebSocket with HTTP long-polling fallback), client reconnection buffers, sub-10ms delivery latency. |
| **Database Engine** | PostgreSQL + Prisma ORM | Postgres `16.2`<br>Prisma `5.11.0` | Apache-2.0 | ACID-compliant relational storage for server-side persistence, JSONB support for delta logs, integer-based currency columns. |
| **Key Derivation & Auth** | `argon2` (Server) / `WebCrypto API` (Browser) | Argon2 `0.40.1`<br>W3C Web Crypto | MIT / Native | OWASP-recommended memory-hard key derivation for wallet passphrases. Browser-native AES-GCM 256 encryption. |

---

## 3. Architectural Trade-Off Analysis

### 3.1 Offline-First Sync: LWW vs. CRDT (State-based) vs. Operational Transformation (OT)
- **Selected Strategy:** **Hybrid Last-Write-Wins (LWW) with Vector Clocks & Delta Logs**.
- **Rationale:** Operational Transformation requires a central authority server at all times (breaks offline mode). Delta-based CRDTs (e.g., Yjs or Automerge) add significant binary bundle size (~120KB) and complex garbage collection overhead for simple item lists. 
- **Implementation:** Every entity record (`Item`, `ShoppingList`, `Expense`) maintains a `updated_at` (ISO 8601 UTC timestamp with microsecond resolution) and a `version` counter. Local edits update Dexie.js immediately and queue a delta record in `outbox_queue`. Upon internet connection, delta batches are sent to the sync server via WebSocket/HTTP. Conflicts resolve by higher version number, falling back to LWW.

### 3.2 Financial Precision: IEEE 754 Floating Point vs. Integer Micro-Cents
- **Trade-off:** Standard JS Numbers (`0.1 + 0.2 = 0.30000000000000004`) lead to financial corruption in wallet calculations.
- **Selected Strategy:** **Integer Cents Representation (RFC 8259 Compliant)**.
- **Rule:** All wallet balances, item prices, and expense amounts are strictly stored as 64-bit integers representing cents (e.g., `$15.45` is stored as `1545`). Division is executed only at the visual presentation layer using `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`.

### 3.3 Auth & Security Model: Centralized OAuth vs. Wallet-Encrypted Token Standard
- **Trade-off:** Standard Firebase Auth requires user emails, phone numbers, or third-party identity providers, contradicting CEO requirements.
- **Selected Strategy:** **Wallet-Key Hash Authentication (Argon2id + JWT + AES-GCM-256)**.
- **Key Flow:**
  1. User enters `Wallet Username` + `Passphrase`.
  2. Client uses Web Crypto `PBKDF2` (100,000 iterations, SHA-256) to derive a **Client Master Key (CMK)** locally.
  3. Client sends `HMAC-SHA256(CMK, "auth_login")` to server.
  4. Server verifies hash against stored `argon2id` hash and issues a signed JWT (`RFC 7519`) containing `wallet_id` valid for 30 days.
  5. Local data in IndexedDB is optionally encrypted at rest using AES-GCM with the CMK.

---

## 4. Comprehensive Schema Definitions

### 4.1 Database Schemas (Prisma / SQL - Server Side)

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model Wallet {
  id               String          @id @default(uuid())
  username         String          @unique @db.VarChar(64)
  password_hash    String          @db.VarChar(255)
  salt             String          @db.VarChar(128)
  balance_cents    BigInt          @default(0)
  currency         String          @default("USD") @db.VarChar(3)
  created_at       DateTime        @default(now())
  updated_at       DateTime        @updatedAt
  
  lists            ShoppingList[]
  expenses         Expense[]
  transactions     Transaction[]
  sync_logs        SyncLog[]

  @@index([username])
}

model ShoppingList {
  id               String          @id @default(uuid())
  wallet_id        String
  wallet           Wallet          @relation(fields: [wallet_id], references: [id], onDelete: Cascade)
  title            String          @db.VarChar(100)
  color_code       String?         @default("#3B82F6") @db.VarChar(7)
  is_archived      Boolean         @default(false)
  version          Int             @default(1)
  created_at       DateTime        @default(now())
  updated_at       DateTime        @updatedAt

  items            ListItem[]

  @@index([wallet_id])
}

enum ItemCategory {
  FRUITS
  VEGETABLES
  DAIRY
  MEAT_SEAFOOD
  BAKERY
  PANTRY
  BEVERAGES
  HOUSEHOLD
  PERSONAL_CARE
  ELECTRONICS
  OTHER
}

model ListItem {
  id               String          @id @default(uuid())
  list_id          String
  list             ShoppingList    @relation(fields: [list_id], references: [id], onDelete: Cascade)
  name             String          @db.VarChar(120)
  category         ItemCategory    @default(OTHER)
  quantity         Float           @default(1.0)
  unit             String?         @default("pcs") @db.VarChar(20)
  estimated_cents  Int?            @default(0)
  notes            String?         @db.Text
  is_checked       Boolean         @default(false)
  is_low_stock     Boolean         @default(false)
  version          Int             @default(1)
  created_at       DateTime        @default(now())
  updated_at       DateTime        @updatedAt

  @@index([list_id])
  @@index([category])
}

enum ExpenseCategory {
  GROCERIES
  RENT
  ELECTRICITY
  GAS_CAR
  LUXURY
  ENTERTAINMENT
  HEALTH
  SUBSCRIPTIONS
  OTHER
}

model Expense {
  id               String          @id @default(uuid())
  wallet_id        String
  wallet           Wallet          @relation(fields: [wallet_id], references: [id], onDelete: Cascade)
  title            String          @db.VarChar(120)
  category         ExpenseCategory @default(OTHER)
  amount_cents     BigInt
  date             DateTime        @default(now())
  notes            String?         @db.Text
  created_at       DateTime        @default(now())
  updated_at       DateTime        @updatedAt

  @@index([wallet_id, date])
  @@index([category])
}

enum TransactionType {
  DEPOSIT
  PURCHASE_CHECKOUT
  EXPENSE_PAYMENT
  REFUND
}

model Transaction {
  id               String          @id @default(uuid())
  wallet_id        String
  wallet           Wallet          @relation(fields: [wallet_id], references: [id], onDelete: Cascade)
  type             TransactionType
  amount_cents     BigInt          // Positive for DEPOSIT/REFUND, Negative for PURCHASE/EXPENSE
  balance_after    BigInt
  reference_id     String?         // ShoppingList ID or Expense ID
  description      String          @db.VarChar(255)
  created_at       DateTime        @default(now())

  @@index([wallet_id, created_at])
}

model SyncLog {
  id               String          @id @default(uuid())
  wallet_id        String
  wallet           Wallet          @relation(fields: [wallet_id], references: [id], onDelete: Cascade)
  device_id        String          @db.VarChar(64)
  entity_type      String          @db.VarChar(32) // "list", "item", "expense", "wallet"
  entity_id        String          @db.VarChar(64)
  operation        String          @db.VarChar(10) // "INSERT", "UPDATE", "DELETE"
  payload          Json
  client_timestamp DateTime
  created_at       DateTime        @default(now())

  @@index([wallet_id, created_at])
}
```

---

## 5. Failure Modes, Edge Cases & Mitigation Strategies

### 5.1 Failure Mode: Offline Purchase Check-in Race Conditions
- **Scenario:** User edits items and checks out a shopping list in offline mode on Device A (deducting $50 from local wallet). Simultaneously, Device B (online) records a rent expense of $800. Wallet actual balance was $820.
- **Risk:** Overdraft or negative wallet balance, data desynchronization upon reconnect.
- **Mitigation Strategy:**
  1. Balance calculations are strictly transaction-log backed on the server using **Postgres Serialized Transactions (`ISOLATION LEVEL SERIALIZABLE`)**.
  2. Offline check-ins compute local balance provisionally.
  3. When Device A syncs, the backend executes atomic ledger balance evaluation:
     ```sql
     BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
     SELECT balance_cents FROM "Wallet" WHERE id = $1 FOR UPDATE;
     -- Calculate total delta; if balance_cents + delta < 0, flag transaction with status 'PENDING_OVERDRAFT_REVIEW'
     COMMIT;
     ```

### 5.2 Failure Mode: Browser Local Storage / IndexedDB Eviction
- **Scenario:** iOS Safari under disk pressure automatically clears IndexedDB storage after 7 days of non-use.
- **Risk:** Total loss of offline-created lists and un-synced financial entries.
- **Mitigation Strategy:**
  1. Call `navigator.storage.persist()` on app init to request durable storage reservation.
  2. Maintain a secondary background backup inside `CacheStorage` via Service Worker for pending sync mutations (`outbox_queue`).

### 5.3 Failure Mode: Web Notification Constraints on iOS Safari
- **Scenario:** Web Push API and background notifications fail on iOS web app unless installed to Home Screen (PWA mode).
- **Risk:** Low stock notifications fail to deliver.
- **Mitigation Strategy:**
  1. Implement both **In-App Toast Queue System** (foreground) and **Web Notification API** (background/push).
  2. Add prompt UI detecting Safari iOS standalone state, instructing user to "Add to Home Screen" to unlock low-stock background alerts.

---

## 6. Security Vulnerabilities & Regulatory Compliance Analysis

### 6.1 Vulnerabilities Audited
1. **OWASP A02:2021 - Cryptographic Failures:** Plaintext balances in IndexedDB.
   - *Fix:* AES-256-GCM encryption layer over financial fields using Web Crypto API before persisting to IndexedDB if user enables "Secure Wallet Locking".
2. **OWASP A07:2021 - Identification & Authentication Failures:** Brute forcing simple wallet passwords.
   - *Fix:* Rate-limiting at Express API Gateway (`express-rate-limit`: max 5 login attempts per IP per 15 minutes) + Argon2id memory-hard hashing parameter `m=65536, t=3, p=4`.
3. **Replay Attacks on Realtime Sync:**
   - *Fix:* Sync messages require signed JWT with nonce and monotonic sequence numbers per device.

### 6.2 Licensing & Dependency Compliance
All selected npm packages comply strictly with permissive licensing models:
- **React, Vite, Express, Socket.IO, Dexie.js, Prisma, Tailwind CSS:** MIT / Apache 2.0.
- **Zero Copyleft or AGPL-3.0 Dependencies:** Ensured no GPL/AGPL libraries were introduced into the frontend runtime bundle.

---

## 7. Operational Workflow & Workload Allocation (Ziad & Maya)

| Sprint Phase | Ziad (Lead: Auth, Wallet, Security, Notifications) | Maya (Lead: Lists, Items, Offline Engine, Expenses) |
| :--- | :--- | :--- |
| **Phase 1: Foundation (Days 1-3)** | • Express REST API Server setup & Prisma schema setup.<br>• Wallet Auth API (Username/Password registration & JWT flow).<br>• Web Crypto CMK key derivation integration. | • React + Vite + Tailwind PWA boilerplate setup.<br>• Dexie.js IndexedDB local database schema creation.<br>• Service Worker & manifest configuration for offline PWA. |
| **Phase 2: Core Features (Days 4-7)** | • Wallet financial engine (Deposit, Balance API, Ledger).<br>• Expense tracking endpoints & category calculations.<br>• Low stock notification triggers & Web Push API setup. | • Shopping List UI & CRUD components.<br>• Item Management UI (Categories, Quantity, Notes).<br>• IndexedDB local sync queue (`outbox_queue`). |
| **Phase 3: Sync & Security (Days 8-10)** | • Socket.IO Realtime Gateway implementation.<br>• Security hardening (Argon2, AES-GCM local storage, OWASP audit). | • Multi-device sync handler & conflict resolution logic (LWW).<br>• Offline purchase checkout integration with Wallet balance. |
| **Phase 4: QA & Launch (Days 11-14)** | • Integration testing for Financial Ledger & Overdrafts.<br>• Performance benchmarking & Deployment. | • E2E Cypress tests for offline list edits & reconnection.<br>• PWA offline cache verification & app store build prep. |
