from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict
import numpy as np

class GoEmotionsClassifier:
    """28-emotion classification using GoEmotions (Reddit-trained)."""
    
    EMOTIONS = [
        'admiration', 'amusement', 'anger', 'annoyance', 'approval', 
        'caring', 'confusion', 'curiosity', 'desire', 'disappointment',
        'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear',
        'gratitude', 'grief', 'joy', 'love', 'nervousness', 'optimism',
        'pride', 'realization', 'relief', 'remorse', 'sadness', 
        'surprise', 'neutral'
    ]
    
    def __init__(self, model_name: str = "SamLowe/roberta-base-go_emotions", threshold: float = 0.3):
        """
        Initialize GoEmotions classifier.
        
        Args:
            model_name: Hugging Face model name
            threshold: Minimum confidence threshold for emotions
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.threshold = threshold
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, texts: List[str], top_k: int = 3) -> List[Dict]:
        """
        Predict emotions for texts.
        
        Args:
            texts: List of text strings
            top_k: Number of top emotions to return
            
        Returns:
            List of dicts with detected emotions and scores
        """
        results = []
        
        for text in texts:
            # Tokenize
            encoded = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            
            input_ids = encoded['input_ids'].to(self.device)
            attention_mask = encoded['attention_mask'].to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(input_ids, attention_mask=attention_mask)
                probs = torch.sigmoid(outputs.logits)  # Multi-label classification
            
            probs_np = probs.cpu().numpy()[0]
            
            # Get emotions above threshold
            detected_emotions = []
            for idx, score in enumerate(probs_np):
                if score >= self.threshold:
                    detected_emotions.append({
                        'emotion': self.EMOTIONS[idx],
                        'score': float(score)
                    })
            
            # Sort by score and get top_k
            detected_emotions.sort(key=lambda x: x['score'], reverse=True)
            top_emotions = detected_emotions[:top_k]
            
            results.append({
                'emotions': top_emotions,
                'primary_emotion': top_emotions[0]['emotion'] if top_emotions else 'neutral',
                'all_scores': {self.EMOTIONS[i]: float(probs_np[i]) for i in range(len(self.EMOTIONS))}
            })
        
        return results


# Example usage
if __name__ == "__main__":
    classifier = GoEmotionsClassifier()
    
    texts = [
        "Amazing score by LeBron. Absolute Cinema",
        "Is there no limit to Itoshi Rin's ego? Man thinks he's really him",
        "This match was aight. Nothing unexpected"
    ]
    
    results = classifier.predict(texts)
    
    for text, result in zip(texts, results):
        print(f"\nText: {text}")
        print(f"Primary emotion: {result['primary_emotion']}")
        print(f"Top emotions: {result['emotions']}")