# Technical Specification: Shopping List & Personal Wallet Manager

**Document Version:** 1.0.0  
**Status:** Approved & Ready for Development  
**Architect:** Marc, Technical Project Manager & System Architect  
**Contributors:** Ziad (Senior Backend Engineer), Maya (Senior Frontend Engineer), Nour (Principal Systems Researcher)  

---

## 1. System Overview & Architecture Philosophy

### 1.1 Core Domain Philosophy
The Shopping List & Personal Wallet Manager is built around a **Wallet-Centric Identity Primitive**. In accordance with explicit product directives, traditional multi-tenant user accounts, email verifications, and user profile endpoints are omitted. 

Instead:
- The **`Wallet` entity** is the root aggregate, cryptographic boundary, and financial ledger.
- A user authenticates into a specific wallet using a `username` (wallet identity slug) and `password`.
- The `password` serves dual purposes:
  1. Authenticating with the backend using server-side **Argon2id** password hashing.
  2. Deriving client-side encryption key seeds via **PBKDF2** (W3C WebCrypto API).
- All Shopping Lists, List Items, Purchase Checkout Receipts, and Financial Expenses (Rent, Electricity, Car Gas, Luxury, etc.) strictly belong to a `Wallet`.

```
                    +------------------------------------------+
                    |             Wallet Aggregate             |
                    |  (username, balance_cents, currency)     |
                    +--------------------+---------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
+------------------+           +------------------+            +-------------------+
|  Shopping Lists  |           |   Expense Logs   |            | Transaction Ledger|
|  (Lists & Items) |           | (Rent, Gas, etc) |            | (Deposits/Debits) |
+------------------+           +------------------+            +-------------------+
```

---

## 2. Tech Stack & Version Pins

| Scope | Technology | Version Pin | License | Architectural Role |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend UI** | React | `18.3.1` | MIT | Component view layer, reactive state |
| **Build Tooling** | Vite | `5.2.x` | MIT | PWA bundling, HMR, Service Worker support |
| **Offline Storage** | Dexie.js | `4.0.1` | Apache-2.0 | Type-safe IndexedDB wrapper, reactive live queries |
| **State & Fetching** | TanStack Query | `5.28.x` | MIT | Optimistic updates, background sync retry queues |
| **Styling & Icons** | Tailwind CSS + Lucide | `3.4.x` / `0.359.0` | MIT | Responsive mobile UI design system |
| **Backend Runtime** | Node.js + Express | `20.12.x` / `4.19.2` | MIT | Asynchronous REST and WS server |
| **Realtime Engine** | Socket.IO | `4.7.5` | MIT | Bidirectional sync with `wallet_{id}` room isolation |
| **Database & ORM** | PostgreSQL + Prisma | `16.2` / `5.11.0` | Apache-2.0 | ACID transactional storage & migration management |
| **Authentication** | Argon2id + WebCrypto | Argon2 `0.40.1` | MIT | OWASP memory-hard password verification & local key derivation |

---

## 3. Financial Math & Precision Standard

To eliminate floating-point precision drift in financial calculations (e.g. `0.1 + 0.2 = 0.30000000000000004`), all financial figures inside database schemas, API payloads, and state stores MUST be encoded as **64-bit Signed Integers representing cents** (Micro-Cents compliant RFC 8259).

- **Rule:** $1.00 USD = `100` cents. $1,250.50 = `125050` cents.
- **Frontend Presentation:** Format at display boundary only via `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`.
- **Database Rules:** Column types use PostgreSQL `BIGINT` mapped to JavaScript `BigInt` or sanitized numbers.

---

## 4. File & Module Structure Definition

