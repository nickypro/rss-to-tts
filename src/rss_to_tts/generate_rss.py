import sqlite3
from datetime import datetime
from xml.etree import ElementTree as ET
import os

DB_NAME = os.environ.get("DB_NAME") or "./db.sqlite"

def generate_rss_feed(db_name=None, output_file='feed.rss'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Get feed metadata
    c.execute("SELECT name, url FROM feeds LIMIT 1")
    feed_name, feed_url = c.fetchone()

    # Create RSS skeleton
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = feed_name
    ET.SubElement(channel, 'link').text = feed_url

    # Add items from database
    c.execute('''SELECT title, url, first_1k, audio_path, published
                 FROM articles ORDER BY published DESC''')
    for article in c.fetchall():
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = article[0]
        ET.SubElement(item, 'link').text = article[1]
        ET.SubElement(item, 'description').text = article[2]
        ET.SubElement(item, 'pubDate').text = article[4]
        enclosure = ET.SubElement(item, 'enclosure',
            url=article[3],
            length=str(os.path.getsize(article[3])),
            type='audio/mpeg'
        )

    # Write to file
    tree = ET.ElementTree(rss)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)