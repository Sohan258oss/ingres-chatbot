import os
import requests
import json
import sqlite3
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS

from Backend.data_manager import KNOWLEDGE_BASE, CONTAMINANT_DATA, WHY_MAP, TIPS, LAYERED_METADATA
from Backend.processors import QueryProcessor, IntentDetector
from Backend.retriever import HybridRetriever
from Backend.reranker import Reranker

# Database path configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "ingres.db")
if not os.path.exists(DB_PATH):
    DB_PATH = "./ingres.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize components
    retriever = HybridRetriever()
    reranker = Reranker()
    app.state.retriever = retriever
    app.state.reranker = reranker

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(assessments)")
            cols = [info[1] for info in cursor.fetchall()]
            state_col = next((c for c in cols if "state" in c.lower()), "State")
            dist_col = next((c for c in cols if "district" in c.lower()), "District")
            block_col = next((c for c in cols if "block" in c.lower() or "taluka" in c.lower()), "Block/Taluka")

            cursor.execute(f'SELECT DISTINCT "{state_col}" FROM assessments')
            app.state.states_list = [r[0] for r in cursor.fetchall() if r[0]]
            cursor.execute(f'SELECT DISTINCT "{dist_col}" FROM assessments')
            app.state.districts_list = [r[0] for r in cursor.fetchall() if r[0]]
            cursor.execute(f'SELECT DISTINCT "{block_col}" FROM assessments')
            app.state.blocks_list = [r[0] for r in cursor.fetchall() if r[0]]

            if not retriever.load_indices():
                print("Indices not found or outdated. Building new indices...")
                retriever.build_indices(app.state.states_list, app.state.districts_list, app.state.blocks_list)
            else:
                print("Indices loaded successfully.")
    except Exception as e:
        print(f"Error initializing: {e}")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- SERVICES --------------------
