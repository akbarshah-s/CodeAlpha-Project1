from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Category, Product, Order, OrderItem
from shop.cart import Cart


class ShopEaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )

        # Create category
        self.category = Category.objects.create(name='Electronics', icon='bi-laptop')

        # Create products
        self.product1 = Product.objects.create(
            name='Test Laptop',
            category=self.category,
            price=Decimal('999.00'),
            discount_price=Decimal('899.00'),
            stock=10,
            featured=True,
            description='A high-performance test laptop.'
        )

        self.product2 = Product.objects.create(
            name='Test Mouse',
            category=self.category,
            price=Decimal('25.00'),
            stock=2,
            featured=False,
            description='An optical mouse.'
        )

    def test_product_properties(self):
        """Test Product custom properties."""
        self.assertEqual(self.product1.current_price, Decimal('899.00'))
        self.assertEqual(self.product2.current_price, Decimal('25.00'))
        self.assertTrue(self.product1.is_in_stock)
        self.assertTrue(self.product2.is_low_stock)
        self.assertEqual(self.product1.discount_percentage, 10)

    def test_cart_operations(self):
        """Test adding, capping at stock, and removing from cart."""
        session = self.client.session
        session.save()

        # Add 5 items of product1
        response = self.client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 5})
        self.assertEqual(response.status_code, 302)

        # Verify cart in session
        cart_data = self.client.session.get('shopease_cart')
        self.assertIsNotNone(cart_data)
        self.assertEqual(cart_data[str(self.product1.id)]['quantity'], 5)

        # Try to add 10 more (stock is only 10 total) -> should cap at 10
        response = self.client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 10})
        cart_data = self.client.session.get('shopease_cart')
        self.assertEqual(cart_data[str(self.product1.id)]['quantity'], 10)

        # Remove item from cart
        response = self.client.get(reverse('cart_remove', args=[self.product1.id]))
        self.assertEqual(response.status_code, 302)
        cart_data = self.client.session.get('shopease_cart')
        self.assertNotIn(str(self.product1.id), cart_data)

    def test_inr_shipping_threshold_and_fee(self):
        """Shipping fees and the free-shipping threshold are shown in INR."""
        cart = Cart(self.client)
        self.assertEqual(cart.get_shipping_price(), Decimal('0.00'))

        self.client.post(reverse('cart_add', args=[self.product2.id]), {'quantity': 1})
        cart = Cart(self.client)
        self.assertEqual(cart.get_shipping_price(), Decimal('474.64'))
        self.assertEqual(cart.get_remaining_for_free_shipping(), Decimal('4721.43'))

        self.client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 6})
        cart = Cart(self.client)
        self.assertEqual(cart.get_shipping_price(), Decimal('0.00'))
        self.assertEqual(cart.get_remaining_for_free_shipping(), Decimal('0.00'))

    def test_homepage_and_filters(self):
        """Test homepage rendering, category filtering, search, and sorting."""
        # 1. Homepage loads
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Laptop')
        self.assertContains(response, 'Test Mouse')

        # 2. Category filter
        response = self.client.get(reverse('home') + f'?category={self.category.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Laptop')

        # 3. Search filter
        response = self.client.get(reverse('home') + '?q=Laptop')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Laptop')
        self.assertNotContains(response, 'Test Mouse')

        # 4. Sorting
        response = self.client.get(reverse('home') + '?sort=price_asc')
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        """Test product detail page."""
        response = self.client.get(reverse('product_detail', args=[self.product1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Laptop')
        self.assertContains(response, '899.00')

    def test_checkout_and_order_creation(self):
        """Test placing an order, stock decrement, and order items creation."""
        # Log in user
        self.client.login(username='testuser', password='testpassword123')

        # Add 2 items of product1 to cart
        self.client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 2})

        # Initial stock check
        self.assertEqual(self.product1.stock, 10)

        # Place order
        checkout_data = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'phone': '1234567890',
            'address': '123 Test Street, Suite 4',
            'city': 'Metropolis',
            'postal_code': '12345',
            'order_notes': 'Please ring doorbell',
            'payment_method': 'cod'
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)

        # Check order exists
        order = Order.objects.filter(email='testuser@example.com').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.order_status, 'Placed')
        self.assertEqual(order.items.count(), 1)

        # Check stock was decremented
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, 8)

        # Check cart was cleared
        cart_data = self.client.session.get('shopease_cart')
        self.assertFalse(cart_data)

        # Check order success view
        success_response = self.client.get(reverse('order_success', args=[order.order_number]))
        self.assertEqual(success_response.status_code, 200)
        self.assertContains(success_response, order.order_number)

    def test_user_registration_and_authentication(self):
        """Test new user registration and login."""
        reg_data = {
            'username': 'newcustomer',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123',
        }
        response = self.client.post(reverse('register'), reg_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newcustomer').exists())

        # Test login
        login_response = self.client.post(reverse('login'), {
            'username': 'newcustomer',
            'password': 'securepassword123'
        })
        self.assertEqual(login_response.status_code, 302)

        # Test profile view
        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, 'Alice')

        # Test update profile
        update_profile_res = self.client.post(reverse('profile'), {
            'first_name': 'AliceUpdated',
            'last_name': 'Smith',
            'email': 'alice@example.com'
        })
        self.assertEqual(update_profile_res.status_code, 302)
        self.user.refresh_from_db()

        # Test logout
        logout_response = self.client.get(reverse('logout'))
        self.assertEqual(logout_response.status_code, 302)

    def test_cart_update_actions(self):
        """Test increasing, decreasing, and setting quantity in cart."""
        self.client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 2})

        # Increase
        res = self.client.post(reverse('cart_update', args=[self.product1.id]), {'action': 'increase'})
        self.assertEqual(res.status_code, 302)
        cart_data = self.client.session.get('shopease_cart')
        self.assertEqual(cart_data[str(self.product1.id)]['quantity'], 3)

        # Decrease
        res = self.client.post(reverse('cart_update', args=[self.product1.id]), {'action': 'decrease'})
        self.assertEqual(res.status_code, 302)
        cart_data = self.client.session.get('shopease_cart')
        self.assertEqual(cart_data[str(self.product1.id)]['quantity'], 2)

        # Clear cart
        res = self.client.get(reverse('cart_clear'))
        self.assertEqual(res.status_code, 302)
        cart_data = self.client.session.get('shopease_cart')
        self.assertFalse(cart_data)

    def test_order_history_and_permissions(self):
        """Test order history access and permission checks."""
        # Unauthenticated access redirects to login
        res = self.client.get(reverse('order_history'))
        self.assertEqual(res.status_code, 302)

        # Log in
        self.client.login(username='testuser', password='testpassword123')
        res = self.client.get(reverse('order_history'))
        self.assertEqual(res.status_code, 200)
