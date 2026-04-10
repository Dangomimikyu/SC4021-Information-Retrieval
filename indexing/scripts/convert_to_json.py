import pandas as pd
import json
from datetime import datetime
import os

# 1. Load the data.csv file
# Ensure the path correctly points to your reddit-scrape-data directory
try:
    # Path: stepping out of /index and /SC4021 (if needed) to find the data
    input_path = "../../reddit-scrape-data/data.csv"
    df = pd.read_csv(input_path) 
    print(f"✅ Successfully loaded {len(df)} posts from {input_path}")
except FileNotFoundError:
    print(f"❌ Error: Could not find file at {input_path}")
    exit()

docs = []

for _, row in df.iterrows():
    # Handle missing values (NaN) to prevent Solr indexing errors
    content = str(row['content']) if pd.notna(row['content']) else "[No content]"
    author = str(row['author']) if pd.notna(row['author']) else "Anonymous"
    
    # Convert Unix timestamp (float) from 'date' column to ISO 8601 format required by Solr
    try:
        dt_object = datetime.fromtimestamp(row['date'])
        ISO_datetime = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        # Fallback to current time if date conversion fails
        ISO_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Map CSV columns to Solr JSON structure
    doc = {
        "id": str(row['post_id']),           # Use post_id as the Unique Key
        "title": str(row['title']),
        "author": author,
        "content": content,
        "subreddit": str(row['subreddit']),
        "upvotes": int(row['upvotes']),
        "num_comments": int(row['num_comments']),
        "datetime": ISO_datetime,
        "comments_raw": str(row['comments']) # Storing the list of comments as text
    }
    docs.append(doc)

# 2. Save to JSON for the Indexing stage
# The file will be used by index_to_solr.py later
output_file = "../dataset/football_index.json"

# Create dataset directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=2, ensure_ascii=False)

print(f"🚀 Success! '{output_file}' is ready with {len(docs)} documents.")