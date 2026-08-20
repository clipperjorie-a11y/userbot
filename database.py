import sqlite3
import time

def init_db():
    conn = sqlite3.connect("ubot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            expired_at INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_subscription(user_id, days=30):
    conn = sqlite3.connect("ubot.db")
    cursor = conn.cursor()
    
    # Cek expired sekarang
    cursor.execute("SELECT expired_at FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    now = int(time.time())
    added_seconds = days * 86400
    
    if row and row[0] > now:
        new_expired = row[0] + added_seconds
    else:
        new_expired = now + added_seconds
        
    cursor.execute("INSERT OR REPLACE INTO users (user_id, expired_at) VALUES (?, ?)", (user_id, new_expired))
    conn.commit()
    conn.close()
    return new_expired

def is_active(user_id):
    conn = sqlite3.connect("ubot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT expired_at FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] > int(time.time()):
        return True
    return False
