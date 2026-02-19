# 💧 MyWaterBot

A full-stack AI-powered chatbot for India's groundwater intelligence. MyWaterBot lets users query groundwater extraction levels, trends, and conservation insights across Indian states and districts — using semantic search, a curated knowledge base, and live web news as fallback.

---

## 🌊 What It Does

MyWaterBot is an intelligent water data assistant focused on **India's groundwater crisis**. Users can:

- Ask questions about groundwater extraction levels in any Indian state, district, or block
- Get categorized status: **Safe**, **Semi-Critical**, **Critical**, or **Over-Exploited**
- Understand *why* certain regions are over-exploited
- View historical groundwater extraction **trends** (2017–2022)
- Get water conservation tips and policy insights
- See an **interactive India map** for visual exploration
- Fall back to **live DuckDuckGo news** for queries outside the knowledge base

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python** | Core backend language |
| **FastAPI** | REST API framework with async support |
| **Uvicorn** | ASGI server |
| **HuggingFace Hub** (`sentence-transformers/all-mpnet-base-v2`) | Semantic search & sentence embeddings |
| **SQLite** | Lightweight database for groundwater assessments & trends |
| **Pandas** | CSV ingestion and data processing |
| **BeautifulSoup4** | Web scraping |
| **DuckDuckGo Search** | Live news fallback for out-of-scope queries |
| **Pydantic** | Request/response data validation |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | UI framework |
| **Vite (rolldown-vite)** | Fast build tool & dev server |
| **@react-map/india** | Interactive India map component |
| **Chart.js + react-chartjs-2** | Bar/line charts for extraction data |
| **Recharts** | Additional charting library |
| **CSS** | Custom styling |

### Deployment & Infrastructure
| Technology | Purpose |
|---|---|
| **Firebase Hosting** | Frontend deployment |
| **Render** | Backend API hosting |

---

## ✨ Features

- 🤖 **AI Semantic Search** — Uses `sentence-transformers/all-mpnet-base-v2` via HuggingFace Inference API to match user queries to the closest knowledge base entry or location
- 🗺️ **Interactive India Map** — Visual groundwater status overview across India
- 📊 **Trend Charts** — Historical extraction data (2017, 2020, 2022) for major states
- 📍 **Location-Aware Queries** — Query by state, district, or block name; returns extraction percentage and risk category
- ❓ **"Why" Explanations** — Dedicated explanations for why regions like Punjab, Rajasthan, and Haryana are over-exploited
- 💡 **Conservation Tips** — Actionable water conservation guidance
- 📰 **Live News Fallback** — When a query doesn't match the knowledge base, real-time groundwater news is fetched from DuckDuckGo
- 🔄 **Streaming Responses** — API supports streaming for responsive chat UX
- 🧪 **Unit Tested** — Pytest-based test suite covering knowledge base queries, location queries, news fallback, "why" queries, and map suppression logic
- 🔒 **CORS Enabled** — Configured for secure cross-origin frontend ↔ backend communication

---

## 📁 Project Structure

```
MyWaterBot/
├── Backend/
│   ├── main.py                      # FastAPI app, semantic search, routing logic
│   ├── ingest_data.py               # CSV → SQLite ingestion script
│   ├── test_bot.py                  # Pytest test suite
│   ├── india_groundwater_2022.csv   # Groundwater extraction data (state/district/block)
│   ├── india_groundwater_trends.csv # Historical trends (2017, 2020, 2022)
│   ├── requirements.txt             # Python dependencies
│   └── embeddings.json              # Cached sentence embeddings
├── Frontend/
│   ├── src/                         # React source files
│   ├── index.html                   # App entry point
│   ├── vite.config.js               # Vite configuration
│   ├── package.json                 # Node dependencies
│   ├── firebase.json                # Firebase hosting config
│   └── .firebaserc                  # Firebase project config
└── ingres.db                        # SQLite database file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- A [HuggingFace API token](https://huggingface.co/settings/tokens)

### Backend Setup

```bash
cd Backend

# Install dependencies
pip install -r requirements.txt

# Set your HuggingFace token
export HF_TOKEN=your_hf_token_here

# Ingest groundwater data into SQLite
python ingest_data.py

# Start the API server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend Setup

```bash
cd Frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## 🧪 Running Tests

```bash
cd Backend
pytest test_bot.py -v
```

---

## 📊 Data

The project uses two CSV datasets:

| Dataset | Description |
|---|---|
| `india_groundwater_2022.csv` | Block-level groundwater extraction (%) and category for all major Indian states (2022) |
| `india_groundwater_trends.csv` | State-level historical extraction trends for 2017, 2020, and 2022 |

Categories used:
- ✅ **Safe** — Extraction < 70%
- ⚠️ **Semi-Critical** — Extraction 70–90%
- 🔴 **Critical** — Extraction 90–100%
- 🚨 **Over-Exploited** — Extraction > 100%

---

## 🌐 Deployment

- **Frontend** is deployed via [Firebase Hosting](https://firebase.google.com/docs/hosting)
- **Backend** is deployed on [Render](https://render.com)

---

## 📄 License

This project is open source. Feel free to use, fork, and contribute!

---

> 💧 *"Water is the driving force of all nature." — Leonardo da Vinci*