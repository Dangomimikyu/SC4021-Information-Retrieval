import pysolr
import time

# 1. Connection to Solr
base_url = "http://localhost:8983/solr/football_core"
solr = pysolr.Solr(base_url, always_commit=True, timeout=10)

print("--- FOOTBALL SEARCH SYSTEM - FIXED & FULL CONTENT ---")

# ------------------------- 1. Detailed Single Query Test -------------------------
params = {
    "rows": 5,
    "sort": "upvotes desc",
    "fl": "title,author,upvotes,content,comments_raw" # Added comments_raw to see why it matched
}

query = 'text:Ronaldo AND upvotes:[10 TO *]'

print(f"\n[Test 1] Searching for: {query}")
start = time.time()
try:
    results = solr.search(query, **params)
    end = time.time()
    
    print(f"-> Documents found: {results.hits}") # Use .hits for total count
    print(f"-> Response time: {end-start:.3f} seconds")
    
    for doc in results:
        author = doc.get('author', 'N/A')
        title = doc.get('title', 'N/A') 
        upvotes = doc.get('upvotes', 0)
        content = doc.get('content', '[No content]')
        
        print("-" * 50)
        print(f"AUTHOR : {author}")
        print(f"TITLE  : {title}")
        print(f"VOTES  : {upvotes}")
        print(f"COMMENTS_RAW: {doc.get('comments_raw', 'N/A')[:1000]}...") # Show first 100 chars of comments_raw
        # If title doesn't have 'Ronaldo', it must be in comments
        if "Ronaldo" not in title and content == "[No content]":
             print("INFO   : Matched keyword in Comments (comments_raw)")
        print("-" * 50)
        
except Exception as e:
    print(f"Error occurred: {e}")

# ------------------------- 2. Multiple Queries Performance Test -------------------------
query_list = [
    'text:"Premier League"',
    'subreddit:soccer AND upvotes:[100 TO *]',
    'author:AutoModerator',
    'title:Goal OR title:Score',
    'datetime:[2025-01-01T00:00:00Z TO *]'
]

print("\n" + "="*50)
print("PERFORMANCE BENCHMARK FOR MULTIPLE QUERIES")
print("="*50)

for q in query_list:
    start = time.time()
    res = solr.search(q, rows=5)
    end = time.time()

    print(f"Query: {q}")
    print(f" - Results found: {res.hits}")
    print(f" - Execution Time: {end - start:.4f}s")
    
    # FIX: Correct way to get the first result from pysolr.Results
    first_result = next(iter(res), None)
    if first_result:
        print(f" - Top Result Title: {first_result.get('title')}\n")