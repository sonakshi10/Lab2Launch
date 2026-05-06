import sqlite3

conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS researcher_profiles (
        user_id TEXT PRIMARY KEY,
        researcher_id TEXT,
        name TEXT,
        domain TEXT,
        h_index INTEGER,
        i10_index INTEGER,
        keywords TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS industry_profiles (
        user_id TEXT PRIMARY KEY,
        company_id TEXT,
        name TEXT,
        domain TEXT,
        location TEXT,
        size TEXT,
        model TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investor_profiles (
        user_id TEXT PRIMARY KEY,
        investor_id TEXT,
        name TEXT,
        domain TEXT,
        risk TEXT,
        geo TEXT,
        investments TEXT
    )
    """)

    conn.commit()


# ---------- SAVE ----------

def save_researcher_profile(user_id, data):
    cursor.execute("""
    INSERT OR REPLACE INTO researcher_profiles
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, *data))
    conn.commit()


def save_industry_profile(user_id, data):
    cursor.execute("""
    INSERT OR REPLACE INTO industry_profiles
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, *data))
    conn.commit()


def save_investor_profile(user_id, data):
    cursor.execute("""
    INSERT OR REPLACE INTO investor_profiles
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, *data))
    conn.commit()


# ---------- LOAD ----------

def load_researcher_profile(user_id):
    cursor.execute("SELECT * FROM researcher_profiles WHERE user_id=?", (user_id,))
    return cursor.fetchone()


def load_industry_profile(user_id):
    cursor.execute("SELECT * FROM industry_profiles WHERE user_id=?", (user_id,))
    return cursor.fetchone()


def load_investor_profile(user_id):
    cursor.execute("SELECT * FROM investor_profiles WHERE user_id=?", (user_id,))
    return cursor.fetchone()