import requests
from bs4 import BeautifulSoup
import os

# Ambil URL dari GitHub Secret
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_URL = "https://amanz.my/feed/"

def main():
    if not WEBHOOK_URL:
        return print("Webhook tak ada!")

    try:
        # 1. Sedut berita paling baru
        res = requests.get(RSS_URL, timeout=20)
        soup = BeautifulSoup(res.content, 'xml')
        item = soup.find('item')
        
        title = item.title.text
        link = item.link.text
        # Ambil gambar kalau ada (Amanz selalunya letak dlm content:encoded)
        desc = "Berita terkini dari Amanz.my"

        # 2. Hantar ke Discord
        payload = {
            "username": "Amanz News Bot",
            "avatar_url": "https://amanz.my/favicon.ico",
            "embeds": [{
                "title": title,
                "url": link,
                "description": desc,
                "color": 16733952
            }]
        }
        
        requests.post(WEBHOOK_URL, json=payload)
        print(f"Hantar: {title}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
