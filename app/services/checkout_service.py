class CheckoutService:
    def __init__(self, users, carts, menus, restaurants, orders):
        self.users = users
        self.carts = carts
        self.menus = menus
        self.restaurants = restaurants
        self.orders = orders

    def checkout(self, customer_id: int):
        customer = self.users.require_active(customer_id)
        if customer.role != "customer":
            raise PermissionError("Only customers can checkout")
        if customer.address is None or not customer.address.strip():
            raise ValueError("A delivery address is required")
        cart = self.carts.cart_repo.get_by_customer(customer_id)
        if cart is None or not cart["items"]:
            raise ValueError("Cart is empty")
        restaurant_id = cart["restaurant_id"]
        restaurant = self.restaurants.get_by_id(restaurant_id)
        if restaurant is None:
            raise LookupError("Restaurant not found")
        if not restaurant["is_open"]:
            raise ValueError("Restaurant is closed")
        menu = self.menus.get_menu(restaurant_id)
        order_items = []
        total_cents = 0
        seen_ids = []
        for entry in cart["items"]:
            quantity = entry["quantity"]
            if type(quantity) is not int or quantity <= 0:
                raise ValueError("Quantities must be positive integers")
            item_id = entry["menu_item_id"]
            if item_id in seen_ids:
                raise ValueError("Cart contains duplicate item entries")
            seen_ids.append(item_id)
            item = None
            for menu_item in menu.items:
                if menu_item.id == item_id:
                    item = menu_item
                    break
            if item is None:
                raise LookupError("Item no longer exists in this menu")
            if not item.is_available:
                raise ValueError("A cart item is unavailable")
            # Use current menu prices, calculated in cents.
            unit_cents = round(item.price * 100)
            line_cents = unit_cents * quantity
            total_cents += line_cents
            order_items.append({
                "menu_item_id": item.id,
                "name": item.name,
                "unit_price": unit_cents / 100,
                "quantity": quantity,
                "line_total": line_cents / 100,
            })
        order = self.orders.create_order(
            customer_id, restaurant_id, customer.address.strip(),
            order_items, total_cents / 100,
        )
        # Clear only after the order saves successfully.
        self.carts.clear_cart(customer_id)
        return order
