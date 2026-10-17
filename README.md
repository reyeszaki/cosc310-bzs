# BZS — Food Delivery App

Team BZS's COSC 310 Milestone 1 restaurant and menu application. A browser frontend served by FastAPI connects restaurant discovery, details, restaurant management, and menu management to persistent JSON storage.

## Milestone 1 scope

- View restaurants; search names and filter by cuisine and open/closed status.
- View a selected restaurant's details and menu.
- Create, edit, open/close, and delete restaurants.
- Add, edit, and delete menu items; change price, category, and availability.
- Filter menus by category, including empty results and unavailable items.
- Validate requests and display API/network errors in the frontend.
- Preserve successful changes across application restarts.

Authentication, accounts, carts, orders, payments, and delivery tracking are outside this slice.

## Requirements and setup

- Python 3.14 (verified locally with 3.14.0).
- Git and the Python packages pinned in `requirements.txt`.
- A current browser. Node.js 22 or newer is needed only for frontend regression tests; no npm packages are required for those tests.

```bash
git clone https://github.com/reyeszaki/cosc310-bzs.git
cd cosc310-bzs
python3 -m venv .venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
python --version
python -m pip install -r requirements.txt
```

Each team member uses their own virtual environment; do not commit it.

## Run the application

From the project root, with the environment active:

```bash
python -m uvicorn app.main:app --reload
```

- Browser frontend: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Keep the terminal running; press Ctrl+C to stop. The frontend uses relative API URLs on the same server. Open the server URL rather than opening `static/index.html` directly. No separate frontend build or CORS configuration is needed.

## API contract

| Method | Path | Result |
| --- | --- | --- |
| GET | `/health` | 200: `{"status":"ok"}` |
| GET | `/restaurants` | 200: restaurant array; optional `search`, `cuisine`, `is_open` |
| POST | `/restaurants` | 201: created restaurant |
| GET | `/restaurants/{restaurant_id}` | 200: restaurant details |
| PUT | `/restaurants/{restaurant_id}` | 200: updated restaurant; all editable fields required |
| DELETE | `/restaurants/{restaurant_id}` | 200: deleted restaurant; 409 while it has menu items |
| GET | `/restaurants/{restaurant_id}/menu` | 200: `{"restaurant_id":1,"items":[...]}`; optional `category` |
| POST | `/restaurants/{restaurant_id}/menu/items` | 201: created menu item |
| PATCH | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 200: updated item; supplied fields only |
| DELETE | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 204: empty response |

Restaurant POST/PUT bodies require `name`, `cuisine`, `address`, and `is_open`. IDs are positive integers assigned by the server. Text is trimmed and cannot be blank. PUT retains the restaurant ID used by its menu.

```json
{"name":"Review Cafe","cuisine":"Cafe","address":"10 Main St","is_open":true}
```

Menu POST bodies require `name`, `description`, `price`, and `category`; `is_available` defaults to true. Prices must be positive with at most two decimal places and ten total digits. Responses include `id` and the owning `restaurant_id`; prices are JSON numbers displayed to two decimal places by the frontend.

```json
{"name":"Chef's Tea","description":"Hot green tea","price":3.25,"category":"drinks","is_available":true}
```

Menu PATCH accepts a nonempty subset, such as `{"price":4.50,"is_available":false}`. Omitted fields remain unchanged; explicit nulls, unknown fields, and ID changes are rejected. Restaurant bodies also reject unknown fields.

Restaurant search matches a name substring; cuisine matches the full cuisine. Menu category matches the full category. Text filters ignore case and surrounding spaces; blank text means no filter. Restaurant filters combine with AND. Omit `is_open` for all statuses; use `true` or `false` to filter. Empty results return an empty array (inside `items` for menus). Unavailable menu items remain visible.

Missing restaurants/items and cross-restaurant item requests return 404 with a `detail` message. Invalid bodies, filters, or nonpositive/noninteger IDs return 422 with validation details. Restaurant deletion returns 409 until its menu items are removed, preventing orphaned items and accidental reassignment when IDs are reused.

See [restaurant API details](docs/restaurant-api.md) and [menu API details](docs/menu-api.md).

## Architecture and storage

```text
Browser: static/index.html + static/app.js
    → registered FastAPI route
    → service
    → repository
    → data/restaurants.json or data/menu_items.json
```

`app/main.py` registers the restaurant and menu routers before mounting static content at `/`. Both data paths and the static directory resolve relative to source files. `app/api/restaurant_routes.py` is a compatibility import of the registered restaurant router, not a second API implementation.

Restaurant records contain `id`, `name`, `cuisine`, `address`, and `is_open`. Menu items contain their own globally assigned `id` plus `restaurant_id`, `name`, `description`, `price`, `category`, and `is_available`. There is no separate menu ID or CSV source. A restaurant with no matching items has an empty menu. The UI loads backend data rather than embedding a separate restaurant/menu list.

Successful writes use atomic file replacement. Thread locks protect repository mutations within one API process. **Use one server worker**; JSON storage is not a multi-process database or a transaction system across files. The restaurant JSON file must exist; menu storage can initialize on first add. IDs use the current maximum plus one and can be reused after deletion, so they are unsuitable as permanent order references without further work. Keep storage writable and retain backups of any data you need.

