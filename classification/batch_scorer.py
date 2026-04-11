import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

ISAAC_MODEL_PATH = "./isaac_model/reddit_sentiment_bert"

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

# Keep tagger + attribute_ruler so token.pos_ (PROPN/NOUN) is correctly set 
print("Loading spaCy NER model...")
nlp = spacy.load("en_core_web_sm", disable=["lemmatizer"])

isaac_model_path = ISAAC_MODEL_PATH
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
        print("Loading DeBERTa ABSA model...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME, use_safetensors=False)
        self.model.to(self.device)
        self.model.eval()
        self.entailment_idx = 2
        print(f"DeBERTa ABSA model loaded (device: {self.device}).")

    def analyze_batch(self, text_aspect_pairs: list, batch_size: int = 32) -> list:
        if not text_aspect_pairs: return []
        results = []
        for i in range(0, len(text_aspect_pairs), batch_size):
            batch = text_aspect_pairs[i:i+batch_size]
            all_texts = []
            all_hyps = []
            
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
                results.append({
                    "aspect": aspect,
                    "sentiment": predicted,
                    "confidence": scores[predicted],
                    "scores": scores
                })
        return results

absa_model = DeBERTaABSA()

# ── PRIMARY PATH ──────────────────────────────────────────────────────────────

def extract_propn_sequences(doc):
    """PRIMARY PATH: group consecutive PROPN tokens to catch names spaCy NER misses.
    """
    ner_texts = {ent.text.lower() for ent in doc.ents}
    aspects = set()
    i = 0
    while i < len(doc):
        token = doc[i]
        if token.pos_ == 'PROPN' and token.is_alpha and not token.is_stop:
            j = i + 1
            while j < len(doc) and doc[j].pos_ == 'PROPN' and doc[j].is_alpha:
                j += 1
            phrase = ' '.join(doc[k].text for k in range(i, j))
            word_count = j - i
            if word_count == 1 and phrase.lower() not in ner_texts:
                i = j
                continue
            if len(phrase) > 2:
                aspects.add(phrase)
            i = j
        else:
            i += 1
    return aspects

# ── FALLBACK PATH (runs only when NER + PROPN find nothing) ───────────────────

def get_subtree_text(token):
    """Return the full noun phrase for a token by walking its dependency subtree.
    """
    subtree_tokens = sorted(token.subtree, key=lambda x: x.i)
    phrase = [t.text for t in subtree_tokens if t.is_alpha or t.is_digit or t.text in ['-', "'"]]
    result = ' '.join(phrase).strip()
    return result if len(result.split()) <= 5 else None

def extract_dependency_aspects(doc):
    """FALLBACK PATH: extract aspects via dependency parsing (subjects, objects, appositions)."""
    aspects = set()
    for token in doc:
        if token.dep_ in ['nsubj', 'nsubjpass', 'dobj'] and token.pos_ in ['NOUN', 'PROPN']:
            aspect_text = get_subtree_text(token)
            if aspect_text:
                aspects.add(aspect_text)
        if token.dep_ == 'pobj' and token.pos_ in ['NOUN', 'PROPN']:
            aspect_text = get_subtree_text(token)
            if aspect_text:
                aspects.add(aspect_text)
        # "a soccer player Lamine Yamal" → apposition relation
        if token.dep_ == 'appos' and token.pos_ in ['NOUN', 'PROPN']:
            aspect_text = get_subtree_text(token)
            if aspect_text:
                aspects.add(aspect_text)
    return aspects

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

POST_BATCH_SIZE = 50

for i in tqdm(range(0, len(docs), POST_BATCH_SIZE)):
    batch_docs = docs[i : i + POST_BATCH_SIZE]
    all_texts_to_score = []
    doc_map = [] 

    for doc_idx, doc in enumerate(batch_docs):
        raw_comments = doc.get("comments_raw", "")
        parsed_texts = parse_comments(raw_comments)
        doc["temp_scored"] = []
        
        for text in parsed_texts:
            text = text[:1500]
            subjectivity = TextBlob(text).sentiment.subjectivity
            if subjectivity < 0.05:
                doc["temp_scored"].append({"text": text, "sentiment": "neutral", "absa_results": {}})
            else:
                all_texts_to_score.append(text)
                doc_map.append(doc_idx)

    CHUNK_SIZE = 200
    for chunk_start in range(0, len(all_texts_to_score), CHUNK_SIZE):
        chunk_texts = all_texts_to_score[chunk_start : chunk_start + CHUNK_SIZE]
        chunk_doc_indices = doc_map[chunk_start : chunk_start + CHUNK_SIZE]
        
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
            
        is_sarcastic_map = []
        sarcasm_idx = 0
        final_sentiments = []
        
        for idx, text in enumerate(chunk_texts):
            final_sentiment = sentiment_map.get(base_preds[idx], "neutral")
            sarcastic_flag = False
            
            if final_sentiment == "positive" and sarcasm_idx < len(sarcasm_results):
                if sarcasm_results[sarcasm_idx]['label'] == 'irony': 
                    final_sentiment = "negative"
                    sarcastic_flag = True
                sarcasm_idx += 1
                
            final_sentiments.append(final_sentiment)
            is_sarcastic_map.append(sarcastic_flag)

        aspects_list = []
        for spacy_doc in nlp.pipe(chunk_texts, batch_size=50):
            # Named entities + PROPN sequences are highest quality sources
            named_entities = set([ent.text for ent in spacy_doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'PRODUCT']])
            propn_aspects = extract_propn_sequences(spacy_doc)

            # fall back to dep aspects/noun chunks only when no named entities found
            ner_lower = {e.lower() for e in named_entities}
            candidates = named_entities | propn_aspects

            if not candidates:
                dep_aspects = extract_dependency_aspects(spacy_doc)
                noun_chunks = set()
                for chunk in spacy_doc.noun_chunks:
                    if any(token.pos_ == 'PRON' for token in chunk):
                        continue
                    chunk_text = re.sub(r'[^\w\s]', '', chunk.text).strip()
                    if len(chunk_text) > 2:
                        noun_chunks.add(chunk_text)
                candidates = dep_aspects | noun_chunks

            _stopwords = {'i', 'you', 'he', 'she', 'it', 'we', 'they',
                          'this', 'that', 'these', 'those', 'thing', 'things',
                          'something', 'anything', 'everything', 'nothing'}
            filtered_aspects = [a for a in candidates if a.lower() not in _stopwords]

            deduped = list(named_entities)
            for aspect in filtered_aspects:
                al = aspect.lower()
                if al in ner_lower:
                    continue
                if any(al in ne for ne in ner_lower):
                    continue
                if any(ne in al for ne in ner_lower):
                    continue
                deduped.append(aspect)

            aspects_list.append(deduped[:10])

        # Track which aspects are NER/PROPN (trusted) vs fallback noun chunks
        ner_aspects_per_idx = [set() for _ in chunk_texts]
        for idx, spacy_doc in enumerate(nlp.pipe(chunk_texts, batch_size=50)):
            named_entities = set([ent.text for ent in spacy_doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'PRODUCT']])
            propn_aspects = extract_propn_sequences(spacy_doc)
            ner_aspects_per_idx[idx] = named_entities | propn_aspects

        text_aspect_pairs = []
        pair_to_chunk_idx = []
        pair_is_ner = []  # True = NER/PROPN entity, False = fallback noun chunk
        for idx, text in enumerate(chunk_texts):
            for aspect in aspects_list[idx]:
                text_aspect_pairs.append((text, aspect))
                pair_to_chunk_idx.append(idx)
                pair_is_ner.append(aspect in ner_aspects_per_idx[idx])

        absa_results_flat = absa_model.analyze_batch(text_aspect_pairs, batch_size=16)

        CONFIDENCE_THRESHOLD = 0.3  # only applied to fallback noun chunks, not NER entities
        final_absa_dicts = [{} for _ in chunk_texts]
        for j, res in enumerate(absa_results_flat):
            # Always keep NER/PROPN entities, filter low-confidence fallback aspects
            if not pair_is_ner[j] and res["confidence"] < CONFIDENCE_THRESHOLD:
                continue
            orig_idx = pair_to_chunk_idx[j]
            if is_sarcastic_map[orig_idx]:
                # res["sentiment"] = absa_model.FLIP_MAP.get(res["sentiment"], res["sentiment"])
                res["sarcasm_flipped"] = True
            else:
                res["sarcasm_flipped"] = False

            aspect_name = res.pop("aspect")
            final_absa_dicts[orig_idx][aspect_name] = res

        for idx, text in enumerate(chunk_texts):
            target_doc_idx = chunk_doc_indices[idx]
            batch_docs[target_doc_idx]["temp_scored"].append({
                "text": text,
                "sentiment": final_sentiments[idx],
                "absa_results": final_absa_dicts[idx]
            })
            
        del inputs, outputs, logits
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
    for doc in batch_docs:
        doc["comments_scored"] = json.dumps(doc.pop("temp_scored"))

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(docs, f, indent=4)

print("done")