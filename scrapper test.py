import requests
import json
import time
import random
from datetime import datetime, timezone
import re


target_subs = [
    # main subreddits
    "soccer",
    "premierleague",
    "football",
    "theother14",

    # big clubs
    "reddevils",    # man u
    "LiverpoolFC",
    "gunners",      # arsenal
    "chelseafc",
    "MCFC",         # man city
    "coys",         # spurs
    
    # others
    "FantasyPL",
    "Championship",
    
    # diversity subreddits
    "realmadrid",
    "Barca",
    "fcbayern",
    "psg",
    "ACMilan",
]


limit_posts_per_sub = 20 
goal_records = 20000
output_file = "football_opinions.json"

# strict filter: aug 1 2025 (start of 25/26 season)
season_start = datetime(2025, 8, 1, tzinfo=timezone.utc).timestamp()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_match_threads(subreddit):
    print(f"searching r/{subreddit} for valid match threads...")
    valid_links = []
    
    # only search for Post Match Threads
    queries = ["Post Match Thread"]
    
    for q in queries:
        # keep limit=100 here to find enough VALID dates, we filter to 10 later
        search_url = f"https://www.reddit.com/r/{subreddit}/search.json?q=title:'{q}'&restrict_sr=1&sort=top&t=year&limit=100"
        
        try:
            res = requests.get(search_url, headers=headers)
            if res.status_code != 200:
                print(f"error fetching threads from r/{subreddit}: {res.status_code}")
                continue
                
            raw_posts = res.json()['data']['children']
            
            for post in raw_posts:
                # strict timestamp check (Aug 1, 2025)
                if post['data']['created_utc'] >= season_start:
                    valid_links.append(post['data']['permalink'])
                    
        except Exception as e:
            print(f"failed to search r/{subreddit}: {e}")
            continue

    # remove dupe
    unique_links = list(set(valid_links))
    print(f"found {len(unique_links)} valid threads in r/{subreddit}")
    return unique_links
    
def clean_text(text):
    # remove emojis/special chars
    text = text.encode('ascii', 'ignore').decode('ascii')
    # replace newlines with space and strip extra spaces
    return re.sub(' +', ' ', text.replace('\n', ' ').replace('\r', '')).strip()

def parse_comments(children, sub_name, thread_url):
    found = []
    for c in children:
        if c['kind'] == 't1' and 'body' in c['data']:
            raw_body = c['data']['body']
            # skip bots/removed
            if "I am a bot" in raw_body or raw_body in ["[removed]", "[deleted]"]:
                continue
            
            cleaned = clean_text(raw_body)
            if len(cleaned) < 10: continue # filter noisy comments less than 10 char

            found.append({
                'author': c['data'].get('author'),
                'text': cleaned,
                'score': c['data']['score'],
                'subreddit': sub_name,
                'id': c['data']['id'],
                'thread_url': thread_url # Added for tracking
            })
            if isinstance(c['data'].get('replies'), dict):
                # Pass thread_url recursively
                found.extend(parse_comments(c['data']['replies']['data']['children'], sub_name, thread_url))
    return found

def fetch_comments(permalink, sub_name):
    json_url = f"https://www.reddit.com{permalink}.json?sort=top&limit=500"
    try:
        res = requests.get(json_url, headers=headers)
        if res.status_code != 200:
            return []
        # Pass permalink here
        return parse_comments(res.json()[1]['data']['children'], sub_name, permalink)
    except:
        return []

# --- main execution ---
all_data = []

for sub in target_subs:
    if len(all_data) >= goal_records:
        break
        
    print(f"--- starting scan: r/{sub} ---")
    threads = fetch_match_threads(sub)
    
    for path in threads[:10]: #keep min 10 subreddit
        if len(all_data) >= goal_records:
            break
            
        print(f"processing: https://www.reddit.com{path}")
        batch = fetch_comments(path, sub) # now path is permalink
        all_data.extend(batch)
        print(f"added {len(batch)} comments. total: {len(all_data)}")
        
        # small sleep between threads
        time.sleep(random.uniform(1.5, 3))
    
    # larger sleep between subreddits
    time.sleep(random.uniform(3, 5))

print(f"writing {len(all_data)} records to {output_file}")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=4)
print("process complete")