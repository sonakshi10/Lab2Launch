import sqlite3
from config import SQLITE_DB_PATH

conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Users table created")