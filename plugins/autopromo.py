from pyrogram import Client, filters
import asyncio
import sqlite3
from database import get_user_access, DB_NAME

is_running = False
forward_message_data = {}  # Menyimpan data pesan yang akan di-forward

# 1. Atur Pesan Forward (Atur Pesan -> Forward dari channel/chat lain)
@Client.on_message(filters.command("setforward", prefixes=".") & filters.me)
async def set_forward_msg(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Balas (reply) ke pesan yang ingin Anda jadikan bahan Auto Forward!")
    
    user_id = message.from_user.id
    forward_message_data[user_id] = {
        "chat_id": message.reply_to_message.chat.id,
        "message_id": message.reply_to_message.id
    }
    await message.reply("✅ Pesan Forward berhasil disimpan! Siap dipromosikan.")

# 2. Atur Jeda Antar Grup (detik)
@Client.on_message(filters.command("setdelaygroup", prefixes=".") & filters.me)
async def set_delay_group(client, message):
    try:
        sec = int(message.text.split()[1])
        conn = sqlite3.connect(DB_NAME)
        conn.cursor().execute("INSERT OR REPLACE INTO settings (user_id, group_delay) VALUES (?, ?)", (message.from_user.id, sec))
        conn.commit(); conn.close()
        await message.reply(f"✅ Interval antar grup diatur ke {sec} detik.")
    except:
        await message.reply("Format: `.setdelaygroup 10`")

# 3. Atur Jeda Antar Putaran (menit)
@Client.on_message(filters.command("setdelayround", prefixes=".") & filters.me)
async def set_delay_round(client, message):
    try:
        mnt = int(message.text.split()[1])
        delay_sec = max(60, mnt * 60) # Minimal 1 menit (60 detik)
        conn = sqlite3.connect(DB_NAME)
        conn.cursor().execute("INSERT OR REPLACE INTO settings (user_id, delay) VALUES (?, ?)", (message.from_user.id, delay_sec))
        conn.commit(); conn.close()
        await message.reply(f"✅ Interval antar putaran diatur ke {delay_sec // 60} menit.")
    except:
        await message.reply("Format: `.setdelayround 5` (Min: 1 menit)")

# 4. Tambah Grup (Sesuai Video)
@Client.on_message(filters.command("addlpm", prefixes=".") & filters.me)
async def add_this_group(client, message):
    chat_id = str(message.chat.id)
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute("INSERT INTO lpm_groups (user_id, group_id) VALUES (?, ?)", (message.from_user.id, chat_id))
    conn.commit(); conn.close()
    await message.reply("✅ Grup berhasil ditambahkan ke Target Promosi!")

# 5. Jalankan Auto Forward (Mulai Promosi)
@Client.on_message(filters.command("startfw", prefixes=".") & filters.me)
async def start_autoforward(client, message):
    global is_running
    user_id = message.from_user.id
    pkg = get_user_access(user_id)
    
    if pkg not in ["basic", "full"]:
        return await message.reply("❌ Paket Anda tidak mendukung Auto Forward.")
        
    if user_id not in forward_message_data:
        return await message.reply("❌ Belum ada pesan forward yang diset. Balas pesan lalu ketik `.setforward` terlebih dahulu.")
        
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT group_id FROM lpm_groups WHERE user_id = ?", (user_id,))
    groups = [row[0] for row in c.fetchall()]
    
    c.execute("SELECT delay, group_delay FROM settings WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    round_delay = res[0] if res and res[0] else 60
    group_delay = res[1] if res and res[1] else 10
    conn.close()
    
    if not groups:
        return await message.reply("❌ Belum ada grup target. Masuk grup lalu ketik `.addlpm`")
        
    is_running = True
    await message.reply(f"🚀 **Auto Forward Berjalan!**\nTarget: {len(groups)} Grup\nJeda Antar Grup: {group_delay}s\nJeda Antar Putaran: {round_delay // 60}m")
    
    msg_info = forward_message_data[user_id]
    
    while is_running:
        for grp in groups:
            if not is_running: break
            try:
                # Memforward pesan dari sumber asal ke grup target
                await client.forward_messages(
                    chat_id=int(grp),
                    from_chat_id=msg_info["chat_id"],
                    message_ids=msg_info["message_id"]
                )
            except: pass
            await asyncio.sleep(group_delay) # Jeda antar grup
            
        if is_running:
            await asyncio.sleep(round_delay) # Jeda antar putaran

# 6. Stop Promosi
@Client.on_message(filters.command("stopfw", prefixes=".") & filters.me)
async def stop_autoforward(client, message):
    global is_running
    is_running = False
    await message.reply("🛑 Auto Forward Berhasil Dihentikan!")
