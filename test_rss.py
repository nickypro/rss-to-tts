import get_rss
import parse_text

rss_url = 'https://www.bitsaboutmoney.com/archive/rss/'
articles = get_rss.get_entries(rss_url)

for article in articles:
    print(article["title"])
    print(article["published"])
    clean_article = parse_text.get_parallel(article["text"])
    print(clean_article)
    break

