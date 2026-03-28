import pandas as pd
import json
import os

def process_football_data():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_file = os.path.abspath(os.path.join(current_dir, '..', '..', 'reddit-scrape-data', 'data.csv'))
    

    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy file tại {input_file}")
        return

    df = pd.read_csv(input_file)
    
    subreddits = sorted(df['subreddit'].dropna().unique().tolist())
    
    teams_raw = df['author_flair'].dropna().unique().tolist()
    teams = set()
    for t in teams_raw:
        clean_name = t.replace(':', '').replace('_', ' ')
        if clean_name and len(clean_name) > 2:
            teams.add(clean_name)
    
    filter_data = {
        "subreddits": subreddits,
        "teams": sorted(list(teams))
    }

    output_dir = os.path.join(current_dir, 'dataset')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'filter_options.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filter_data, f, indent=2, ensure_ascii=False)
        
    print(f"Thành công! File JSON đã được tạo tại: {output_path}")


process_football_data()