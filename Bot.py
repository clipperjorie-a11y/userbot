import logging, sqlite3, time, asyncio, random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from config import BOT_TOKEN, OWNER_ID, PRICING
from database import init_db, get_user_package

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

init_db()

# --- BAGIAN 1: TELEGRAM BOT PANEL INTERAKTIF (MENU UTAMA) ---

def main_menu_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚀 Buat Userbot", callback_data="buat_ubot"),
        InlineKeyboardButton("🛒 Toko", callback_data="toko"),
        InlineKeyboardButton("⭐ Fitur Unggulan", callback_data="fitur"),
        InlineKeyboardButton("📖 Panduan Buat", callback_data="panduan"),
        InlineKeyboardButton("💳 Klaim Token", callback_data="klaim"),
        InlineKeyboardButton("🎁 Coba Gratis", callback_data="coba")
    )
    if user_id == OWNER_ID:
        keyboard.add(InlineKeyboardButton("🛠️ Panel Reseller / Buat Token", callback_data="admin_panel"))
    return keyboard

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    text = (
        "<b>USERBOT JASEB OTOMATIS & AUTOREPLAY JORIE</b>\n\n"
        "🤖 Selamat datang! Silakan gunakan tombol di bawah "
        "untuk mulai membuat bot atau melihat menu utama."
    )
    await message.answer(text, reply_markup=main_menu_keyboard(message.from_user.id))

@dp.callback_query_handler(lambda c: c.data in ["buat_ubot", "toko", "fitur", "panduan", "klaim", "coba", "admin_panel", "back_home", "buy_basic", "buy_autoreply", "buy_full"])
async def menu_callbacks(callback_query: types.CallbackQuery):
    code = callback_query.data
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    
    if code == "buat_ubot":
        pkg = get_user_package(user_id)
        if pkg:
            await bot.send_message(user_id, f"✅ Paket aktif Anda: <b>{pkg.upper()}</b>\n\nBot Anda sudah siap! Gunakan perintah berikut di akun Anda:\n• <code>.addlpm</code> (di grup target)\n• <code>.startbc [teks]</code> (sebar biasa)\n• <code>.startfw</code> (forward pesan)\n• <code>.addwtb [kata] | [balasan]</code> (komentar wtb)\n• <code>.setdelayround [menit]</code> (minimal 1 menit)")
        else:
            await bot.send_message(user_id, "❌ Anda belum memiliki paket aktif. Silakan beli di menu <b>🛒 Toko</b> atau klaim token dari reseller.")
            
    elif code == "toko":
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton("📦 Paket Basic (AutoBC & Forward) - Mulai 2k", callback_data="buy_basic"),
            InlineKeyboardButton("📦 Paket AutoReply (WTB Channel) - Mulai 3k", callback_data="buy_autoreply"),
            InlineKeyboardButton("📦 Paket Full Fitur (All in One) - Mulai 3k", callback_data="buy_full"),
            InlineKeyboardButton("⬅️ Kembali", callback_data="back_home")
        )
        await bot.send_message(user_id, "🛒 <b>DAFTAR HARGA PAKET UBOT:</b>\n\n• <b>Basic:</b> 1d(2k), 1b(4k), Perm(15k) [Garansi 6 bln]\n• <b>AutoReply:</b> 1d(3k), 1b(5k), Perm(20k) [Garansi 6 bln]\n• <b>Full Fitur:</b> 1d(3k), 1b(7k), Perm(35k) [Garansi 6 bln]\n\nSilakan transfer sesuai harga paket ke QRIS toko, lalu konfirmasi ke owner untuk mendapatkan token.", reply_markup=kb)
        
    elif code in ["buy_basic", "buy_autoreply", "buy_full"]:
        paket_name = code.replace("buy_", "")
        await bot.send_message(user_id, f"💳 <b>INVOICE PEMBELIAN ({paket_name.upper()})</b>\n\nSilakan transfer ke QRIS resmi toko. Setelah transfer, kirim bukti pembayaran ke Owner untuk mendapatkan token serial key aktivasi.")
        
    elif code == "fitur":
        await bot.send_message(user_id, "⭐ <b>Fitur Unggulan Lengkap:</b>\n- Auto Broadcast Sebar Biasa & Auto-Forward\n- Auto-Reply Komentar Channel (WTB Responder)\n- Anti-Banned Word (Filter Kata Terlarang)\n- Pengaturan Delay Fleksibel (Minimal 1 Menit)")
    elif code == "panduan":
        await bot.send_message(user_id, "📖 <b>Panduan Penggunaan:</b>\n1. Beli paket di Toko / Klaim token via `/klaim [TOKEN]`.\n2. Aktifkan fitur menggunakan perintah berawalan titik (`.`) di Telegram Anda.")
    elif code == "coba":
        await bot.send_message(user_id, "🎁 Gunakan opsi durasi 1 hari (1d) di menu Toko untuk mencoba semua fitur.")
    elif code == "klaim":
        await bot.send_message(user_id, "💳 Masukkan token Anda dengan format:\n`/klaim KODE_TOKEN`")
    elif code == "admin_panel":
        if user_id == OWNER_ID:
            await bot.send_message(user_id, "🛠️ <b>Panel Reseller / Admin:</b>\nBuat token aktivasi dengan format:\n`/gentoken [basic/autoreply/full] [jumlah_hari]`\nContoh: `/gentoken full 30`")
    elif code == "back_home":
        await bot.edit_message_text(
            "<b>USERBOT JASEB OTOMATIS & AUTOREPLAY JORIE</b>\n\n🤖 Selamat datang kembali di Menu Utama:",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=main_menu_keyboard(user_id)
        )

