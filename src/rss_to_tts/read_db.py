import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def print_feeds(db_name="./data/db.sqlite"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM feeds")
    feeds = c.fetchall()
    columns = [desc[0] for desc in c.description]
    df_feeds = pd.DataFrame(feeds, columns=columns)
    print("\n=== Feeds Table ===")
    print(df_feeds)
    conn.close()

def print_articles(db_name="./data/db.sqlite"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM articles")
    articles = c.fetchall()
    columns = [desc[0] for desc in c.description]
    df_articles = pd.DataFrame(articles, columns=columns)
    print("\n=== Articles Table ===")
    print(df_articles)
    conn.close()

def read_db(db_name="./data/db.sqlite"):
    print_feeds(db_name)
    print_articles(db_name)

if __name__ == "__main__":
    read_db()
