#!/usr/bin/env python3
import os
import sqlite3
import argparse
import sys

DB_NAME = os.environ.get("DB_NAME") or "./data/db.sqlite"

def delete_articles_by_pattern(pattern):
    """Delete all articles with URLs containing the specified pattern."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get all articles and filter in Python for reliable case-insensitive matching
    cursor.execute("""
        SELECT a.id, a.title, a.url, a.article_path, a.audio_path
        FROM articles a
    """)
    
    all_articles = cursor.fetchall()
    pattern = pattern.lower()
    matching_articles = [a for a in all_articles if pattern in a[2].lower()]
    
    if not matching_articles:
        print(f"No articles found with URL containing '{pattern}'")
        conn.close()
        return

    # Display matched articles
    print(f"Found {len(matching_articles)} articles to delete:")
    for i, (_, title, url, _, _) in enumerate(matching_articles, 1):
        print(f"{i}. {title}")
        print(f"   {url}")
    
    # Ask for confirmation
    confirm = input("\nDelete these articles? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled")
        conn.close()
        return
    
    # Delete files and database entries
    print("\nDeleting articles...")
    for article_id, title, _, article_path, audio_path in matching_articles:
        print(f"Deleting: {title}")
        
        # Delete text file
        if article_path and os.path.exists(article_path):
            os.remove(article_path)
        
        # Delete audio file
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Delete database entry
        cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    
    conn.commit()
    conn.close()
    
    print(f"\nDeleted {len(matching_articles)} articles")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete articles with URLs containing a pattern")
    parser.add_argument("pattern", help="The URL pattern to search for (e.g., 'aella')")
    args = parser.parse_args()
    
    delete_articles_by_pattern(args.pattern)
