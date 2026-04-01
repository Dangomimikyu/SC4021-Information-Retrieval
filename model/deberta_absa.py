import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict


class DeBERTaABSA:
    """

    Example output:
        text = "Haaland was brilliant but the defence was shocking"
        aspects = ["Haaland", "defence"]
        output = {"Haaland": {"sentiment": "positive", ...},
                  "defence": {"sentiment": "negative", ...}}
    """

    MODEL_NAME = "microsoft/deberta-base-mnli"
    LABELS = ["positive", "negative", "neutral"]
    FLIP_MAP = {"positive": "negative", "negative": "positive", "neutral": "neutral"}

    def __init__(self):
        print("Loading DeBERTa ABSA model...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME)
        self.model.to(self.device)
        self.model.eval()
        # NLI models output: contradiction=0, neutral=1, entailment=2
        self.entailment_idx = 2
        print(f"DeBERTa ABSA model loaded (device: {self.device}).")

    def _classify_aspect(self, text: str, aspect: str) -> Dict:
        """Score sentiment for a single (text, aspect) pair using NLI hypotheses."""
        scores = {}
        for label in self.LABELS:
            hypothesis = f"The text expresses {label} sentiment toward {aspect}."
            encoding = self.tokenizer(
                text,
                hypothesis,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            encoding = {k: v.to(self.device) for k, v in encoding.items()}
            with torch.no_grad():
                logits = self.model(**encoding).logits
                probs = torch.softmax(logits, dim=1).squeeze()
            # entailment probability = how much the text supports this sentiment label
            scores[label] = round(probs[self.entailment_idx].item(), 4)

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
                result["sentiment"] = self.FLIP_MAP.get(result["sentiment"], result["sentiment"])
                result["sarcasm_flipped"] = True
            else:
                result["sarcasm_flipped"] = False

            results[aspect] = result

        return results

    def analyze_batch(self, records: List[Dict]) -> List[Dict]:
        """
        Batch version of analyze(). Each record needs 'text' and 'aspects',
        'is_sarcastic' is optional.
        """
        for record in records:
            record["absa_results"] = self.analyze(
                text=record["text"],
                aspects=record.get("aspects", []),
                is_sarcastic=record.get("is_sarcastic", False),
            )
        return records
