# %%
import feedparser

# Loop through the entries and print the titles
def get_entries(rss_url, feed_type="rss", verbose=False, feed_config=None):
    if "feed_type" in feed_config:
        feed_type = feed_config["feed_type"]

    if feed_type == "rss":
        return get_rss_entries(rss_url, verbose)
    elif feed_type == "substack":
        return get_substack_entries(rss_url, verbose)
    elif feed_type == "lesswrong":
        return get_lesswrong_feed(rss_url, verbose)
    else:
        raise ValueError(f"Invalid type: {feed_type}")

# URL of the R    feed = feedparser.parse(rss_url)
def get_rss_entries(rss_url, verbose=False):
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




def get_lesswrong_feed(profile_url, limit=20, verbose=False):
    """
    Get recent posts from a LessWrong user via GraphQL API

    Args:
        profile_url: LessWrong profile URL
        limit: Maximum number of posts to retrieve
        verbose: Whether to print post titles

    Returns:
        List of article dictionaries with standardized fields
    """
    import requests
    import json
    verbose = True

    # Function to query the GraphQL API
    url = 'https://www.lesswrong.com/graphql?'
    headers = {"content-type": "application/json", "user-agent": "Mozilla/5.0"}
    def query_graphql(query):
        r = requests.post(url, json={'query': query}, headers=headers)
        return json.loads(r.text)

    # Get the slug from the profile URL
    slug = profile_url.split("/")[-1]

    # Query to get user ID from username
    query_user = """{
        me: user(input: {selector: {slug:"%s"}}){
        result {
        displayName
        username
        slug
        _id
      }}
    }""" % slug


    # Get user data
    user_data = query_graphql(query_user)

    if not user_data.get('data') \
            or not user_data['data'].get('me') \
            or not user_data['data']['me'].get('result'):
        if verbose:
            print(f"User '{username}' not found")
        return []
    if verbose:
        print(user_data)

    user_id = user_data['data']['me']['result']['_id']
    display_name = user_data['data']['me']['result']['displayName']

    # Query to get posts by user ID
    query_posts = """{
      posts: posts(input: {terms: {userId: "%s", limit: %d}}){results {
        title
        postedAt
        url
        slug
        htmlBody
        contents {
          markdown
        }
      }}
    }""" % (user_id, limit)

    # Get posts data
    posts_data = query_graphql(query_posts)

    if not posts_data.get('data') or not posts_data['data'].get('posts'):
        if verbose:
            print(f"No posts found for user '{username}'")
        return []

    posts = posts_data['data']['posts']['results']

    if verbose:
        print(f"Found {len(posts)} posts for {display_name}")

    # Format posts similar to other feed functions
    articles = []
    for post in posts:
        # Use contents.markdown if available, otherwise use htmlBody
        content = post.get('contents', {}).get('markdown')

        # Create post URL
        post_url = f"https://www.lesswrong.com/posts/{post['slug']}"

        article = {
            "title": post['title'],
            "text": content,
            "published": post['postedAt'],
            "url": post_url,
            "links": [{"href": post_url}],
            "author": display_name
        }

        if verbose:
            print(f"- {post['title']}")

        articles.append(article)

    return articles


if __name__ == "__main__":
    rss_url = 'https://www.bitsaboutmoney.com/archive/rss/'
    get_entries(rss_url, verbose=True)

    substack_url = 'https://biostasis.substack.com'
    get_substack_entries(substack_url, verbose=True)



# %%