def get_wikipedia_image(query):
    try:
        term = query.title().replace(' ', '_')
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{term}"
        headers = {"User-Agent": "MyWaterBot_AI_Bot/1.0 (support@mywaterbot.ai)"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "thumbnail" in data:
                return data["thumbnail"]["source"]
    except Exception:
        pass
    return None

def get_image_url(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=1)
            if results:
                return results[0]['image']
    except Exception as e:
        print(f"Image search error for '{query}': {e}")
    return get_wikipedia_image(query)

def get_latest_news():
    query = "groundwater levels India"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return get_cached_news()
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = [item.get_text().strip() for item in soup.find_all('h3') if item.get_text().strip()][:3]
        return headlines if headlines else get_cached_news()
    except Exception:
        return get_cached_news()

def get_cached_news():
    return [
        "Groundwater levels in India showing signs of improvement in some regions due to better monsoon.",
        "New CGWB report highlights critical depletion in northwestern states.",
        "Government announces new initiatives for community-led groundwater management."
    ]

# -------------------- HELPERS --------------------
def format_layered_response(term, definition):
    meta = LAYERED_METADATA.get(term.lower(), {
        "why": "Crucial for understanding water sustainability and resource management.",
        "impact": "Directly affects long-term water availability and quality.",
        "tip": "Support local water conservation initiatives."
    })
    return (
        f"**Definition:** {definition}\n\n"
        f"**Why it matters:** {meta['why']}\n\n"
        f"**Impact/Interpretation:** {meta['impact']}\n\n"
        f"**Actionable Tip:** {meta['tip']}"
    )

def explain_extraction(name, value):
    if value <= 70:
        status, meaning = "relatively safe", "groundwater use is within sustainable limits"
        impact = "Minimal impact on water table; sustainable for future use."
        tip = "Maintain current practices and consider rainwater harvesting to stay safe."
    elif value <= 100:
        status, meaning = "stressed", "water usage is close to or exceeding recharge capacity"
        impact = "Lowering water tables; increased pumping costs; potential for seasonal scarcity."
        tip = "Reduce water-intensive crops; adopt drip irrigation; implement community-led recharge."
    else:
        status, meaning = "over-exploited", "groundwater is being extracted much faster than it can recharge"
        impact = "Rapidly falling water levels; drying borewells; long-term ecological damage."
        tip = "Urgent: Stop new borewells; shift to millets; mandatory rainwater harvesting."

    return (
        f"**Definition:** Average groundwater extraction of {value}% for {name.title()}.\n\n"
        f"**Why it matters:** It indicates the balance between usage and natural replenishment.\n\n"
        f"**Impact/Interpretation:** This places it in a **{status}** category. {meaning}. {impact}\n\n"
        f"**Actionable Tip:** {tip}"
    )

def get_suggestions(user_input, intent, found_data=None):
    suggestions = ["Conservation tips", "What is an aquifer?", "Show India map"]
    if found_data:
        loc_name = found_data[0]['name'].title()
        suggestions = [f"Why is {loc_name} stressed?", f"Show trend for {loc_name}", f"How to reduce extraction in {loc_name}"]
    elif intent == "WHY":
        suggestions.insert(0, "Compare Punjab and Bihar")
    elif intent == "TIPS":
        suggestions.insert(0, "Search a state like Punjab")
    elif intent == "DEFINITION":
        suggestions.insert(0, "What is a water table?")

    seen = set()
    unique = [s for s in suggestions if s.lower() not in seen and not seen.add(s.lower())]
    return unique[:3]

# -------------------- MAIN API --------------------
class WaterQuery(BaseModel):
    message: str

last_data_cache = {"data": []}

@app.post("/ask")
async def ask_bot(item: WaterQuery, request: Request):
    user_input = item.message.strip()

    # 1. Intent Detection
    intent = IntentDetector.detect(user_input)

    # 2. Query Normalization & Expansion
    norm_query = QueryProcessor.normalize(user_input)
    expanded_query = QueryProcessor.expand(norm_query)

    # 3. YES/NO/CHART Handling
    if norm_query in ["yes", "show chart", "sure", "ok"]:
        if last_data_cache["data"]:
            data = last_data_cache["data"]
            last_data_cache["data"] = []
            return {"text": "Here’s a visual breakdown of the data", "chartData": data, "suggestions": get_suggestions(user_input, intent, data)}
        return {"text": "I don’t have any prepared data yet.", "chartData": [], "suggestions": get_suggestions(user_input, intent)}
    
    if norm_query in ["no", "n", "nope", "stop"]:
        last_data_cache["data"] = []
        return {"text": "No problem! What would you like to do next?", "chartData": [], "suggestions": get_suggestions(user_input, intent)}

    # 4. Retrieval Pipeline
    retriever = request.app.state.retriever
    reranker = request.app.state.reranker

    indices = retriever.get_indices_for_intent(intent)
    threshold = retriever.get_threshold_for_intent(intent)

    # Multi-index Search
    candidates = retriever.search(expanded_query, indices, top_k=10, threshold=threshold * 0.8) # Search more for reranking

    # Reranking
    reranked = reranker.rerank(norm_query, candidates)

    # Filter by threshold
    results = [r for r in reranked if r["rerank_score"] >= threshold]

    # Handling Uncertainty
    uncertainty_note = ""
    if not results and reranked and reranked[0]["rerank_score"] >= threshold * 0.7:
        results = [reranked[0]]
        uncertainty_note = "_I'm not entirely sure, but this might be what you're looking for:_\n\n"

    if results:
        best_match = results[0]["name"]
        match_idx = results[0]["index"]

        # Grounding Statements
        grounding = "\n\n**Source:** Data aggregated from Central Ground Water Board (CGWB) 2022 Assessment."

        # Branch based on index using elif for efficiency
        if match_idx == "causes":
            img_url = await run_in_threadpool(get_image_url, f"{best_match} groundwater stress")
            return {
                "text": f"{uncertainty_note}### Why is **{best_match.title()}** stressed?\n\n{WHY_MAP.get(best_match.lower(), results[0]['name'])}{grounding}",
                "chartData": [], "imageUrl": img_url, "suggestions": get_suggestions(user_input, intent)
            }

        elif match_idx == "concepts":
            img_url = await run_in_threadpool(get_image_url, best_match)
            # Find the full definition (concatenating chunks if it's a key)
            definition = ""
            if best_match.lower() in KNOWLEDGE_BASE:
                definition = " ".join(KNOWLEDGE_BASE[best_match.lower()])
            else:
                definition = best_match # It was a chunk itself

            layered_text = format_layered_response(best_match, definition)
            return {
                "text": f"{uncertainty_note}### {best_match.title()}\n\n{layered_text}{grounding}",
                "chartData": [], "imageUrl": img_url, "suggestions": get_suggestions(user_input, intent)
            }

        elif match_idx == "tips":
            img_url = await run_in_threadpool(get_image_url, best_match)
            tip_text = TIPS.get(best_match.lower(), best_match)
            return {
                "text": f"{uncertainty_note}### {best_match.title()} Tip\n\n{tip_text}{grounding}",
                "chartData": [], "imageUrl": img_url, "suggestions": get_suggestions(user_input, intent)
            }

        elif match_idx == "locations":
            # Data Lookup
            found_data = []
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(assessments)")
                    cols = [info[1] for info in cursor.fetchall()]
                    state_col = next((c for c in cols if "state" in c.lower()), "State")
                    dist_col = next((c for c in cols if "district" in c.lower()), "District")
                    block_col = next((c for c in cols if "block" in c.lower() or "taluka" in c.lower()), "Block/Taluka")
                    extract_col = next((c for c in cols if "extraction" in c.lower() or "stage" in c.lower()), "Stage of Ground Water Extraction (%)")

                    seen = set()
                    for res in results[:5]:
                        if res["index"] != "locations": continue
                        name = res["name"]
                        if name.lower() in seen: continue
                        seen.add(name.lower())

                        if name in request.app.state.states_list:
                            cursor.execute(f'SELECT AVG("{extract_col}") FROM assessments WHERE "{state_col}" = ?', (name,))
                        elif name in request.app.state.districts_list:
                            cursor.execute(f'SELECT AVG("{extract_col}") FROM assessments WHERE "{dist_col}" = ?', (name,))
                        else:
                            cursor.execute(f'SELECT "{extract_col}" FROM assessments WHERE "{block_col}" = ?', (name,))

                        val = cursor.fetchone()
                        if val and val[0] is not None:
                            found_data.append({"name": name, "extraction": round(val[0], 2)})

                if found_data:
                    last_data_cache["data"] = found_data
                    unified_responses = []
                    for d in found_data:
                        explanation = explain_extraction(d["name"], d["extraction"])
                        cause_text = f"\n\n**Root Causes:** {WHY_MAP[d['name'].lower()]}" if d['name'].lower() in WHY_MAP else ""
                        contaminant_text = f"\n\n**Note:** Reported high levels of {', '.join(CONTAMINANT_DATA[d['name'].lower()])}." if d['name'].lower() in CONTAMINANT_DATA else ""
                        unified_responses.append(f"### {d['name'].title()}\n{explanation}{cause_text}{contaminant_text}")

                    full_response = "\n\n---\n\n".join(unified_responses)
                    img_url = await run_in_threadpool(get_image_url, f"{found_data[0]['name']} India groundwater")
                    return {
                        "text": f"{uncertainty_note}{full_response}{grounding}\n\nWould you like a chart? (Yes/No)",
                        "chartData": [], "imageUrl": img_url, "suggestions": get_suggestions(user_input, intent, found_data)
                    }
            except Exception as e:
                return {"text": f"Database error: {str(e)}", "chartData": [], "suggestions": get_suggestions(user_input, intent)}

    # Fallback to News
    news = await run_in_threadpool(get_latest_news)
    news_str = "\n".join([f"• {item}" for item in news])
    return {
        "text": f"I couldn't find specific data for your query, but here are the latest groundwater updates:\n\n{news_str}",
        "chartData": [], "suggestions": get_suggestions(user_input, intent)
    }

@app.get("/get-news")
async def get_news():
    news = await run_in_threadpool(get_latest_news)
    return {"news": news}

@app.get("/")
def read_root():
    return {"status": "Online", "message": "MyWaterBot AI Groundwater API is running"}
