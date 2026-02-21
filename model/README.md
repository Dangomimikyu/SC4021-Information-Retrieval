# Initial Sentiment analysis model (incomplete)

Text input is in JSON format.\
Sample Text input:\
{
  "posts": [\
    {
      "post_id": "abc123",\
      "subreddit": "soccer",\
      "title": "Match Thread: Arsenal vs Manchester City",\
      "created_utc": 1708473600\
      "upvotes": 1523,\
      "comments": [\
        {
          "comment_id": "xyz789",\
          "author": "user123",\
          "body": "What a brilliant goal by Haaland! Absolutely world class finish.",\
          "created_utc": 1708474200,\
          "score": 342,\
          "parent_id": null,\
          "user_flair": "Manchester City"\
        },\
        {
          "comment_id": "xyz790",\
          "author": "user456",\
          "body": "Arsenal's defense was terrible today. We need a new CB.",\
          "created_utc": 1708474300,\
          "score": 156,\
          "parent_id": null,\
          "user_flair": "Arsenal"\
        }
      ]
    }
  ]
}

Downstream pipeline:\
JSON input -> Data Processor -> BERT -> VADER -> GoEmotions -> Search API\
The BERT, VADER and GoEmotions models handle different parts of the analysis. BERT and VADER are responsible for sentiment analysis while GoEmotions handles decoding meaning/emotions from the text.\

Currently I don't have a pretrained model identified so the search should not work.\

## Start the API

python api.py

## Or with uvicorn

uvicorn api:app --reload --host 0.0.0.0 --port 8000

## Test Endpoint

curl [http://localhost:8000/]

## Analyze posts

curl -X POST "[http://localhost:8000/analyze]" \
  -H "Content-Type: application/json" \
  -d @reddit_posts.json

## Search opinions

curl -X POST "[http://localhost:8000/search]" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "haaland",
    "sentiment": "positive",
    "min_intensity": 0.5,
    "limit": 10
  }'
