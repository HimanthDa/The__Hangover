import os
import sys
import shutil
from pathlib import Path

# ── Step 1: Add project root to Python path ──────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Step 2: Point Django at settings ─────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ── Step 3: Bootstrap DB on Vercel BEFORE the WSGI app starts ────────────────
def _vercel_bootstrap():
    """Run DB migrations and seed on Vercel cold start."""
    db_path = Path('/tmp/db.sqlite3')
    if 'DATABASE_URL' not in os.environ:
        repo_db = ROOT / 'db.sqlite3'
        if not db_path.exists() and repo_db.exists():
            try:
                shutil.copy2(repo_db, db_path)
                print('[vercel] Seeded SQLite database copied to /tmp/')
            except Exception as copy_err:
                print(f'[vercel] Copy DB error: {copy_err}')

    import django
    django.setup()

    from django.core.management import call_command

    db_path = Path('/tmp/db.sqlite3')
    if db_path.exists() and db_path.stat().st_size == 0:
        try:
            db_path.unlink()
        except Exception:
            pass

    # Always run migrate (idempotent, fast if already done)
    try:
        call_command('migrate', interactive=False, verbosity=0)
        print('[vercel] Migrations OK')
    except Exception as e:
        print(f'[vercel] migrate error: {e}')
        return

    # Seed products if table is empty
    try:
        from products.models import Product
        if not Product.objects.exists():
            call_command('seed_products')
            print('[vercel] Products seeded')
    except Exception as e:
        print(f'[vercel] seed error: {e}')

    # Collect static files if not done yet
    try:
        static_root = Path('/tmp/staticfiles')
        if not static_root.exists():
            call_command('collectstatic', interactive=False, verbosity=0)
    except Exception as e:
        print(f'[vercel] collectstatic error: {e}')


IS_VERCEL = 'VERCEL' in os.environ or 'VERCEL_ENV' in os.environ

if IS_VERCEL:
    try:
        _vercel_bootstrap()
    except Exception as err:
        print(f'[vercel] bootstrap FATAL: {err}')

# ── Step 4: Create WSGI app ───────────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()

# Vercel accepts either name
app = application
handler = application




