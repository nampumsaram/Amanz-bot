from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_URL = "https://amanz.my/feed/"
DB_FILE = "last_link.txt"

def main():
    if not WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK tak dijumpai di GitHub Secret!")
        sys.exit(1)

    # Baca last sent link
    last_sent = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_sent = f.read().strip()

    try:
        print("🚀 Memeriksa berita baru dari Amanz...")
        res = requests.get(RSS_URL, impersonate="chrome", timeout=30)

        if res.status_code != 200:
            print(f"❌ Gagal fetch RSS: {res.status_code}")
            return

        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')

        if not items:
            print("⚠️ Tiada artikel dalam RSS.")
            return

        # Cari artikel baru (yang belum dihantar)
        new_items = []
        for item in items:
            link = item.link.text.strip()
            if link == last_sent:
                break
            new_items.append(item)

        if not new_items:
            print("😴 Tiada berita baru.")
            return

        print(f"🔥 Jumpa {len(new_items)} berita baru!")

        # Hantar dari yang paling lama ke paling baru
        for item in reversed(new_items):
            title = item.title.text
            link = item.link.text
            pub_date = item.find("pubDate").text if item.find("pubDate") else ""

            # Embed Cantik
            embed = {
                "title": title,
                "url": link,
                "description": "Berita terkini dari Amanz.my",
                "color": 0xE74C3C,   # Warna merah Amanz
                "footer": {
                    "text": pub_date
                }
            }

            payload = {
                "username": "Amanz Bot",
                "avatar_url": "https://amanz.my/wp-content/uploads/2021/01/amanz-logo.png",
                "embeds": [embed]
            }

            requests.post(WEBHOOK_URL, json=payload, impersonate="chrome")
            print(f"✅ Dihantar: {title}")

        # Update last_link.txt dengan artikel paling baru
        with open(DB_FILE, "w") as f:
            f.write(items[0].link.text.strip())

        print("✅ Semua berita baru telah dihantar ke Discord.")

    except Exception as e:
        print(f"🔥 Error: {e}")

if __name__ == "__main__":
    main()