```
shopping-list-wallet/
├── package.json
├── docker-compose.yml
├── .env.example
├── SPEC.md
├── ROADMAP.md
├── server/                           # Backend System (Ziad Lead)
│   ├── src/
│   │   ├── config/
│   │   │   ├── database.ts           # Prisma client initialization
│   │   │   └── environment.ts        # Enforced environment variable validation
│   │   ├── controllers/
│   │   │   ├── auth.controller.ts     # Wallet auth & token issuance
│   │   │   ├── list.controller.ts     # Shopping list & item endpoints
│   │   │   ├── wallet.controller.ts   # Wallet balance, deposits, checkouts
│   │   │   ├── expense.controller.ts  # Expense tracking endpoints
│   │   │   └── sync.controller.ts     # Delta mutation sync batch endpoint
│   │   ├── middleware/
│   │   │   ├── auth.middleware.ts     # JWT Bearer token validator
│   │   │   ├── error.middleware.ts    # Centralized HTTP error handler
│   │   │   └── rateLimit.middleware.ts# Anti-bruteforce protection
│   │   ├── services/
│   │   │   ├── auth.service.ts        # Argon2id hashing & verification logic
│   │   │   ├── wallet.service.ts      # Ledger balance transactions with isolation
│   │   │   ├── sync.service.ts        # Delta mutation LWW conflict resolution
│   │   │   └── notification.service.ts# Web Push notification dispatcher
│   │   ├── sockets/
│   │   │   ├── socket.server.ts       # Socket.IO instance and connection handler
│   │   │   └── sync.gateway.ts        # Realtime delta emission & room broadcast
│   │   ├── routes/
│   │   │   ├── auth.routes.ts
│   │   │   ├── list.routes.ts
│   │   │   ├── wallet.routes.ts
│   │   │   ├── expense.routes.ts
│   │   │   └── sync.routes.ts
│   │   └── index.ts                   # Express & Socket server entry point
│   ├── prisma/
│   │   └── schema.prisma              # PostgreSQL relational database schema
│   └── tests/                         # Integration & unit test suite
│
└── client/                            # Frontend System (Maya Lead)
    ├── src/
    │   ├── assets/
    │   ├── components/
    │   │   ├── common/                # Buttons, Modal, Toast Container, Badges
    │   │   ├── auth/                  # Wallet Login / Create Form
    │   │   ├── lists/                 # List View, Item Form, Low-Stock Badges
    │   │   ├── wallet/                # Balance Header, Deposit Modal, Checkout Receipt
    │   │   └── expenses/              # Expense Entry Form, Category Analytics Charts
    │   ├── db/
    │   │   ├── schema.ts              # Dexie.js IndexedDB schema & types
    │   │   └── dexie.ts               # Dexie instance initialization
    │   ├── hooks/
    │   │   ├── useWalletAuth.ts       # Wallet session & PBKDF2 context
    │   │   ├── useLiveLists.ts        # Dexie useLiveQuery hooks for lists & items
    │   │   ├── useLiveExpenses.ts     # Dexie useLiveQuery hooks for expenses
    │   │   └── useSyncEngine.ts       # Outbox sync trigger & online network monitor
    │   ├── services/
    │   │   ├── api.client.ts          # Axios / Fetch client with Bearer token injection
    │   │   ├── crypto.service.ts      # WebCrypto PBKDF2 key derivation & AES-GCM helper
    │   │   ├── outbox.service.ts      # Dexie outbox queue append and flush worker
    │   │   └── socket.client.ts       # Socket.IO client setup & room sub listener
    │   ├── context/
    │   │   ├── AuthContext.tsx
    │   │   └── SyncContext.tsx
    │   ├── App.tsx
    │   └── main.tsx
    ├── public/
    │   ├── manifest.json              # PWA Installation manifest
    │   └── sw.js                      # Service Worker for offline fallback
    ├── vite.config.ts
    └── tailwind.config.js
```

---

## 5. Module Contracts & Workload Assignment Matrix

