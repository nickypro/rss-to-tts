import feedparser

# URL of the RSS feed
rss_url = 'https://www.bitsaboutmoney.com/archive/rss/'

# Parse the RSS feed

# Loop through the entries and print the titles
def get_entries(feed_url, verbose=False):
    feed = feedparser.parse(rss_url)

    articles = []
    for entry in feed.entries:
        title = f"{entry.title}"
        date =  f"Published: {entry.published}"
        text = "\n\n".join([c.value for c in entry.content])
        text = "\n\n".join(text.split("</p>"))
        article = f"{title}\n{date}\n\n{text}"

        if verbose:
            print(title)
        articles.append({"title": title, "text": article, "published": entry.published})

    return articles

if __name__ == "__main__":
    get_entries(rss_url, verbose=True)


