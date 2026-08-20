import sqlite3, time
DB_NAME = "ubot_jaseb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabel Users & Resellers
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, package TEXT, expired_at INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS resellers (user_id INTEGER PRIMARY KEY, package TEXT, expired_at INTEGER)")
    
    # Tabel Pengaturan User
    c.execute("CREATE TABLE IF NOT EXISTS settings (user_id INTEGER PRIMARY KEY, delay INTEGER DEFAULT 60)")
    c.execute("CREATE TABLE IF NOT EXISTS lpm_groups (user_id INTEGER, group_id TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS wtb_rules (user_id INTEGER, keyword TEXT, reply_text TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS banned_words (user_id INTEGER, word TEXT)")
    conn.commit(); conn.close()

def get_user_access(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT package, expired_at FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    if res and res[1] > int(time.time()):
        return res[0] # Return nama paket (basic/autoreply/full)
    return None

def set_delay(user_id, minutes):
    delay_sec = max(60, int(minutes) * 60) # Minimal 60 detik (1 menit)
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute("INSERT OR REPLACE INTO settings (user_id, delay) VALUES (?, ?)", (user_id, delay_sec))
    conn.commit(); conn.close()
    return delay_sec
