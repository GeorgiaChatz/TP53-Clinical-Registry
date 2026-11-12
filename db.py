"""Storage selector; secrets are environment variables in Streamlit Community Cloud."""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Cloud secrets do not require python-dotenv

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL.startswith(('postgres://', 'postgresql://')):
    from db_postgres import *
    BACKEND = 'Supabase / PostgreSQL'
elif DATABASE_URL:
    raise RuntimeError('DATABASE_URL must start with postgresql:// (or postgres://).')
else:
    from db_sqlite import *
    BACKEND = 'SQLite demo (temporary on Streamlit Cloud)'
