from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from textblob import TextBlob
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

app = FastAPI()

isaac_model_path = "./isaac_model/reddit_sentiment_bert" 
isaac_tokenizer = AutoTokenizer.from_pretrained(isaac_model_path)
isaac_model = AutoModelForSequenceClassification.from_pretrained(isaac_model_path)

sarcasm_pipeline = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-irony")

class TweetBatchRequest(BaseModel):
    texts: List[str]

class CommentResult(BaseModel):
    text: str
    sentiment: str

@app.post("/analyze", response_model=List[CommentResult])
async def analyze_tweets(request: TweetBatchRequest):
    results = []
    
    for text in request.texts:
        # subjectivity filter
        subjectivity = TextBlob(text).sentiment.subjectivity
        if subjectivity < 0.5:
            # passing it back as neutral to keep the frontend UI intact
            results.append(CommentResult(text=text, sentiment="neutral"))
            continue
            
        # base polarit isaac
        inputs = isaac_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = isaac_model(**inputs).logits
        base_pred = logits.argmax().item() 
        
        sentiment_map = {0: "negative", 1: "positive", 2: "neutral"}
        final_sentiment = sentiment_map.get(base_pred, "neutral")

        # sarcasm 
        if final_sentiment == "positive":
            sarcasm_res = sarcasm_pipeline(text)[0]
            if sarcasm_res['label'] == 'irony': 
                final_sentiment = "negative"
                
        results.append(CommentResult(text=text, sentiment=final_sentiment))
        
    return results