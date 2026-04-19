from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_URL = "https://amanz.my/feed/"

def main():
    if not WEBHOOK_URL:
        print("❌ Webhook tak jumpa!")
        sys.exit(1)

    try:
        print("🚀 Melancarkan 'Impersonate Chrome'...")
        # Teknik impersonate="chrome" ni la yang akan buat Cloudflare keliru
        res = requests.get(RSS_URL, impersonate="chrome", timeout=30)
        
        if res.status_code != 200:
            print(f"❌ Masih kena block. Status: {res.status_code}")
            return

        soup = BeautifulSoup(res.content, 'xml')
        item = soup.find('item')
        
        if item is None:
            print("⚠️ Data kosong. Amanz mungkin hantar page challenge.")
            return

        title = item.title.text
        link = item.link.text
        
        print(f"✅ Berjaya sedut: {title}")

        # Hantar ke Discord
        payload = {
            "content": f"🔥 **Berita Terkini Amanz!**\n\n**{title}**\n{link}"
        }
        
        # Untuk hantar ke Discord, requests biasa pun ok
        requests.post(WEBHOOK_URL, json=payload, impersonate="chrome")
        print("✅ Berjaya hantar ke Discord!")

    except Exception as e:
        print(f"🔥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
