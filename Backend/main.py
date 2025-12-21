from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from thefuzz import process, fuzz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WaterQuery(BaseModel):
    message: str

last_data_cache = {"data": []}

# -------------------- KNOWLEDGE --------------------
KNOWLEDGE_BASE = {
    "groundwater": "Groundwater is water stored beneath the Earth’s surface in soil and rock formations called aquifers.",
    "extraction": "Groundwater extraction refers to pumping water from underground sources for agriculture, drinking, and industry.",
    "recharge": "Recharge is the process by which rainfall replenishes underground aquifers.",
    "over-exploited": "An over-exploited region extracts more groundwater than it naturally recharges.",
    "safe": "A 'Safe' category means groundwater extraction is below 70% of available recharge.",
    "critical": "A 'Critical' category indicates extraction is between 90% and 100% of recharge capacity.",
    "stage": "Stage of Extraction is the ratio of groundwater used to groundwater available."
}

# -------------------- WHY MAP --------------------
WHY_MAP = {
    # --- NORTH INDIA ---
    "punjab": "High dependence on groundwater for water-intensive crops like paddy and wheat; subsidized electricity leads to over-pumping.",
    "haryana": "Intensive agricultural practices and high irrigation demand for cereal crops beyond natural recharge levels.",
    "delhi": "Massive population density, rapid urbanization, and high concretization preventing rainwater from recharging aquifers.",
    "uttar pradesh": "Heavy agricultural extraction in western districts for sugarcane; industrial pollution in areas like Kanpur (tanneries).",
    "himachal pradesh": "Seasonal water scarcity despite high rainfall due to steep terrain causing quick runoff and limited storage.",
    "chandigarh": "Increasing urban demand and high per-capita water consumption leading to localized stress.",

    # --- WEST INDIA ---
    "rajasthan": "Arid climate, extremely low rainfall, and high evaporation rates; historic reliance on deep fossil water.",
    "gujarat": "Industrial demand and high salinity ingress in coastal areas; intensive irrigation in districts like Mehsana.",
    "maharashtra": "Hard rock (Basalt) terrain with low storage capacity; over-extraction for sugarcane in the Marathwada/Vidarbha belts.",
    "goa": "Increased tourism demand and seasonal salinity intrusion into coastal wells.",

    # --- SOUTH INDIA ---
    "karnataka": "Hard rock terrain (Deccan Trap) with low storage; high borewell density for IT hubs and agriculture.",
    "tamil nadu": "Over-reliance on groundwater due to surface water scarcity and frequent failures of the North-East monsoon.",
    "kerala": "High rainfall but hilly topography leads to quick runoff; increasing contamination of open wells.",
    "andhra pradesh": "Significant extraction for irrigation in drought-prone upland districts like Anantapur.",
    "telangana": "Rapid industrial growth and expansion of irrigation in hard-rock areas with low permeability.",

    # --- EAST & CENTRAL INDIA ---
    "west bengal": "Intensive 'Boro' rice cultivation and geogenic arsenic contamination in the Gangetic delta.",
    "bihar": "Generally 'Safe' but seeing localized stress and arsenic/fluoride issues due to rising domestic demand.",
    "odisha": "Expanding industrial footprint and rising agricultural extraction in the coastal plains.",
    "madhya pradesh": "Hard rock terrain limiting recharge speed; rising demand for wheat and soy cultivation.",
    "chhattisgarh": "Increasing industrial mining activities affecting local water tables and quality.",

    # --- MAJOR CITIES ---
    "bengaluru": "Rapid expansion into peripheral zones without piped water; over-reliance on private tankers and deep borewells.",
    "chennai": "Coastal location leading to seawater intrusion; high domestic demand following reservoir failures (Day Zero risk).",
    "mumbai": "Unregulated borewells in dense settlements (slums) and high concretization limiting natural recharge.",
    "hyderabad": "Fast urbanization and industrial growth placing extreme pressure on the city's hard-rock aquifer system.",
    "kolkata": "Subsidence risks (sinking ground) due to deep extraction from the deltaic silt layers.",
    "ahmedabad": "High industrial water demand and semi-critical levels due to agricultural pumping in the surrounding district.",
    "pune": "Rapid residential growth and significant use of groundwater for construction and domestic backup.",
    "gurugram": "Extremely high construction demand and deep extraction for high-rise residential complexes.",
    "jaipur": "Semi-arid climate coupled with tourism and luxury residential demand exceeding replenishment."
}

# -------------------- EXPLANATION ENGINE --------------------
def explain_extraction(name, value):
    if value <= 70:
        status = "relatively safe"
        meaning = "groundwater use is within sustainable limits"
    elif value <= 100:
        status = "stressed"
        meaning = "water usage is close to or exceeding recharge capacity"
    else:
        status = "over-exploited"
        meaning = "groundwater is being extracted much faster than it can recharge"

    return (
        f"**{name}** has an average groundwater extraction of **{value}%**. "
        f"This places it in a **{status}** category, meaning {meaning}."
    )

