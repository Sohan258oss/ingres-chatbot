# Backend/reranker.py
import os
from typing import List, Dict, Any
from huggingface_hub import InferenceClient

class Reranker:
    def __init__(self):
        self.model_id = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self.hf_token = os.getenv("HF_TOKEN")
        self.client = InferenceClient(
            token=self.hf_token,
            base_url="https://router.huggingface.co/hf-inference",
            headers={"X-Wait-For-Model": "true"}
        )

    def rerank(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reranks candidates using a cross-encoder model in a single batch call."""
        if not candidates:
            return []

        # Batching inputs to reduce latency
        inputs = [f"{query} [SEP] {cand['name']}" for cand in candidates]

        try:
            # Inference API handles batching for text_classification
            responses = self.client.text_classification(inputs, model=self.model_id)

            # Map scores back to candidates
            for i, res in enumerate(responses):
                # response[i] is a list of dicts like [{"label": "...", "score": ...}]
                if isinstance(res, list) and len(res) > 0:
                    score = res[0].get("score", 0)
                    candidates[i]["rerank_score"] = score
                else:
                    candidates[i]["rerank_score"] = candidates[i].get("score", 0)
        except Exception as e:
            print(f"Reranking batch error: {e}. Falling back to individual scoring or semantic score.")
            for cand in candidates:
                if "rerank_score" not in cand:
                    cand["rerank_score"] = cand["score"]

        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return candidates
