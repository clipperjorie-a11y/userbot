import aiohttp, asyncio, time, sqlite3
from pyrogram import Client, filters
from config import ORDERKUOTA_MERCHANT_ID, ORDERKUOTA_API_KEY, PRICING
from database import DB_NAME

async def create_qris(amount, ref_id):
    # UBAH URL KE ORDERKUOTA
    url = "https://api.orderkuota.com/api/v2/qris" # Pastikan endpoint ini sesuai dengan dokumentasi resmi Orderkuota
    payload = {"merchant_id": ORDERKUOTA_MERCHANT_ID, "api_key": ORDERKUOTA_API_KEY, "amount": amount, "merchant_ref": ref_id}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                res = await resp.json()
                return res.get("qris_data"), res.get("trx_id")
        except: return None, None

async def check_payment(trx_id):
    # UBAH URL KE ORDERKUOTA
    url = f"https://api.orderkuota.com/api/v2/check-status?trx_id={trx_id}"
    headers = {"Authorization": f"Bearer {ORDERKUOTA_API_KEY}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                return (await resp.json()).get("status") == "PAID"
        except: return False

@Client.on_message(filters.command("buy", prefixes="."))
async def buy_package(client, message):
    try:
        args = message.text.split()
        paket = args[1].lower()
        durasi = args[2].lower()
        
        if paket not in PRICING or durasi not in PRICING[paket]:
            return await message.reply("❌ Paket atau durasi tidak valid. Cek daftar harga!")
            
        harga = PRICING[paket][durasi]
        user_id = message.from_user.id
        ref_id = f"BUY-{user_id}-{int(time.time())}"
        
        msg = await message.reply("🔄 Sedang membuat invoice QRIS Orderkuota...")
        qris, trx_id = await create_qris(harga, ref_id)
        
        if not qris: return await msg.edit("❌ Gagal membuat QRIS Orderkuota. Sistem sedang sibuk atau API Key salah.")
        
        await msg.edit(f"**INVOICE PEMBELIAN USERBOT**\n\n📦 Paket: {paket.upper()}\n⏳ Durasi: {durasi.upper()}\n💰 Harga: Rp {harga:,}\n🧾 ID Trx: `{trx_id}`\n\nSilakan scan kode QRIS di bawah ke aplikasi pembayaran Anda:\n\n`{qris}`\n\n*(Sistem mengecek pembayaran otomatis selama 10 menit...)*")
        
        # Polling pembayaran
        for _ in range(120): # 120 x 5 detik = 10 menit
            await asyncio.sleep(5)
            if await check_payment(trx_id):
                days_add = 1 if durasi == "1d" else 30 if durasi == "1b" else 180
                exp = int(time.time()) + (days_add * 86400)
                
                conn = sqlite3.connect(DB_NAME)
                conn.cursor().execute("INSERT OR REPLACE INTO users (user_id, package, expired_at) VALUES (?, ?, ?)", (user_id, paket, exp))
                conn.commit(); conn.close()
                
                return await message.reply(f"✅ **PEMBAYARAN BERHASIL!**\nPaket {paket.upper()} ({durasi}) aktif. Selamat menggunakan bot!")
                
    except IndexError:
        await message.reply("❌ Format pembelian salah!\nContoh: `.buy full 1b` atau `.buy basic perm`")
