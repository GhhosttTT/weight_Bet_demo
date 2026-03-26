import os
import sqlite3

def list_db(path):
    print('Checking', path, 'exists=', os.path.exists(path))
    if not os.path.exists(path):
        return
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    rows = cur.fetchall()
    print('Tables:', rows)
    conn.close()

candidates = [
    os.path.abspath('weight_loss_betting.db'),
    os.path.abspath(os.path.join('backend','weight_loss_betting.db')),
    os.path.abspath(os.path.join('backend','backend','weight_loss_betting.db')),
    os.path.abspath(os.path.join('backend','test.db')),
    os.path.abspath('app.db'),
]
for p in candidates:
    list_db(p)

