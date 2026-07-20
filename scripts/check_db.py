import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'query_history.db'
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count} rows")

    cursor.execute(f"PRAGMA table_info({table})")
    cols = [(r[1], r[2]) for r in cursor.fetchall()]
    print(f"    Columns: {cols}")

conn.close()
