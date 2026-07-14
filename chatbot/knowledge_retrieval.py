"""
THE DIFFERENTIATOR.

Most student projects do `if "internship" in message: return internship_text`.
That breaks the moment someone phrases things differently ("how do I join
your team as a student?"). Instead we use TF-IDF + cosine similarity over
the knowledge base -- lightweight, no external embedding API needed (works
fully offline, zero extra API cost), but genuinely handles paraphrasing.

If the best match score is below KB_CONFIDENCE_THRESHOLD, we say so instead
of forcing Gemini to guess -- this is what "confidence-based escalation"
means and it's worth explicitly mentioning in your report/demo.
"""
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import settings

KB_PATH = Path(__file__).parent.parent / "knowledge_base" / "company_info.json"

class KnowledgeBase:
    def __init__(self):
        self.entries = []
        self.vectorizer = None
        self.matrix = None
        self.reload()

    def reload(self):
        """Re-reads the JSON file and rebuilds the TF-IDF index.
        Call this after editing the knowledge base -- no app restart needed."""
        with open(KB_PATH, "r", encoding="utf-8") as f:
            self.entries = json.load(f)
        corpus = [f"{e['topic']}. {e['content']}" for e in self.entries]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 2):
        """Returns (matches, confidence) where matches is a list of KB
        entries most relevant to the query, sorted by similarity."""
        if not self.entries:
            return [], 0.0
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix).flatten()
        ranked = scores.argsort()[::-1][:top_k]
        top_score = float(scores[ranked[0]]) if len(ranked) else 0.0
        matches = [self.entries[i] for i in ranked if scores[i] > 0]
        return matches, top_score

    def is_confident(self, score: float) -> bool:
        return score >= settings.KB_CONFIDENCE_THRESHOLD

kb = KnowledgeBase()
