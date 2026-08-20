from pyrogram import Client, filters
from database import DB_NAME
import sqlite3, time

# Owner menambahkan reseller
@Client.on_message(filters.command("addreseller", prefixes=".") & filters.user(OWNER_ID))
async def add_reseller(client, message):
    # Format: .addreseller <user_id> <paket> <durasi_hari>
    try:
        args = message.text.split()
        user_id, package, days = int(args[1]), args[2].lower(), int(args[3])
        exp = int(time.time()) + (days * 86400) if days < 1000 else int(time.time()) + (180 * 86400) # 180 hari = 6 bln garansi perm
        
        conn = sqlite3.connect(DB_NAME)
        conn.cursor().execute("INSERT OR REPLACE INTO resellers (user_id, package, expired_at) VALUES (?, ?, ?)", (user_id, package, exp))
        conn.commit(); conn.close()
        await message.reply(f"✅ Reseller {user_id} paket {package} berhasil ditambahkan selama {days} hari.")
    except: await message.reply("Format: `.addreseller [ID_USER] [basic/autoreply/full] [jumlah_hari]`")

# Reseller menambahkan user
@Client.on_message(filters.command("adduser", prefixes="."))
async def add_user(client, message):
    sender_id = message.from_user.id
    
    # Cek akses reseller
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT package, expired_at FROM resellers WHERE user_id = ?", (sender_id,))
    reseller = c.fetchone()
    
    if not reseller or reseller[1] < int(time.time()):
        return await message.reply("❌ Anda bukan reseller aktif.")
        
    try:
        args = message.text.split()
        target_id, package, days = int(args[1]), args[2].lower(), int(args[3])
        
        # Validasi batas paket reseller
        if reseller[0] != "full" and package != reseller[0]:
            return await message.reply(f"❌ Reseller paket '{reseller[0]}' tidak bisa menjual paket '{package}'.")
            
        exp = int(time.time()) + (days * 86400)
        c.execute("INSERT OR REPLACE INTO users (user_id, package, expired_at) VALUES (?, ?, ?)", (target_id, package, exp))
        conn.commit()
        await message.reply(f"✅ User {target_id} berhasil diaktifkan untuk paket {package}.")
    except: await message.reply("Format: `.adduser [ID_USER] [paket] [jumlah_hari]`")
    finally: conn.close()
