import torch
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    AutoTokenizer,
    AutoModelForSequenceClassification
)
from typing import List, Dict
import numpy as np

class BertSentimentAnalyzer:
    def __init__(self, model_name: str = "bert-base-uncased", use_gpu: bool = True):

        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        #Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

        self.model.to(self.device)
        self.model.eval()

        self.label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}

    def predict(self, texts: List[str], batch_size: int = 16) -> List[Dict]:
        """
        Predict sentiment for list of texts.
        
        Returns:
            List of dicts with sentiment, confidence, and scores
        """
        
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]

            #Tokenize
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )

            #Move to Device
            input_ids = encoded['input_ids'].to(self.device)
            attention_mask = encoded['attention_mask'].to(self.device)

            #Predict
            with torch.no_grad():
                outputs = self.model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)

            #Process Results
            probs_np = probs.cpu().numpy()
            predictions = torch.argmax(probs, dim=1).cpu().numpy()

            for j, pred in enumerate(predictions):
                results.append({
                    'sentiment': self.label_map[pred],
                    'confidence': float(probs_np[j][pred]),
                    'scores': {
                        'negative': float(probs_np[j][0]),
                        'neutral': float(probs_np[j][1]),
                        'positive': float(probs_np[j][2])
                    }
                })

            return results
        
    def fine_tune(self, train_texts: List[str], train_labels: List[int], epochs: int=3, learning_rate: float=2e-5):
        from torch.utils.data import Dataset, DataLoader
        from transformers import AdamW

        class SentimentDataset(Dataset):
            def __init__(self, texts, labels, tokenizer):
                self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=512)
                self.labels = labels

            def __getitem__(self, idx):
                item = {key: torch.tensor(val[idx])
                        for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
                return item

        dataset = SentimentDataset(train_texts, train_labels, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        #Training Loop
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                total_loss += loss.item()
                loss.backward()
                optimizer.step()
            
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

        self.model.eval()

#Example Usage
if __name__ == "__main__":
    analyzer = BertSentimentAnalyzer()

    texts = [
        "Amazing score by LeBron. Absolute Cinema",
        "Is there no limit to Itoshi Rin's ego? Man thinks he's really him",
        "This match was aight. Nothing unexpected"
    ]

    results = analyzer.predict(texts)

    for text, result in zip(texts, results):
        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment']}, Confidence: {result['confidence']:.4f}")
        print(f"Scores: {result['scores']}")
        print("-" * 50)
