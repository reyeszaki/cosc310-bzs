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

This covers the backend only. The checkout screen, payments, taxes and delivery fees are not included. Saving an order and clearing the cart happen separately. If the order saves but clearing the cart fails, both will remain. Handling simultaneous checkouts and repeated requests is still unfinished. These could create duplicate orders or overwrite data.

See the PR verification update below for the checks run on this integration.

AI provenance: We used OpenAI Codex to help develop the checkout and order features, including generating draft code.

PR verification update: 54 local tests pass, including 8 in tests/test_checkout.py.
These use isolated files and TestClient; they include persistence reloading,
price changes, snapshots, ownership, validation and save/clear failures.
No separate server restart or browser walkthrough was run. This feature depends
on cart PR #91; integrate that first. The cart price conversion is included here.
