from transformers import pipeline
from typing import List, Dict


class DeBERTaABSA:
    """
    how it works: for each aspect, we create an input like "Regarding {aspect}: {text}" and run it through a sentiment analysis model.
    The model outputs scores for positive, negative, and neutral sentiments, which we use to determine
    the predicted sentiment and confidence. If the comment is flagged as sarcastic, flip the predicted sentiment (positive <-> negative).

    Example output:
        text = "Haaland was brilliant but the defence was shocking"
        aspects = ["Haaland", "defence"]
        output = {"Haaland": "positive", "defence": "negative"}
    """

    MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    LABEL_MAP = {"positive": "positive", "negative": "negative", "neutral": "neutral"}
    FLIP_MAP = {"positive": "negative", "negative": "positive", "neutral": "neutral"}

    def __init__(self):
        print("Loading ABSA model...")
        self.sentiment_pipeline = pipeline(
            task="sentiment-analysis",
            model=self.MODEL_NAME,
            top_k=None,       # return scores for all labels
            device=-1,        # CPU
        )
        print("ABSA model loaded.")

    def _classify_aspect(self, text: str, aspect: str) -> Dict:
        """Run sentiment and confidence scoring on a single aspect-conditioned input."""
        aspect_input = f"Regarding {aspect}: {text}"

        if len(aspect_input) > 512:
            aspect_input = aspect_input[:512]

        scores_raw = self.sentiment_pipeline(aspect_input)[0]

        # scores_raw is a list of {"label": ..., "score": ...}
        scores = {item["label"].lower(): round(item["score"], 4) for item in scores_raw}

        predicted = max(scores, key=scores.get)

        return {
            "sentiment": predicted,
            "confidence": scores[predicted],
            "scores": scores,
        }

    def analyze(
        self,
        text: str,
        aspects: List[str],
        is_sarcastic: bool = False,
    ) -> Dict[str, Dict]:
        if not aspects:
            return {}

        results = {}
        for aspect in aspects:
            result = self._classify_aspect(text, aspect)

            if is_sarcastic:
                result["sentiment"] = self.FLIP_MAP[result["sentiment"]]
                result["sarcasm_flipped"] = True
            else:
                result["sarcasm_flipped"] = False

            results[aspect] = result

        return results

    def analyze_batch(self, records: List[Dict]) -> List[Dict]:
        """
        
        Runs analyze() on each record and stores the result in 'absa_results'.

        """
        for record in records:
            record["absa_results"] = self.analyze(
                text=record["text"],
                aspects=record.get("aspects", []),
                is_sarcastic=record.get("is_sarcastic", False),
            )
        return records
