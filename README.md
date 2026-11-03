# IndianShopEase – Modern E-Commerce Platform

A complete, responsive, modern E-Commerce web application built with **Python Django**, **HTML5**, **CSS3**, and **JavaScript**, designed with a minimalist emerald green, clean white, and light grey slate aesthetic.

IndianShopEase provides a full commercial-grade shopping experience from product catalog discovery and real-time inventory management to session-backed cart management, atomic checkout, and administrator order tracking.

---

## 🌟 Key Features

### 1. Storefront & UI/UX Design
- **Modern Palette**: Emerald green (`#10b981`), crisp white, and light grey slate.
- **Responsive Layout**: Optimized for mobile, tablet, laptop, and desktop viewports.
- **Hero Showcase**: High-impact banner with value propositions, trust badges, and featured staff picks.
- **Product Cards**: Elevating hover animations, discount percentage tags, stock status dots, and direct Add-to-Cart actions.
- **Instant Product Search & Filters**: Live search across names, categories, and descriptions; category pills navigation; multi-criteria sorting (Price: Low-High, High-Low, Newest, A-Z).

### 2. Product Catalog & Details
- Detailed view with high-resolution imagery and SKU generation.
- Dynamic stock indicator:
  - **In Stock** (exact quantity available)
  - **Low Stock** badge (alerts when stock $\le$ 5)
  - **Sold Out** state (disables order actions)
- Interactive quantity stepper protected against exceeding available stock.
- "Buy Now with 1-Click" shortcut leading straight to checkout.
- Related products recommendations within the same category.

### 3. Shopping Cart System
- **Session-backed Cart**: Works seamlessly for both authenticated members and guest shoppers.
- Real-time or AJAX-enhanced cart updates with toast notifications.
- Automatic calculations:
  - Item subtotal
  - Shipping rate (free for orders of ₹4,746.43 or more; ₹474.64 flat rate otherwise)
  - Estimated grand total
- Full inventory guards: users cannot add or increment beyond actual warehouse stock.
- Promo coupon integration (e.g. `SHOPEASE10`).

### 4. User Authentication & Profile
- Built on Django's secure authentication framework.
- User registration with password matching and length validation.
- User login, remember-me support, and secure logout.
- Customer Profile dashboard:
  - Account statistics (total orders, active orders)
  - Edit personal details (name, email)
  - Quick access to order history

### 5. Checkout & Order Processing
- Step-by-step clean checkout form (Customer details, Shipping address, Payment method).
- **Atomic Database Transaction**:
  - Validates stock availability for every cart item at submission time.
  - Decrements product stock inventory automatically.
  - Generates a unique tracking Order ID (e.g., `SE-A1B2C3D4`).
  - Creates relational `Order` and `OrderItem` records.
  - Clears the active shopping cart session upon success.
- Order Confirmation screen with print receipt functionality.

### 6. Order Tracking & History
- Customer order history page displaying order IDs, status pills, and line item previews.
- Visual 4-step delivery progress tracker:
  $$\text{Placed} \longrightarrow \text{Processing} \longrightarrow \text{Shipped} \longrightarrow \text{Delivered}$$
- Support for order cancellation status.

### 7. Django Admin Dashboard
- Complete admin control at `/admin/`.
- Manage products, live pricing, stock counts, and featured statuses.
- Update order statuses (`Placed`, `Processing`, `Shipped`, `Delivered`, `Cancelled`) individually or using bulk actions.
- Inline order items display with calculated line totals.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, Django 5.x
- **Database**: SQLite3 (Django ORM)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling & UI**: Custom CSS (`style.css`), Bootstrap 5.3 (Grid & Utilities), Bootstrap Icons
- **Image Processing**: Pillow

---

## 📁 Project Structure

