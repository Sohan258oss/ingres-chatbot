# Backend/retriever.py
import os
import math
import json
import sqlite3
from typing import List, Dict, Any
from huggingface_hub import InferenceClient
from Backend.data_manager import KNOWLEDGE_BASE, WHY_MAP, TIPS

class HybridRetriever:
    def __init__(self):
        self.model_id = "sentence-transformers/all-mpnet-base-v2"
        self.hf_token = os.getenv("HF_TOKEN")
        self.client = InferenceClient(
            token=self.hf_token,
            base_url="https://router.huggingface.co/hf-inference",
            headers={"X-Wait-For-Model": "true"}
        )
        self.indices = {
            "locations": {"entities": [], "embeddings": []},
            "concepts": {"entities": [], "embeddings": []},
            "causes": {"entities": [], "embeddings": []},
            "tips": {"entities": [], "embeddings": []}
        }
        self.embeddings_path = os.path.join(os.path.dirname(__file__), "multi_index_embeddings.json")

    def _query_api(self, inputs: List[str]) -> List[List[float]]:
        try:
            response = self.client.feature_extraction(inputs, model=self.model_id)
            if hasattr(response, "tolist"):
                response = response.tolist()

            # Normalize to 2D list: [num_inputs, embedding_dim]
            if isinstance(response, list) and len(response) > 0:
                if not isinstance(response[0], list): # Single embedding returned as 1D
                    return [response]
                # Handle nested lists if API returns [[[v1, v2...]]]
                cleaned = []
                for item in response:
                    temp = item
                    while isinstance(temp, list) and len(temp) > 0 and isinstance(temp[0], list):
                        temp = temp[0]
                    cleaned.append(temp)
                return cleaned
            return []
        except Exception as e:
            print(f"HF API Error: {e}")
            return []

    def load_indices(self):
        if os.path.exists(self.embeddings_path):
            try:
                with open(self.embeddings_path, "r") as f:
                    data = json.load(f)
                if data.get("model") == self.model_id:
                    self.indices = data["indices"]
                    return True
            except Exception as e:
                print(f"Error loading indices: {e}")
        return False

    def save_indices(self):
        with open(self.embeddings_path, "w") as f:
            json.dump({
                "indices": self.indices,
                "model": self.model_id
            }, f)

    def build_indices(self, states, districts, blocks):
        # 1. Locations
        loc_entities = sorted(list(set(states + districts + blocks)))
        print(f"Encoding {len(loc_entities)} locations...")
        self.indices["locations"]["entities"] = loc_entities
        self.indices["locations"]["embeddings"] = self._encode_batch(loc_entities)

        # 2. Concepts (Keys + Chunks)
        concept_data = []
        for key, chunks in KNOWLEDGE_BASE.items():
            concept_data.append(key)
            concept_data.extend(chunks)
        concept_data = sorted(list(set(concept_data)))
        print(f"Encoding {len(concept_data)} concept items...")
        self.indices["concepts"]["entities"] = concept_data
        self.indices["concepts"]["embeddings"] = self._encode_batch(concept_data)

        # 3. Causes
        cause_data = []
        for key, val in WHY_MAP.items():
            cause_data.append(key)
            cause_data.append(val)
        cause_data = sorted(list(set(cause_data)))
        print(f"Encoding {len(cause_data)} cause items...")
        self.indices["causes"]["entities"] = cause_data
        self.indices["causes"]["embeddings"] = self._encode_batch(cause_data)

        # 4. Tips
        tip_data = []
        for key, val in TIPS.items():
            tip_data.append(key)
            tip_data.append(val)
        tip_data = sorted(list(set(tip_data)))
        print(f"Encoding {len(tip_data)} tip items...")
        self.indices["tips"]["entities"] = tip_data
        self.indices["tips"]["embeddings"] = self._encode_batch(tip_data)

        self.save_indices()

    def _encode_batch(self, entities, batch_size=32):
        embeddings = []
        for i in range(0, len(entities), batch_size):
            batch = entities[i : i + batch_size]
            res = self._query_api(batch)
            if res:
                embeddings.extend(res)
        return embeddings

    @staticmethod
    def cosine_similarity(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        return dot / (mag_a * mag_b) if mag_a * mag_b > 0 else 0

    @staticmethod
    def keyword_overlap(query, document):
        q_words = set(query.lower().split())
        d_words = set(document.lower().split())
        if not q_words: return 0
        intersection = q_words.intersection(d_words)
        return len(intersection) / len(q_words)

    def search(self, query: str, index_names: List[str], top_k=5, threshold=0.5) -> List[Dict[str, Any]]:
        query_emb_list = self._query_api([query])
        if not query_emb_list:
            return []
        query_emb = query_emb_list[0]

        all_results = []
        for idx_name in index_names:
            idx = self.indices.get(idx_name)
            if not idx: continue

            entities = idx["entities"]
            embs = idx["embeddings"]

            for i, emb in enumerate(embs):
                sem_score = self.cosine_similarity(query_emb, emb)
                key_score = self.keyword_overlap(query, entities[i])

                # Hybrid Scoring: 0.7 Semantic + 0.3 Keyword
                final_score = 0.7 * sem_score + 0.3 * key_score

                if final_score >= threshold:
                    all_results.append({
                        "name": entities[i],
                        "score": final_score,
                        "semantic": sem_score,
                        "keyword": key_score,
                        "index": idx_name
                    })

        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]

    def get_indices_for_intent(self, intent: str) -> List[str]:
        mapping = {
            "WHY": ["causes", "locations"],
            "DEFINITION": ["concepts"],
            "TIPS": ["tips"],
            "LOCATION_LOOKUP": ["locations"],
            "COMPARISON": ["locations"],
            "VISUALIZATION": ["locations", "concepts"]
        }
        return mapping.get(intent, ["concepts", "locations"])

    def get_threshold_for_intent(self, intent: str) -> float:
        thresholds = {
            "WHY": 0.55,
            "DEFINITION": 0.6,
            "TIPS": 0.5,
            "LOCATION_LOOKUP": 0.65,
            "COMPARISON": 0.6,
            "VISUALIZATION": 0.55
        }
        return thresholds.get(intent, 0.6)
