import sqlite3
from config import SQLITE_DB_PATH


def signup(email, password, role):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (email, password, role.lower())
        )
        conn.commit()
        return {"status": "success", "user_id": email, "role": role.lower()}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "User already exists"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
    finally:
        conn.close()


def login(email, password):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password, role FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"status": "error", "message": "User not found"}

    user_id, stored_password, role = user

    if password != stored_password:
        return {"status": "error", "message": "Invalid password"}

    return {
        "status": "success",
        "user_id": email,
        "role": role.lower()
    }
