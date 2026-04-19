from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys

# 1. Ambil Webhook dari GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_URL = "https://amanz.my/feed/"

def main():
    # Cek Webhook macam Grok cakap
    if not WEBHOOK_URL:
        print("❌ ERROR: Webhook tak dijumpai dlm GitHub Secrets!")
        sys.exit(1)

    try:
        print("🚀 Memulakan misi sedut berita Amanz...")
        
        # Guna curl_cffi untuk menyamar jadi Chrome (Tembus Cloudflare)
        res = requests.get(RSS_URL, impersonate="chrome", timeout=30)
        
        if res.status_code != 200:
            print(f"❌ Kena Block! Status: {res.status_code}")
            return

        # Parsing XML
        soup = BeautifulSoup(res.content, 'xml')
        item = soup.find('item')
        
        # Elakkan error 'NoneType' yang kau kena tadi
        if not item:
            print("⚠️ Amanz hantar page kosong/challenge. Tak jumpa tag <item>.")
            return

        title = item.title.text
        link = item.link.text
        
        print(f"✅ Berita dijumpai: {title}")

        # 2. Hantar ke Discord dengan gaya hensem (Embed)
        payload = {
            "embeds": [{
                "title": f"🔥 {title}",
                "url": link,
                "description": "Klik link di atas untuk baca berita penuh di Amanz.my",
                "color": 16733952, # Warna oren Amanz
                "footer": {"text": "Amanz News Bot • April 2026"}
            }]
        }
        
        print("📤 Menghantar ke Discord...")
        r = requests.post(WEBHOOK_URL, json=payload, impersonate="chrome")
        
        if r.status_code in [200, 204]:
            print("✅ BERJAYA! Check Discord kau sekarang.")
        else:
            print(f"❌ Gagal hantar ke Discord. Status: {r.status_code}")

    except Exception as e:
        print(f"🔥 Error Besar: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
