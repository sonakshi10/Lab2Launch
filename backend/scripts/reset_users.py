import sqlite3
from config import SQLITE_DB_PATH

conn = sqlite3.connect(SQLITE_DB_PATH)
conn.execute("DELETE FROM users")
conn.commit()
conn.close()

print("Users table cleared")