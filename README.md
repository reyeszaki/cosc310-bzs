# BZS — Food Delivery App

Team BZS's COSC 310 Milestone 1 restaurant and menu application. A browser frontend served by FastAPI connects restaurant discovery, details, restaurant management, and menu management to persistent JSON storage.

## Milestone 1 scope

- View restaurants; search names and filter by cuisine and open/closed status.
- View a selected restaurant's details and menu.
- Create, edit, open/close, and delete restaurants.
- Add, edit, and delete menu items; change price, category, and availability.
- Filter menus by category, including empty results and unavailable items.
- Validate requests through the API.
- Preserve successful changes across application restarts.

Authentication, accounts, carts, orders, payments, and delivery tracking are outside this slice.

## Requirements and setup

- Python 3.14 (verified locally with 3.14.0).
- Git and the Python packages pinned in `requirements.txt`.
- A current browser.

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
| DELETE | `/restaurants/{restaurant_id}` | 200: deleted restaurant |
| GET | `/restaurants/{restaurant_id}/menu` | 200: `{"restaurant_id":1,"items":[...]}`; optional `category` |
| POST | `/restaurants/{restaurant_id}/menu/items` | 201: created menu item |
| PATCH | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 200: updated item; supplied fields only |
| DELETE | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 204: empty response |

Restaurant POST/PUT bodies require `name`, `cuisine`, `address`, and `is_open`. IDs are integers assigned by the server. Restaurant text fields require at least one character; whitespace-only values are not rejected by the current model. PUT retains the restaurant ID used by its menu.

```json
{"name":"Review Cafe","cuisine":"Cafe","address":"10 Main St","is_open":true}
```

Menu POST bodies require `name`, `description`, `price`, and `category`; `is_available` defaults to true. Prices must be positive with at most two decimal places and ten total digits. Responses include `id` and the owning `restaurant_id`; prices are JSON numbers displayed to two decimal places by the frontend.

```json
{"name":"Chef's Tea","description":"Hot green tea","price":3.25,"category":"drinks","is_available":true}
```

Menu PATCH accepts a nonempty subset, such as `{"price":4.50,"is_available":false}`. Omitted fields remain unchanged; explicit nulls, unknown fields, and ID changes are rejected. Restaurant bodies currently ignore unknown fields.

Restaurant search matches a name substring; cuisine matches the full cuisine. Menu category matches the full category. Text filters ignore case and surrounding spaces; blank text means no filter. Restaurant filters combine with AND. Omit `is_open` for all statuses; use `true` or `false` to filter. Empty results return an empty array (inside `items` for menus). Unavailable menu items remain visible.

Missing restaurants/items and cross-restaurant item requests return 404 with a `detail` message. Invalid bodies, boolean filters, or noninteger IDs return 422 with validation details. Menu paths also reject nonpositive IDs. Remove menu items before deleting their restaurant; restaurant deletion currently does not remove or block existing menu items.

See [restaurant API details](docs/restaurant-api.md) and [menu API details](docs/menu-api.md).

## Architecture and storage

```text
Browser: static/index.html + static/app.js
    → registered FastAPI route
    → service
    → repository
    → data/restaurants.json or data/menu_items.json
```

`app/main.py` registers the restaurant and menu routers before mounting static content at `/`. Data paths resolve relative to source files. Static hosting uses the `static` directory relative to the working directory, so start the server from the project root. `app/api/restaurant_routes.py` contains an older router; `app/main.py` uses `app/api/routers/restaurant_routers.py`.

Restaurant records contain `id`, `name`, `cuisine`, `address`, and `is_open`. Menu items contain their own globally assigned `id` plus `restaurant_id`, `name`, `description`, `price`, `category`, and `is_available`. There is no separate menu ID or CSV source. A restaurant with no matching items has an empty menu. The UI loads backend data rather than embedding a separate restaurant/menu list.

Menu writes use atomic file replacement and a thread lock within one API process. Restaurant writes save directly to JSON without those protections. **Use one server worker**; JSON storage is not a multi-process database or a transaction system across files. The restaurant JSON file must exist; menu storage can initialize on first add. IDs use the current maximum plus one and can be reused after deletion, so they are unsuitable as permanent order references without further work. Keep storage writable and retain backups of any data you need.

