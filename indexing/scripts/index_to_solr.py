import pysolr
import json

# 1. Connection settings
# Ensure 'football_core' matches your core name in docker-compose.yml
solr_url = 'http://localhost:8983/solr/football_core'
solr = pysolr.Solr(solr_url, always_commit=True, timeout=10)

# 2. Path to the JSON file you just created
input_file = '../dataset/football_index.json'

def index_data():
    try:
        # Load the JSON data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} documents from JSON.")
        
        # Uploading to Solr
        print(f"🚀 Starting indexing to Solr at {solr_url}...")
        solr.add(data)
        print("✨ Indexing complete! All data has been sent to Docker Solr.")

    except FileNotFoundError:
        print(f"❌ Error: Could not find {input_path}. Please run convert_data.py first.")
    except Exception as e:
        print(f"❌ An error occurred during indexing: {e}")

if __name__ == "__main__":
    index_data()