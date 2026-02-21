from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict
import numpy as np

class VADERAnalyzer:
    """Fast sentiment analysis using VADER (optimized for social media)."""
    
    def __init__(self, custom_lexicon: Dict[str, float] = None):
        """
        Initialize VADER with optional custom football lexicon.
        
        Args:
            custom_lexicon: Dict of {word: sentiment_score} for football terms
        """
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Add football-specific terms
        if custom_lexicon:
            self.analyzer.lexicon.update(custom_lexicon)
        else:
            # Default football lexicon
            football_terms = {
                'brilliant': 3.5,
                'worldclass': 3.5,
                'masterclass': 3.5,
                'goat': 3.5,
                'legend': 3.0,
                'rocket': 2.5,
                'banger': 2.5,
                'clinical': 2.5,
                'terrible': -3.0,
                'awful': -3.0,
                'disaster': -3.5,
                'embarrassing': -3.0,
                'shocking': -2.5,
                'pathetic': -3.0,
                'robbery': -2.5,
                'rigged': -2.5
            }
            self.analyzer.lexicon.update(football_terms)
    
    def analyze(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment for list of texts.
        
        Returns:
            List of dicts with compound score and sentiment label
        """
        results = []
        
        for text in texts:
            scores = self.analyzer.polarity_scores(text)
            
            # Classify based on compound score
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            results.append({
                'sentiment': sentiment,
                'compound': compound,
                'positive': scores['pos'],
                'neutral': scores['neu'],
                'negative': scores['neg'],
                'intensity': abs(compound)  # Strength of opinion
            })
        
        return results
    
    def get_opinion_strength(self, text: str) -> str:
        """Categorize opinion strength."""
        scores = self.analyzer.polarity_scores(text)
        intensity = abs(scores['compound'])
        
        if intensity >= 0.7:
            return 'very_strong'
        elif intensity >= 0.4:
            return 'strong'
        elif intensity >= 0.1:
            return 'moderate'
        else:
            return 'weak'


# Example usage
if __name__ == "__main__":
    vader = VADERAnalyzer()
    
    texts = [
        "Amazing score by LeBron. Absolute Cinema",
        "Is there no limit to Itoshi Rin's ego? Man thinks he's really him",
        "This match was aight. Nothing unexpected"
    ]
    
    results = vader.analyze(texts)
    
    for text, result in zip(texts, results):
        print(f"\nText: {text}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Compound: {result['compound']:.3f}")
        print(f"Intensity: {result['intensity']:.3f}")