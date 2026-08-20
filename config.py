import os

# Ambil credential Telegram dari https://my.telegram.org
API_ID = int(os.getenv("API_ID", "1234567")) 
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH_HERE")

# API Orderkuita
ORDERKUITA_MERCHANT_ID = os.getenv("ORDERKUITA_MERCHANT_ID", "YOUR_MERCHANT_ID")
ORDERKUITA_API_KEY = os.getenv("ORDERKUITA_API_KEY", "YOUR_API_KEY")
