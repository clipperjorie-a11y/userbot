from pyrogram import Client, filters
import asyncio
import sqlite3
from database import get_user_access, set_delay, DB_NAME

is_running = False

@Client.on_message(filters.command("setdelay", prefixes=".") & filters.me)
async def cmd_setdelay(client, message):
    try:
        mnt = int(message.text.split()[1])
        final_sec = set_delay(message.from_user.id, mnt)
        await message.reply(f"✅ Delay berhasil diatur menjadi {final_sec // 60} menit.")
    except: await message.reply("Format: `.setdelay [angka_dalam_menit]` (Min: 1)")

@Client.on_message(filters.command("addlpm", prefixes=".") & filters.me)
async def add_this_group(client, message):
    # Tambah grup otomatis dari chat saat ini (Sesuai video)
    chat_id = str(message.chat.id)
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute("INSERT INTO lpm_groups (user_id, group_id) VALUES (?, ?)", (message.from_user.id, chat_id))
    conn.commit(); conn.close()
    await message.reply(f"✅ Grup ini berhasil ditambahkan ke database promosi.")

@Client.on_message(filters.command("startbc", prefixes=".") & filters.me)
async def start_bc(client, message):
    global is_running
    user_id = message.from_user.id
    pkg = get_user_access(user_id)
    
    if pkg not in ["basic", "full"]: 
        return await message.reply("❌ Paket Anda tidak mendukung Auto-Broadcast.")
        
    try: text = message.text.split(" ", 1)[1]
    except: return await message.reply("❌ Masukkan teks! `.startbc Teks promo...`")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT group_id FROM lpm_groups WHERE user_id = ?", (user_id,))
    groups = [row[0] for row in c.fetchall()]
    c.execute("SELECT delay FROM settings WHERE user_id = ?", (user_id,))
    delay_data = c.fetchone()
    delay = delay_data[0] if delay_data else 60
    conn.close()
    
    is_running = True
    await message.reply(f"🚀 **AutoBC Jalan!**\nTarget: {len(groups)} Grup\nDelay: {delay // 60} menit.")
    
    while is_running:
        for grp in groups:
            if not is_running: break
            try: await client.send_message(int(grp), text)
            except: pass
            await asyncio.sleep(5) # Jeda antar grup 5 detik
        if is_running:
            await asyncio.sleep(delay) # Jeda antar putaran sesuai kemauan user