# -------------------- MAIN API --------------------
@app.post("/ask")
async def ask_bot(item: WaterQuery):
    user_input = item.message.strip().lower()

    # Normalize terms
    if "overexploited" in user_input or "over exploited" in user_input:
        user_input = user_input.replace("overexploited", "over-exploited").replace("over exploited", "over-exploited")

    SYNONYMS = {"usage": "extraction", "withdrawal": "extraction", "consumption": "extraction"}
    is_usage_query = any(w in user_input for w in ["usage", "extraction"])
    for k, v in SYNONYMS.items():
        user_input = user_input.replace(k, v)

    # YES/NO chart flow
    if user_input in ["yes", "show chart", "sure", "ok"]:
        if last_data_cache["data"]:
            data = last_data_cache["data"]
            last_data_cache["data"] = []
            return {"text": "Here’s a visual breakdown of the data 📊", "chartData": data}
        return {"text": "I don’t have any prepared data yet.", "chartData": []}

    found_data = []
    text_prefix = ""

    try:
        with sqlite3.connect("./ingres.db") as conn:
            cursor = conn.cursor()

            # Top / highest states
            if any(w in user_input for w in ["top", "highest", "over-exploited"]):
                cursor.execute(
                    'SELECT State, AVG("Stage of Ground Water Extraction (%)") '
                    'FROM assessments GROUP BY State '
                    'ORDER BY AVG("Stage of Ground Water Extraction (%)") DESC LIMIT 5'
                )
                rows = cursor.fetchall()
                found_data = [{"name": r[0], "extraction": round(r[1], 2)} for r in rows]
                text_prefix = "the top 5 states by groundwater extraction"

            # Comparison logic (State / District / Block)
            else:
                cursor.execute("SELECT DISTINCT State FROM assessments")
                states = [r[0] for r in cursor.fetchall() if r[0]]
                cursor.execute("SELECT DISTINCT District FROM assessments")
                districts = [r[0] for r in cursor.fetchall() if r[0]]
                cursor.execute('SELECT DISTINCT "Block/Taluka" FROM assessments')
                blocks = [r[0] for r in cursor.fetchall() if r[0]]

                all_entities = states + districts + blocks
                words = user_input.replace("compare", "").replace("vs", " ").replace("and", " ").split()
                seen = set()

                for w in words:
                    if len(w) < 3:
                        continue
                    best, score = process.extractOne(w, all_entities, scorer=fuzz.token_sort_ratio)
                    if score > 80 and best.lower() not in seen:
                        seen.add(best.lower())

                        if best in states:
                            cursor.execute(
                                'SELECT AVG("Stage of Ground Water Extraction (%)") FROM assessments WHERE State = ?',
                                (best,)
                            )
                        elif best in districts:
                            cursor.execute(
                                'SELECT AVG("Stage of Ground Water Extraction (%)") FROM assessments WHERE District = ?',
                                (best,)
                            )
                        else:
                            cursor.execute(
                                'SELECT "Stage of Ground Water Extraction (%)" FROM assessments WHERE "Block/Taluka" = ?',
                                (best,)
                            )

                        val = cursor.fetchone()[0]
                        if val:
                            found_data.append({"name": best, "extraction": round(val, 2)})

                text_prefix = "the groundwater comparison"

    except Exception as e:
        return {"text": f"Database error: {str(e)}", "chartData": []}

    # -------------------- RESPONSE --------------------
    if found_data:
        last_data_cache["data"] = found_data
        explanations = "\n\n".join(
            [explain_extraction(d["name"], d["extraction"]) for d in found_data]
        )

        intro = ""
        if is_usage_query:
            intro = (
                "Groundwater extraction measures how much underground water is being used "
                "relative to what nature can replenish.\n\n"
            )

        return {
            "text": (
                f"{intro}"
                f"Here’s what the data shows for {text_prefix}:\n\n"
                f"{explanations}\n\n"
                f"Would you like to see this as a chart? (Yes/No)"
            ),
            "chartData": []
        }

    # WHY logic
    if "why" in user_input:
        for key, reason in WHY_MAP.items():
            if key in user_input:
                return {
                    "text": (
                        f"### Why is **{key.title()}** facing groundwater stress?\n\n"
                        f"{reason}\n\n"
                        f"**Impact:** Falling water tables, higher pumping costs, "
                        f"and long-term risks to drinking water and agriculture."
                    ),
                    "chartData": []
                }

    # Knowledge fallback
    for key, value in KNOWLEDGE_BASE.items():
        if key in user_input:
            return {"text": value, "chartData": []}

    return {"text": "I couldn’t identify those regions. Try ‘Compare Jaipur and Patna’.", "chartData": []}


@app.get("/")
def read_root():
    return {"status": "INGRES API is running"}
