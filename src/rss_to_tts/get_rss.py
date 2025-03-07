# %%
import feedparser

# URL of the RSS feed

# Parse the RSS feed
def get_substack_entries(substack_url, verbose=False):
    from substack_api import Newsletter

    # Initialize a newsletter by its URL
    newsletter = Newsletter(substack_url)

    # Get recent posts (returns Post objects)
    recent_posts = newsletter.get_posts(limit=5)
    print(recent_posts)

    articles = []
    for post in recent_posts:
        metadata = post.get_metadata()
        print(metadata)
        content = post.get_content()
        articles.append({
            "title": metadata["title"],
            "text": content,
            "published": metadata["post_date"],
            "url": metadata["canonical_url"],
            "links": [{"href": metadata["canonical_url"]}],
            "type": metadata["type"],
            "subtitle": metadata["subtitle"],
            "podcast_url": metadata["podcast_url"],
            "podcast_duration": metadata["podcast_duration"],
            "cover_image": metadata["cover_image"],
        })
        # End of Selection
    return articles


# Loop through the entries and print the titles
def get_entries(rss_url, verbose=False):
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
        articles.append({
            "title": title,
            "text": article,
            "published": entry.published,
            "url": entry.links[0].href,
            "links": entry.links,
        })

    return articles

if __name__ == "__main__":
    rss_url = 'https://www.bitsaboutmoney.com/archive/rss/'
    get_entries(rss_url, verbose=True)

    substack_url = 'https://biostasis.substack.com'
    get_substack_entries(substack_url, verbose=True)



# %%