### 5.1 Ziad — Backend, Wallet Engine & Security Contracts
1. **Wallet Authentication (`auth.service.ts` / `auth.controller.ts`)**:
   - `POST /api/v1/auth/wallet/access`: Accepts `{ username, password }`.
   - Hashes/verifies via Argon2id (`timeCost: 3`, `memoryCost: 65536`, `parallelism: 4`).
   - Issues 30-day JWT signed token containing `wallet_id` and `username`.
2. **Wallet & Financial Ledger (`wallet.service.ts`)**:
   - `GET /api/v1/wallet`: Returns current balance (cents) and summary.
   - `POST /api/v1/wallet/deposit`: Adds balance in cents; creates `Transaction` record (TYPE: `DEPOSIT`).
   - `POST /api/v1/wallet/checkout`: Converts a Checked-off `ShoppingList` into a purchase event, computes total estimated cents, verifies sufficient balance, debits wallet balance inside PostgreSQL `SERIALIZABLE` transaction with `SELECT ... FOR UPDATE`, records `Transaction` record (TYPE: `PURCHASE_CHECKOUT`), and archives the list.
3. **Expense Management (`expense.service.ts`)**:
   - `GET /api/v1/expenses`: Query expenses by category (Rent, Electricity, Gas, Luxury, etc.) and date range.
   - `POST /api/v1/expenses`: Insert expense, immediately deduct amount from wallet balance within ACID transaction, append transaction ledger entry (TYPE: `EXPENSE_PAYMENT`).
4. **Sync Gateway & Socket.IO (`sync.service.ts`, `sync.gateway.ts`)**:
   - `POST /api/v1/sync/delta`: Accept batch array of `OutboxMutation` items. Execute LWW comparison using `version` and `updated_at`. Returns sync outcome status per entity.
   - Socket.IO gateway setup listening on room `wallet_{wallet_id}`. Emits `entity_updated` events when another device syncs updates.

### 5.2 Maya — Frontend UI, Dexie Outbox Engine & PWA Contracts
1. **Dexie Offline Core (`db/schema.ts`, `outbox.service.ts`)**:
   - Local tables: `wallets`, `lists`, `items`, `expenses`, `outbox`.
   - Every user mutation locally updates Dexie tables first and queues an entry into `outbox` (`INSERT`, `UPDATE`, `DELETE`).
2. **Offline Outbox Worker & Reconnect Sync (`hooks/useSyncEngine.ts`)**:
   - Monitors `navigator.onLine` and `window.addEventListener('online')`.
   - When online, reads all records in `outbox`, sends to `POST /api/v1/sync/delta`. On `200 OK`, deletes flushed outbox items.
3. **Shopping List & Item UI Components (`components/lists/*`)**:
   - Views for active and archived lists. Color badges, item entry with auto-category detection (Fruits, Vegetables, Dairy, Household, etc.).
   - Item controls: quantity, unit, estimated unit price in cents, low-stock toggle (`is_low_stock`), notes modal.
   - Instant live queries using `useLiveQuery` from Dexie.
4. **Personal Wallet & Expense Dashboard UI (`components/wallet/*`, `components/expenses/*`)**:
   - Real-time balance counter.
   - Quick deposit modal.
   - One-click "Check Out & Purchase List" with instant local balance validation.
   - Expense log form with category selector (Rent, Electricity, Car Gas, Luxury, Subscriptions, Other).
   - Category spending summary chart.

---

## 6. Full Database Schemas & Interfaces

### 6.1 Server-Side PostgreSQL Schema (Prisma Schema)

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
  amount_cents     BigInt
  balance_after    BigInt
  reference_id     String?
  description      String          @db.VarChar(255)
  created_at       DateTime        @default(now())

  @@index([wallet_id, created_at])
}

model SyncLog {
  id               String          @id @default(uuid())
  wallet_id        String
  wallet           Wallet          @relation(fields: [wallet_id], references: [id], onDelete: Cascade)
  device_id        String          @db.VarChar(64)
  entity_type      String          @db.VarChar(32)
  entity_id        String          @db.VarChar(64)
  operation        String          @db.VarChar(10)
  payload          Json
  client_timestamp DateTime
  created_at       DateTime        @default(now())

  @@index([wallet_id, created_at])
}
```

### 6.2 Client-Side Dexie.js Schema & Interfaces (`client/src/db/schema.ts`)

```typescript
import Dexie, { Table } from 'dexie';

