# here ill add the 5 methods to handling cart operations:

# add item, remove item, update quantity (to get a specific item and set its quantity), get/retrieve cart, clear cart
# all based on the different schemas we have for cart

from decimal import Decimal

from app.schema.cart_schema import Cart, CartItem, CartItemCreate, CartItemUpdate


class CartService:
    def __init__(self, cart_repo, menu_service, require_active_customer):
        self.cart_repo = cart_repo
        self.menu_service = menu_service
        self.require_active_customer = require_active_customer

    def get_or_create_cart(self, customer_id: int) -> Cart:
        self.require_active_customer(customer_id)
        cart = self.cart_repo.get_by_customer(customer_id)

        if cart is None:
            cart = self._empty_cart(customer_id)
            self.cart_repo.save(cart)

        return self._cart_with_totals(cart)

    def add_item(self, customer_id: int, request: CartItemCreate) -> Cart:
        self.require_active_customer(customer_id)
        cart = self._load_cart(customer_id)

        if cart["items"] and cart["restaurant_id"] != request.restaurant_id:
            raise ValueError("Cart items must be from the same restaurant")

        menu = self.menu_service.get_menu(request.restaurant_id)
        for menu_item in menu.items:
            if menu_item.id == request.menu_item_id:
                break
        else:
            raise LookupError("Menu item not found")

        if not menu_item.is_available:
            raise ValueError("Menu item is unavailable")

        for item in cart["items"]:
            if item["menu_item_id"] == request.menu_item_id:
                item["quantity"] += request.quantity
                break
        else:
            cart["items"].append({
                "menu_item_id": request.menu_item_id,
                "quantity": request.quantity,
            })

        cart["restaurant_id"] = request.restaurant_id
        return self._save_cart(cart)

    def update_quantity(
        self, customer_id: int, menu_item_id: int, request: CartItemUpdate
    ) -> Cart:
        self.require_active_customer(customer_id)
        cart = self._load_cart(customer_id)

        for item in cart["items"]:
            if item["menu_item_id"] == menu_item_id:
                item["quantity"] = request.quantity
                return self._save_cart(cart)

        raise LookupError("Item not found in cart")

    def remove_item(self, customer_id: int, menu_item_id: int) -> Cart:
        self.require_active_customer(customer_id)
        cart = self._load_cart(customer_id)

        for index, item in enumerate(cart["items"]):
            if item["menu_item_id"] == menu_item_id:
                del cart["items"][index]

                if not cart["items"]:
                    cart["restaurant_id"] = None

                return self._save_cart(cart)

        raise LookupError("Item not found in cart")

    def clear_cart(self, customer_id: int) -> Cart:
        self.require_active_customer(customer_id)
        return self._save_cart(self._empty_cart(customer_id))

    def _empty_cart(self, customer_id: int) -> dict:
        return {"customer_id": customer_id, "restaurant_id": None, "items": []}

    def _load_cart(self, customer_id: int) -> dict:
        cart = self.cart_repo.get_by_customer(customer_id)
        if cart is None:
            return self._empty_cart(customer_id)
        return cart

    def _save_cart(self, cart: dict) -> Cart:
        cart_with_totals = self._cart_with_totals(cart)
        self.cart_repo.save(cart)
        return cart_with_totals

    def _cart_with_totals(self, cart: dict) -> Cart:
        items = []
        subtotal = Decimal("0.00")

        if cart["items"]:
            menu = self.menu_service.get_menu(cart["restaurant_id"])
            menu_items = {item.id: item for item in menu.items}

            for entry in cart["items"]:
                item = menu_items.get(entry["menu_item_id"])
                if item is None:
                    raise LookupError("A cart item no longer exists on the menu")

                quantity = entry["quantity"]
                line_total = item.price * quantity
                subtotal += line_total

                items.append(CartItem(
                    menu_item_id=item.id,
                    name=item.name,
                    unit_price=item.price,
                    quantity=quantity,
                    line_total=line_total,
                ))

        return Cart(
            customer_id=cart["customer_id"],
            restaurant_id=cart["restaurant_id"],
            items=items,
            subtotal=subtotal,
            total=subtotal,
        )