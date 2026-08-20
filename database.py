import sqlite3

def init_db():
    conn = sqlite3.connect("bot_store.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            trx_id TEXT PRIMARY KEY,
            user_id INTEGER,
            package TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()
