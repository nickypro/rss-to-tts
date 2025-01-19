import os
import re
import numpy as np
import soundfile as sf
from tqdm import tqdm

import get_rss
import parse_text
import tts

# Ensure the articles directory exists
os.makedirs("./articles", exist_ok=True)
os.makedirs("./audio", exist_ok=True)

# Fetch articles from the RSS feed
rss_url = 'https://www.bitsaboutmoney.com/archive/rss/'
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

    def split_text(some_text):
        # splits by . ! ? : ; \n\n
        regex = r'[^.!?:;\n]+(?:[.!?:;]|\n\n)' 
        return re.findall(regex, some_text)

    def combine_blocks(blocks, max_chars=400):
        result, current = [], ""
        for b in blocks:
            if len(current + b) > max_chars:
                result.append(current)
                current = b
            else:
                current = current + b
        return result + [current]


    for article in articles:
        audio_path = f"./audio/bits-about-money/{article['safe_title']}.mp3"
        if os.path.exists(file_path):
            print("Exists:", audio_path)
            continue
        print("Processing:", audio_path, "...")
        text = article["clean_article"]
        blocks = combine_blocks(split_text(text), max_chars=400)

        combined_audio = np.array([])  # Initialize empty array
        for b in tqdm(blocks):
            audio, out_ps = tts.generate_default(b)
            combined_audio = np.concatenate([combined_audio, audio])  # Add each new audio to combined

        sf.write(audio_path, combined_audio, 24000)    

    # Second loop - update file timestamps
    from email.utils import parsedate_to_datetime

    for article in articles:
        audio_path = f"./audio/bits-about-money/{article['safe_title']}.mp3"
        if os.path.exists(audio_path):
            pub_timestamp = parsedate_to_datetime(article["published"]).timestamp()
            os.utime(audio_path, (pub_timestamp, pub_timestamp))



process_articles(rss_url)

