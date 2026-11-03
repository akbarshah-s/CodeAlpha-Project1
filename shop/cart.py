from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    """
    Session-based shopping cart supporting guest and authenticated users.
    """
    FREE_SHIPPING_THRESHOLD = Decimal('4746.43')
    STANDARD_SHIPPING_PRICE = Decimal('474.64')

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        Guarantees that quantity does not exceed product stock.
        Returns a tuple (success: bool, current_qty: int, message: str)
        """
        product_id = str(product.id)
        current_in_cart = self.cart.get(product_id, {}).get('quantity', 0)

        if override_quantity:
            target_quantity = quantity
        else:
            target_quantity = current_in_cart + quantity

        if product.stock <= 0:
            return False, 0, f"Sorry, '{product.name}' is currently out of stock."

        if target_quantity > product.stock:
            # Cap at maximum stock
            allowed_quantity = product.stock
            self.cart[product_id] = {
                'quantity': allowed_quantity,
                'price': str(product.current_price)
            }
            self.save()
            diff_added = allowed_quantity - current_in_cart
            if diff_added > 0:
                return True, allowed_quantity, f"Added {diff_added} item(s). Reached maximum available stock ({product.stock}) for '{product.name}'."
            else:
                return False, allowed_quantity, f"Cannot add more. You already have the maximum available stock ({product.stock}) in your cart."

        if target_quantity <= 0:
            self.remove(product)
            return True, 0, f"Removed '{product.name}' from your cart."

        self.cart[product_id] = {
            'quantity': target_quantity,
            'price': str(product.current_price)
        }
        self.save()
        return True, target_quantity, f"Updated '{product.name}' in your cart (Qty: {target_quantity})."

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_copy = {k: v.copy() for k, v in self.cart.items()}

        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item_id, item in cart_copy.items():
            if 'product' not in item:
                continue
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_shipping_price(self):
        subtotal = self.get_subtotal_price()
        if subtotal == 0 or subtotal >= self.FREE_SHIPPING_THRESHOLD:
            return Decimal('0.00')
        return self.STANDARD_SHIPPING_PRICE

    def get_remaining_for_free_shipping(self):
        return max(self.FREE_SHIPPING_THRESHOLD - self.get_subtotal_price(), Decimal('0.00'))

    def get_total_price(self):
        return self.get_subtotal_price() + self.get_shipping_price()

    def clear(self):
        """
        Remove cart from session.
        """
        self.cart = {}
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        self.save()
