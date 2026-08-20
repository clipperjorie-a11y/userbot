import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, OWNER_ID
from database import init_db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

init_db()

# Tombol Menu Utama (Persis seperti di video demo kamu)
def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚀 Buat Userbot", callback_data="buat_ubot"),
        InlineKeyboardButton("🛒 Toko", callback_data="toko"),
        InlineKeyboardButton("⭐ Fitur Unggulan", callback_data="fitur"),
        InlineKeyboardButton("📖 Panduan Buat", callback_data="panduan"),
        InlineKeyboardButton("💳 Klaim Token", callback_data="klaim"),
        InlineKeyboardButton("🎁 Coba Gratis", callback_data="coba")
    )
    return keyboard

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    text = (
        "<b>USERBOT JASEB OTOMATIS & AUTOREPLAY JORIE</b>\n\n"
        "🤖 Selamat datang! Silakan gunakan tombol di bawah "
        "untuk mulai membuat bot atau melihat menu utama."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())

# Handler interaksi tombol
@dp.callback_query_handler(lambda c: c.data in ["buat_ubot", "toko", "fitur", "panduan", "klaim", "coba", "back_home"])
async def menu_callbacks(callback_query: types.CallbackQuery):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    
    if code == "buat_ubot":
        await bot.send_message(
            callback_query.from_user.id, 
            "📝 <b>Langkah-langkah Membuat Userbot:</b>\n\n"
            "1. Beli paket langganan di menu Toko.\n"
            "2. Ikuti instruksi verifikasi otomatis.\n"
            "3. Bot siap digunakan!"
        )
    elif code == "toko":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📦 Paket Basic (Rp 4.000)", callback_data="buy_basic"))
        kb.add(InlineKeyboardButton("⬅️ Kembali", callback_data="back_home"))
        await bot.send_message(callback_query.from_user.id, "🛒 <b>Silakan pilih paket bot yang tersedia:</b>", reply_markup=kb)
    elif code == "fitur":
        await bot.send_message(callback_query.from_user.id, "⭐ <b>Fitur Unggulan:</b>\n- Auto Broadcast LPM\n- Auto Forward Channel\n- Auto Reply WTB Komen")
    elif code == "panduan":
        await bot.send_message(callback_query.from_user.id, "📖 Silakan ikuti panduan instalasi di channel resmi.")
    elif code == "coba":
        await bot.send_message(callback_query.from_user.id, "🎁 Fitur uji coba gratis tersedia bagi pengguna baru.")
    elif code == "klaim":
        await bot.send_message(callback_query.from_user.id, "💳 Masukkan token atau serial key Anda.")
    elif code == "back_home":
        await bot.edit_message_text(
            "<b>USERBOT JASEB OTOMATIS & AUTOREPLAY JORIE</b>\n\n"
            "🤖 Selamat datang kembali di Menu Utama:",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=main_menu_keyboard()
        )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
