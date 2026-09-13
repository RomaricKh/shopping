# Sprint Roadmap & Task Allocation Matrix

**Project Title:** Shopping List Manager & Wallet System  
**Lead Researchers & Engineers:** Nour (Research Lead), Ziad (Backend/Auth/Security), Maya (Frontend/Offline Sync/UI)  
**Sprint Duration:** 2 Weeks (14 Days)  

---

## 1. Milestone Breakdown & Assignees

### Milestone 1: Wallet-Centric Authentication & Identity Primitive
- **Lead:** Ziad
- **Deliverables:**
  - `POST /api/v1/wallet/register` & `POST /api/v1/wallet/login` using **Argon2id** password hashing.
  - JWT creation & validation middleware (`RFC 7519`).
  - Rate limiting middleware on wallet login endpoints (`express-rate-limit`).
  - Frontend Wallet Creation & Login UI screens.

### Milestone 2: Offline-First Local Data Storage Engine
- **Lead:** Maya
- **Deliverables:**
  - Dexie.js (IndexedDB) schema setup (`wallets`, `lists`, `items`, `expenses`, `outbox_mutations`).
  - Service Worker integration for PWA assets caching and offline fallback mode.
  - Reactive Dexie `useLiveQuery` hooks for list and item reactive UI rendering.

### Milestone 3: Core Shopping List & Item Management
- **Lead:** Maya
- **Deliverables:**
  - List CRUD operations (Create, Edit, Archive, Delete).
  - Item CRUD with Categories (Fruits, Veggies, Dairy, etc.), Quantities, Units, and Notes.
  - Low-stock toggle trigger and UI indicators.

### Milestone 4: Personal Wallet Ledger & Purchase Checkout
- **Lead:** Ziad
- **Deliverables:**
  - Database transactional financial ledger model (Integer Cents).
  - Balance deposit endpoint (`POST /api/v1/wallet/deposit`).
  - Shopping List Checkout transaction API (`POST /api/v1/lists/:id/checkout`) deducting calculated item costs from wallet balance atomically.

### Milestone 5: Broad Expense Tracking
- **Lead:** Ziad & Maya (Joint)
- **Deliverables:**
  - Expense tracking categories: Rent, Electricity, Car Gas, Luxury, Subscriptions.
  - Add/Edit Expense modal with date picker and integer currency parsing.
  - Expense summary & monthly aggregate visualization (Chart UI / breakdown).

### Milestone 6: Realtime Delta Synchronization Engine
- **Lead:** Maya & Ziad
- **Deliverables:**
  - Socket.IO connection handler bound to `wallet_{wallet_id}` room.
  - Client `OutboxManager` flushing local offline mutation queue upon network status `online`.
  - Server Last-Write-Wins (LWW) conflict resolver for conflicting list/item modifications.

### Milestone 7: Low Stock & Reorder Notifications
- **Lead:** Ziad
- **Deliverables:**
  - Browser Web Notification API triggers when items marked `is_low_stock = true`.
  - In-app notification toast system for non-PWA environments.

### Milestone 8: Security Audit, Encryption & Final Deployment
- **Lead:** Nour & Ziad
- **Deliverables:**
  - Client Web Crypto PBKDF2/AES-GCM encrypted local storage optional layer.
  - Automated Jest unit tests & Cypress E2E offline sync integration testing.
  - Production build optimizations & containerization (Docker + Nginx PWA reverse proxy).

---

## 2. Weekly Execution Timeline

| Day | Task Focus | Owner | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Day 1-2** | System Bootstrap & Wallet Schema | Ziad | Express + Prisma Postgres database migrations complete. |
| **Day 3-4** | Offline PWA Shell & IndexedDB | Maya | Dexie.js local DB instantiated and working offline in browser. |
| **Day 5-6** | Shopping Lists & Category UI | Maya | Full CRUD for Lists & Items rendered reactively from Dexie. |
| **Day 7-8** | Wallet Ledger & Expense Engine | Ziad | Balance calculation & deposit ledger endpoints tested. |
| **Day 9-10**| Socket.IO Delta Sync Engine | Maya/Ziad | Offline mutations sync automatically on network reconnect. |
| **Day 11-12**| Notifications & Expense Analytics | Ziad/Maya | Low stock notifications and expense pie/bar charts rendering. |
| **Day 13-14**| End-to-End Testing & Deployment | Team | Zero critical vulnerabilities, PWA passing Lighthouse offline test. |
