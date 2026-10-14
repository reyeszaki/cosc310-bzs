# Part C: menu API handoff

Implements the M1 menu backend on `feature/menu-items`, following route -> service -> repository -> JSON.

## Story mapping and acceptance criteria

The live GitHub issues were inspected on 2026-10-12. They contain story descriptions, with no separate acceptance-criteria lists or comments. The following criteria combine those descriptions with the matching criteria in the supplied User stories PDF; the PDF's story numbers are different from the issue numbers.

| Assigned issue | Implemented criteria | Relevant tests in `tests/test_menus.py` |
| --- | --- | --- |
| [#18 Manage menu items](https://github.com/reyeszaki/cosc310-bzs/issues/18) | Add name, description, positive price, and category; edit and remove items; show successful changes on the next read | Add/update/persistence, all-field update, removal, required-field and invalid-input tests |
| [#19 View menu](https://github.com/reyeszaki/cosc310-bzs/issues/19) | Return names, descriptions, prices, and availability for the requested restaurant; retain unavailable items with a clear flag | View/filter test, empty-menu and restaurant-isolation checks |
| [#20 Filter menu by category](https://github.com/reyeszaki/cosc310-bzs/issues/20) | Return only matching items; clear the filter to restore the full menu | View/filter test, unknown and blank category checks |

The PDF's matching stories are US-18 (manage items), US-05 (view), and US-06 (filter). The availability flag supports displaying out-of-stock items as required by the view criteria. Separate category management, cart restrictions, and authentication are outside this slice.

Implementation assumptions: names, descriptions, and categories must contain non-whitespace text. Prices have at most two decimal places and ten total digits. Categories are free-text strings; matching ignores case and surrounding whitespace. PATCH performs partial updates. Removal is included because issue #18 explicitly requests it.

## Contract for B and D

Restaurant and item IDs are positive integers. Restaurant IDs match `data/restaurants.json`. Items are stored separately in `data/menu_items.json`; restaurant responses are unchanged.

| Method | Path | Success |
| --- | --- | --- |
| GET | `/restaurants/{restaurant_id}/menu` | 200, `{ "restaurant_id": 1, "items": [...] }` |
| POST | `/restaurants/{restaurant_id}/menu/items` | 201, created item |
| PATCH | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 200, updated item |
| DELETE | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 204, empty body |

GET accepts an optional `category` query parameter. Matching ignores case and surrounding whitespace. Unknown categories return an empty item list; restaurants with no items also return an empty list. Clearing the filter restores the full menu.

Create request example:

```json
{
  "name": "Mochi",
  "description": "Sweet rice cakes",
  "price": 4.50,
  "category": "desserts",
  "is_available": true
}
```

`is_available` defaults to true. Every response item includes these fields plus `id` and `restaurant_id`. Price is a JSON number; the frontend should format it to two decimal places for display. PATCH accepts any nonempty subset of the five editable fields, for example `{ "price": 5.25, "is_available": false }`. Omitted fields remain unchanged. Null values, unknown fields, and attempts to set IDs are rejected.

Missing restaurant/item: HTTP 404 with `{ "detail": "..." }`. Invalid payload or nonpositive IDs: HTTP 422 with FastAPI's validation details. Items cannot be edited or removed through another restaurant's URL. Interactive documentation is at `/docs`, with the schema at `/openapi.json`.

## Demo and verification

1. Start `python -m uvicorn app.main:app --reload` from the project root.
2. Open `/docs` and GET `/restaurants/1/menu`; show descriptions, numeric prices, and an unavailable dessert.
3. GET the same menu with `category=drinks`, then clear the filter.
4. POST a new item; note its returned ID.
5. PATCH its price, category, and availability; GET to show the change.
6. Restart the server and GET again to show persistence.
7. DELETE the demo item when finished.
8. Run `python -m pytest -q` to demonstrate isolated automated tests.

The complete local suite passes: 37 tests. A new Python subprocess reads added and updated records to verify persistence without relying on in-memory state. A simulated replacement failure verifies that the original JSON remains intact. Tests also check the generated OpenAPI contract.

Tests override the menu service dependency with temporary JSON repositories. They do not write committed demo data. The existing restaurant and health tests continue to pass.

Persistence uses a temporary file and atomic replacement so failed writes do not truncate the current data. An in-process lock serializes menu mutations. Run one API worker for this JSON-backed milestone; multiple processes need shared locking or a database. Item IDs are allocated as the current maximum plus one and may be reused after deleting the highest ID; future order references require durable ID allocation.

Frontend pages, independent category management, authentication, carts, and order operations remain separate work. A teammate still needs to review the branch before merging.


## Example requests

Start the server, then use `/docs` or these commands in another terminal. Replace `ITEM_ID` with the ID returned by POST.

```bash
curl http://127.0.0.1:8000/restaurants/1/menu
curl 'http://127.0.0.1:8000/restaurants/1/menu?category=drinks'

curl -X POST http://127.0.0.1:8000/restaurants/1/menu/items \
  -H 'Content-Type: application/json' \
  -d '{"name":"Mochi","description":"Sweet rice cakes","price":4.50,"category":"desserts"}'

curl -X PATCH http://127.0.0.1:8000/restaurants/1/menu/items/ITEM_ID \
  -H 'Content-Type: application/json' \
  -d '{"price":5.25,"is_available":false}'

curl -X DELETE http://127.0.0.1:8000/restaurants/1/menu/items/ITEM_ID
```

A successful POST returns an item like this (the generated ID depends on current data):

```json
{
  "id": 7,
  "restaurant_id": 1,
  "name": "Mochi",
  "description": "Sweet rice cakes",
  "price": 4.5,
  "category": "desserts",
  "is_available": true
}
```

Submitting `{"price":0}` to PATCH returns 422 before any repository write. Requesting `/restaurants/999/menu` returns 404. A GET of an existing restaurant with no items returns 200 with `items: []`.

## Request walkthrough for the demo

For POST `/restaurants/1/menu/items`:

1. FastAPI uses `MenuItemCreate` in `app/schema/menu_schema.py` to validate the JSON. Missing/blank fields and invalid prices return 422 before the handler runs.
2. `add_item` in `app/api/routers/menu_routers.py` passes the restaurant ID and validated request to `MenuService`. Routes handle HTTP, including mapping `LookupError` to 404.
3. `MenuService.add_item` in `app/services/menu_service.py` checks the restaurant through `RestaurantRepository`, then converts the validated model into JSON-compatible fields.
4. `MenuRepository.add` in `app/repository/menu_repo.py` reads existing items, assigns the next integer ID, and saves the new list. Only repositories access files.
5. `_save` writes a temporary file next to `data/menu_items.json`, then atomically replaces the stored file. This protects the previous data if a write fails. The lock prevents simultaneous requests within one process from overwriting each other.
6. The service returns a `MenuItem`; FastAPI serializes that response model with HTTP 201. A later GET reads JSON again, so the change is immediately visible and remains available after restart.

For PATCH, `exclude_unset=True` tells Pydantic to include only fields actually sent by the client; the repository merges those fields into the existing record. The validator distinguishes omitted fields from explicit nulls, and rejects empty patches. For GET, the service optionally filters the restaurant's items and returns a `Menu` wrapper.

## Files in this feature

| File | Purpose |
| --- | --- |
| `app/main.py` | Registers the menu router alongside the existing restaurant router. |
| `app/api/routers/menu_routers.py` | HTTP endpoints, dependency injection, and OpenAPI descriptions/errors. |
| `app/schema/menu_schema.py` | Pydantic create/update/item/menu/error models and validation. |
| `app/services/menu_service.py` | Restaurant checks, filtering, and menu operations. |
| `app/repository/menu_repo.py` | JSON reads, item writes, ID assignment, locking, and atomic replacement. |
| `data/menu_items.json` | Fictional demo menus linked to the existing restaurant IDs. |
| `tests/test_menus.py` | Isolated API, validation, persistence, failure, and documentation tests. |
| `README.md` | Part C endpoint overview and documentation links. |
| `docs/menu-api.md` | Issue mapping, contract, examples, demo, assumptions, and layer walkthrough. |
| `docs/PROVENANCE.md` | Honest record of AI assistance and verification. |
| `docs/decision-menu-storage.md` | Proposed storage Decision Receipt, pending teammate review. |
| `scrum/menu-progress.md` | Implementation handoff note, not a claimed team meeting. |

The pre-existing `.gitignore` change is preserved and is not part of the menu implementation. No dependencies, existing restaurant implementation files, or CI configuration were changed. Changes are local and uncommitted.
