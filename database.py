import sqlite3
import time

def init_db():
    conn = sqlite3.connect("bot_panel_full.db")
    c = conn.cursor()
    
    # Tabel User & Masa Aktif Paket
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            package TEXT,
            expired_at INTEGER
        )
    """)
    
    # Tabel Token / Serial Key dari Reseller/Owner
    c.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            package TEXT,
            duration_days INTEGER,
            is_used INTEGER DEFAULT 0
        )
    """)
    
    # Tabel Pengaturan User (Delay minimal 1 menit / 60 detik)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER PRIMARY KEY,
            delay_round INTEGER DEFAULT 60,
            delay_group INTEGER DEFAULT 10
        )
    """)
    
    # Tabel Target Grup LPM
    c.execute("""
        CREATE TABLE IF NOT EXISTS lpm_groups (
            user_id INTEGER,
            group_id TEXT
        )
    """)
    
    # Tabel Aturan Auto-Reply WTB (Komen Channel)
    c.execute("""
        CREATE TABLE IF NOT EXISTS wtb_rules (
            user_id INTEGER,
            keyword TEXT,
            reply_text TEXT
        )
    """)
    
    # Tabel Anti-Banned Words
    c.execute("""
        CREATE TABLE IF NOT EXISTS banned_words (
            user_id INTEGER,
            word TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def get_user_package(user_id):
    conn = sqlite3.connect("bot_panel_full.db")
    c = conn.cursor()
    c.execute("SELECT package, expired_at FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[1] > int(time.time()):
        return row[0]
    return None
