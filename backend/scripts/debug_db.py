import os, sys
from sqlalchemy import create_engine
from sqlalchemy import inspect
from app.config import settings
from app.database import engine, Base

out_path = os.path.abspath(os.path.join(os.getcwd(), 'scripts', 'debug_db_output.txt'))
with open(out_path, 'w', encoding='utf-8') as f:
    def w(*args):
        print(*args)
        f.write(' '.join(str(a) for a in args) + "\n")

    try:
        w('PWD=', os.getcwd())
        w('settings.DATABASE_URL=', settings.DATABASE_URL)
        w('engine.url=', getattr(engine, 'url', None))
        try:
            ins = inspect(engine)
            tables = ins.get_table_names()
            w('Tables via engine:', tables)
        except Exception as e:
            w('Inspect engine error:', repr(e))

        url = str(getattr(engine, 'url', settings.DATABASE_URL))
        if url.startswith('sqlite'):
            path = url.replace('sqlite:///', '')
            path = os.path.abspath(path)
            w('Resolved sqlite path:', path)
            w('File exists:', os.path.exists(path))
            try:
                conn = __import__('sqlite3').connect(path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                w('Tables in file:', cur.fetchall())
                conn.close()
            except Exception as e:
                w('Error reading sqlite file:', repr(e))
        else:
            w('Not sqlite, URL:', url)

        # create tables on engine
        try:
            Base.metadata.create_all(bind=engine)
            w('Called Base.metadata.create_all on engine')
        except Exception as e:
            w('Create_all error on engine:', repr(e))

        # ensure nested test path
        nested = os.path.abspath(os.path.join(os.getcwd(), 'backend', os.path.basename(path))) if url.startswith('sqlite') else None
        if nested:
            w('Nested path:', nested)
            try:
                os.makedirs(os.path.dirname(nested), exist_ok=True)
                open(nested, 'a').close()
                alt = create_engine(f'sqlite:///{nested}', connect_args={'check_same_thread': False})
                Base.metadata.create_all(bind=alt)
                w('Created tables on nested path')
                conn = __import__('sqlite3').connect(nested)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                w('Tables in nested file:', cur.fetchall())
                conn.close()
            except Exception as e:
                w('Nested create error:', repr(e))

    except Exception as e:
        w('Unexpected error in debug script:', repr(e))

print('Wrote debug output to', out_path)

