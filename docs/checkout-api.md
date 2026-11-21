Checkout and orders - backend integration

This adds checkout and order handling to our project. It uses the account authentication code and the cart service from PR #91.

To register the routes in app/main.py:
    from app.api.routers import orders_routers
    app.include_router(orders_routers.router)

This integration includes the cart price conversion in _cart_with_totals:
    line_total = Decimal(str(item.price)) * quantity

The order repository creates data/orders.json when it first saves an order.
Do not overwrite an existing orders file with an empty file.

Endpoints:
    POST /checkout (bearer token, no request body)
    GET /orders
    GET /orders/{order_id}

The customer page now connects to these endpoints. Payments, taxes and delivery fees are not included. Saving an order and clearing the cart happen separately. If the order saves but clearing the cart fails, both will remain. Handling simultaneous checkouts and repeated requests is still unfinished. These could create duplicate orders or overwrite data.

See the PR verification update below for the checks run on this integration.

AI provenance: We used OpenAI Codex to help develop the checkout and order features, including generating draft code.

PR verification update: 54 local tests pass, including 8 in tests/test_checkout.py.
These use isolated files and TestClient; they include persistence reloading,
price changes, snapshots, ownership, validation and save/clear failures.
No separate server restart or browser walkthrough was run. This feature depends
on cart PR #91; integrate that first. The cart price conversion is included here.


## Customer page walkthrough

1. Start the app with `python -m uvicorn app.main:app --reload` and open `/`.
2. Create a customer account, then sign in with that email and password.
3. Save your profile and delivery address in Customer Account.
4. Open an available restaurant and use Add to Cart beside an available item.
5. Update quantities or remove items in Your Cart. The displayed total comes from the backend.
6. Select Place Order. The page displays the saved order and reloads the cart and orders.
7. Refresh the page to restore the session, or sign out to invalidate the token.

The token is stored in sessionStorage for this browser tab. Passwords are not stored.
After a server restart, sign in again because server-side sessions are in memory.
Order history is displayed newest first. Deactivation is available in Customer Account.
Existing restaurant/menu management controls remain as before; their backend role
permissions still need separate work. Hiding a frontend control is not authorization.

Frontend verification: all 58 existing pytest tests pass. A headless Chrome check
using temporary storage passed registration, invalid login, sign-in, address saving,
cart additions and quantity updates, unavailable-item controls, mixed-restaurant
rejection, checkout, order display, page refresh and logout, with no page errors.
A full server restart was not tested for this change.