```text
IndianShopEase/
│
├── manage.py                     # Django management script
├── requirements.txt              # Project dependencies
├── README.md                     # Documentation
│
├── store_project/                # Project configuration
│   ├── __init__.py
│   ├── settings.py               # Django settings, apps, templates, media
│   ├── urls.py                   # Master URL routing
│   ├── asgi.py
│   └── wsgi.py
│
├── shop/                         # Core e-commerce application
│   ├── __init__.py
│   ├── admin.py                  # Django Admin customization & actions
│   ├── apps.py                   # App config
│   ├── cart.py                   # Session-based Shopping Cart engine
│   ├── context_processors.py     # Global cart & category context
│   ├── forms.py                  # Registration, Profile, Checkout forms
│   ├── models.py                 # Category, Product, Order, OrderItem
│   ├── tests.py                  # Full automated test suite
│   ├── urls.py                   # Shop views routing
│   ├── views.py                  # Views for catalog, cart, checkout, auth
│   │
│   ├── migrations/               # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   │
│   └── management/
│       └── commands/
│           └── seed_products.py  # Seed sample products & demo accounts
│
├── templates/                    # HTML Templates
│   ├── base.html                 # Master layout with nav, search, & footer
│   ├── home.html                 # Hero, categories, deals, & catalog
│   ├── product_detail.html       # Product page with stock & reviews
│   ├── cart.html                 # Shopping cart table & summary
│   ├── checkout.html             # Order checkout & payment options
│   ├── order_success.html        # Order confirmation & receipt
│   ├── orders.html               # Order history listing
│   ├── order_detail.html         # Order tracking & invoice view
│   ├── login.html                # User login form
│   ├── register.html             # Customer registration
│   └── profile.html              # Customer profile & account stats
│
├── static/                       # Static assets
│   ├── css/
│   │   └── style.css             # Custom styles & responsive theme
│   ├── js/
│   │   └── main.js               # AJAX add-to-cart, toasts, stepper
│   └── images/
│
└── media/                        # Uploaded and seeded product images
    └── products/
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python (version 3.10 or higher) and `pip` are installed on your system.

### 2. Setup Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Sample Products

Run the custom management command to populate 16 curated products across 5 categories:

```bash
python manage.py seed_products
```

Create an administrator account for local development with:

```bash
python manage.py createsuperuser
```

Predictable demo accounts are disabled by default. To create them for a local
demonstration only, run `python manage.py seed_products --demo-users`. Never use
this option on a public deployment.

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to:
**`http://127.0.0.1:8000/`**

### 7. Deploy to Render

This repository includes a Render Blueprint in `render.yaml`. It provisions a
Django web service, PostgreSQL database, and persistent product-media disk.
The persistent service and database use paid Render plans; review the current
prices in Render before creating the Blueprint.

1. Push the project to a GitHub repository and connect that repository in Render.
2. In Render, choose **New → Blueprint**, select the repository, and review the
   services and costs before applying the Blueprint.
3. After the first deployment, open the web service Shell and create an admin
   account:

   ```bash
   python manage.py createsuperuser
   python manage.py seed_products --no-demo-users
   ```

4. Open the deployed service URL. Sign in to `/admin/` with the account created
   above. If you add a custom domain, include it in both `ALLOWED_HOSTS` and
   `CSRF_TRUSTED_ORIGINS` in Render.

The production settings read secrets and database configuration from the
environment, serve collected static files with WhiteNoise, and store uploads on
the persistent disk. The bundled media images are copied to that disk when the
service starts. Demo accounts are disabled by default.

All store prices are displayed in INR. Existing database product prices and
order totals are converted by migration using the published rate of
₹94.928524 per USD on November 3, 2026; newly seeded sample products use the
same rate. Shipping is ₹474.64 below the ₹4,746.43 free-shipping threshold.

---

Demo accounts are disabled by default. Create a local administrator with
`python manage.py createsuperuser` instead of using shared default credentials.

---

## 🧪 Running Automated Tests

Run the complete test suite covering models, cart operations, atomic stock deductions, checkout, and authentication:

```bash
python manage.py test
```

---

## 🛒 Key Workflow Demonstration

1. **Browse & Filter**: Visit `http://127.0.0.1:8000/` to explore products. Use the category pills, sort dropdown, or search bar (press `/` to focus).
2. **View Product Details**: Click any product or eye icon to view details, specifications, and live stock count.
3. **Cart Operations**: Add products to cart. Test adding more than the available stock — the cart engine automatically caps the quantity and warns the user.
4. **Checkout**: Proceed to `/checkout/` as a guest or logged-in user. Fill in contact and shipping details, choose payment method, and click **Place Order Now**.
5. **Stock Deduction & Confirmation**: The order is created atomically in `db.sqlite3`, inventory stock is reduced by the purchased quantities, and an invoice receipt with order tracking is displayed.
6. **Admin Management**: Create a local admin account with `python manage.py createsuperuser`, then log into `http://127.0.0.1:8000/admin/`. View customer orders, update order status to `Processing`, `Shipped`, or `Delivered`, and verify stock updates.
