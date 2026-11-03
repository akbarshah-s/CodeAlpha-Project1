from .cart import Cart
from .models import Category


def cart_context(request):
    """
    Context processor to make cart data and categories accessible to all templates.
    """
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_total_items': len(cart),
        'nav_categories': Category.objects.all(),
        'free_shipping_threshold': cart.FREE_SHIPPING_THRESHOLD,
    }
