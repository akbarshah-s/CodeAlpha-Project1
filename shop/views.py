from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q

from .models import Category, Product, Order, OrderItem
from .forms import UserRegistrationForm, UserProfileForm, CheckoutForm, AddToCartForm
from .cart import Cart


def home(request):
    """
    Homepage displaying Hero banner, Search, Featured products,
    Latest arrivals, Categories, and Special offers.
    """
    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    products = Product.objects.all()

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Sorting options
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        # Default sort
        products = products.order_by('-featured', '-created_at')

    # Specific sections for homepage when no search/category filter active
    featured_products = Product.objects.filter(featured=True)[:8]
    latest_products = Product.objects.order_by('-created_at')[:8]
    special_offers = Product.objects.filter(discount_price__isnull=False)[:4]

    context = {
        'products': products,
        'search_query': search_query,
        'selected_category': selected_category,
        'sort_by': sort_by,
        'featured_products': featured_products,
        'latest_products': latest_products,
        'special_offers': special_offers,
        'total_products_count': products.count(),
    }
    return render(request, 'home.html', context)


def product_detail(request, slug):
    """
    Product details page with large preview, specifications,
    stock indicator, quantity selector, and related products.
    """
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    form = AddToCartForm()

    context = {
        'product': product,
        'related_products': related_products,
        'form': form,
    }
    return render(request, 'product_detail.html', context)


def cart_detail(request):
    """
    Shopping cart page with item summary, quantity updates,
    subtotal, shipping cost, and checkout trigger.
    """
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


def cart_add(request, product_id):
    """
    Add product to cart or increase quantity.
    Supports both standard HTTP POST and AJAX JSON responses.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = 1
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

    success, current_qty, msg = cart.add(product=product, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': msg,
            'cart_count': len(cart),
            'cart_subtotal': str(cart.get_subtotal_price()),
            'current_qty': current_qty,
        })

    if success:
        messages.success(request, msg)
    else:
        messages.warning(request, msg)

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'cart_detail'
    return redirect(next_url)


def cart_update(request, product_id):
    """
    Update item quantity in cart (increment, decrement, or direct input).
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    action = request.POST.get('action')
    try:
        qty = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        qty = 1

    current_item = cart.cart.get(str(product_id), {})
    current_qty = current_item.get('quantity', 1)

    if action == 'increase':
        success, new_qty, msg = cart.add(product=product, quantity=1)
    elif action == 'decrease':
        if current_qty > 1:
            success, new_qty, msg = cart.add(product=product, quantity=-1)
        else:
            cart.remove(product)
            success = True
            new_qty = 0
            msg = f"Removed '{product.name}' from your cart."
    elif action == 'set':
        success, new_qty, msg = cart.add(product=product, quantity=qty, override_quantity=True)
    else:
        success = False
        new_qty = current_qty
        msg = "Invalid cart action."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': msg,
            'cart_count': len(cart),
            'cart_subtotal': str(cart.get_subtotal_price()),
            'cart_total': str(cart.get_total_price()),
            'shipping_price': str(cart.get_shipping_price()),
            'new_qty': new_qty,
        })

    if success:
        messages.success(request, msg)
    else:
        messages.warning(request, msg)

    return redirect('cart_detail')


def cart_remove(request, product_id):
    """
    Remove product from cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"'{product.name}' was removed from your cart.")
    return redirect('cart_detail')


def cart_clear(request):
    """
    Clear all items from cart.
    """
    cart = Cart(request)
    cart.clear()
    messages.info(request, "Your shopping cart is now empty.")
    return redirect('cart_detail')


def checkout(request):
    """
    Checkout page. Validates cart, customer information,
    deducts product stock in an atomic database transaction,
    creates Order and OrderItems, and clears cart.
    """
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Validate inventory before placing order
            out_of_stock_items = []
            for item in cart:
                prod = item['product']
                if prod.stock < item['quantity']:
                    out_of_stock_items.append(f"{prod.name} (available: {prod.stock})")

            if out_of_stock_items:
                messages.error(request, f"Insufficient stock for: {', '.join(out_of_stock_items)}. Please adjust quantities.")
                return redirect('cart_detail')

            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.total_price = cart.get_total_price()
                    order.order_status = 'Placed'
                    order.save()

                    # Create order items and decrement stock
                    for item in cart:
                        product = item['product']
                        quantity = item['quantity']
                        price = item['price']

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=price
                        )

                        # Deduct stock
                        product.stock -= quantity
                        product.save()

                    # Clear session cart
                    cart.clear()

                    messages.success(request, f"Thank you! Your order #{order.order_number} has been placed successfully.")
                    return redirect('order_success', order_number=order.order_number)

            except Exception as e:
                messages.error(request, f"An error occurred while processing your order: {str(e)}")
                return redirect('checkout')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'email': request.user.email,
            }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'subtotal': cart.get_subtotal_price(),
        'shipping': cart.get_shipping_price(),
        'total': cart.get_total_price(),
    }
    return render(request, 'checkout.html', context)


def order_success(request, order_number):
    """
    Displays successful order placement confirmation and order overview.
    """
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'order_success.html', {'order': order})


@login_required
def order_history(request):
    """
    Lists order history for the authenticated user.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})


def order_detail(request, order_number):
    """
    Displays details and status for a specific order.
    Accessible by the order owner or matching guest email/phone.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Permission check: if order belongs to a user, only that user or staff can view
    if order.user and (not request.user.is_authenticated or (request.user != order.user and not request.user.is_staff)):
        messages.error(request, "You do not have permission to view this order.")
        return redirect('home')

    return render(request, 'order_detail.html', {'order': order})


def register_view(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to IndianShopEase, {user.first_name or user.username}! Your account has been created.")
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """
    User login view with username and password.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'home'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, "You have been logged out. See you again soon!")
    return redirect('home')


@login_required
def profile_view(request):
    """
    User profile view allowing account detail updates and viewing recent orders.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_orders = Order.objects.filter(user=request.user).count()

    context = {
        'form': form,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
    }
    return render(request, 'profile.html', context)
