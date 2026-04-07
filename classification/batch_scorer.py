import json
import re
from textblob import TextBlob
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"running on : {device}")

isaac_model_path = "./isaac_model/reddit_sentiment_bert" 
isaac_tokenizer = AutoTokenizer.from_pretrained(isaac_model_path)
isaac_model = AutoModelForSequenceClassification.from_pretrained(isaac_model_path)
isaac_model.to(device)

sarcasm_pipeline = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-irony", 
                            device=0 if torch.cuda.is_available() else -1, use_safetensors=True)

def parse_comments(raw: str) -> list:
    if not raw or raw == '[]' or not isinstance(raw, str): return []
    regex = re.compile(r"'((?:\\.|[^'])*)'|\"((?:\\.|[^\"_])*)\"")
    matches = regex.findall(raw)
    results = []
    for m in matches:
        content = m[0] or m[1]
        content = content.replace("\\'", "'").replace('\\"', '"').replace('\\n', ' ').replace('\\r', '').strip()
        if content and content != "[]": results.append(content)
    return results

input_path = "../indexing/dataset/football_index.json"
output_path = "../indexing/dataset/football_index_scored.json"

print("Loading dataset...")
with open(input_path, 'r', encoding='utf-8') as f:
    docs = json.load(f)

for doc in tqdm(docs):
    raw_comments = doc.get("comments_raw", "")
    parsed_texts = parse_comments(raw_comments)
    scored_comments = []

    texts_to_score = []
    for text in parsed_texts:
        text = text[:1500]
        
        subjectivity = TextBlob(text).sentiment.subjectivity
        if subjectivity < 0.2:
            scored_comments.append({"text": text, "sentiment": "neutral"})
        else:
            texts_to_score.append(text)

    # Process megathreads in chunks of 200 to prevent VRAM overflow
    CHUNK_SIZE = 200
    for i in range(0, len(texts_to_score), CHUNK_SIZE):
        chunk_texts = texts_to_score[i : i + CHUNK_SIZE]
        
        inputs = isaac_tokenizer(chunk_texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = isaac_model(**inputs)
            logits = outputs.logits
        
        base_preds = logits.argmax(dim=1).tolist()
        
        sentiment_map = {0: "negative", 1: "positive", 2: "neutral"}
        
        positive_indices = [idx for idx, p in enumerate(base_preds) if sentiment_map.get(p) == "positive"]
        positive_texts = [chunk_texts[idx] for idx in positive_indices]
        
        sarcasm_results = []
        if positive_texts:
            sarcasm_results = sarcasm_pipeline(positive_texts, truncation=True, max_length=512, batch_size=32)
            
        sarcasm_idx = 0
        for idx, text in enumerate(chunk_texts):
            final_sentiment = sentiment_map.get(base_preds[idx], "neutral")
            
            if final_sentiment == "positive":
                if sarcasm_results[sarcasm_idx]['label'] == 'irony': 
                    final_sentiment = "negative"
                sarcasm_idx += 1
                
            scored_comments.append({"text": text, "sentiment": final_sentiment})
            
        # Explicitly clear VRAM references after every chunk
        del inputs, outputs, logits
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    doc["comments_scored"] = json.dumps(scored_comments)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(docs, f, indent=4)

print("done")