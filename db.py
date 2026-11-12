"""Choose PostgreSQL when DATABASE_URL is configured, SQLite otherwise."""
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv('DATABASE_URL', '').startswith(('postgresql://','postgres://')):
    from db_postgres import *
else:
    from db_sqlite import *
