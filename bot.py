import logging, sqlite3, time, asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, OWNER_ID

logging.basicConfig(level=logging.INFO)

# Inisialisasi Bot Panel & Userbot sekaligus menggunakan Pyrogram
# Masukkan API_ID dan API_HASH kamu (dapat dari my.telegram.org)
API_ID = 1234567       
API_HASH = "YOUR_HASH" 

# Jalankan sebagai Bot API (menggunakan Token BotFather)
bot = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Inisialisasi Database
def init_db():
    conn = sqlite3.connect("bot_panel_full.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, package TEXT, expired_at INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, package TEXT, duration_days INTEGER, is_used INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS settings (user_id INTEGER PRIMARY KEY, delay_round INTEGER DEFAULT 60)")
    c.execute("CREATE TABLE IF NOT EXISTS lpm_groups (user_id INTEGER, group_id TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS wtb_rules (user_id INTEGER, keyword TEXT, reply_text TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS banned_words (user_id INTEGER, word TEXT)")
    conn.commit()
    conn.close()

init_db()

def get_user_package(user_id):
    conn = sqlite3.connect("bot_panel_full.db")
    c = conn.cursor()
    c.execute("SELECT package, expired_at FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[1] > int(time.time()):
        return row[0]
    return None

def main_menu_keyboard(user_id):
    buttons = [
        [InlineKeyboardButton("🚀 Buat Userbot", callback_data="buat_ubot"), InlineKeyboardButton("🛒 Toko", callback_data="toko")],
        [InlineKeyboardButton("⭐ Fitur Unggulan", callback_data="fitur"), InlineKeyboardButton("📖 Panduan Buat", callback_data="panduan")],
        [InlineKeyboardButton("💳 Klaim Token", callback_data="klaim"), InlineKeyboardButton("🎁 Coba Gratis", callback_data="coba")]
    ]
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton("🛠️ Panel Reseller", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    text = (
        "<b>USERBOT JASEB OTOMATIS & AUTOREPLAY JORIE</b>\n\n"
        "🤖 Selamat datang! Silakan gunakan tombol di bawah "
        "untuk mulai membuat bot atau melihat menu utama."
    )
    await message.reply_text(text, reply_markup=main_menu_keyboard(message.from_user.id))

@bot.on_callback_query()
async def menu_callbacks(client, callback):
    code = callback.data
    user_id = callback.from_user.id
    await callback.answer()
    
    if code == "buat_ubot":
        pkg = get_user_package(user_id)
        if pkg:
            await client.send_message(user_id, f"✅ Paket aktif Anda: <b>{pkg.upper()}</b>\n\nBot Anda siap! Gunakan perintah di akun Anda:\n• <code>.addlpm</code>\n• <code>.startbc [teks]</code>\n• <code>.startfw</code>")
        else:
            await client.send_message(user_id, "❌ Anda belum memiliki paket aktif. Silakan beli di menu <b>🛒 Toko</b>.")
    elif code == "toko":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Paket Basic - Rp 4.000", callback_data="buy_basic")],
            [InlineKeyboardButton("📦 Paket Full - Rp 7.000", callback_data="buy_full")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="back_home")]
        ])
        await client.send_message(user_id, "🛒 <b>SILAKAN PILIH PAKET:</b>\nTransfer ke QRIS lalu konfirmasi ke owner.", reply_markup=kb)
    elif code in ["buy_basic", "buy_full"]:
        await client.send_message(user_id, "💳 Silakan transfer via QRIS lalu kirim bukti ke Owner untuk mendapatkan token.")
    elif code == "fitur":
        await client.send_message(user_id, "⭐ Fitur: AutoBC, Auto-Forward, Auto-Reply WTB Komen, Anti-Banned Word.")
    elif code == "panduan":
        await client.send_message(user_id, "📖 Panduan: Beli paket -> Klaim token -> Jalankan perintah ubot.")
    elif code == "coba":
        await client.send_message(user_id, "🎁 Gunakan durasi 1 hari di menu Toko.")
    elif code == "klaim":
        await client.send_message(user_id, "💳 Format klaim: `/klaim KODE_TOKEN`")
    elif code == "admin_panel":
        if user_id == OWNER_ID:
            await client.send_message(user_id, "🛠️ Format buat token: `/gentoken [basic/full] [hari]`")
    elif code == "back_home":
        await callback.message.edit_text("<b>MENU UTAMA BOT JASEB</b>", reply_markup=main_menu_keyboard(user_id))

@bot.on_message(filters.command("gentoken"))
async def gentoken_cmd(client, message):
    if message.from_user.id != OWNER_ID: return
    try:
        args = message.text.split()
        pkg, days = args[1].lower(), int(args[2])
        import random, string
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        conn = sqlite3.connect("bot_panel_full.db")
        conn.cursor().execute("INSERT INTO tokens (token, package, duration_days) VALUES (?, ?, ?)", (token, pkg, days))
        conn.commit(); conn.close()
        await message.reply_text(f"✅ Token: <code>{token}</code> (Paket: {pkg}, {days} Hari)")
    except:
        await message.reply_text("Format: `/gentoken [paket] [hari]`")

@bot.on_message(filters.command("klaim"))
async def klaim_cmd(client, message):
    try:
        token = message.text.split()[1].strip()
        user_id = message.from_user.id
        conn = sqlite3.connect("bot_panel_full.db")
        c = conn.cursor()
        c.execute("SELECT package, duration_days, is_used FROM tokens WHERE token = ?", (token,))
        row = c.fetchone()
        if not row or row[2] == 1:
            conn.close()
            return await message.reply_text("❌ Token tidak valid / sudah digunakan.")
        pkg, days = row[0], row[1]
        exp = int(time.time()) + (days * 86400)
        c.execute("INSERT OR REPLACE INTO users (user_id, package, expired_at) VALUES (?, ?, ?)", (user_id, pkg, exp))
        c.execute("UPDATE tokens SET is_used = 1 WHERE token = ?", (token,))
        conn.commit(); conn.close()
        await message.reply_text(f"✅ Berhasil klaim paket <b>{pkg.upper()}</b> selama {days} hari!")
    except:
        await message.reply_text("Format: `/klaim [TOKEN]`")

if __name__ == "__main__":
    print("=================================================")
    print("🚀 BOT PANEL PYROGRAM SIAP DIJALANKAN!")
    print("=================================================")
    bot.run()