Tests inject temporary repository paths so writes do not change the committed demo data. For direct repository use, both repositories accept a `data_path` argument.

## Tests and continuous integration

```bash
python -m pytest -q
```

The current suite has 49 tests covering health, restaurant reads/search, selected restaurant errors, menu management, validation, filtering, ownership, and persistence. Menu tests use temporary storage, including a separate Python process to check saved menu changes and a simulated failed write.

[GitHub Actions](.github/workflows/pytest.yml) runs pytest on Python 3.10 for pushes to `main` and pull requests targeting `main`. Local setup uses Python 3.14.0. The existing Starlette/httpx TestClient deprecation warning remains.

The application, tests, and CI in this PR have been restored to their pre-review versions. The additional integration fixes and tests were removed at my request because they changed other members' parts. The earlier 70-test/browser results apply to that removed implementation, not the current code.

## Integration issues for team review

- Some frontend errors are not displayed, and item text containing apostrophes can break the Edit Item button.
- Restaurant deletion can leave menu items behind. Since IDs can be reused, remove a restaurant's menu items before deleting it.
- Restaurant writes are not protected against overlapping requests or failed writes.
- Restaurant validation allows whitespace-only text. User-provided frontend text is inserted into HTML without escaping.

These issues remain for the owners to review; the documentation update does not change their implementation.

## Manual end-to-end walkthrough

These steps write to JSON. Use a disposable project copy if you want to keep the seed data unchanged.

1. Start the app and open `/`. Confirm the seeded restaurants appear. Filter by `ramen`, cuisine `Japanese`, and `Open Only`; reset and try a name with no matches.
2. Create `Review Cafe`, cuisine `Cafe`, address `10 Main St`, status Open. Find it by name, then click **View Details & Menu**. Confirm details and an empty menu.
3. Click **Edit Info**, change the name to `Updated Review Cafe` and status to Closed, then save. Confirm details changed and search with `Closed Only`. Use **Set Open** to verify the status toggle.
4. Add `Green Tea`, description `Hot green tea`, price `3.25`, category `drinks`. Click **Edit Item**, change price to `4.50` and availability to No, and update. Confirm the price and unavailable status remain visible.
5. Filter the menu with ` DRINKS `, then `mains`, then **Show All Items**. Expect the item, an empty result, then the item again.
6. In `/docs`, try a missing restaurant ID (404), an empty restaurant name (422), and item price `0` (422); confirm valid data stays unchanged.
7. Stop and restart the server, refresh the browser, find the restaurant again, and verify its edited details and menu values persisted.
8. Delete the demo menu item, then delete the demo restaurant. Confirm it disappears from the list. Run the test command above.

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
| `tests/` | Restaurant and menu pytest tests |
| `.github/workflows/pytest.yml` | Continuous integration |
| `docs/` | API documentation and AI provenance |
| `scrum/team-agreement.md` | Team agreement |

See [PROVENANCE.md](docs/PROVENANCE.md) for how AI was used.


## M0 submission

Milestone 0 established the backend foundation: the FastAPI application, health endpoint, restaurant list, Pydantic restaurant model, JSON storage, and pytest/GitHub Actions setup.

The M0 submitted version is identified by the [`foundation-gate`](https://github.com/reyeszaki/cosc310-bzs/tree/foundation-gate) tag. This tag preserves the M0 version separately from later milestone work and must not be moved or overwritten.

## M1 submission

One team member submits a PDF to the Canvas group assignment containing:

1. Repository URL, with teaching-team access verified before the deadline.
2. GitHub Project Board URL, with the required workflow columns and user stories/issues.
3. URL of the immutable tag or release named `m1-vertical-slice`.
4. The full commit SHA referenced by that tag.
5. Contribution percentages for each team member, totaling 100% and agreed by everyone.

Before selecting the final commit, complete teammate review, integrate approved changes, confirm CI, and include actual scrum meeting notes under `scrum/` using the course sprint-planning template. All contributors must confirm the shared `docs/PROVENANCE.md` uses the required course fields and labels for their AI-influenced artifacts. A progress note alone is not a replacement for meeting records.

Create the submission tag only after choosing the final reviewed version. Do not move or overwrite the submitted tag after the deadline. If a revision is required, the assignment specifies a new tag named `milestone1-r1`. The tag identifies the assessed version; later work does not alter the original submission.