@dp.message_handler(commands=["gentoken"])
async def gentoken_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID: return
    try:
        args = message.text.split()
        pkg, days = args[1].lower(), int(args[2])
        import random, string
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        conn = sqlite3.connect("bot_panel_full.db")
        conn.cursor().execute("INSERT INTO tokens (token, package, duration_days) VALUES (?, ?, ?)", (token, pkg, days))
        conn.commit(); conn.close()
        
        await message.reply(f"✅ <b>Token Berhasil Dibuat!</b>\nPaket: {pkg.upper()}\nDurasi: {days} Hari\nToken: <code>{token}</code>")
    except:
        await message.reply("Format: `/gentoken [basic/autoreply/full] [jumlah_hari]`")

@dp.message_handler(commands=["klaim"])
async def klaim_cmd(message: types.Message):
    try:
        token = message.text.split()[1].strip()
        user_id = message.from_user.id
        
        conn = sqlite3.connect("bot_panel_full.db")
        c = conn.cursor()
        c.execute("SELECT package, duration_days, is_used FROM tokens WHERE token = ?", (token,))
        row = c.fetchone()
        
        if not row or row[2] == 1:
            conn.close()
            return await message.reply("❌ Token tidak valid atau sudah digunakan.")
            
        pkg, days = row[0], row[1]
        exp = int(time.time()) + (days * 86400)
        
        c.execute("INSERT OR REPLACE INTO users (user_id, package, expired_at) VALUES (?, ?, ?)", (user_id, pkg, exp))
        c.execute("UPDATE tokens SET is_used = 1 WHERE token = ?", (token,))
        conn.commit(); conn.close()
        
        await message.reply(f"✅ <b>KLAIM BERHASIL!</b>\nPaket <b>{pkg.upper()}</b> aktif selama {days} hari.")
    except:
        await message.reply("Format: `/klaim [KODE_TOKEN]`")


# --- BAGIAN 2: MESIN USERBOT FULL FITUR (AUTOPROMO, FORWARD, & WTB KOMEN) ---
# Berjalan otomatis untuk user yang aktif saat script utama dijalankan.

API_ID = 1234567       # Ganti dengan API ID Telegram Anda dari my.telegram.org
API_HASH = "YOUR_HASH" # Ganti dengan API Hash Telegram Anda

ubot = Client("my_session_jaseb", api_id=API_ID, api_hash=API_HASH)
is_bc_running = False
forward_cache = {}

# 1. Tambah Grup LPM
@ubot.on_message(filters.command("addlpm", prefixes=".") & filters.me)
async def ubot_addlpm(client, message):
    chat_id = str(message.chat.id)
    conn = sqlite3.connect("bot_panel_full.db")
    conn.cursor().execute("INSERT INTO lpm_groups (user_id, group_id) VALUES (?, ?)", (message.from_user.id, chat_id))
    conn.commit(); conn.close()
    await message.reply("✅ Grup ini berhasil ditambahkan ke Target Broadcast.")

# 2. Atur Jeda Antar Putaran (Minimal 1 Menit)
@ubot.on_message(filters.command("setdelayround", prefixes=".") & filters.me)
async def ubot_setdelay(client, message):
    try:
        mnt = int(message.text.split()[1])
        sec = max(60, mnt * 60) # Minimal 60 detik / 1 menit
        conn = sqlite3.connect("bot_panel_full.db")
        conn.cursor().execute("INSERT OR REPLACE INTO settings (user_id, delay_round) VALUES (?, ?)", (message.from_user.id, sec))
        conn.commit(); conn.close()
        await message.reply(f"✅ Jeda antar putaran diatur ke {sec // 60} menit.")
    except:
        await message.reply("Format: `.setdelayround [menit]` (Min: 1 menit)")

