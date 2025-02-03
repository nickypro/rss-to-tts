import sqlite3
import pandas as pd

def print_articles(db_name="./data/db.sqlite"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

        # c.execute("""CREATE TABLE IF NOT EXISTS articles (
        #              id INTEGER PRIMARY KEY AUTOINCREMENT,
        #              feed_id INTEGER,
        #              title TEXT,
        #              first_1k TEXT,
        #              url TEXT UNIQUE,
        #              article_path TEXT,
        #              audio_path TEXT,
        #              published DATETIME,
        #              FOREIGN KEY (feed_id) REFERENCES feeds (id)

    c.execute("SELECT * FROM articles LIMIT 5")
    articles = c.fetchall()

    # Create a DataFrame from the fetched articles
    df = pd.DataFrame(articles, columns=[desc[0] for desc in c.description])
    print(df)

    conn.close()

# Call the function to print articles
print_articles()
