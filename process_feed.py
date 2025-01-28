import os
import re
import numpy as np
import soundfile as sf
from tqdm import tqdm

import get_rss
import parse_text
import tts
import parallel

# Ensure the articles directory exists
os.makedirs("./articles", exist_ok=True)
os.makedirs("./audio", exist_ok=True)

# Fetch articles from the RSS feed
#rss_url  = 'https://www.bitsaboutmoney.com/archive/rss/'
#save_dir = "./audio/bits-about-money"
rss_url = "https://biostasis.substack.com/feed"
save_dir = "./audio/biostasis-standard"
os.makedirs(save_dir, exist_ok=True)
articles = get_rss.get_entries(rss_url)

def process_articles(rss_url):
    for article in articles:
        # Strip whitespace from the title
        article["title"] = article["title"].strip()
        print(f"Processing: {article['title']}")

        # Create a safe filename from the article title
        article["safe_title"] = "".join(c if c.isalnum() else "_" for c in article['title'])
        file_path = f"./articles/{article['safe_title']}.txt"

        # Check if the file already exists
        if os.path.exists(file_path):
            print(f"Loading from file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file:
                article["clean_article"] = file.read()
        else:
            # Process the article if the file doesn't exist
            print(f"Processing and saving to file: {file_path}")
            clean_article = parse_text.get_parallel(article["text"])
            article["clean_article"] = clean_article

            # Save the processed article to a file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(clean_article)

        # Print the clean article (or loaded content)
        print(article["title"])
        print("-" * 40)  # Separator for readability

    def tts_article(article):
        audio_path = f"{save_dir}/{article['safe_title']}.mp3"
        if os.path.exists(audio_path):
            print("Exists:", audio_path)
            return None

        with tqdm(total=1, desc=f"Processing {article['safe_title']}", unit="article",
                 bar_format="{desc}: {elapsed}") as pbar:
            text = article["clean_article"]
            audio = tts.generate_default(text)
            audio.stream_to_file(audio_path)
            pbar.update(1)
            pbar.set_description(f"Completed {article['safe_title']}")  # Update description when done
            return audio

    audios = parallel.process_in_parallel(articles, tts_article)

    # Second loop - update file timestamps
    from email.utils import parsedate_to_datetime

    for article in articles:
        audio_path = f"./audio/bits-about-money/{article['safe_title']}.mp3"
        if os.path.exists(audio_path):
            pub_timestamp = parsedate_to_datetime(article["published"]).timestamp()
            os.utime(audio_path, (pub_timestamp, pub_timestamp))



process_articles(rss_url)

