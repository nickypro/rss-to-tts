import os
from tqdm import tqdm
import json
import sqlite3
from datetime import datetime

from . import get_rss
from . import parse_text
from . import tts
from . import parallel

LOCAL_TTS = True

# Ensure the articles directory exists
os.makedirs("./data", exist_ok=True)
os.makedirs("./data/articles", exist_ok=True)
os.makedirs("./data/audio", exist_ok=True)

DB_NAME = os.environ.get("DB_NAME") or "./data/db.sqlite"

# Add config loading at the top
def load_config(config_path="config.json"):
    try:
        with open(config_path) as f:
            config = json.load(f)
            if 'feeds' not in config:
                raise ValueError("Config must contain 'feeds' array")
            return config['feeds']
    except FileNotFoundError:
        raise Exception(f"Config file {config_path} not found")

def init_tables(c):
    # Check if the feeds table exists, if not, create it
    c.execute("""CREATE TABLE IF NOT EXISTS feeds (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     slug TEXT UNIQUE,
                     name TEXT,
                     url TEXT
                 )""")
    c.execute("""CREATE TABLE IF NOT EXISTS articles (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     feed_id INTEGER,
                     title TEXT,
                     first_1k TEXT,
                     url TEXT UNIQUE,
                     article_path TEXT,
                     audio_path TEXT,
                     published DATETIME,
                     FOREIGN KEY (feed_id) REFERENCES feeds (id)
                 )""")

def process_feed(feed_config):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    init_tables(c)
    # Insert/update feed
    c.execute("""INSERT OR REPLACE INTO feeds (slug, name, url)
                 VALUES (?, ?, ?)""",
              (feed_config['slug'], feed_config['feed_name'], feed_config['rss_url']))
    c.execute("SELECT id FROM feeds WHERE slug = ?", (feed_config['slug'],))
    feed_id = c.fetchone()[0]

    # Fetch new articles
    articles = get_rss.get_entries(feed_config['rss_url'], feed_config=feed_config)
    print(f"Found {len(articles)} articles")
    save_dir = feed_config['save_dir']
    os.makedirs(save_dir, exist_ok=True)

    for article in articles:
        # Check if article exists
        c.execute("SELECT id FROM articles WHERE url = ?", (article['url'],))
        article_id = c.fetchone()

        # Get paths
        safe_title = "".join(c if c.isalnum() else "_" for c in article['title'].strip())
        article_path = f"./data/articles/{safe_title}.txt"
        audio_path = f"{save_dir}/{safe_title}.mp3"

        # Process content
        if os.path.exists(article_path):
            print(f"Article exists {article_path}")
            with open(article_path, 'r', encoding='utf-8') as f:
                clean_article = f.read()
        else:
            print(f"Parsing article {article_path}...")
            clean_article = parse_text.get_parallel(article["text"], model=feed_config.get("custom_model", None))

        first_1k = clean_article[:1000]

        # Write processed text
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(clean_article)

        # Generate audio
        if not os.path.exists(audio_path):
            print(f"Processing audio {audio_path} ...")
            if LOCAL_TTS:
                from . import tts_local
                import soundfile as sf
                audio, out_ps = tts_local.generate_default(clean_article)
                sf.write(audio_path, audio, 24000)

            else:
                audio = tts.generate_default(clean_article)
                audio.stream_to_file(audio_path)
        else:
            print(f"Audio exists {audio_path}")

        # Insert article
        pub_date = datetime.strptime(article['published'], '%a, %d %b %Y %H:%M:%S %Z')

        # Set the audio file's modification time to match publication date
        if os.path.exists(audio_path):
            try:
                pub_date_timestamp = pub_date.timestamp()
                os.utime(audio_path, (pub_date_timestamp, pub_date_timestamp))
                print(f"Updated file timestamp for {audio_path}")
            except Exception as e:
                print(f"Error setting timestamp: {e}")

        if article_id is None:
            c.execute("""INSERT INTO articles
                         (feed_id, title, first_1k, url, article_path, audio_path, published)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (feed_id, article['title'], first_1k, article['url'],
                       article_path, audio_path, pub_date))
        else:
            print(f"Article already exists {article['url']}")

    conn.commit()
    conn.close()

# Modified main execution
if __name__ == "__main__":
    all_feeds = load_config()
    for feed_config in all_feeds:
        print(f"Processing feed: {feed_config['feed_name']}")
        process_feed(feed_config)
