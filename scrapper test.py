import requests
import json
import time
import random
from datetime import datetime, timezone


# here are some subreddits lmao but ill just try prem first
target_subs = [
    "PremierLeague",
    # "soccer",
    # "reddevils", 
    # "LiverpoolFC",
    # "Gunners",
    # "ChelseaFC",
    # "MCFC",
    # "coys" 
]

limit_posts_per_sub = 20 
goal_records = 10000
output_file = "football_opinions.json"

# strict filter: aug 1 2025 (start of 25/26 season)
season_start = datetime(2025, 8, 1, tzinfo=timezone.utc).timestamp()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_match_threads(subreddit):
    print(f"searching r/{subreddit} for valid match threads...")
    # fetch 'year' to get candidate pool, strict filter applied below
    search_url = f"https://www.reddit.com/r/{subreddit}/search.json?q=title:'Match Thread'&restrict_sr=1&sort=top&t=year&limit={limit_posts_per_sub}"
    
    try:
        res = requests.get(search_url, headers=headers)
        if res.status_code != 200:
            print(f"error fetching threads from r/{subreddit}: {res.status_code}")
            return []
            
        raw_posts = res.json()['data']['children']
        valid_links = []
        
        for post in raw_posts:
            # strict timestamp check
            if post['data']['created_utc'] >= season_start:
                valid_links.append(post['data']['permalink'])
        
        print(f"found {len(valid_links)} valid threads in r/{subreddit}")
        return valid_links
    except Exception as e:
        print(f"failed to search r/{subreddit}: {e}")
        return []

def parse_comments(children, sub_name):
    found = []
    for c in children:
        if c['kind'] == 't1' and 'body' in c['data']:
            found.append({
                'author': c['data'].get('author'),
                'text': c['data']['body'],
                'score': c['data']['score'],
                'subreddit': sub_name,
                'id': c['data']['id']
            })
            if isinstance(c['data'].get('replies'), dict):
                found.extend(parse_comments(c['data']['replies']['data']['children'], sub_name))
    return found

def fetch_comments(permalink, sub_name):
    json_url = f"https://www.reddit.com{permalink}.json?sort=top&limit=500"
    try:
        res = requests.get(json_url, headers=headers)
        if res.status_code != 200:
            return []
        return parse_comments(res.json()[1]['data']['children'], sub_name)
    except:
        return []

# --- main execution ---
all_data = []

for sub in target_subs:
    if len(all_data) >= goal_records:
        break
        
    print(f"--- starting scan: r/{sub} ---")
    threads = fetch_match_threads(sub)
    
    for path in threads:
        if len(all_data) >= goal_records:
            break
            
        print(f"processing: https://www.reddit.com{path}")
        batch = fetch_comments(path, sub)
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