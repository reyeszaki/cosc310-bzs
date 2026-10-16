# Part C menu API

Supports #18 Manage menu items, #19 View menu, and #20 Filter menu by category.
Open `/docs` for interactive requests and full request/response schemas.

## Endpoints

All paths start with `/restaurants/{restaurant_id}/menu`. IDs are positive integers;
restaurant IDs match `data/restaurants.json`.

| Method | Path suffix | Success response |
| --- | --- | --- |
| GET | (none) | 200: `{ "restaurant_id": 1, "items": [...] }` |
| POST | `/items` | 201: created item |
| PATCH | `/items/{item_id}` | 200: updated item |
| DELETE | `/items/{item_id}` | 204: no body |

GET accepts optional `?category=drinks`. Matching ignores case and surrounding
spaces. Omit or clear the parameter to show all items. An unknown category or an
existing restaurant with no items returns an empty list. Unavailable items remain
visible with `is_available: false`.

## Item fields and validation

POST requires `name`, `description`, `price`, and `category`:

```json
{
  "name": "Mochi",
  "description": "Sweet rice cakes",
  "price": 4.50,
  "category": "desserts",
  "is_available": true
}
```

- Text fields cannot be blank. Categories are free text, one per item.
- Price must be positive, with at most two decimal places and ten total digits.
- Availability defaults to true. Responses also include generated `id` and `restaurant_id`.
- Prices are JSON numbers; the frontend should display two decimal places.
- PATCH accepts a nonempty subset, for example `{ "price": 5.25, "is_available": false }`.
  Omitted fields stay unchanged. Explicit nulls, unknown fields, and ID changes are rejected.
- Successful changes are saved in `data/menu_items.json` and visible on the next GET.

## Errors and limits

- **404:** Missing restaurant or item, including an item requested under the wrong
  restaurant. Body: `{ "detail": "Explanation" }`.
- **422:** Invalid input or nonpositive IDs. Body contains FastAPI validation details.
- Run one server worker: the file lock coordinates threads within one process only.
- Item IDs use the current maximum plus one; deleting the highest ID allows reuse.
  This is sufficient for this slice, but should change before storing order references.
- Authentication, carts, and separate category management are outside Part C.

## Simple demo

1. Run `python -m uvicorn app.main:app --reload`; leave that terminal running.
2. Open `http://127.0.0.1:8000/docs` and GET restaurant 1's menu.
3. Filter by `drinks`, then clear the filter.
4. POST the example above and note the returned item ID.
5. PATCH that ID with `{ "price": 5.25, "is_available": false }`; GET to show the change.
6. Try `{ "price": 0 }` and a missing restaurant to show 422 and 404.
7. Stop with Ctrl+C, restart, and GET again to show persistence.
8. DELETE the demo item; GET to show it was removed.
9. In another terminal with the virtual environment active, run `python -m pytest -q`.
