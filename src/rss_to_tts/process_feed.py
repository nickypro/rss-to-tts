import os
from tqdm import tqdm
import json
import sqlite3
from datetime import datetime

import .get_rss as get_rss
import .parse_text as parse_text
import .tts as tts
import .parallel as parallel

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
    articles = get_rss.get_entries(feed_config['rss_url'])
    save_dir = feed_config['save_dir']
    os.makedirs(save_dir, exist_ok=True)

    for article in articles:
        # Check if article exists
        c.execute("SELECT id FROM articles WHERE url = ?", (article['url'],))
        if c.fetchone() is not None:
            continue

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
            clean_article = parse_text.get_parallel(article["text"])

        first_1k = clean_article[:1000]

        # Write processed text
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(clean_article)

        # Generate audio
        if not os.path.exists(audio_path):
            print(f"Processing audio {audio_path} ...")
            audio = tts.generate_default(clean_article)
            audio.stream_to_file(audio_path)
        else:
            print(f"Audio exists {audio_path}")

        # Insert article
        pub_date = datetime.strptime(article['published'], '%a, %d %b %Y %H:%M:%S %Z')
        c.execute("""INSERT INTO articles
                     (feed_id, title, first_1k, url, article_path, audio_path, published)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (feed_id, article['title'], first_1k, article['url'],
                   article_path, audio_path, pub_date))

    conn.commit()
    conn.close()

# Modified main execution
if __name__ == "__main__":
    all_feeds = load_config()
    for feed_config in all_feeds:
        print(f"Processing feed: {feed_config['feed_name']}")
        process_feed(feed_config)

# # Fetch articles from the RSS feed
# #rss_url  = 'https://www.bitsaboutmoney.com/archive/rss/'
# #save_dir = "./audio/bits-about-money"
# #rss_url = "https://biostasis.substack.com/feed"
# #save_dir = "./audio/biostasis-standard"
# os.makedirs(save_dir, exist_ok=True)
# articles = get_rss.get_entries(rss_url)

# def process_articles(rss_url):
#     for article in articles:
#         # Strip whitespace from the title
#         article["title"] = article["title"].strip()
#         print(f"Processing: {article['title']}")

#         # Create a safe filename from the article title
#         article["safe_title"] = "".join(c if c.isalnum() else "_" for c in article['title'])
#         file_path = f"./articles/{article['safe_title']}.txt"

#         # Check if the file already exists
#         if os.path.exists(file_path):
#             print(f"Loading from file: {file_path}")
#             with open(file_path, "r", encoding="utf-8") as file:
#                 article["clean_article"] = file.read()
#         else:
#             # Process the article if the file doesn't exist
#             print(f"Processing and saving to file: {file_path}")
#             clean_article = parse_text.get_parallel(article["text"])
#             article["clean_article"] = clean_article

#             # Save the processed article to a file
#             with open(file_path, "w", encoding="utf-8") as file:
#                 file.write(clean_article)

#         # Print the clean article (or loaded content)
#         print(article["title"])
#         print("-" * 40)  # Separator for readability

#     def tts_article(article):
#         audio_path = f"{save_dir}/{article['safe_title']}.mp3"
#         if os.path.exists(audio_path):
#             print("Exists:", audio_path)
#             return None

#         with tqdm(total=1, desc=f"Processing {article['safe_title']}", unit="article",
#                  bar_format="{desc}: {elapsed}") as pbar:
#             text = article["clean_article"]
#             audio = tts.generate_default(text)
#             audio.stream_to_file(audio_path)
#             pbar.update(1)
#             pbar.set_description(f"Completed {article['safe_title']}")  # Update description when done
#             return audio

#     audios = parallel.process_in_parallel(articles, tts_article)

#     # Second loop - update file timestamps
#     from email.utils import parsedate_to_datetime

#     for article in articles:
#         audio_path = f"./audio/bits-about-money/{article['safe_title']}.mp3"
#         if os.path.exists(audio_path):
#             pub_timestamp = parsedate_to_datetime(article["published"]).timestamp()
#             os.utime(audio_path, (pub_timestamp, pub_timestamp))



# process_articles(rss_url)

