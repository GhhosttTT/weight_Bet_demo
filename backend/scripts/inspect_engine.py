from app.database import engine, Base
from sqlalchemy import inspect
import os

print('Engine URL:', engine.url)
try:
    insp = inspect(engine)
    print('Tables via engine:', insp.get_table_names())
except Exception as e:
    print('Inspect engine error:', e)

# if sqlite, show file path and tables
url = str(engine.url)
if url.startswith('sqlite'):
    path = url.replace('sqlite:///', '')
    path = os.path.abspath(path)
    print('Resolved sqlite path:', path)
    print('File exists:', os.path.exists(path))
    try:
        import sqlite3
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print('Tables in file:', cur.fetchall())
        conn.close()
    except Exception as e:
        print('Error reading sqlite file:', e)
else:
    print('Not sqlite, URL:', url)

