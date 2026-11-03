import os
from decimal import Decimal, ROUND_HALF_UP
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from shop.models import Category, Product
from PIL import Image, ImageDraw, ImageFont


USD_TO_INR_RATE = Decimal('94.928524')


def usd_to_inr(amount):
    return (amount * USD_TO_INR_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = 'Seeds sample categories, products with generated images, and optionally demo accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerate-images',
            action='store_true',
            help='Regenerate the bundled sample product images.',
        )
        parser.add_argument(
            '--demo-users',
            action='store_true',
            help='Create predictable demo accounts (local development only).',
        )
        parser.add_argument(
            '--no-demo-users',
            action='store_true',
            help='Do not create demo accounts (the default).',
        )

    def handle(self, *args, **options):
        self.stdout.write("Seeding database for IndianShopEase...")

        # Demo accounts
        if options['demo_users'] and not options['no_demo_users']:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@indianshopease.local', 'admin123')
                self.stdout.write(self.style.SUCCESS("[OK] Created default superuser: admin (password: admin123)"))
            else:
                self.stdout.write("[i] Superuser 'admin' already exists.")

            if not User.objects.filter(username='john_doe').exists():
                User.objects.create_user('john_doe', 'john@example.com', 'password123', first_name='John', last_name='Doe')
                self.stdout.write(self.style.SUCCESS("[OK] Created demo customer: john_doe (password: password123)"))
        else:
            self.stdout.write("[i] Skipping demo account creation.")

        # 2. Categories
        categories_data = [
            {'name': 'Electronics', 'icon': 'bi-laptop', 'description': 'Cutting-edge gadgets, audio gear, and personal computing.'},
            {'name': 'Fashion', 'icon': 'bi-handbag', 'description': 'Modern, high-comfort apparel and minimalist styles.'},
            {'name': 'Home & Living', 'icon': 'bi-house-heart', 'description': 'Refined decor, kitchenware, and lifestyle essentials.'},
            {'name': 'Fitness & Sports', 'icon': 'bi-activity', 'description': 'Premium gear engineered for wellness and performance.'},
            {'name': 'Accessories', 'icon': 'bi-watch', 'description': 'Timeless sunglasses, leather goods, and daily carry items.'},
        ]

        cat_objs = {}
        for cdata in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cdata['name'],
                defaults={'icon': cdata['icon'], 'description': cdata['description']}
            )
            cat_objs[cdata['name']] = cat
        self.stdout.write(self.style.SUCCESS(f"[OK] Created/verified {len(cat_objs)} product categories."))

        # 3. Ensure media/products folder exists
        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_products_dir, exist_ok=True)

        def generate_product_image(filename, title, category_name, bg_color, accent_color, regenerate=False):
            filepath = os.path.join(media_products_dir, filename)
            if os.path.exists(filepath) and not regenerate:
                return f"products/{filename}"

            # Create high quality 800x800 image
            width, height = 800, 800
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)

            # Draw stylish decorative rounded rectangle card in center
            card_box = [60, 60, width - 60, height - 60]
            draw.rectangle(card_box, fill=(255, 255, 255), outline=accent_color, width=4)

            # Draw accent header banner
            header_box = [60, 60, width - 60, 150]
            draw.rectangle(header_box, fill=accent_color)

            # Text rendering with standard font fallback
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                badge_font = ImageFont.truetype("arial.ttf", 26)
                sub_font = ImageFont.truetype("arial.ttf", 22)
            except Exception:
                title_font = ImageFont.load_default()
                badge_font = ImageFont.load_default()
                sub_font = ImageFont.load_default()

            # Brand badge
            draw.text((100, 95), f"INDIANSHOPEASE • {category_name.upper()}", fill=(255, 255, 255), font=badge_font)

            # Decorative circle in center
            circle_center = (400, 420)
            circle_radius = 160
            draw.ellipse([
                circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                circle_center[0] + circle_radius, circle_center[1] + circle_radius
            ], fill=bg_color, outline=accent_color, width=3)

            # Center emblem initials or icon text
            words = title.split()
            initials = "".join([w[0] for w in words[:2]]).upper()
            draw.text((360, 380), initials, fill=accent_color, font=title_font)

            # Product title
            # Wrap title if long
            draw.text((100, 640), title, fill=(15, 23, 42), font=title_font)
            draw.text((100, 695), "Premium Quality • 100% Guaranteed", fill=(100, 116, 139), font=sub_font)

            img.save(filepath, 'PNG', quality=95)
            return f"products/{filename}"

        # 4. Products Data
        products_data = [
            # Electronics
            {
                'name': 'Aura Pro Wireless Headphones',
                'category': 'Electronics',
                'price': usd_to_inr(Decimal('149.99')),
                'discount_price': usd_to_inr(Decimal('129.99')),
                'stock': 28,
                'featured': True,
                'bg_color': (240, 253, 244),
                'accent_color': (16, 185, 129),
                'filename': 'headphones.png',
                'description': 'Engineered for audio perfection. The Aura Pro delivers active noise cancellation, 40-hour battery life, ultra-plush memory foam ear cups, and studio-grade acoustics with transparency mode.'
            },
            {
                'name': 'UltraView 4K Curved Monitor',
                'category': 'Electronics',
                'price': usd_to_inr(Decimal('399.00')),
                'discount_price': usd_to_inr(Decimal('349.00')),
                'stock': 12,
                'featured': True,
                'bg_color': (236, 253, 245),
                'accent_color': (5, 150, 105),
                'filename': 'monitor.png',
                'description': 'Immerse your vision in stunning 34-inch ultra-wide 4K HDR resolution. Features a 144Hz refresh rate, 1ms response time, USB-C 90W power delivery, and ergonomic tilt & height adjustment.'
            },
            {
                'name': 'Apex Mechanical Keyboard',
                'category': 'Electronics',
                'price': usd_to_inr(Decimal('89.50')),
                'discount_price': None,
                'stock': 18,
                'featured': False,
                'bg_color': (241, 245, 249),
                'accent_color': (15, 118, 110),
                'filename': 'keyboard.png',
                'description': 'Custom hot-swappable tactile switches, aircraft-grade brushed aluminum frame, customizable RGB backlighting, and detachable braided braided Type-C cable for typing enthusiasts.'
            },
            {
                'name': 'Quantum Smart Watch Series 5',
                'category': 'Electronics',
                'price': usd_to_inr(Decimal('199.99')),
                'discount_price': usd_to_inr(Decimal('179.99')),
                'stock': 35,
                'featured': True,
                'bg_color': (240, 253, 250),
                'accent_color': (13, 148, 136),
                'filename': 'smartwatch.png',
                'description': 'Track your health metrics with surgical precision. Always-on AMOLED display, ECG monitoring, blood oxygen sensor, GPS route tracking, and water resistance up to 50 meters.'
            },

            # Fashion
            {
                'name': 'Classic Minimalist Wool Coat',
                'category': 'Fashion',
                'price': usd_to_inr(Decimal('135.00')),
                'discount_price': usd_to_inr(Decimal('115.00')),
                'stock': 15,
                'featured': True,
                'bg_color': (248, 250, 252),
                'accent_color': (71, 85, 105),
                'filename': 'wool_coat.png',
                'description': 'Tailored from premium double-faced Australian wool blend. Clean silhouettes, notched lapels, horn button closures, and fully lined interior for effortless winter warmth.'
            },
            {
                'name': 'Urban Oversized Organic Hoodie',
                'category': 'Fashion',
                'price': usd_to_inr(Decimal('58.00')),
                'discount_price': usd_to_inr(Decimal('49.00')),
                'stock': 40,
                'featured': False,
                'bg_color': (240, 253, 244),
                'accent_color': (22, 163, 74),
                'filename': 'hoodie.png',
                'description': 'Crafted from 100% GOTS-certified heavyweight French terry cotton (450 GSM). Relaxed drop-shoulder silhouette with fleece lining and reinforced kangaroo pocket.'
            },
            {
                'name': 'CloudStride Running Shoes',
                'category': 'Fashion',
                'price': usd_to_inr(Decimal('89.99')),
                'discount_price': None,
                'stock': 22,
                'featured': True,
                'bg_color': (243, 244, 246),
                'accent_color': (16, 185, 129),
                'filename': 'shoes.png',
                'description': 'Engineered mesh upper with responsive nitrogen-infused foam midsole. Delivers cloud-like cushioning, high-traction rubber outsole, and zero break-in period.'
            },
            {
                'name': 'Artisan Leather Crossbody Bag',
                'category': 'Fashion',
                'price': usd_to_inr(Decimal('75.00')),
                'discount_price': usd_to_inr(Decimal('64.00')),
                'stock': 9,
                'featured': False,
                'bg_color': (254, 243, 199),
                'accent_color': (180, 83, 9),
                'filename': 'leather_bag.png',
                'description': 'Handcrafted from full-grain vegetable-tanned leather. Brass hardware, adjustable shoulder strap, magnetic snap flap, and interior phone and zippered compartments.'
            },

            # Home & Living
            {
                'name': 'Nordic Ceramic Pour-Over Set',
                'category': 'Home & Living',
                'price': usd_to_inr(Decimal('45.00')),
                'discount_price': None,
                'stock': 20,
                'featured': False,
                'bg_color': (245, 245, 244),
                'accent_color': (87, 83, 78),
                'filename': 'coffee_set.png',
                'description': 'Brew specialty cafe coffee at home. Includes matte ceramic dripper cone, heat-resistant borosilicate glass carafe, and 40 unbleached paper filters.'
            },
            {
                'name': 'Aroma Diffuser & Ambient Lamp',
                'category': 'Home & Living',
                'price': usd_to_inr(Decimal('36.00')),
                'discount_price': usd_to_inr(Decimal('29.99')),
                'stock': 55,
                'featured': True,
                'bg_color': (240, 253, 244),
                'accent_color': (5, 150, 105),
                'filename': 'diffuser.png',
                'description': 'Ultrasonic whisper-quiet mist technology paired with warm LED ambient lighting. Auto shut-off safety protection and 500ml capacity for up to 16 hours continuous use.'
            },
            {
                'name': 'Ergonomic Memory Foam Pillow',
                'category': 'Home & Living',
                'price': usd_to_inr(Decimal('49.00')),
                'discount_price': None,
                'stock': 25,
                'featured': False,
                'bg_color': (241, 245, 249),
                'accent_color': (100, 116, 139),
                'filename': 'pillow.png',
                'description': 'Orthopedic contoured design supports natural cervical spine alignment. Cooling bamboo fiber washable cover and high-density slow-rebound memory foam core.'
            },

            # Fitness & Sports
            {
                'name': 'HydroFlask Insulated Steel Bottle',
                'category': 'Fitness & Sports',
                'price': usd_to_inr(Decimal('32.00')),
                'discount_price': None,
                'stock': 65,
                'featured': False,
                'bg_color': (236, 253, 245),
                'accent_color': (16, 185, 129),
                'filename': 'bottle.png',
                'description': '32oz double-wall vacuum insulated 18/8 food-grade stainless steel. Keeps beverages ice cold for 24 hours or steaming hot for 12 hours. Sweat-free powder coat finish.'
            },
            {
                'name': 'Smart Body Composition Scale',
                'category': 'Fitness & Sports',
                'price': usd_to_inr(Decimal('69.00')),
                'discount_price': usd_to_inr(Decimal('54.99')),
                'stock': 19,
                'featured': True,
                'bg_color': (240, 253, 250),
                'accent_color': (13, 148, 136),
                'filename': 'scale.png',
                'description': 'Measures 14 essential health metrics including BMI, Body Fat %, Muscle Mass, and Bone Density with high-precision sensors. Syncs with Apple Health & Google Fit.'
            },
            {
                'name': 'Pro Resistance Loop Bands Set',
                'category': 'Fitness & Sports',
                'price': usd_to_inr(Decimal('24.99')),
                'discount_price': usd_to_inr(Decimal('19.99')),
                'stock': 45,
                'featured': False,
                'bg_color': (240, 253, 244),
                'accent_color': (4, 120, 87),
                'filename': 'bands.png',
                'description': 'Set of 5 natural latex resistance bands ranging from 5 lbs to 40 lbs of resistance. Includes carry pouch, exercise instructional guide, and door anchor.'
            },

            # Accessories
            {
                'name': 'Polarized Bamboo Sunglasses',
                'category': 'Accessories',
                'price': usd_to_inr(Decimal('42.00')),
                'discount_price': usd_to_inr(Decimal('35.00')),
                'stock': 14,
                'featured': False,
                'bg_color': (254, 242, 242),
                'accent_color': (185, 28, 28),
                'filename': 'sunglasses.png',
                'description': 'Eco-friendly sustainably harvested bamboo wooden arms with UV400 polarized anti-glare scratch-resistant lenses. Includes microfiber pouch and bamboo travel cylinder.'
            },
            {
                'name': 'MagSafe Slim Leather Wallet',
                'category': 'Accessories',
                'price': usd_to_inr(Decimal('29.00')),
                'discount_price': None,
                'stock': 38,
                'featured': True,
                'bg_color': (248, 250, 252),
                'accent_color': (51, 65, 85),
                'filename': 'wallet.png',
                'description': 'Ultra-slim magnetic cardholder crafted with top-grain leather and RFID shielding. Snaps firmly to iPhone with reinforced neodymium magnets, holding up to 3 cards.'
            },
        ]

        if options['regenerate_images']:
            for pdata in products_data:
                img_rel_path = generate_product_image(
                    pdata['filename'],
                    pdata['name'],
                    pdata['category'],
                    pdata['bg_color'],
                    pdata['accent_color'],
                    regenerate=True,
                )
                product = Product.objects.get(name=pdata['name'])
                product.image = img_rel_path
                product.save(update_fields=['image'])

            self.stdout.write(self.style.SUCCESS(
                f"Regenerated images for {len(products_data)} IndianShopEase products."
            ))
            return

        created_count = 0
        updated_count = 0

        for pdata in products_data:
            img_rel_path = generate_product_image(
                pdata['filename'],
                pdata['name'],
                pdata['category'],
                pdata['bg_color'],
                pdata['accent_color'],
                regenerate=options['regenerate_images'],
            )

            product, created = Product.objects.update_or_create(
                name=pdata['name'],
                defaults={
                    'category': cat_objs[pdata['category']],
                    'price': pdata['price'],
                    'discount_price': pdata['discount_price'],
                    'stock': pdata['stock'],
                    'featured': pdata['featured'],
                    'description': pdata['description'],
                    'image': img_rel_path,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] Products seeded: {created_count} created, {updated_count} updated."))
        self.stdout.write(self.style.SUCCESS("[SUCCESS] Database seeding completed successfully!"))
