import os
from sqlalchemy import create_engine
from app.config import settings
from app.database import Base

# Resolve sqlite path the app uses
db_url = settings.DATABASE_URL
if not db_url.startswith('sqlite:'):
    raise SystemExit('Not sqlite DB, abort')
path = db_url.replace('sqlite:///', '').replace('sqlite://', '')
if not os.path.isabs(path):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.abspath(os.path.join(base_dir, path))
# ensure directory
os.makedirs(os.path.dirname(path), exist_ok=True)
# touch file
open(path, 'a').close()
print('Using sqlite file:', path)
# create engine and tables
engine = create_engine(f'sqlite:///{path}', connect_args={'check_same_thread': False})
try:
    Base.metadata.create_all(bind=engine)
    print('Created tables on', path)
except Exception as e:
    print('Create tables error:', e)
# list tables
import sqlite3
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', cur.fetchall())
conn.close()
