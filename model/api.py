from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime
import json

from opinion_pipeline import OpinionSearchPipeline

app = FastAPI(
    title="Football Opinion Search API",
    description="Search and analyze football opinions from Reddit",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = None
opinions_df = None

class RedditPost(BaseModel):
    """Schema for Reddit post input."""
    post_id: str
    subreddit: str
    title: str
    created_utc: int
    upvotes: int
    comments: List[Dict[str, Any]]

class RedditInput(BaseModel):
    """Schema for batch input."""
    posts: List[RedditPost]

class OpinionResponse(BaseModel):
    """Schema for opinion search results."""
    comment_id: str
    text: str
    author: str
    sentiment: str
    confidence: float
    emotion: str
    opinion_score: float
    entities: Dict
    timestamp: int

class SearchRequest(BaseModel):
    """Schema for search request."""
    query: Optional[str] = None
    sentiment: Optional[str] = None
    emotion: Optional[str] = None
    min_intensity: Optional[float] = 0.0
    limit: Optional[int] = 50

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup."""
    global pipeline
    pipeline = OpinionSearchPipeline(use_gpu=True)
    print("✓ API ready!")

@app.get("/")
async def root():
    """API health check."""
    return {
        "status": "online",
        "service": "Football Opinion Search Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
async def analyze_posts(data: RedditInput):
    """
    Analyze Reddit posts and extract opinions.
    
    Processes input JSON through the complete ML pipeline.
    """
    global opinions_df
    
    # Save input to temporary file
    temp_file = f"temp_input_{datetime.now().timestamp()}.json"
    with open(temp_file, 'w') as f:
        json.dump(data.dict(), f)
    
    # Process through pipeline
    try:
        opinions_df = pipeline.process_batch(temp_file)
        
        return {
            "status": "success",
            "processed_comments": len(opinions_df),
            "unique_posts": opinions_df['post_id'].nunique(),
            "sentiment_distribution": {
                "positive": int((opinions_df['bert_sentiment'] == 'positive').sum()),
                "negative": int((opinions_df['bert_sentiment'] == 'negative').sum()),
                "neutral": int((opinions_df['bert_sentiment'] == 'neutral').sum())
            },
            "top_emotions": opinions_df['primary_emotion'].value_counts().head(5).to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_opinions(request: SearchRequest):
    """
    Search opinions with filters.
    
    Query parameters:
    - query: Text search term
    - sentiment: Filter by sentiment (positive/negative/neutral)
    - emotion: Filter by emotion
    - min_intensity: Minimum opinion intensity (0-1)
    - limit: Maximum results to return
    """
    global opinions_df
    
    if opinions_df is None or opinions_df.empty:
        raise HTTPException(
            status_code=400, 
            detail="No data analyzed yet. Please call /analyze first."
        )
    
    # Search
    results = pipeline.search_opinions(
        opinions_df,
        query=request.query,
        sentiment=request.sentiment,
        emotion=request.emotion,
        min_intensity=request.min_intensity
    )
    
    # Limit results
    results = results.head(request.limit)
    
    # Format response
    opinions = []
    for _, row in results.iterrows():
        opinions.append({
            "comment_id": row['comment_id'],
            "text": row['text'],
            "author": row['author'],
            "sentiment": row['bert_sentiment'],
            "confidence": float(row['bert_confidence']),
            "emotion": row['primary_emotion'],
            "opinion_score": float(row['opinion_score']),
            "entities": row['entities'],
            "mentioned_players": row['mentioned_players'],
            "mentioned_teams": row['mentioned_teams'],
            "timestamp": int(row['timestamp']),
            "engagement_score": int(row['engagement_score'])
        })
    
    return {
        "total_results": len(results),
        "query": request.dict(),
        "opinions": opinions
    }

@app.get("/topics")
async def get_topics():
    """Get discovered topics from analyzed data."""
    global pipeline
    
    if pipeline.topic_model is None:
        raise HTTPException(
            status_code=400,
            detail="No topics available. Run /analyze first."
        )
    
    topic_info = pipeline.get_topic_summary()
    
    return {
        "total_topics": len(topic_info),
        "topics": topic_info.to_dict('records')
    }

@app.get("/stats")
async def get_statistics():
    """Get overall statistics of analyzed data."""
    global opinions_df
    
    if opinions_df is None or opinions_df.empty:
        raise HTTPException(status_code=400, detail="No data available")
    
    stats = {
        "total_comments": len(opinions_df),
        "unique_authors": opinions_df['author'].nunique(),
        "sentiment_distribution": {
            "positive": int((opinions_df['bert_sentiment'] == 'positive').sum()),
            "negative": int((opinions_df['bert_sentiment'] == 'negative').sum()),
            "neutral": int((opinions_df['bert_sentiment'] == 'neutral').sum())
        },
        "top_emotions": opinions_df['primary_emotion'].value_counts().head(10).to_dict(),
        "average_opinion_score": float(opinions_df['opinion_score'].mean()),
        "average_intensity": float(opinions_df['opinion_intensity'].mean()),
        "most_mentioned_players": pd.Series(
            [p for players in opinions_df['mentioned_players'] for p in players]
        ).value_counts().head(10).to_dict(),
        "most_mentioned_teams": pd.Series(
            [t for teams in opinions_df['mentioned_teams'] for t in teams]
        ).value_counts().head(10).to_dict()
    }
    
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)