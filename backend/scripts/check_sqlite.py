import sqlite3
from config import SQLITE_DB_PATH

conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()

# list tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\nTables in DB:")
for t in tables:
    table_name = t[0]
    count = cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'").fetchone()[0]
    print(f"{table_name}: {count} rows")

conn.close()