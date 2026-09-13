# Engineering Roadmap & Milestone Breakdown

**Project Title:** Shopping List & Personal Wallet Manager  
**Engineering Leads:** Ziad (Backend & Systems) & Maya (Frontend & Offline Engine)  
**Project Manager:** Marc (Technical PM & Architect)  
**Timeline:** 14-Day Accelerated Sprint  

---

## Sprint Overview & Core Workload Distribution

```
                       [ DAY 1 - DAY 3: FOUNDATION & STORAGE ]
             +---------------------------------------------------------+
             | Ziad: Express, Prisma Postgres, Argon2id Auth API       |
             | Maya: Vite React Tailwind Shell, Dexie IndexedDB Schema |
             +---------------------------------------------------------+
                                          |
                                          v
                    [ DAY 4 - DAY 7: CORE FEATURES & BUSINESS LOGIC ]
             +---------------------------------------------------------+
             | Ziad: Ledger Isolation, Expense APIs, Checkout Logic    |
             | Maya: Shopping Lists CRUD, Item Categories, Expense Dashboard |
             +---------------------------------------------------------+
                                          |
                                          v
                      [ DAY 8 - DAY 10: REALTIME & OFFLINE SYNC ]
             +---------------------------------------------------------+
             | Ziad: Socket.IO Gateway, Delta Mutation LWW Processor   |
             | Maya: Dexie Outbox Engine, Reconnect Sync & PWA SW      |
             +---------------------------------------------------------+
                                          |
                                          v
                      [ DAY 11 - DAY 14: TESTING, POLISH & LAUNCH ]
             +---------------------------------------------------------+
             | Ziad: Push Notifications, Rate Limiting, Load Audit     |
             | Maya: In-App Toasts, Offline Cypress E2E Tests, PWA Audit|
             +---------------------------------------------------------+
```

---

## Detailed Milestones & Tasks

### Milestone 1: Environment Setup & Wallet Authentication Engine
- **Lead Owner:** Ziad
- **Dependencies:** None
- **Tasks:**
  - [ ] Initialize Express.js TypeScript backend boilerplate in `server/`.
  - [ ] Setup Prisma ORM connected to PostgreSQL database container.
  - [ ] Design Prisma schema for `Wallet`, `ShoppingList`, `ListItem`, `Expense`, `Transaction`, `SyncLog`.
  - [ ] Implement `Argon2id` password hashing module (`timeCost: 3`, `memoryCost: 65536`, `parallelism: 4`).
  - [ ] Build `POST /api/v1/auth/wallet/access` endpoint for seamless login/wallet creation.
  - [ ] Implement JWT token issuance (30-day expiry) with Bearer auth middleware.

### Milestone 2: Frontend PWA Shell & Dexie IndexedDB Architecture
- **Lead Owner:** Maya
- **Dependencies:** None
- **Tasks:**
  - [ ] Initialize React + Vite + Tailwind CSS project in `client/`.
  - [ ] Implement Dexie.js IndexedDB schema (`wallets`, `lists`, `items`, `expenses`, `outbox`).
  - [ ] Configure `WebCrypto API` helper module for PBKDF2 client key derivation.
  - [ ] Set up Service Worker (`sw.js`) and PWA `manifest.json` for offline asset caching.
  - [ ] Implement browser `navigator.storage.persist()` registration trigger.

### Milestone 3: Shopping List & Item Management (Offline First)
- **Lead Owner:** Maya
- **Dependencies:** Milestone 2
- **Tasks:**
  - [ ] Build Shopping List Dashboard component with creation modal and color code selections.
  - [ ] Build List Detail View with reactive `useLiveQuery` hooks.
  - [ ] Implement Item CRUD with category dropdown (Fruits, Vegetables, Dairy, Household, etc.).
  - [ ] Add Item Quantity, Unit, Estimated Price in Cents, Notes Modal, and Low Stock Toggle (`is_low_stock`).
  - [ ] Implement auto-appending of mutations to Dexie `outbox` table.