# 3. Auto Broadcast Sebar Biasa
@ubot.on_message(filters.command("startbc", prefixes=".") & filters.me)
async def ubot_startbc(client, message):
    global is_bc_running
    user_id = message.from_user.id
    if not get_user_package(user_id):
        return await message.reply("❌ Paket Anda tidak aktif / sudah habis.")
    try: text = message.text.split(" ", 1)[1]
    except: return await message.reply("Format: `.startbc [teks promo]`")
    
    conn = sqlite3.connect("bot_panel_full.db")
    c = conn.cursor()
    c.execute("SELECT group_id FROM lpm_groups WHERE user_id = ?", (user_id,))
    groups = [r[0] for r in c.fetchall()]
    c.execute("SELECT delay_round FROM settings WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    delay = res[0] if res else 60
    conn.close()
    
    if not groups: return await message.reply("❌ Belum ada target grup! Ketik `.addlpm` di grup.")
    
    is_bc_running = True
    await message.reply(f"🚀 AutoBC Sebar Biasa Dimulai ke {len(groups)} grup!")
    
    while is_bc_running:
        for grp in groups:
            if not is_bc_running: break
            try: await client.send_message(int(grp), text)
            except FloodWait as e: await asyncio.sleep(e.value)
            except: pass
            await asyncio.sleep(5)
        if is_bc_running: await asyncio.sleep(delay)

@ubot.on_message(filters.command("stopbc", prefixes=".") & filters.me)
async def ubot_stopbc(client, message):
    global is_bc_running
    is_bc_running = False
    await message.reply("🛑 Auto Broadcast Dihentikan.")

# 4. Auto-Forward Pesan Channel
@ubot.on_message(filters.command("setforward", prefixes=".") & filters.me)
async def ubot_setforward(client, message):
    if not message.reply_to_message: return await message.reply("Balas pesan yang mau di-forward lalu ketik `.setforward`")
    forward_cache[message.from_user.id] = {"chat": message.reply_to_message.chat.id, "id": message.reply_to_message.id}
    await message.reply("✅ Pesan Forward berhasil diset!")

@ubot.on_message(filters.command("startfw", prefixes=".") & filters.me)
async def ubot_startfw(client, message):
    global is_bc_running
    user_id = message.from_user.id
    if user_id not in forward_cache: return await message.reply("❌ Set pesan forward dulu dengan `.setforward`")
    
    conn = sqlite3.connect("bot_panel_full.db")
    c = conn.cursor()
    c.execute("SELECT group_id FROM lpm_groups WHERE user_id = ?", (user_id,))
    groups = [r[0] for r in c.fetchall()]
    c.execute("SELECT delay_round FROM settings WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    delay = res[0] if res else 60
    conn.close()
    
    is_bc_running = True
    msg_data = forward_cache[user_id]
    await message.reply("🚀 Auto-Forward Berjalan!")
    
    while is_bc_running:
        for grp in groups:
            if not is_bc_running: break
            try: await client.forward_messages(int(grp), msg_data["chat"], msg_data["id"])
            except: pass
            await asyncio.sleep(5)
        if is_bc_running: await asyncio.sleep(delay)

# 5. Auto-Reply Komentar Channel (WTB Responder + Banned Words Filter)
@ubot.on_message(filters.group & filters.incoming)
async def ubot_wtb_reply(client, message):
    if not message.reply_to_message or not message.reply_to_message.forward_from_chat: return
    user_id = client.me.id
    text = message.text.lower() if message.text else ""
    
    conn = sqlite3.connect("bot_panel_full.db")
    c = conn.cursor()
    c.execute("SELECT word FROM banned_words WHERE user_id = ?", (user_id,))
    if any(bw[0].lower() in text for bw in c.fetchall()):
        conn.close(); return
        
    c.execute("SELECT keyword, reply_text FROM wtb_rules WHERE user_id = ?", (user_id,))
    rules = c.fetchall()
    conn.close()
    
    for kw, reply in rules:
        if kw.lower() in text:
            try: await message.reply(reply); break
            except: pass

@ubot.on_message(filters.command("addwtb", prefixes=".") & filters.me)
async def ubot_addwtb(client, message):
    try:
        args = message.text.split(" ", 1)[1].split("|")
        conn = sqlite3.connect("bot_panel_full.db")
        conn.cursor().execute("INSERT INTO wtb_rules (user_id, keyword, reply_text) VALUES (?, ?, ?)", (message.from_user.id, args[0].strip().lower(), args[1].strip()))
        conn.commit(); conn.close()
        await message.reply("✅ Aturan WTB berhasil ditambahkan.")
    except: await message.reply("Format: `.addwtb [kata_kunci] | [teks_balasan]`")

@ubot.on_message(filters.command("addbanned", prefixes=".") & filters.me)
async def ubot_addbanned(client, message):
    try:
        word = message.text.split()[1].strip().lower()
        conn = sqlite3.connect("bot_panel_full.db")
        conn.cursor().execute("INSERT INTO banned_words (user_id, word) VALUES (?, ?)", (message.from_user.id, word))
        conn.commit(); conn.close()
        await message.reply(f"✅ Kata terlarang '{word}' berhasil ditambahkan.")
    except: await message.reply("Format: `.addbanned [kata]`")


# --- RUNNER UTAMA (MENJALANKAN BOT TELEGRAM & USERBOT BERSAMAAN) ---
async def main():
    # Menjalankan Bot Telegram Panel & Userbot secara paralel di Termux
    await asyncio.gather(
        dp.start_polling(),
        ubot.start()
    )

if __name__ == "__main__":
    print("=================================================")
    print("🚀 BOT PANEL & USERBOT FULL FITUR SIAP DIJALANKAN!")
    print("=================================================")
    asyncio.run(main())
