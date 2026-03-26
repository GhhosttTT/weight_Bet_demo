import os
import sqlite3
from sqlalchemy import create_engine
from app.config import settings
from app.database import engine, Base

print('PWD=', os.getcwd())
print('settings.DATABASE_URL=', settings.DATABASE_URL)
print('engine.url=', getattr(engine, 'url', None))

# Ensure file for engine if sqlite
if settings.DATABASE_URL.startswith('sqlite:'):
    path = settings.DATABASE_URL.replace('sqlite:///', '').replace('sqlite://', '')
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    print('resolved settings sqlite path=', path)
    os.makedirs(os.path.dirname(path) or os.getcwd(), exist_ok=True)
    open(path, 'a').close()
    # create tables on engine
    try:
        Base.metadata.create_all(bind=engine)
        print('Created tables using settings engine')
    except Exception as e:
        print('Error creating tables on engine:', e)

# Also ensure nested path used by tests
nested = os.path.abspath(os.path.join(os.getcwd(), 'backend', os.path.basename(path)))
print('nested path=', nested)
os.makedirs(os.path.dirname(nested), exist_ok=True)
open(nested, 'a').close()
try:
    alt = create_engine(f'sqlite:///{nested}', connect_args={'check_same_thread': False})
    Base.metadata.create_all(bind=alt)
    print('Created tables in nested path')
except Exception as e:
    print('Error creating tables in nested path:', e)

# List tables in both files
for p in [path, nested]:
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        print(f'tables in {p}:', tables)
        conn.close()
    except Exception as e:
        print('Error listing tables in', p, e)

