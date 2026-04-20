from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys
import re

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

# Konfigurasi Feed (Warna & Link sahaja)
FEEDS =[
    {
        "name": "Amanz News",
        "url": "https://amanz.my/feed/",
        "color": 15158332, 
        "icon": "https://amanz.my/wp-content/uploads/2021/01/amanz-logo.png",
        "file": "last_link_amanz.txt"
    },
    {
        "name": "Phys.org Science",
        "url": "https://phys.org/rss-feed/",
        "color": 27558,
        "icon": "https://i.imgur.com/8YvA5fG.png", 
        "file": "last_link_phys.txt"
    }
]

def get_image(item):
    media = item.find('media:content') or item.find('media:thumbnail') or item.find('enclosure')
    if media and media.get('url'):
        return media.get('url')
    desc = item.description.text if item.description else ""
    img_match = re.search(r'<img[^>]+src="([^">]+)"', desc)
    if img_match:
        return img_match.group(1)
    return None

def process_feed(feed_config):
    name = feed_config["name"]
    rss_url = feed_config["url"]
    db_file = feed_config["file"]
    
    last_sent = ""
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            last_sent = f.read().strip()

    try:
        print(f"🚀 Memeriksa {name}...")
        res = requests.get(rss_url, impersonate="chrome", timeout=30)
        if res.status_code != 200: return

        soup = BeautifulSoup(res.content, 'xml')
        
        # 👇 PERUBAHAN DI SINI: Limitkan kepada 7 item sahaja ([0 hingga 6])
        items = soup.find_all('item')[:7]
        
        if not items: return

        new_items =[]
        for item in items:
            link = item.link.text.strip()
            # Kalau jumpa link yang sama dalam senarai 7 berita ni, dia berhenti
            if link == last_sent: break
            new_items.append(item)

        if not new_items: return

        for item in reversed(new_items):
            title = item.title.text
            link = item.link.text
            pub_date = item.find("pubDate").text if item.find("pubDate") else ""
            raw_desc = item.description.text if item.description else ""
            clean_text = BeautifulSoup(raw_desc, "html.parser").get_text()
            short_desc = (clean_text[:180] + '...') if len(clean_text) > 180 else clean_text
            image_url = get_image(item)

            embed = {
                "author": {
                    "name": name, 
                    "url": link, 
                    "icon_url": feed_config["icon"]
                },
                "title": title,
                "url": link,
                "description": short_desc,
                "color": feed_config["color"],
                "image": {"url": image_url} if image_url else {},
                "footer": {"text": f"Diterbitkan: {pub_date}"}
            }

            requests.post(WEBHOOK_URL, json={"embeds": [embed]}, impersonate="chrome")
            print(f"✅ {name}: {title}")

        with open(db_file, "w") as f:
            f.write(items[0].link.text.strip())

    except Exception as e:
        print(f"🔥 Error {name}: {e}")

def main():
    if not WEBHOOK_URL:
        print("⚠️ DISCORD_WEBHOOK tidak dijumpai! Sila set environment variable.")
        sys.exit(1)
    for feed in FEEDS:
        process_feed(feed)

if __name__ == "__main__":
    main()
