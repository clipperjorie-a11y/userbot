from pyrogram import Client
from config import API_ID, API_HASH
from database import init_db

# Memuat semua perintah dari dalam folder "plugins"
plugins = dict(root="plugins")

# Membuat sesi Userbot
app = Client("my_ubot_jaseb", api_id=API_ID, api_hash=API_HASH, plugins=plugins)

if __name__ == "__main__":
    # Inisialisasi Database saat pertama kali jalan
    init_db()
    print("=======================================")
    print("🚀 UBOT JASEB PREMIUM BERHASIL NYALA!")
    print("=======================================")
    app.run()
