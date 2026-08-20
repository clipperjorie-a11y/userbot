import os

API_ID = int(os.getenv("API_ID", "1234567"))
API_HASH = os.getenv("API_HASH", "API_HASH_ANDA")
OWNER_ID = 123456789 # Ganti dengan ID Telegram Anda

# API Orderkuota (GANTI NAMA VARIABELNYA)
ORDERKUOTA_MERCHANT_ID = "MERCHANT_ANDA"
ORDERKUOTA_API_KEY = "API_KEY_ANDA"

# Skema Harga Userbot: "paket": {"1d": harga, "1b": harga, "perm": harga}
PRICING = {
    "basic": {"1d": 2000, "1b": 4000, "perm": 15000},
    "autoreply": {"1d": 3000, "1b": 5000, "perm": 20000},
    "full": {"1d": 3000, "1b": 7000, "perm": 35000}
}