Tests inject temporary repository paths so writes do not change the committed demo data. For direct repository use, both repositories accept a `data_path` argument.

## Tests and continuous integration

```bash
python -m pytest -q
node --test tests/frontend.test.cjs
```

The Python suite covers routes, services, repositories, validation, search/filter combinations, ownership, failed writes, concurrent restaurant creation, OpenAPI contracts, static serving, and the combined flow over real HTTP. The HTTP check starts Uvicorn with temporary data, terminates it, starts a new process, and reads the saved changes. It requires permission to bind a local loopback port.

The dependency-free Node tests cover apostrophes in menu Edit handlers, literal rendering of user text, visible API/network/non-JSON errors, and clearing stale restaurant selection after a failed details request. These tests simulate the DOM; they do not replace browser verification.

[GitHub Actions](.github/workflows/pytest.yml) runs the Python suite on Python 3.14 and frontend regression tests on Node 22 for pushes to `main` and pull requests targeting `main`.

Verification on 2026-10-16: 70 Python tests and 5 frontend regression tests passed. A separate headless Chrome check exercised browser create/search/details/edit/menu/category/error flows and confirmed those browser writes survived a server process restart. The baseline main commit's [Actions run](https://github.com/reyeszaki/cosc310-bzs/actions/runs/38990208335) and its test step succeeded. [PR #37](https://github.com/reyeszaki/cosc310-bzs/pull/37) was subsequently opened, and [its Actions run](https://github.com/reyeszaki/cosc310-bzs/actions/runs/38991463232) passed both Python and frontend tests. The existing Starlette/httpx TestClient deprecation warning remains. A fresh dependency installation and other browsers were not tested in this review.

## Manual end-to-end walkthrough

These steps write to JSON. Use a disposable project copy if you want to keep the seed data unchanged.

1. Start the app and open `/`. Confirm the seeded restaurants appear. Filter by `ramen`, cuisine `Japanese`, and `Open Only`; reset and try a name with no matches.
2. Create `Review Cafe`, cuisine `Cafe`, address `10 Main St`, status Open. Find it by name, then click **View Details & Menu**. Confirm details and an empty menu.
3. Click **Edit Info**, change the name to `Updated Review Cafe` and status to Closed, then save. Confirm details changed and search with `Closed Only`. Use **Set Open** to verify the status toggle.
4. Add `Chef's Tea`, description `Hot green tea`, price `3.25`, category `drinks`. Click **Edit Item**, change price to `4.50` and availability to No, and update. Confirm the price and unavailable status remain visible.
5. Filter the menu with ` DRINKS `, then `mains`, then **Show All Items**. Expect the item, an empty result, then the item again.
6. Try deleting this restaurant while its item exists; expect a visible message requiring removal of menu items first. In `/docs`, try a missing restaurant ID (404), a blank restaurant name (422), and item price `0` (422); confirm valid data stays unchanged.
7. Stop and restart the server, refresh the browser, find the restaurant again, and verify its edited details and menu values persisted.
8. Delete the demo menu item, then delete the demo restaurant. Confirm it disappears from the list. Run both test commands above.

## Project files and handoff

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI entry point, router registration, static hosting |
| `static/` | Browser interface and API calls |
| `app/api/routers/` | Restaurant and menu HTTP routes |
| `app/schema/` | Pydantic request/response models |
| `app/services/` | Search, management, and ownership rules |
| `app/repository/` | JSON reads and persistent writes |
| `data/` | Fictional seed restaurants and menu items |
| `tests/` | Backend integration and frontend regression tests |
| `.github/workflows/pytest.yml` | Continuous integration |
| `docs/` | API handoffs, review results, AI assistance provenance |
| `scrum/team-agreement.md` | Team agreement |

The [M1 integration review](docs/m1-integration-review.md) records fixes, executed checks, and remaining limitations. [AI assistance provenance](docs/PROVENANCE.md) records tooling contributions. The earlier M0 submission tag `foundation-gate` remains historical; this README describes M1. Team review and submission procedures still apply.


## M1 submission

One team member submits a PDF to the Canvas group assignment containing:

1. Repository URL, with teaching-team access verified before the deadline.
2. GitHub Project Board URL, with the required workflow columns and user stories/issues.
3. URL of the immutable tag or release named `m1-vertical-slice`.
4. The full commit SHA referenced by that tag.
5. Contribution percentages for each team member, totaling 100% and agreed by everyone.

Before selecting the final commit, complete teammate review, integrate approved changes, confirm CI, and include actual scrum meeting notes under `scrum/` using the course sprint-planning template. All contributors must confirm the shared `docs/PROVENANCE.md` uses the required course fields and labels for their AI-influenced artifacts. A progress note alone is not a replacement for meeting records.

Create the submission tag only after choosing the final reviewed version. Do not move or overwrite the submitted tag after the deadline. If a revision is required, the assignment specifies a new tag named `milestone1-r1`. The tag identifies the assessed version; later work does not alter the original submission.
