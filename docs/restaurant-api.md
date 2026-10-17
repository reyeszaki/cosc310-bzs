# Parts A & B restaurant API

Supports #11 View restaurant, #16 Manage restaurant details, and #29 Search and Filter restaurants.
Open `/docs` for interactive requests and full request/response schemas.

## Endpoints

All paths start with `/restaurants`. IDs are positive integers; restaurant records are stored in `data/restaurants.json`.

| Method | Path | Success response |
| --- | --- | --- |
| GET | `/restaurants` | 200: `[ { "id": 1, "name": "...", ... } ]` |
| POST | `/restaurants` | 201: created restaurant |
| GET | `/restaurants/{restaurant_id}` | 200: restaurant details |
| PUT | `/restaurants/{restaurant_id}` | 200: updated restaurant |
| DELETE | `/restaurants/{restaurant_id}` | 200: deleted restaurant; 409 if menu items remain |

`GET /restaurants` accepts optional query parameters `?search=...`, `?cuisine=...`, and `?is_open=true|false`. Matching on `search` and `cuisine` ignores case and surrounding spaces. Omit `is_open` for all statuses; blank text parameters mean no text filter. Search matches a name substring; cuisine matches the full cuisine. Filters combine with AND. If no restaurants match the filter criteria, an empty list `[]` is returned.

## Restaurant fields and validation

POST and PUT require `name`, `cuisine`, `address`, and `is_open`:

```json
{
  "name": "Ichiraku Ramen",
  "cuisine": "Japanese",
  "address": "123 Noodle Way",
  "is_open": true
}
```

- Text fields (`name`, `cuisine`, `address`) are trimmed and cannot be blank. Unknown fields, including client-supplied IDs, are rejected. PUT requires all four editable fields and preserves the existing ID.
- `is_open` is a boolean (`true` or `false`) indicating whether the restaurant is currently open.
- Responses include the server-assigned integer `id`.
- Successful create, update, and delete operations are saved directly to `data/restaurants.json` and remain visible on subsequent requests and across server restarts.

## Errors and limits

- **404:** Missing restaurant ID on `GET /restaurants/{restaurant_id}`, `PUT /restaurants/{restaurant_id}`, or `DELETE /restaurants/{restaurant_id}`. Body: `{ "detail": "Restaurant with id ... not found" }`.
- **409:** Restaurant still has menu items. Delete its items first; this prevents orphaned items and accidental reassignment to a reused restaurant ID.
- **422:** Invalid request body (such as blank strings or missing required fields), invalid `is_open`, or nonpositive/non-integer IDs. Body contains FastAPI validation details.
- Use one API worker. Repository writes use a thread lock and atomic file replacement; storage is not a multi-process database.
- Authentication, user accounts, shopping carts, and orders are outside the scope of Milestone 1.

## Simple demo

1. Run `python -m uvicorn app.main:app --reload`; leave that terminal running.
2. Open `http://127.0.0.1:8000/docs` and execute `GET /restaurants` to view all restaurants.
3. Filter using `search`, `cuisine`, or `is_open`, then clear the filters.
4. `POST /restaurants` with the example JSON above and note the returned restaurant `id`.
5. `PUT /restaurants/{restaurant_id}` using that ID with `{ "name": "Ichiraku Ramen", "cuisine": "Japanese", "address": "123 Noodle Way", "is_open": false }`; run `GET /restaurants/{restaurant_id}` to verify the change.
6. Request a non-existent ID (such as `999`) to demonstrate the `404` response, and submit an empty `name` (`""`) to demonstrate the `422` validation response.
7. Stop the server with Ctrl+C, restart it, and run `GET /restaurants` again to demonstrate persistence.
8. Remove any menu items belonging to the demo restaurant first, then `DELETE /restaurants/{restaurant_id}` on the demo restaurant and run `GET` to confirm it was removed.
9. In another terminal with the virtual environment active, run `python -m pytest -q`.
