# The Hangover

A full-stack professional website for beverages: cold drinks, soft drinks, and wines. It combines **informational content** (history, ingredients, origins) with **e-commerce** (browse, cart, checkout).

## Features

- **Pages:** Home, About, Contact, Cold Drinks, Soft Drinks, Wines, Drink History, Wine History, Product Detail, Shopping Cart, Checkout, Order Confirmation, Login/Signup, Admin Dashboard
- **Frontend:** Responsive layout, navigation, search, filters (price, category), product cards with add-to-cart and quantity
- **Backend:** Django with SQLite; user registration/login; session-based cart; order creation; admin panel for products, categories, and orders
- **Product info:** Name, category, brand, price, description, ingredients, history, image, alcohol % (wines), country of origin
- **Wine section:** Educational content on types (Red, White, Rosé, Sparkling), winemaking process, regions, and history timeline

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript (Django templates)
- **Backend:** Django 4.x
- **Database:** SQLite (default; can switch to MySQL/PostgreSQL in production)
- **Authentication:** Django built-in auth (sessions)

## Project Structure

```
The Hangover/
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── main/                   # Home, About, Contact, Drink/Wine History
├── products/               # Categories, Products, list & detail views
├── cart/                   # Session cart, add/update/remove
├── orders/                 # Checkout, Order, OrderItem
├── accounts/               # Login, Signup, Logout, Admin Dashboard
├── templates/              # Base + all page templates
├── static/                 # CSS, JS
├── media/                  # Uploaded product images (created at runtime)
├── manage.py
├── requirements.txt
└── README.md
```

## How to Run Locally

### 1. Create and activate a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser (for admin and dashboard)

```bash
python manage.py createsuperuser
```
Enter username, email (optional), and password. This user will be able to log in and access `/admin/` and `/accounts/dashboard/`.

### 5. Seed sample products (optional)

```bash
python manage.py seed_products
```
This creates three categories (Cold Drinks, Soft Drinks, Wines) and several sample beverages.

### 6. Start the development server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

- **Home:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/ (use the superuser you created)
- **Dashboard:** http://127.0.0.1:8000/accounts/dashboard/ (staff only)

## Admin Panel

- **Add/edit drinks:** Admin → Products → Products (or Categories)
- **Upload images:** When adding/editing a product, use the Image field
- **Manage orders:** Admin → Orders → Orders
- **Manage users:** Admin → Authentication and authorization → Users

## E-commerce (Demo)

- **Cart:** Stored in session; add/update/remove from cart pages and product pages.
- **Checkout:** Fill shipping details and the page will immediately render a QR code containing the total amount (e.g. `AMOUNT:₹123.45`). Scanning the code with your payment app will give you the correct amount to pay; the QR updates automatically when the total changes. After scanning, submit the form to place the order. The server does not actually process any payment – it’s purely a demo.
- **Order confirmation / detail / receipt:** These pages also show the dynamically generated QR code so you can scan the order amount again if needed. A PDF version of the receipt can be downloaded.
- **Fallback:** if the `qrcode` and `Pillow` Python packages are missing, a static image (`static/images/qr.jpg.jpg`) will be shown instead of the generated code.
- **Order persistence:** Orders are saved in the database when placed; history is available for logged‑in users.

## Design

- Beverage-themed colors (wine red, amber, cream)
- Clean, modern UI with responsive layout
- Mobile-friendly navigation and product grid

## Notes for Beginners

- Templates use Django Template Language (DTL): `{{ variable }}`, `{% tag %}`, `{% url 'app:name' %}`
- Static files live in `static/` and are referenced with `{% load static %}` and `{% static 'css/style.css' %}`
- Product images uploaded via admin are stored in `media/products/`
- Cart is session-based: no cart model; see `cart/utils.py` and `cart/context_processors.py`

## License

This project is for educational and portfolio use.
