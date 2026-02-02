# Backend/processors.py
import re

class QueryProcessor:
    SYNONYMS = {
        "usage": "extraction",
        "withdrawal": "extraction",
        "consumption": "extraction",
        "drawing": "extraction",
        "pumping": "extraction",
        "replenish": "recharge",
        "refill": "recharge",
        "contamination": "pollution",
        "dirt": "pollution",
        "poison": "pollution"
    }

    EXPANSIONS = {
        "groundwater": ["aquifer", "borewell", "water table"],
        "extraction": ["over-exploited", "stage of extraction"],
        "recharge": ["rainwater harvesting", "check dam"],
        "farming": ["irrigation", "paddy", "sugarcane", "millets"]
    }

    @classmethod
    def normalize(cls, query: str) -> str:
        query = query.lower().strip()
        for old, new in cls.SYNONYMS.items():
            query = re.sub(rf'\b{old}\b', new, query)
        return query

    @classmethod
    def expand(cls, query: str) -> str:
        query_low = query.lower()
        expanded_terms = []
        for term, expansions in cls.EXPANSIONS.items():
            if term in query_low:
                expanded_terms.extend(expansions)

        if expanded_terms:
            return query + " " + " ".join(list(set(expanded_terms)))
        return query

class IntentDetector:
    INTENTS = {
        "WHY": [r"\bwhy\b", r"\bcause\b", r"\breason\b", r"\bhow come\b"],
        "DEFINITION": [r"\bwhat is\b", r"\bdefine\b", r"\bmeaning of\b", r"\bexplain\b"],
        "TIPS": [r"\btip\b", r"\bhow to\b", r"\bway to\b", r"\bconservation\b", r"\bhelp\b"],
        "COMPARISON": [r"\bcompare\b", r"\bvs\b", r"\bdifference between\b", r"\bbetter than\b"],
        "VISUALIZATION": [r"\bchart\b", r"\bgraph\b", r"\bplot\b", r"\bmap\b", r"\bshow\b"],
        "LOCATION_LOOKUP": [r"\bin\s+[a-z]+", r"\bdata for\b", r"\blevels of\b"]
    }

    @classmethod
    def detect(cls, query: str) -> str:
        query = query.lower()

        # Priority checks
        if any(re.search(p, query) for p in cls.INTENTS["WHY"]):
            return "WHY"
        if any(re.search(p, query) for p in cls.INTENTS["COMPARISON"]):
            return "COMPARISON"
        if any(re.search(p, query) for p in cls.INTENTS["DEFINITION"]):
            return "DEFINITION"
        if any(re.search(p, query) for p in cls.INTENTS["TIPS"]):
            return "TIPS"
        if any(re.search(p, query) for p in cls.INTENTS["VISUALIZATION"]):
            return "VISUALIZATION"

        # Default to LOCATION_LOOKUP if a place-like pattern is found or general query
        return "LOCATION_LOOKUP"
