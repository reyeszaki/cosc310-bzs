# Part C menus

Part C handles viewing a restaurant's menu, filtering by category, and adding,
updating, or deleting menu items. It supports issues #18, #19, and #20.

## How the code fits together

The menu follows the same structure as the restaurant code:

**Route → Service → Repository → JSON**

| File | What it does |
| --- | --- |
| `app/api/routers/menu_routers.py` | Receives the request and returns a response or a 404 error. |
| `app/schema/menu_schema.py` | Defines the fields and checks the input. |
| `app/services/menu_service.py` | Checks the restaurant exists and handles menu filtering. |
| `app/repository/menu_repo.py` | Reads and writes `data/menu_items.json`. |
| `tests/test_menus.py` | Checks the main menu operations using temporary files. |

For example, when we update an item, the route receives the new fields, the service
checks the restaurant, and the repository finds the item using both IDs and saves
it. The updated item is returned to the frontend.

## Endpoints

| Method | Path | Result |
| --- | --- | --- |
| GET | `/restaurants/{restaurant_id}/menu` | 200: the restaurant ID and its menu items |
| POST | `/restaurants/{restaurant_id}/menu/items` | 201: the new item |
| PUT | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 200: the updated item |
| DELETE | `/restaurants/{restaurant_id}/menu/items/{item_id}` | 204: no response body |

PUT replaces PATCH for menu updates. PUT sends **all editable fields**, like the
restaurant update endpoint. The frontend edit form already contains those fields.
To change only the price, send the other current values along with the new price.
Older clients that still use PATCH must switch to PUT.

## Item fields

Use this body to add an item:

```json
{
  "name": "Green Tea",
  "description": "Hot green tea",
  "price": 3.25,
  "category": "drinks",
  "is_available": true
}
```

- `name`, `description`, and `category` are required and cannot be blank.
- `price` is required, must be positive, and can have up to two decimal places.
  The largest accepted price is 99999999.99.
- `is_available` defaults to true when adding an item. PUT requires it explicitly.
- The server assigns `id` and `restaurant_id`. Do not include them in the body.
- Responses contain the item fields plus both IDs. Prices are JSON numbers.

To update the item, send the same five fields to its PUT URL. For example:

```json
{
  "name": "Green Tea",
  "description": "Hot green tea",
  "price": 4.50,
  "category": "drinks",
  "is_available": false
}
```

## Viewing and filtering

GET returns a menu in this form:

```json
{"restaurant_id": 1, "items": []}
```

The `items` list contains the matching items. An empty list means there are no
items to show. Unavailable items stay visible with `is_available: false`.

Add `?category=drinks` to filter. Matching ignores case and surrounding spaces.
A blank category shows everything. An unknown category returns an empty list.

## Errors and storage

- **404:** The restaurant or item does not exist, or the item belongs to another
  restaurant. The response contains a `detail` message.
- **422:** Required fields are missing, values are invalid, extra fields are sent,
  or a URL ID is not an integer. PUT does not accept partial or null values.
- The repository reads JSON on each request and writes it after each successful
  change. Creating a new repository or restarting the app reads those saved values.
- Storage now uses the same simple read/write approach as the restaurant repository.
  It does not have the previous file lock or atomic replacement. Use one worker and
  avoid simultaneous edits; an interrupted write can damage the file. Keep backups.
- IDs use the current maximum plus one and can be reused after deletion.

## Demo steps

1. Start the app from the project root with `python -m uvicorn app.main:app --reload`.
2. Open `/docs` and GET restaurant 1's menu.
3. Try category `drinks`, then clear the filter.
4. POST the add example and note the returned item ID.
5. PUT the update example using that ID. GET the menu again to see the new price
   and unavailable status.
6. Try price `0` for a 422 response and a missing restaurant for a 404 response.
7. Stop and restart the app. GET the menu to check the saved changes.
8. DELETE the demo item and GET the menu again.
9. Run `python -m pytest -q`.
