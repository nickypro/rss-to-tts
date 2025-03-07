# %%
import sqlite3
import os
from xml.etree import ElementTree as ET
from datetime import datetime

DB_PATH = os.environ.get("DB_NAME") or "./data/db.sqlite"
BASE_URL = os.environ.get("BASE_URL") or "https://rss.nicky.pro/"

def generate_rss_feed(slug, db_path=None, base_dir="./data"):
    if db_path is None:
        db_path = DB_PATH
    if not os.path.exists(db_path):
        raise Exception(f"Database file {db_path} does not exist")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get feed metadata for the given slug
    c.execute("SELECT id, name, url FROM feeds WHERE slug = ?", (slug,))
    result = c.fetchone()
    if result is None:
        raise Exception(f"No feed found for slug: {slug}")
    feed_id, feed_name, feed_url = result

    # Create the RSS skeleton
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = feed_name
    ET.SubElement(channel, 'link').text = feed_url

    # Use a LIKE query on the audio_path to find articles for this feed.
    # Assuming the audio_path for a feed is stored like "./data/audio/{slug}/..."
    query = '''
        SELECT title, url, first_1k, audio_path, published
        FROM articles
        WHERE audio_path LIKE ?
        ORDER BY published DESC
    '''
    like_pattern = f"./data/audio/{slug}/%"
    c.execute(query, (like_pattern,))
    articles = c.fetchall()
    print(f"[DEBUG] Found {len(articles)} articles for feed '{slug}' using LIKE filter '{like_pattern}'.")

    for article in articles:
        title, link, description, audio_path, published = article

        # Strip the "./data/" prefix so that the URL becomes relative.
        if audio_path.startswith("./data/"):
            relative_audio_path = audio_path[len("./data/"):]
        else:
            relative_audio_path = audio_path

        online_audio_path = BASE_URL + relative_audio_path

        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = title
        ET.SubElement(item, 'link').text = link
        # Create a description with a "Read more" link in HTML format
        description_with_link = f"{description}<br/><br/><a href='{link}'>Read more...</a>"
        ET.SubElement(item, 'description').text = description_with_link

        # Format the published date in RFC 822 format for podcast compatibility
        if isinstance(published, str):
            try:
                # Try to parse the string into a datetime object
                pub_date = datetime.strptime(published, '%Y-%m-%d %H:%M:%S')
                pub_date_str = pub_date.strftime('%a, %d %b %Y %H:%M:%S %z')
            except ValueError:
                # If parsing fails, use the string as is
                pub_date_str = published
        else:
            # If it's already a datetime object
            try:
                pub_date_str = published.strftime('%a, %d %b %Y %H:%M:%S %z')
            except AttributeError:
                # Fallback if it's neither a string nor a datetime
                pub_date_str = str(published)

        ET.SubElement(item, 'pubDate').text = pub_date_str

        # Calculate file size (assumes the file exists)
        audio_full_path = os.path.join(base_dir, relative_audio_path)
        try:
            file_length = os.path.getsize(audio_full_path)
        except OSError:
            file_length = 0
        ET.SubElement(item, 'enclosure',
                      url=online_audio_path,
                      length=str(file_length),
                      type='audio/mpeg')

    # Write the feed to a file inside ./data/{slug}/feed.rss
    feed_output_dir = os.path.join(base_dir, slug)
    os.makedirs(feed_output_dir, exist_ok=True)
    output_file = os.path.join(feed_output_dir, "feed.rss")
    tree = ET.ElementTree(rss)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"[DEBUG] RSS feed generated at {output_file}")

    conn.close()


if __name__ == "__main__":
    import sys
    # Generate feeds for provided slugs, or for all feeds in the database.
    if len(sys.argv) > 1:
        feed_slugs = sys.argv[1:]
    else:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT slug FROM feeds")
        feed_slugs = [row[0] for row in c.fetchall()]
        conn.close()

    for slug in feed_slugs:
        print(f"Generating RSS for feed: {slug}")
        generate_rss_feed(slug)
# %%
