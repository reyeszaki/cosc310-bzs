# M2 Sprint Planning and Outcomes

## Sprint Information

- **Sprint / Milestone:** Milestone 2 — Integrated Core System (customer → restaurant → menu → cart → checkout → order)
- **Sprint dates:** November 16–20, 2026
- **Planning:** Asynchronous in the team Discord (`#general`) and through GitHub issues and pull requests, November 18–20, 2026
- **Facilitator:**
- **Record status:** Final — sprint completed November 20, 2026

### Team Members

All four members took part in the asynchronous planning and coordination in Discord.

- Beab Girma Yifrashewa
- Jean Zachary Reyes
- Shawn Goh
- Keyan Sharifpour

## 1. Sprint Goal

Build on the M1 restaurant and menu flow so a signed-in customer can browse restaurants and menus, add available items to a cart, update or remove them, check out, and see the created order — with business rules enforced by the backend and the flow connected to the frontend.

## 2. Sprint Backlog

| User Story | Description | Priority | Owner | Dependencies | Result |
| --- | --- | --- | --- | --- | --- |
| Accounts epic #46: US-01 #51, US-02 #52, US-35 #89, US-36 #90 | Sign up, log in/out, view and update profile and delivery address, deactivate account, backend authentication and role checks | High | Beab | None | Done — PR #88 |
| Cart backend #57 | View cart, add/remove items, update quantities, clear cart, backend-calculated totals | High | Keyan (cart backend and tests), Zach (authentication wiring) | Accounts (current customer), restaurant and menu data | Done — PR #91 |
| US-10 Place order #60 | Validate the cart, recalculate prices, create and persist the order, then clear the cart | High | Zach | Cart, accounts, order storage | Done — PR #92 |
| Frontend integration | Connect sign-up, sign-in, cart and checkout to the browser UI | High | Zach | Accounts, cart and checkout APIs | Done — PR #93 |
| Menu simplification | Replace menu `PATCH` updates with `PUT` and simplify menu code | Medium | Zach | None | Done — PR #45 |
| US-03 Reset password #53 | Reset a forgotten password | Low | Beab | Accounts | Moved to M3 (not required for M2) |
| Menu category management | Manage menu categories | Low | Zach | Menu | Moved to M3 — PR #87 has merge conflicts with `main` |
| Restaurant and menu permissions | Restrict restaurant and menu management to owners and admins | Medium | Zach | Accounts | Moved to M3 — PR #94 needs a seeded admin/owner account first |

## 3. Task Decomposition

### Accounts and authentication — Beab

- [x] User schemas, JSON repository and service (sign up, login/logout, profile update, deactivation)
- [x] Salted password hashing; passwords never returned by the API
- [x] Shared authentication in `app/api/dependencies.py` (`get_current_user`, `require_role`, `require_active`)
- [x] Manual API testing in `/docs` (201, 401, 403, 409, 422 cases, logout, deactivation, restart persistence)
- [x] pytest tests: repository persistence, API authentication, role check, multi-subsystem flow, regression
- [x] Provenance entry

### Cart — Keyan, Zach, Shawn

- [x] Cart repository, schema, service and routes (Keyan)
- [x] Connect cart to authentication; reject closed restaurants (Zach)
- [x] Cart tests and fixture fix (Keyan)
- [x] Handle `LookupError` in get/clear cart (404 instead of 500) and use a source-relative data path (Shawn, after review by Beab)

### Checkout and orders — Zach, Shawn

- [x] Checkout service, order repository and order routes (Zach)
- [x] Checkout integration tests (Zach)
- [x] Inject the order service through a FastAPI dependency; new `TestClient` per test (Shawn)

### Frontend — Zach

- [x] Connect accounts, cart and checkout to the frontend
- [x] Customer error handling and checkout retries

### Shared handoff and submission

- [x] PRs reviewed by a teammate before merging (#88 by Shawn, #91 by Beab, #92 and #93 by Shawn)
- [x] CI passing on merged PRs

## 4. Dependencies and Integration

| Dependency | Who Coordinated It | Resolution |
| --- | --- | --- |
| Cart and checkout need the current customer | Beab, Zach | Cart and order routes use `require_role("customer")` from `dependencies.py`; deactivated customers are rejected |
| Cart needs valid restaurant and menu items | Keyan, Zach | Cart service checks the restaurant is open and the item exists and is available |
| Checkout needs the customer's cart | Zach, Keyan | Checkout reads the cart through the cart service and clears it only after the order is saved |
| #91 and #92 both added cart files | Beab, Zach | Merged #91 first, then updated #92 from `main` |

## 5. Risks and Blockers

| Risk | What Happened / Action |
| --- | --- |
| Cart could return 500 when a cart item was removed from the menu | Found in review of #91; fixed before merge (404) |
| Cart data path depended on where the server was started | Found in review of #91; fixed with `Path(__file__)` |
| Teammates got 401 when testing login in `/docs` | Cause was the default `"string"` request body / missing bearer token; shared steps in Discord |
| Late, large PRs (#94, 16 files) | Not merged for M2; to be split into smaller PRs in M3 |

## 6. Definition of Done

- [x] Customer → restaurant → menu → cart → checkout → order flow works on `main`
- [x] Business rules enforced by the backend (deactivated customer, single-restaurant cart, unavailable items, authentication and roles)
- [x] Tests cover successful operations and error cases; CI passes on merged PRs
- [x] Each merged PR reviewed by a teammate

## 7. Sprint Commitment

| Team Member | Responsibility | Status |
| --- | --- | --- |
| Beab Girma Yifrashewa | Accounts and authentication (#88); review of cart PR #91 | Complete |
| Jean Zachary Reyes | Checkout and orders (#92), frontend integration (#93), menu updates (#45), cart authentication wiring | Complete |
| Shawn Goh | Reviews and merges (#88, #92, #93); cart fixes in #91; order service refactor in #92 | Complete |
| Keyan Sharifpour | Cart backend and tests (#91) | Complete |