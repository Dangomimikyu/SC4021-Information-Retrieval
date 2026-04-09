import json
import re
from textblob import TextBlob
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm 
import spacy
from typing import List, Dict

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"running on : {device}")

# Load standard spaCy NER
print("Loading standard spaCy NER model...")
nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])

# Load Models
isaac_model_path = "./isaac_model/reddit_sentiment_bert" 
isaac_tokenizer = AutoTokenizer.from_pretrained(isaac_model_path)
isaac_model = AutoModelForSequenceClassification.from_pretrained(isaac_model_path)
isaac_model.to(device)
isaac_model.eval()

sarcasm_pipeline = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-irony", 
                            device=0 if torch.cuda.is_available() else -1, use_safetensors=False)

class DeBERTaABSA:
    MODEL_NAME = "microsoft/deberta-base-mnli"
    LABELS = ["positive", "negative", "neutral"]
    FLIP_MAP = {"positive": "negative", "negative": "positive", "neutral": "neutral"}

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME, use_safetensors=False)
        self.model.to(self.device)
        self.model.eval()
        self.entailment_idx = 2

    def analyze_batch(self, text_aspect_pairs: list, batch_size: int = 32) -> list:
        if not text_aspect_pairs: return []
        results = []
        for i in range(0, len(text_aspect_pairs), batch_size):
            batch = text_aspect_pairs[i:i+batch_size]
            all_texts, all_hyps = [], []
            for text, aspect in batch:
                for label in self.LABELS:
                    all_texts.append(text)
                    all_hyps.append(f"The text expresses {label} sentiment toward {aspect}.")
            
            encoding = self.tokenizer(all_texts, all_hyps, return_tensors="pt", truncation="only_first", max_length=500, padding=True)
            encoding = {k: v.to(self.device) for k, v in encoding.items()}
            with torch.no_grad():
                logits = self.model(**encoding).logits
                probs = torch.softmax(logits, dim=1)[:, self.entailment_idx]
            
            probs = probs.view(len(batch), 3).tolist()
            for j, (text, aspect) in enumerate(batch):
                scores = {self.LABELS[k]: round(probs[j][k], 4) for k in range(3)}
                predicted = max(scores, key=scores.get)
                results.append({"aspect": aspect, "sentiment": predicted, "confidence": scores[predicted]})
        return results

absa_model = DeBERTaABSA()

def parse_comments(raw: str) -> list:
    if not raw or raw == '[]' or not isinstance(raw, str): return []
    regex = re.compile(r"'((?:\\.|[^'])*)'|\"((?:\\.|[^\"_])*)\"")
    matches = regex.findall(raw)
    return [m[0] or m[1] for m in matches if (m[0] or m[1])]

input_path = "../indexing/dataset/football_index.json"
output_path = "../indexing/dataset/football_index_scored2.json"

print("Loading dataset...")
with open(input_path, 'r', encoding='utf-8') as f:
    docs = json.load(f)

# TARGETED SUBSET: Only the Barcelona vs Atletico Madrid thread
target_id = "1rjzgaz" 
subset_docs = [d for d in docs if d.get("id") == target_id]

print(f"Targeting match: {subset_docs[0].get('title')} ({len(subset_docs)} doc found)")

for doc in subset_docs:
    raw_comments = doc.get("comments_raw", "")
    parsed_texts = parse_comments(raw_comments)
    scored_comments = []
    texts_to_score = []

    for text in parsed_texts:
        text = text[:1500]
        subjectivity = TextBlob(text).sentiment.subjectivity
        
        # LOWERED THRESHOLD: Most football comments will pass this now
        if subjectivity < 0.05:
            scored_comments.append({"text": text, "sentiment": "neutral", "absa_results": {}})
        else:
            texts_to_score.append(text)

    CHUNK_SIZE = 100
    for i in range(0, len(texts_to_score), CHUNK_SIZE):
        chunk_texts = texts_to_score[i : i + CHUNK_SIZE]
        
        inputs = isaac_tokenizer(chunk_texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = isaac_model(**inputs)
            base_preds = outputs.logits.argmax(dim=1).tolist()
        
        sentiment_map = {0: "negative", 1: "positive", 2: "neutral"}
        positive_indices = [idx for idx, p in enumerate(base_preds) if sentiment_map.get(p) == "positive"]
        positive_texts = [chunk_texts[idx] for idx in positive_indices]
        
        sarcasm_results = []
        if positive_texts:
            sarcasm_results = sarcasm_pipeline(positive_texts, truncation=True, max_length=512, batch_size=32)
            
        sarcasm_idx = 0
        final_sentiments, is_sarcastic_map = [], []
        for idx, text in enumerate(chunk_texts):
            final_sent = sentiment_map.get(base_preds[idx], "neutral")
            sarcastic = False
            if final_sent == "positive" and sarcasm_idx < len(sarcasm_results):
                if sarcasm_results[sarcasm_idx]['label'] == 'irony': 
                    final_sent = "negative"
                    sarcastic = True
                sarcasm_idx += 1
            final_sentiments.append(final_sent)
            is_sarcastic_map.append(sarcastic)

        # NER Processing
        aspects_list = []
        for spacy_doc in nlp.pipe(chunk_texts, batch_size=50):
            ents = list(set([ent.text for ent in spacy_doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE']]))
            aspects_list.append(ents)

        text_aspect_pairs, pair_to_chunk_idx = [], []
        for idx, text in enumerate(chunk_texts):
            for aspect in aspects_list[idx]:
                text_aspect_pairs.append((text, aspect))
                pair_to_chunk_idx.append(idx)

        absa_results_flat = absa_model.analyze_batch(text_aspect_pairs, batch_size=32)
        final_absa_dicts = [{} for _ in chunk_texts]
        for j, res in enumerate(absa_results_flat):
            orig_idx = pair_to_chunk_idx[j]
            res["sarcasm_flipped"] = is_sarcastic_map[orig_idx]
            if res["sarcasm_flipped"]:
                res["sentiment"] = absa_model.FLIP_MAP.get(res["sentiment"], res["sentiment"])
            
            aspect_name = res.pop("aspect")
            final_absa_dicts[orig_idx][aspect_name] = res

        for idx, text in enumerate(chunk_texts):
            scored_comments.append({"text": text, "sentiment": final_sentiments[idx], "absa_results": final_absa_dicts[idx]})
            
        if torch.cuda.is_available(): torch.cuda.empty_cache()
    
    doc["comments_scored"] = json.dumps(scored_comments)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(subset_docs, f, indent=4)

print(f"Done. Subset saved to {output_path}")