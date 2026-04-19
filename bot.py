from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys
import re

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

# Konfigurasi Feed (Boleh tambah banyak lagi kat sini)
FEEDS = [
    {
        "name": "Amanz.my",
        "url": "https://amanz.my/feed/",
        "color": 15158332, # Merah
        "icon": "https://amanz.my/wp-content/uploads/2021/01/amanz-logo.png",
        "file": "last_link_amanz.txt"
    },
    {
        "name": "Phys.org",
        "url": "https://phys.org/rss-feed/",
        "color": 13107, # Biru
        "icon": "https://phys.b-cdn.net/favicon.ico",
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
        if res.status_code != 200:
            print(f"❌ Gagal akses {name}")
            return

        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')
        if not items: return

        new_items = []
        for item in items:
            link = item.link.text.strip()
            if link == last_sent: break
            new_items.append(item)

        if not new_items:
            print(f"😴 {name}: Tiada berita baru.")
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
                "author": {"name": name, "url": rss_url, "icon_url": feed_config["icon"]},
                "title": title,
                "url": link,
                "description": short_desc,
                "color": feed_config["color"],
                "image": {"url": image_url} if image_url else {},
                "footer": {"text": f"Diterbitkan: {pub_date}"}
            }

            requests.post(WEBHOOK_URL, json={"username": name, "avatar_url": feed_config["icon"], "embeds": [embed]}, impersonate="chrome")
            print(f"✅ {name}: {title}")

        with open(db_file, "w") as f:
            f.write(items[0].link.text.strip())

    except Exception as e:
        print(f"🔥 Error {name}: {e}")

def main():
    if not WEBHOOK_URL:
        sys.exit(1)
    for feed in FEEDS:
        process_feed(feed)

if __name__ == "__main__":
    main()
