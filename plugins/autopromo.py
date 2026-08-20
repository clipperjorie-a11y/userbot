import asyncio
from database import is_active

# Daftar ID/Username Group LPM Target
LPM_GROUPS = ["@lpmgrup1", "@lpmgrup2"]

async def run_jaseb_promo(client, user_id, text, delay=60):
    while True:
        if not is_active(user_id):
            print(f"Masa aktif User {user_id} habis. Autopromo dihentikan.")
            break
            
        for group in LPM_GROUPS:
            try:
                await client.send_message(group, text)
                print(f"Berhasil kirim promo ke {group}")
            except Exception as e:
                print(f"Gagal kirim ke {group}: {e}")
            await asyncio.sleep(5) # Delay antar grup
            
        await asyncio.sleep(delay) # Delay antar putaran
