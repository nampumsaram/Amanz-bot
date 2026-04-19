from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys
import re

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_URL = "https://amanz.my/feed/"
DB_FILE = "last_link.txt"

AMANZ_COLOR = 15158332 
AMANZ_LOGO = "https://amanz.my/wp-content/uploads/2021/01/amanz-logo.png"

def get_image(item):
    media = item.find('media:content') or item.find('media:thumbnail')
    if media and media.get('url'):
        return media.get('url')
    desc = item.description.text if item.description else ""
    img_match = re.search(r'<img[^>]+src="([^">]+)"', desc)
    if img_match:
        return img_match.group(1)
    return None

def main():
    if not WEBHOOK_URL:
        print("❌ Webhook Secret tak dijumpai!")
        sys.exit(1)

    last_sent = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_sent = f.read().strip()

    try:
        print("🚀 Memeriksa berita terkini Amanz...")
        res = requests.get(RSS_URL, impersonate="chrome", timeout=30)
        if res.status_code != 200:
            print(f"❌ Gagal akses. Status: {res.status_code}")
            return

        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')
        if not items:
            print("⚠️ RSS kosong.")
            return

        new_items = []
        for item in items:
            link = item.link.text.strip()
            if link == last_sent:
                break
            new_items.append(item)

        if not new_items:
            print("😴 Tiada berita baru.")
            return

        for item in reversed(new_items):
            title = item.title.text
            link = item.link.text
            pub_date = item.find("pubDate").text if item.find("pubDate") else ""
            raw_desc = item.description.text if item.description else ""
            clean_text = BeautifulSoup(raw_desc, "html.parser").get_text()
            short_desc = (clean_text[:200] + '...') if len(clean_text) > 200 else clean_text
            image_url = get_image(item)

            embed = {
                "author": {"name": "Amanz.my", "url": "https://amanz.my", "icon_url": AMANZ_LOGO},
                "title": title,
                "url": link,
                "description": short_desc,
                "color": AMANZ_COLOR,
                "image": {"url": image_url} if image_url else {},
                "footer": {"text": f"Diterbitkan: {pub_date}"}
            }

            payload = {"username": "Amanz News", "avatar_url": AMANZ_LOGO, "embeds": [embed]}
            requests.post(WEBHOOK_URL, json=payload, impersonate="chrome")
            print(f"✅ Berjaya: {title}")

        with open(DB_FILE, "w") as f:
            f.write(items[0].link.text.strip())

    except Exception as e:
        print(f"🔥 Error: {e}")

if __name__ == "__main__":
    main()
