import sqlite3
from pathlib import Path
path = Path('instance/home_builders.db')
print('DB exists:', path.exists(), path)
if not path.exists():
    raise SystemExit('Database file missing')
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name,type FROM sqlite_master WHERE type IN ('table','index') ORDER BY name;")
print('schema objects:')
for row in cur.fetchall():
    print(row)
for table in ['user','person','activity_log','user_settings','attendance','category']:
    try:
        cur.execute(f"PRAGMA table_info({table});")
        cols = cur.fetchall()
        print('\n', table, 'columns:')
        for col in cols:
            print(col)
    except Exception as e:
        print('skip', table, e)
conn.close()