export interface LocalWallet {
  id: string;
  username: string;
  balance_cents: number;
  currency: string;
  updated_at: string;
}

export interface LocalShoppingList {
  id: string;
  wallet_id: string;
  title: string;
  color_code: string;
  is_archived: number; // 0 = active, 1 = archived
  version: number;
  updated_at: string;
}

export interface LocalListItem {
  id: string;
  list_id: string;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  estimated_cents: number;
  notes?: string;
  is_checked: number; // 0 or 1
  is_low_stock: number; // 0 or 1
  version: number;
  updated_at: string;
}

export interface LocalExpense {
  id: string;
  wallet_id: string;
  title: string;
  category: 'GROCERIES' | 'RENT' | 'ELECTRICITY' | 'GAS_CAR' | 'LUXURY' | 'ENTERTAINMENT' | 'HEALTH' | 'SUBSCRIPTIONS' | 'OTHER';
  amount_cents: number;
  date: string;
  notes?: string;
  updated_at: string;
}

export interface OutboxMutation {
  id?: number;
  wallet_id: string;
  entity_type: 'list' | 'item' | 'expense' | 'wallet';
  entity_id: string;
  operation: 'INSERT' | 'UPDATE' | 'DELETE';
  payload: any;
  created_at: string;
}

export class ShoppingWalletDB extends Dexie {
  wallets!: Table<LocalWallet, string>;
  lists!: Table<LocalShoppingList, string>;
  items!: Table<LocalListItem, string>;
  expenses!: Table<LocalExpense, string>;
  outbox!: Table<OutboxMutation, number>;

  constructor() {
    super('ShoppingWalletDB');
    this.version(1).stores({
      wallets: 'id, username',
      lists: 'id, wallet_id, is_archived, updated_at',
      items: 'id, list_id, category, is_checked, is_low_stock, updated_at',
      expenses: 'id, wallet_id, category, date, updated_at',
      outbox: '++id, wallet_id, entity_type, created_at'
    });
  }
}

export const db = new ShoppingWalletDB();
```

---

## 7. Sync Protocol & Conflict Resolution Specification

1. **Local-First Writes**:
   - When a user performs an action (e.g. adding item to list or logging rent expense), the app writes to Dexie IndexedDB immediately.
   - An `OutboxMutation` object is added to the local `outbox` table in Dexie.
2. **Delta Flush Procedure**:
   - Upon network connection, `OutboxService` queries all outbox records sorted by `id ASC`.
   - Sends HTTP `POST /api/v1/sync/delta` with payload `{ mutations: OutboxMutation[] }`.
3. **Server-Side LWW Processing**:
   - For each mutation:
     - Compare server `version` vs payload `version`.
     - If `payload.version >= server.version`, apply update and increment `version` by 1.
     - If `payload.version < server.version`, reject incoming field updates (Last-Write-Wins based on version & timestamp).
4. **Realtime Socket Broadcast**:
   - Server broadcasts the finalized entity mutation event over Socket.IO room `wallet_{wallet_id}`.
   - Passive connected clients update their local Dexie DB and UI triggers re-render via `useLiveQuery`.

---

## 8. Quality Assurance & Architectural Criteria

1. **Zero Currency Drift**: Guaranteed by integer cents calculations across client, Express, and PostgreSQL `BIGINT`.
2. **Seamless Offline Execution**: All UI CRUD functions execute without active internet connection.
3. **Storage Persistence**: Web PWA uses `navigator.storage.persist()` on app setup.
4. **Security Standard**: Argon2id password hashing, WebCrypto client key derivation, JWT room authentication, strict parameter sanitization.