### Milestone 4: Personal Wallet Ledger & Financial Transaction Engine
- **Lead Owner:** Ziad
- **Dependencies:** Milestone 1
- **Tasks:**
  - [ ] Implement `GET /api/v1/wallet` and `POST /api/v1/wallet/deposit`.
  - [ ] Implement `POST /api/v1/wallet/checkout` with PostgreSQL `SERIALIZABLE` isolation and `SELECT FOR UPDATE` locking.
  - [ ] Compute checked list estimated total cents, ensure non-negative balance, and record `Transaction` ledger log.
  - [ ] Build transaction history query endpoints.

### Milestone 5: Expense Tracking Engine (Rent, Electricity, Gas, Luxury)
- **Lead Owner:** Ziad (Backend) & Maya (Frontend)
- **Dependencies:** Milestone 3 & 4
- **Tasks:**
  - [ ] **Ziad:** Implement `POST /api/v1/expenses` and `GET /api/v1/expenses` with category filtering (`RENT`, `ELECTRICITY`, `GAS_CAR`, `LUXURY`, `GROCERIES`, `OTHER`).
  - [ ] **Ziad:** Auto-deduct expense amounts from wallet integer cents balance inside database transaction.
  - [ ] **Maya:** Build Expense Entry Form and Category Breakdown Dashboard with visual summary charts.
  - [ ] **Maya:** Hook expense inputs to local Dexie writes and Outbox Queue.

### Milestone 6: Socket.IO Realtime Engine & Reconnect Outbox Sync
- **Lead Owner:** Ziad (Backend) & Maya (Frontend)
- **Dependencies:** Milestone 1, 2, 3, 4, 5
- **Tasks:**
  - [ ] **Ziad:** Set up Socket.IO server with JWT token auth on connection handshake and `wallet_{id}` room join logic.
  - [ ] **Ziad:** Implement `POST /api/v1/sync/delta` endpoint processing batch outbox mutations with Last-Write-Wins (LWW) conflict resolution using version numbers and ISO timestamps.
  - [ ] **Maya:** Create `useSyncEngine` custom hook to monitor network state (`navigator.onLine`).
  - [ ] **Maya:** Implement automatic outbox flush worker on `online` event and Socket.IO real-time entity update listeners.

### Milestone 7: Low-Stock Notifications & Privacy Security Hardening
- **Lead Owner:** Ziad (Backend) & Maya (Frontend)
- **Dependencies:** Milestone 6
- **Tasks:**
  - [ ] **Ziad:** Configure Web Push Protocol triggers for low-stock items (`is_low_stock = true`).
  - [ ] **Ziad:** Implement strict Express rate limiting on auth endpoints to prevent passphrase brute forcing.
  - [ ] **Maya:** Implement local In-App Toast notification queue for low stock warnings.
  - [ ] **Maya:** Conduct XSS defense audit with DOMPurify for item notes and expense descriptions.

### Milestone 8: End-to-End Integration, Testing & Deployment
- **Lead Owner:** Joint (Ziad & Maya)
- **Dependencies:** Milestones 1 - 7
- **Tasks:**
  - [ ] Execute Cypress offline E2E test suite simulating network drop during list creation and re-connection sync.
  - [ ] Run financial audit test verifying zero floating-point cents drift across 10,000 randomized expense and deposit transactions.
  - [ ] Run Lighthouse PWA audit (Verify offline load, installability, performance score >= 90).
  - [ ] Package Node.js backend Docker container and static PWA build distribution.

---

## Critical Path & Risk Matrix

| Risk Scenario | Severity | Mitigation Strategy | Owner |
| :--- | :--- | :--- | :--- |
| **Concurrent Offline Overdraft** | High | PostgreSQL pessimistic lock (`FOR UPDATE`) on checkout; client receives `OVERDRAFT_WARNING` status on sync. | Ziad |
| **Browser Storage Eviction** | Medium | Request `navigator.storage.persist()`; redundancy backup in SW `CacheStorage`. | Maya |
| **Sync Race Conditions** | Medium | Incremental entity `version` counting with server LWW authority. | Ziad & Maya |
| **Financial Floating Drift** | Critical | Enforce strict integer cents across DB schema, JSON APIs, and Dexie models. | Ziad & Maya |
