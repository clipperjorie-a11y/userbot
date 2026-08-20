from pyrogram import Client, filters
import sqlite3
from database import get_user_access, DB_NAME

@Client.on_message(filters.group & filters.incoming)
async def wtb_channel_comment(client, message):
    # Pyrogram mendeteksi komen di channel sebagai pesan di grup diskusi (linked_chat)
    # yang memiliki atribut 'reply_to_message' dari channel aslinya.
    if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
        return # Bukan pesan forward dari channel
        
    user_id = client.me.id
    pkg = get_user_access(user_id)
    if pkg not in ["autoreply", "full"]: return
    
    text = message.text.lower() if message.text else ""
    
    # 1. Cek Banned Words
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT word FROM banned_words WHERE user_id = ?", (user_id,))
    banned_words = [row[0].lower() for row in c.fetchall()]
    
    for bw in banned_words:
        if bw in text:
            return # Abaikan jika ada kata terlarang
            
    # 2. Cek Keyword WTB
    c.execute("SELECT keyword, reply_text FROM wtb_rules WHERE user_id = ?", (user_id,))
    rules = c.fetchall()
    conn.close()
    
    for kw, reply in rules:
        if kw.lower() in text:
            try:
                # Membalas pesan ini akan masuk sebagai komentar di channel
                await message.reply(reply) 
                break
            except: pass
