import pandas as pd
from typing import List, Dict, Any
import spacy
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from data_processor import DataProcessor
from bert_sentiment import BertSentimentAnalyzer
from vader_sentiment import VADERAnalyzer
from goemotions_classifier import GoEmotionsClassifier

class OpinionSearchPipeline:
    """Complete pipeline for processing Reddit comments into searchable opinions."""
    
    def __init__(self, use_gpu: bool = True):
        """Initialize all components."""
        print("Initializing Opinion Search Pipeline...")
        
        # Data processing
        self.data_processor = DataProcessor()
        
        # Sentiment models
        self.bert_analyzer = BertSentimentAnalyzer(use_gpu=use_gpu)
        self.vader_analyzer = VADERAnalyzer()
        self.emotion_classifier = GoEmotionsClassifier()
        
        # NER for entity extraction
        self.nlp = spacy.load("en_core_web_lg")
        
        # Topic modeling
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.topic_model = None
        
        print("Pipeline initialized successfully!")
    
    def extract_entities(self, texts: List[str]) -> List[Dict]:
        """Extract player names, teams, and events using NER."""
        results = []
        
        for text in texts:
            doc = self.nlp(text)
            
            entities = {
                'persons': [],  # Player names
                'orgs': [],     # Team names
                'events': [],   # Match events
                'all_entities': []
            }
            
            for ent in doc.ents:
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_
                }
                entities['all_entities'].append(entity_info)
                
                if ent.label_ == 'PERSON':
                    entities['persons'].append(ent.text)
                elif ent.label_ == 'ORG':
                    entities['orgs'].append(ent.text)
                elif ent.label_ == 'EVENT':
                    entities['events'].append(ent.text)
            
            results.append(entities)
        
        return results
    
    def analyze_topics(self, texts: List[str], n_topics: int = 10) -> Dict:
        """Discover topics in discussions using BERTopic."""
        # Create embeddings
        embeddings = self.sentence_model.encode(texts, show_progress_bar=True)
        
        # Fit topic model
        self.topic_model = BERTopic(
            embedding_model=self.sentence_model,
            min_topic_size=5,
            nr_topics=n_topics
        )
        
        topics, probs = self.topic_model.fit_transform(texts, embeddings)
        
        # Get topic info
        topic_info = self.topic_model.get_topic_info()
        
        return {
            'topics': topics,
            'probabilities': probs,
            'topic_info': topic_info
        }
    
    def process_batch(self, json_path: str) -> pd.DataFrame:
        """Process a batch of Reddit posts through the complete pipeline."""
        print(f"\n{'='*60}")
        print("Processing Reddit data through opinion pipeline")
        print(f"{'='*60}")
        
        # Step 1: Load and preprocess data
        print("\n[1/6] Loading and preprocessing data...")
        raw_data = self.data_processor.load_json(json_path)
        df = self.data_processor.process_posts(raw_data)
        print(f"   ✓ Processed {len(df)} comments")
        
        if df.empty:
            print("   ✗ No valid comments found!")
            return df
        
        texts = df['text'].tolist()
        
        # Step 2: BERT sentiment analysis
        print("\n[2/6] Running BERT sentiment analysis...")
        bert_results = self.bert_analyzer.predict(texts, batch_size=32)
        df['bert_sentiment'] = [r['sentiment'] for r in bert_results]
        df['bert_confidence'] = [r['confidence'] for r in bert_results]
        df['bert_scores'] = [r['scores'] for r in bert_results]
        print(f"   ✓ Analyzed {len(bert_results)} comments")
        
        # Step 3: VADER sentiment analysis
        print("\n[3/6] Running VADER sentiment analysis...")
        vader_results = self.vader_analyzer.analyze(texts)
        df['vader_sentiment'] = [r['sentiment'] for r in vader_results]
        df['vader_compound'] = [r['compound'] for r in vader_results]
        df['opinion_intensity'] = [r['intensity'] for r in vader_results]
        print(f"   ✓ Analyzed {len(vader_results)} comments")
        
        # Step 4: Emotion classification
        print("\n[4/6] Running emotion classification...")
        emotion_results = self.emotion_classifier.predict(texts, top_k=3)
        df['primary_emotion'] = [r['primary_emotion'] for r in emotion_results]
        df['emotions'] = [r['emotions'] for r in emotion_results]
        print(f"   ✓ Classified {len(emotion_results)} comments")
        
        # Step 5: Entity extraction
        print("\n[5/6] Extracting named entities...")
        entity_results = self.extract_entities(texts)
        df['entities'] = entity_results
        df['mentioned_players'] = [e['persons'] for e in entity_results]
        df['mentioned_teams'] = [e['orgs'] for e in entity_results]
        print(f"   ✓ Extracted entities from {len(entity_results)} comments")
        
        # Step 6: Topic modeling
        print("\n[6/6] Discovering topics...")
        topic_results = self.analyze_topics(texts, n_topics=10)
        df['topic'] = topic_results['topics']
        df['topic_probability'] = topic_results['probabilities']
        print(f"   ✓ Identified {len(topic_results['topic_info'])} topics")
        
        # Create composite opinion score
        df['opinion_score'] = self._calculate_opinion_score(df)
        
        print(f"\n{'='*60}")
        print("Pipeline processing complete!")
        print(f"{'='*60}\n")
        
        return df
    
    def _calculate_opinion_score(self, df: pd.DataFrame) -> List[float]:
        """Calculate composite opinion score combining multiple signals."""
        scores = []
        
        for _, row in df.iterrows():
            # Base sentiment score (-1 to 1)
            base_score = row['vader_compound']
            
            # Confidence weight from BERT
            confidence_weight = row['bert_confidence']
            
            # Engagement weight (normalized score)
            engagement = min(row['engagement_score'] / 100, 1.0)
            
            # Intensity multiplier
            intensity = row['opinion_intensity']
            
            # Combined score
            opinion_score = (
                base_score * 0.5 +  # Sentiment direction
                confidence_weight * 0.2 +  # Model confidence
                engagement * 0.2 +  # Community validation
                intensity * 0.1  # Opinion strength
            )
            
            scores.append(opinion_score)
        
        return scores
    
    def get_topic_summary(self) -> pd.DataFrame:
        """Get summary of discovered topics."""
        if self.topic_model is None:
            return pd.DataFrame()
        
        return self.topic_model.get_topic_info()
    
    def search_opinions(self, df: pd.DataFrame, 
                        query: str = None,
                        sentiment: str = None,
                        emotion: str = None,
                        min_intensity: float = 0.0) -> pd.DataFrame:
        """Search and filter opinions based on criteria."""
        filtered = df.copy()
        
        # Text search
        if query:
            filtered = filtered[
                filtered['text'].str.contains(query, case=False, na=False)
            ]
        
        # Sentiment filter
        if sentiment:
            filtered = filtered[filtered['bert_sentiment'] == sentiment]
        
        # Emotion filter
        if emotion:
            filtered = filtered[filtered['primary_emotion'] == emotion]
        
        # Intensity filter
        if min_intensity > 0:
            filtered = filtered[filtered['opinion_intensity'] >= min_intensity]
        
        # Sort by opinion score
        filtered = filtered.sort_values('opinion_score', ascending=False)
        
        return filtered


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = OpinionSearchPipeline(use_gpu=True)
    
    # Process Reddit data
    df = pipeline.process_batch('reddit_posts.json')
    
    # Save results
    df.to_csv('analyzed_opinions.csv', index=False)
    print(f"\n✓ Saved results to analyzed_opinions.csv")
    
    # Get topic summary
    topics = pipeline.get_topic_summary()
    print(f"\n📊 Topic Summary:")
    print(topics[['Topic', 'Count', 'Name']].head(10))
    
    # Example searches
    print(f"\n🔍 Example Searches:")
    
    # Search for opinions about Haaland
    haaland_opinions = pipeline.search_opinions(
        df, 
        query="haaland",
        min_intensity=0.5
    )
    print(f"\nFound {len(haaland_opinions)} strong opinions about Haaland")
    
    # Search for angry comments
    angry_comments = pipeline.search_opinions(
        df,
        emotion="anger",
        min_intensity=0.3
    )
    print(f"Found {len(angry_comments)} angry comments")
    
    # Get positive opinions with high engagement
    positive_engaged = df[
        (df['bert_sentiment'] == 'positive') & 
        (df['engagement_score'] > 100)
    ].sort_values('opinion_score', ascending=False)
    print(f"Found {len(positive_engaged)} highly-engaged positive opinions")