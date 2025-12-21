from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from thefuzz import process, fuzz

app = FastAPI()

# 1. CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Data Model
class WaterQuery(BaseModel):
    message: str

# 3. Knowledge Base for FAQ
KNOWLEDGE_BASE = {
    "groundwater": "Groundwater is the water found underground in the cracks and spaces in soil, sand and rock.",
    "extraction": "Groundwater extraction is the process of taking water from underground sources for irrigation, drinking, or industrial use.",
    "recharge": "Recharge is the primary method through which water enters an aquifer, usually through rainfall soaking into the ground.",
    "over-exploited": "A region is 'over-exploited' when the amount of water being pumped out is more than the amount of rain soaking back into the ground.",
    "safe": "A 'Safe' category means the groundwater extraction is less than 70% of the available annual recharge.",
    "critical": "A 'Critical' category means extraction is between 90% and 100% of the annual replenishable resource.",
    "stage": "The 'Stage of Extraction' is the percentage of groundwater used compared to what is available."
}

# 4. The Chatbot Logic
@app.post("/ask")
async def ask_bot(item: WaterQuery):
    user_input = item.message.strip().lower()

    # --- A. Identity & Help Questions ---
    help_triggers = ["what is ingres", "who are you", "help", "what can you do", "how to use"]
    if any(q in user_input for q in help_triggers):
        return {
            "text": "I am the INGRES AI assistant. I can help you analyze India's 2022 groundwater data! Try asking:\n\n"
                    "🔹 **Compare**: 'Compare Punjab and Kerala'\n"
                    "🔹 **Trends**: 'Which states have the highest extraction?'\n"
                    "🔹 **Status**: 'Which states are over-exploited?' or 'Extraction above 100'\n"
                    "🔹 **Definitions**: 'What is an aquifer?'",
            "chartData": []
        }
    
    # --- B. Knowledge Base Check ---
    for key, value in KNOWLEDGE_BASE.items():
        if key in user_input:
            return {"text": value, "chartData": []}

    # --- C. Category & Threshold Queries ---
    if any(word in user_input for word in ["over-exploited", "critical", "safe", "above", "more than"]):
        try:
            with sqlite3.connect("./ingres.db") as conn:
                cursor = conn.cursor()
                if "above" in user_input or "more than" in user_input:
                    cursor.execute("""
                        SELECT state, AVG(extraction) as avg_ext 
                        FROM assessments 
                        GROUP BY state HAVING avg_ext > 100
                        ORDER BY avg_ext DESC
                    """)
                    rows = cursor.fetchall()
                    text_prefix = "States where average extraction exceeds 100%:"
                else:
                    cat = "Over-Exploited" if "over" in user_input else "Critical" if "critical" in user_input else "Safe"
                    cursor.execute("""
                        SELECT state, COUNT(*) as count 
                        FROM assessments 
                        WHERE category LIKE ? 
                        GROUP BY state 
                        ORDER BY count DESC LIMIT 5
                    """, (f"%{cat}%",))
                    rows = cursor.fetchall()
                    text_prefix = f"States with the highest number of {cat} blocks:"

                data = [{"name": r[0].capitalize(), "extraction": round(r[1], 2)} for r in rows]
                return {
                    "text": f"{text_prefix} {', '.join([d['name'] for d in data])}.",
                    "chartData": data
                }
        except Exception as e:
            return {"text": f"Error filtering data: {str(e)}", "chartData": []}

    # --- D. Trends (Top 5) ---
    if "top" in user_input or "highest" in user_input:
        try:
            with sqlite3.connect("./ingres.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT state, AVG(extraction) as avg_ext 
                    FROM assessments 
                    GROUP BY state 
                    ORDER BY avg_ext DESC LIMIT 5
                """)
                rows = cursor.fetchall()
                top_data = [{"name": r[0].capitalize(), "extraction": round(r[1], 2)} for r in rows]
                return {
                    "text": f"The top 5 states with the highest extraction are: {', '.join([d['name'] for d in top_data])}.",
                    "chartData": top_data
                }
        except Exception as e:
            return {"text": f"Error fetching trends: {str(e)}", "chartData": []}

    # --- E. Database Logic (Fuzzy Matching) ---
    try:
        with sqlite3.connect("./ingres.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT state FROM assessments")
            all_states = [row[0] for row in cursor.fetchall() if row[0]]
            cursor.execute("SELECT DISTINCT district_name FROM assessments")
            all_districts = [row[0] for row in cursor.fetchall() if row[0]]

            raw_entities = user_input.replace("compare", "").replace("and", " ").replace("vs", " ").split()
            raw_entities = [e.strip() for e in raw_entities if len(e) > 2]
            comparison_data = []

            for entity in raw_entities:
                best_state, state_score = process.extractOne(entity, all_states, scorer=fuzz.token_sort_ratio)
                best_dist, dist_score = process.extractOne(entity, all_districts, scorer=fuzz.token_sort_ratio)

                if state_score > 80:
                    cursor.execute("SELECT extraction FROM assessments WHERE state = ?", (best_state,))
                    rows = cursor.fetchall()
                    avg_val = sum(r[0] for r in rows) / len(rows)
                    comparison_data.append({"name": best_state.capitalize(), "extraction": round(avg_val, 2)})
                elif dist_score > 80:
                    cursor.execute("SELECT extraction FROM assessments WHERE district_name = ?", (best_dist,))
                    row = cursor.fetchone()
                    if row:
                        comparison_data.append({"name": best_dist.capitalize(), "extraction": row[0]})
            
            if comparison_data:
                return {
                    "text": f"Comparing groundwater levels for {', '.join([d['name'] for d in comparison_data])}.",
                    "chartData": comparison_data
                }
    except Exception as e:
        return {"text": f"Error: {str(e)}", "chartData": []}

    return {
        "text": "I couldn't find data for that. Try asking 'Which states are over-exploited?' or 'Compare Punjab and Delhi'.", 
        "chartData": []
    }

@app.get("/")
def read_root():
    return {"status": "INGRES API is running"}