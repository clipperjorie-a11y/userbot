import aiohttp
import asyncio
import time
from config import ORDERKUITA_MERCHANT_ID, ORDERKUITA_API_KEY
from database import add_subscription

async def create_qris(amount, ref_id):
    url = "https://orderkuita.com/api/v2/qris" # Sesuaikan Endpoint API Orderkuita
    payload = {
        "merchant_id": ORDERKUITA_MERCHANT_ID,
        "api_key": ORDERKUITA_API_KEY,
        "amount": amount,
        "merchant_ref": ref_id
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                res = await resp.json()
                return res.get("qris_data"), res.get("trx_id")
        except Exception:
            return None, None

async def check_payment(trx_id):
    url = f"https://orderkuita.com/api/v2/check-status?trx_id={trx_id}"
    headers = {"Authorization": f"Bearer {ORDERKUITA_API_KEY}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                res = await resp.json()
                return res.get("status") == "PAID"
        except Exception:
            return False

async def process_auto_pay(client, message, amount=15000):
    user_id = message.from_user.id
    ref_id = f"PAY-{user_id}-{int(time.time())}"
    
    qris_data, trx_id = await create_qris(amount, ref_id)
    if not qris_data:
        return await message.reply("Gagal membuat QRIS Orderkuita.")
        
    await message.reply(f"Silakan bayar menggunakan QRIS berikut:\n`{qris_data}`\n\nID Trx: `{trx_id}`\nMenunggu pembayaran...")
    
    # Polling status pembayaran (Max 10 menit)
    for _ in range(120):
        await asyncio.sleep(5)
        if await check_payment(trx_id):
            new_exp = add_subscription(user_id, days=30)
            return await message.reply(f"✅ Pembayaran Berhasil! Masa aktif bertambah hingga timestamp: {new_exp}")
