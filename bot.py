from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import sys
import re

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

FEEDS = [
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
    if media and media.get('url'): return media.get('url')
    desc = item.description.text if item.description else ""
    img_match = re.search(r'<img[^>]+src="([^">]+)"', desc)
    return img_match.group(1) if img_match else None

def process_feed(feed_config):
    name = feed_config["name"]
    db_file = feed_config["file"]
    last_sent = ""
    if os.path.exists(db_file):
        with open(db_file, "r") as f: last_sent = f.read().strip()

    try:
        print(f"🚀 Memeriksa {name}...")
        res = requests.get(feed_config["url"], impersonate="chrome", timeout=30)
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')[:7]
        
        if not items: return

        print(f"DEBUG: Last link tersimpan: {last_sent}")
        new_items = []
        for item in items:
            link = item.link.text.strip()
            if link == last_sent:
                print(f"DEBUG: Jumpa link sama ({link}), berhenti.")
                break
            new_items.append(item)
            print(f"DEBUG: Ada berita baru: {item.title.text}")

        if not new_items: 
            print(f"✅ {name}: Tiada berita baru.")
            return

        for item in reversed(new_items):
            embed = {
                "author": {"name": name, "url": item.link.text, "icon_url": feed_config["icon"]},
                "title": item.title.text,
                "url": item.link.text,
                "description": BeautifulSoup(item.description.text, "html.parser").get_text()[:180] + "..." if item.description else "",
                "color": feed_config["color"],
                "image": {"url": get_image(item)} if get_image(item) else {}
            }
            requests.post(WEBHOOK_URL, json={"embeds": [embed]}, impersonate="chrome")
            print(f"✅ {name}: Berjaya hantar {item.title.text}")

        with open(db_file, "w") as f: f.write(items[0].link.text.strip())
    except Exception as e:
        print(f"🔥 Error {name}: {e}")

def main():
    if not WEBHOOK_URL: sys.exit(1)
    for feed in FEEDS: process_feed(feed)

if __name__ == "__main__":
    main()
