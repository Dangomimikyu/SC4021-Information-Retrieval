import json
import re
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class DataProcessor:

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.football_stop_words = {
            'game', 'match', 'play', 'playing', 'player', 'team'
        }
        self.stop_words.update(self.football_stop_words)

    def load_json(self, json_path: str) -> Dict:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        #Remove special characters, keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)

        #Remove whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize_and_filter(self, text: str, remove_stopwords: bool = False) -> List[str]:
        tokens = word_tokenize(text.lower())

        if remove_stopwords:
            tokens = [t for t in tokens if t not in self.stop_words and len(t) > 2]

        return tokens

    def extract_features(self, comment: Dict) -> Dict:
        features = {
            'comment_length': len(comment['body']),
            'word_count': len(comment['body'].split()),
            'has_flair': bool(comment.get('user_flair')),
            'team_affiliation': comment.get('user_flair', 'neutral'),
            'engagement_score': comment.get('score', 0),
            'timestamp': comment.get('created_utc', 0),
            'is_reply': bool(comment.get('parent_id'))
        }
        return features
    
    def process_posts(self, data: Dict) -> pd.DataFrame:
        processed_data = []

        for post in data.get('posts', []):
            post_id = post['post_id']
            subreddit = post['subreddit']
            post_title = post['title']
            post_time = post['created_utc']

            for comment in post.get('comments', []):
                clean_text = self.clean_text(comment['body'])

                #Skip short or empty comments
                if not clean_text or len(clean_text) < 10:
                    continue 

                features = self.extract_features(comment)

                record = {
                    'post_id': post_id,
                    'subreddit': subreddit,
                    'post_title': post_title,
                    'post_time': post_time,
                    'comment_id': comment['id'],
                    'author': comment['author'],
                    'text': clean_text,
                    'original_text': comment['body'],
                    **features
                }

                processed_data.append(record)

        df = pd.DataFrame(processed_data)

        if not df.empty:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.dayofweek

        return df
    
    def get_context_window(self, df: pd.DataFrame, comment_id: str, window_size: int = 3) -> List[str]:
        idx = df[df('comment_id') == comment_id].index
        if len(idx) == 0:
            return []
        
        idx = idx[0]
        start = max(0, idx - window_size)
        end = min(len(df), idx + window_size + 1)

        context = df.iloc[start:end]['text'].tolist()
        return context
    
if __name__ == "__main__":
    processor = DataProcessor()
    data = processor.load_json('reddit_posts.json')
    df = processor.process_posts(data)

    print(f"Processed {len(df)} comments from {df['post_id'].nunique()} posts")
    print(f"\nSample data:\n{df.head()}")
    df.to_csv('processed_reddit_comments.csv', index=False) 

