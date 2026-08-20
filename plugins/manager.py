from pyrogram import Client, filters
import sqlite3
from database import DB_NAME

# Fitur Tambah Kata Kunci WTB
@Client.on_message(filters.command("addwtb", prefixes=".") & filters.me)
async def add_wtb_rule(client, message):
    try:
        # Format: .addwtb netflix | Halo kak, saya jual netflix
        args = message.text.split(" ", 1)[1].split("|")
        keyword = args[0].strip().lower()
        reply = args[1].strip()
        user_id = message.from_user.id
        
        conn = sqlite3.connect(DB_NAME)
        conn.cursor().execute("INSERT INTO wtb_rules (user_id, keyword, reply_text) VALUES (?, ?, ?)", (user_id, keyword, reply))
        conn.commit(); conn.close()
        await message.reply(f"✅ Kata kunci '{keyword}' berhasil ditambahkan ke Auto-Reply WTB.")
    except:
        await message.reply("❌ Format salah! Gunakan: `.addwtb kata_kunci | teks_balasan`")

# Fitur Tambah Banned Word (Anti-Banned)
@Client.on_message(filters.command("addbanned", prefixes=".") & filters.me)
async def add_banned_word(client, message):
    try:
        word = message.text.split(" ", 1)[1].strip().lower()
        user_id = message.from_user.id
        
        conn = sqlite3.connect(DB_NAME)
        conn.cursor().execute("INSERT INTO banned_words (user_id, word) VALUES (?, ?)", (user_id, word))
        conn.commit(); conn.close()
        await message.reply(f"✅ Kata '{word}' dimasukkan ke daftar hitam. Bot tidak akan membalas jika ada kata ini.")
    except:
        await message.reply("❌ Format salah! Gunakan: `.addbanned kata_terlarang`")
