from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_URL = "https://amanz.my/feed/"
DB_FILE = "last_link.txt"

def main():
    if not WEBHOOK_URL:
        print("❌ Webhook tak jumpa!")
        sys.exit(1)

    # 1. Baca 'ingatan' bot (link terakhir yang dihantar)
    last_sent_link = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_sent_link = f.read().strip()

    try:
        print("🚀 Memeriksa berita baru...")
        res = requests.get(RSS_URL, impersonate="chrome", timeout=30)
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')

        if not items:
            print("⚠️ RSS Kosong.")
            return

        # 2. Cari berita yang belum pernah dihantar
        new_items = []
        for item in items:
            link = item.link.text.strip()
            if link == last_sent_link:
                break # Berhenti bila jumpa berita lama
            new_items.append(item)

        if not new_items:
            print("😴 Tiada berita baru. Bot akan tidur.")
            return

        # 3. Kalau 'ingatan' kosong (First time run), jangan spam.
        # Simpan je link terbaru dan keluar.
        if last_sent_link == "":
            with open(DB_FILE, "w") as f:
                f.write(items[0].link.text.strip())
            print("✅ Setup pertama kali selesai. 'Ingatan' sudah disimpan.")
            return

        print(f"🔥 Ada {len(new_items)} berita fresh!")

        # 4. Hantar berita fresh ke Discord (Paling lama ke paling baru)
        for item in reversed(new_items):
            title = item.title.text
            link = item.link.text
            
            payload = {
                "content": f"🚀 **{title}**\n{link}"
            }
            requests.post(WEBHOOK_URL, json=payload, impersonate="chrome")
            print(f"✅ Dihantar: {title}")

        # 5. Kemaskini 'ingatan' dengan link paling baru
        with open(DB_FILE, "w") as f:
            f.write(items[0].link.text.strip())

    except Exception as e:
        print(f"🔥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
