from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# 1. CORS Setup - This allows your Firebase website to talk to Render
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

# 3. The Database Brain
@app.post("/ask")
async def ask_bot(item: WaterQuery):
    user_input = item.message.strip().lower()

    # --- 1. Identity & Name Questions ---
    about_triggers = [
        "what is ingres", 
        "who are you", 
        "what does ingres stand for", 
        "full form of ingres"
    ]
    if any(q in user_input for q in about_triggers):
        return {
            "text": "INGRES stands for **India Groundwater Resource Estimation System**. I am an AI assistant designed to help you explore and understand India's groundwater data from the 2022 assessment.",
            "chartData": []
        }
    
    # --- 2. Purpose & Capability Questions ---
    purpose_triggers = [
        "what it does", 
        "how to use", 
        "capabilities", 
        "purpose of ingres", 
        "how can you help"
    ]
    if any(q in user_input for q in purpose_triggers):
        return {
            "text": "I can analyze groundwater extraction across India! You can ask me to **compare** states or districts (e.g., 'Compare Punjab and Kerala') and I will generate a visual chart for you.",
            "chartData": []
        }
    
    # --- 3. DATABASE LOGIC (Existing comparison code) ---
    conn = sqlite3.connect("ingres.db")
    cursor = conn.cursor()

    # Identify the entities (States/Districts) being compared
    entities = user_input.replace("compare", "").replace("and", " ").replace("vs", " ").split()
    entities = [e.strip() for e in entities if len(e) > 2]

    comparison_data = []

    for entity in entities:
        # Check if the entity is a STATE
        cursor.execute("SELECT extraction FROM assessments WHERE state LIKE ?", (f"%{entity}%",))
        state_rows = cursor.fetchall()
        
        if state_rows:
            avg_extraction = sum(r[0] for r in state_rows) / len(state_rows)
            comparison_data.append({
                "name": entity.capitalize(),
                "extraction": round(avg_extraction, 2)
            })
            continue 

        # If not a state, check if it's a DISTRICT or BLOCK
        cursor.execute("SELECT extraction, block_name FROM assessments WHERE district_name LIKE ? OR block_name LIKE ?", (f"%{entity}%", f"%{entity}%"))
        row = cursor.fetchone()
        if row:
            comparison_data.append({
                "name": entity.capitalize(),
                "extraction": row[0]
            })

    conn.close()

    if not comparison_data:
        return {
            "text": "I couldn't find any data for those names. Try asking 'What is INGRES?' or 'Compare Punjab and Haryana'.", 
            "chartData": []
        }

    return {
        "text": f"Comparing groundwater levels for {', '.join([d['name'] for d in comparison_data])}.",
        "chartData": comparison_data
    }

# This root route helps check if the API is alive
@app.get("/")
def read_root():
    return {"status": "INGRES API is running"}