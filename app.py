# ============================================================
# Personalized Travel Itinerary Planner
# Skill Wallet Capstone Project 4
# Author: Keshav Rathore | Medi-Caps University | EN23CS301508
# Platform ID: 6ac33976fb8fc7965cd9236d
# ============================================================

import streamlit as st
import json
import re
import io
import os
import sqlite3
import uuid
from datetime import datetime, date, timedelta
from typing import Optional

# ── ReportLab ──────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Optional AI Clients ─────────────────────────────────────
# Support both new google-genai SDK and legacy google-generativeai
GEMINI_AVAILABLE = False
GEMINI_NEW_SDK   = False

try:
    from google import genai as genai_new
    GEMINI_AVAILABLE = True
    GEMINI_NEW_SDK   = True
except ImportError:
    try:
        import google.generativeai as genai_legacy  # type: ignore
        GEMINI_AVAILABLE = True
        GEMINI_NEW_SDK   = False
    except ImportError:
        pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ╔══════════════════════════════════════════════════════════╗
# ║                   PAGE CONFIGURATION                     ║
# ╚══════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="✈️ Travel Itinerary Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ╔══════════════════════════════════════════════════════════╗
# ║               WANDERLUST CSS STYLING                     ║
# ╚══════════════════════════════════════════════════════════╝
WANDERLUST_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --ocean:    #0077b6;
    --sky:      #00b4d8;
    --sand:     #f4a261;
    --sunset:   #e76f51;
    --forest:   #2d6a4f;
    --cream:    #fefae0;
    --card-bg:  rgba(255,255,255,0.92);
    --shadow:   0 8px 32px rgba(0,119,182,0.12);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #0077b6 0%, #00b4d8 40%, #e76f51 100%);
    border-radius: 18px;
    padding: 2.4rem 2rem 2rem 2rem;
    margin-bottom: 1.6rem;
    text-align: center;
    box-shadow: 0 12px 40px rgba(0,119,182,0.25);
}
.hero-banner h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    color: #fff;
    margin: 0 0 0.3rem 0;
    text-shadow: 0 2px 8px rgba(0,0,0,0.18);
}
.hero-banner p {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.90);
    margin: 0;
}

/* Cards */
.card {
    background: var(--card-bg);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin: 0.8rem 0;
    box-shadow: var(--shadow);
    border-left: 5px solid var(--ocean);
    transition: transform 0.2s;
}
.card:hover { transform: translateY(-2px); }

/* Day card */
.day-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0,119,182,0.10);
    border-top: 4px solid var(--ocean);
}
.day-card h3 {
    color: var(--ocean);
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
}

/* Time-slot rows */
.slot-row {
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    padding: 0.55rem 0;
    border-bottom: 1px dashed #e0f0ff;
}
.slot-icon { font-size: 1.4rem; min-width: 2rem; }
.slot-label {
    font-weight: 600;
    color: var(--ocean);
    font-size: 0.82rem;
    min-width: 120px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.slot-content { flex: 1; color: #333; font-size: 0.95rem; }
.slot-cost {
    color: var(--forest);
    font-weight: 600;
    font-size: 0.88rem;
    white-space: nowrap;
}

/* Budget tracker */
.budget-bar-wrap {
    background: #e8f4f8;
    border-radius: 20px;
    height: 14px;
    width: 100%;
    overflow: hidden;
    margin: 0.4rem 0;
}
.budget-bar-fill {
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg, #2d6a4f, #52b788);
    transition: width 0.4s;
}

/* Destination card */
.dest-card {
    background: linear-gradient(135deg, #fff 0%, #f0f9ff 100%);
    border-radius: 14px;
    padding: 1.4rem;
    border: 2px solid transparent;
    background-clip: padding-box;
    box-shadow: 0 4px 20px rgba(0,119,182,0.10);
    text-align: center;
    transition: box-shadow 0.2s;
}
.dest-card:hover { box-shadow: 0 8px 32px rgba(0,119,182,0.20); }
.dest-card h2 { color: var(--ocean); font-family: 'Playfair Display', serif; margin: 0.5rem 0; }
.dest-card .tags span {
    display: inline-block;
    background: var(--ocean);
    color: #fff;
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    font-size: 0.76rem;
    margin: 0.18rem;
    font-weight: 500;
}

/* Metric chip */
.metric-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #e8f4f8;
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--ocean);
    margin: 0.2rem;
}

/* Footer */
.footer {
    margin-top: 2.5rem;
    padding: 1.5rem;
    background: linear-gradient(90deg, #0077b6, #00b4d8);
    border-radius: 14px;
    color: #fff;
    text-align: center;
    font-size: 0.88rem;
}
.footer a { color: #fefae0; }

/* Sidebar tweaks */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d2137 100%);
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #e0f0ff !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f0f9ff;
    border-radius: 12px;
    padding: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    color: #0077b6;
}
.stTabs [aria-selected="true"] {
    background: #0077b6 !important;
    color: #fff !important;
}

/* Streamlit button override */
.stButton > button {
    background: linear-gradient(90deg, #0077b6, #00b4d8);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1.4rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; color: #fff; }
</style>
"""
st.markdown(WANDERLUST_CSS, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════╗
# ║               SESSION STATE INIT                         ║
# ╚══════════════════════════════════════════════════════════╝
def _init_state():
    defaults = {
        "api_provider":      "Demo Mode",
        "api_key":           "",
        "demo_mode":         True,
        "preferences":       {},
        "recommendations":   [],
        "itinerary":         {},
        "trip_history":      [],
        "active_trip_id":    None,
        "swap_instructions": {},
        "budget_tracker":    {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ╔══════════════════════════════════════════════════════════╗
# ║              SQLITE PERSISTENCE (LOCAL)                  ║
# ╚══════════════════════════════════════════════════════════╝
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trips.db")

def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id          TEXT PRIMARY KEY,
            name        TEXT,
            destination TEXT,
            created_at  TEXT,
            preferences TEXT,
            itinerary   TEXT
        )
    """)
    conn.commit()
    return conn

def db_save_trip(name: str, destination: str, preferences: dict, itinerary: dict) -> str:
    trip_id = str(uuid.uuid4())[:8]
    conn = _get_db()
    conn.execute(
        "INSERT INTO trips VALUES (?,?,?,?,?,?)",
        (
            trip_id, name, destination,
            datetime.now().isoformat(),
            json.dumps(preferences),
            json.dumps(itinerary),
        )
    )
    conn.commit()
    conn.close()
    return trip_id

def db_list_trips():
    try:
        conn = _get_db()
        rows = conn.execute(
            "SELECT id, name, destination, created_at FROM trips ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "destination": r[2], "created_at": r[3]} for r in rows]
    except Exception:
        return []

def db_load_trip(trip_id: str):
    try:
        conn = _get_db()
        row = conn.execute(
            "SELECT preferences, itinerary FROM trips WHERE id=?", (trip_id,)
        ).fetchone()
        conn.close()
        if row:
            return json.loads(row[0]), json.loads(row[1])
    except Exception:
        pass
    return None, None

def db_delete_trip(trip_id: str):
    try:
        conn = _get_db()
        conn.execute("DELETE FROM trips WHERE id=?", (trip_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass

# ╔══════════════════════════════════════════════════════════╗
# ║                   MOCK DATA BANK                         ║
# ╚══════════════════════════════════════════════════════════╝
MOCK_DESTINATIONS = {
    "Beach": [
        {
            "city": "Goa, India", "emoji": "🏖️", "score": 97,
            "why": "Perfect for sun-seekers with vibrant nightlife & water sports.",
            "tags": ["Beach", "Nightlife", "Food", "Budget-Friendly"],
            "season": "Nov–Mar", "avg_daily_usd": 45,
        },
        {
            "city": "Bali, Indonesia", "emoji": "🌺", "score": 94,
            "why": "Spiritual retreats, rice terraces, & world-class surf spots.",
            "tags": ["Beach", "Culture", "Adventure", "Wellness"],
            "season": "Apr–Oct", "avg_daily_usd": 60,
        },
        {
            "city": "Phuket, Thailand", "emoji": "🐘", "score": 89,
            "why": "Iconic islands, elephant sanctuaries & street-food paradise.",
            "tags": ["Beach", "Food", "Family", "Moderate"],
            "season": "Nov–Apr", "avg_daily_usd": 55,
        },
    ],
    "Mountains": [
        {
            "city": "Manali, India", "emoji": "🏔️", "score": 96,
            "why": "Snow-capped Himalayas, trekking trails & cozy café culture.",
            "tags": ["Mountains", "Adventure", "Trekking", "Budget"],
            "season": "Oct–Dec & Mar–Jun", "avg_daily_usd": 35,
        },
        {
            "city": "Interlaken, Switzerland", "emoji": "🇨🇭", "score": 93,
            "why": "Skydiving, Swiss Alps & picture-perfect alpine lakes.",
            "tags": ["Mountains", "Adventure", "Luxury", "Romance"],
            "season": "Jun–Sep", "avg_daily_usd": 180,
        },
        {
            "city": "Queenstown, New Zealand", "emoji": "🏂", "score": 91,
            "why": "Adrenaline capital of the world — bungee, jet-boat & skiing.",
            "tags": ["Mountains", "Adventure", "Extreme Sports"],
            "season": "Dec–Feb", "avg_daily_usd": 120,
        },
    ],
    "Cultural": [
        {
            "city": "Kyoto, Japan", "emoji": "⛩️", "score": 98,
            "why": "Ancient temples, tea ceremonies & cherry-blossom serenity.",
            "tags": ["Culture", "History", "Food", "Photography"],
            "season": "Mar–May & Oct–Nov", "avg_daily_usd": 80,
        },
        {
            "city": "Rome, Italy", "emoji": "🏛️", "score": 95,
            "why": "2,000 years of history, pasta perfection & piazza life.",
            "tags": ["History", "Food", "Art", "Architecture"],
            "season": "Apr–Jun & Sep–Oct", "avg_daily_usd": 95,
        },
        {
            "city": "Jaipur, India", "emoji": "🐪", "score": 90,
            "why": "Pink City forts, royal cuisine & vibrant bazaars.",
            "tags": ["Culture", "History", "Food", "Budget"],
            "season": "Oct–Mar", "avg_daily_usd": 30,
        },
    ],
    "Urban": [
        {
            "city": "Tokyo, Japan", "emoji": "🗼", "score": 99,
            "why": "Hyper-modern yet deeply traditional — ramen, neon & zen.",
            "tags": ["Urban", "Food", "Tech", "Nightlife", "Shopping"],
            "season": "Mar–May & Sep–Nov", "avg_daily_usd": 100,
        },
        {
            "city": "New York City, USA", "emoji": "🗽", "score": 96,
            "why": "The city that never sleeps — art, food, culture, fashion.",
            "tags": ["Urban", "Culture", "Nightlife", "Luxury"],
            "season": "Apr–Jun & Sep–Nov", "avg_daily_usd": 200,
        },
        {
            "city": "Singapore", "emoji": "🦁", "score": 93,
            "why": "Garden city with hawker paradise, skyline & clean transit.",
            "tags": ["Urban", "Food", "Family", "Shopping"],
            "season": "Feb–Apr", "avg_daily_usd": 110,
        },
    ],
}

MOCK_ITINERARY_TEMPLATE = {
    "Day 1": {
        "theme": "Arrival & First Impressions",
        "cluster": "City Centre",
        "slots": [
            {"time": "Morning",   "icon": "🌅", "label": "Morning Sightseeing",
             "activity": "Check in & explore the city centre on foot — visit a landmark viewpoint.",
             "cost_usd": 0,  "cost_inr": 0},
            {"time": "Lunch",     "icon": "🍜", "label": "Lunch",
             "activity": "Try a highly-rated local restaurant for an authentic regional lunch.",
             "cost_usd": 12, "cost_inr": 1000},
            {"time": "Afternoon", "icon": "🏛️", "label": "Afternoon Leisure",
             "activity": "Visit the iconic heritage museum or art gallery in the neighbourhood.",
             "cost_usd": 8,  "cost_inr": 660},
            {"time": "Evening",   "icon": "🌆", "label": "Evening & Dining",
             "activity": "Sunset stroll at the waterfront promenade followed by dinner at a rooftop.",
             "cost_usd": 25, "cost_inr": 2075},
        ],
    },
    "Day 2": {
        "theme": "Deep Dive — Culture & Cuisine",
        "cluster": "Old Town Quarter",
        "slots": [
            {"time": "Morning",   "icon": "⛩️", "label": "Morning Sightseeing",
             "activity": "Guided walking tour of the historic old quarter & local markets.",
             "cost_usd": 15, "cost_inr": 1245},
            {"time": "Lunch",     "icon": "🥘", "label": "Lunch",
             "activity": "Street food tour — sample 5 signature local dishes.",
             "cost_usd": 10, "cost_inr": 830},
            {"time": "Afternoon", "icon": "🎨", "label": "Afternoon Leisure",
             "activity": "Workshop: local craft, cooking class, or pottery depending on destination.",
             "cost_usd": 20, "cost_inr": 1660},
            {"time": "Evening",   "icon": "🎭", "label": "Evening & Dining",
             "activity": "Cultural performance / live music evening with dinner pairing.",
             "cost_usd": 30, "cost_inr": 2490},
        ],
    },
    "Day 3": {
        "theme": "Adventure & Nature",
        "cluster": "Outskirts & Nature Zone",
        "slots": [
            {"time": "Morning",   "icon": "🥾", "label": "Morning Sightseeing",
             "activity": "Half-day nature hike, boat tour, or cycling trail — pick your pace.",
             "cost_usd": 18, "cost_inr": 1494},
            {"time": "Lunch",     "icon": "🌿", "label": "Lunch",
             "activity": "Picnic-style lunch at scenic viewpoint or lakeside café.",
             "cost_usd": 9,  "cost_inr": 747},
            {"time": "Afternoon", "icon": "🏊", "label": "Afternoon Leisure",
             "activity": "Swimming, kayaking, or zip-lining (based on destination type).",
             "cost_usd": 22, "cost_inr": 1826},
            {"time": "Evening",   "icon": "🔥", "label": "Evening & Dining",
             "activity": "Bonfire / beachside BBQ dinner with local music.",
             "cost_usd": 20, "cost_inr": 1660},
        ],
    },
    "Day 4": {
        "theme": "Hidden Gems & Local Life",
        "cluster": "Residential & Market District",
        "slots": [
            {"time": "Morning",   "icon": "🛒", "label": "Morning Sightseeing",
             "activity": "Morning visit to the local wet market and neighbourhood bakery.",
             "cost_usd": 5,  "cost_inr": 415},
            {"time": "Lunch",     "icon": "🍱", "label": "Lunch",
             "activity": "Lunch at a family-run restaurant recommended by locals.",
             "cost_usd": 8,  "cost_inr": 664},
            {"time": "Afternoon", "icon": "🏘️", "label": "Afternoon Leisure",
             "activity": "Guided bicycle tour through hidden residential alleys and parks.",
             "cost_usd": 15, "cost_inr": 1245},
            {"time": "Evening",   "icon": "🍷", "label": "Evening & Dining",
             "activity": "Wine and tapas evening at a speakeasy-style rooftop bar.",
             "cost_usd": 28, "cost_inr": 2324},
        ],
    },
    "Day 5": {
        "theme": "Wellness & Reflection",
        "cluster": "Spa & Riverside Zone",
        "slots": [
            {"time": "Morning",   "icon": "🧘", "label": "Morning Sightseeing",
             "activity": "Sunrise yoga session at riverside park or hotel rooftop.",
             "cost_usd": 10, "cost_inr": 830},
            {"time": "Lunch",     "icon": "🥗", "label": "Lunch",
             "activity": "Plant-based café with farm-to-table fresh ingredients.",
             "cost_usd": 14, "cost_inr": 1162},
            {"time": "Afternoon", "icon": "💆", "label": "Afternoon Leisure",
             "activity": "Traditional spa treatment or hot-spring soak.",
             "cost_usd": 35, "cost_inr": 2905},
            {"time": "Evening",   "icon": "🌙", "label": "Evening & Dining",
             "activity": "Farewell dinner at the destination's most iconic fine-dining spot.",
             "cost_usd": 45, "cost_inr": 3735},
        ],
    },
}

EMERGENCY_CONTACTS = [
    ("Police Emergency",         "100 (India) / 911 (US) / 999 (UK) / 112 (EU)"),
    ("Ambulance",                "102 (India) / 911 (US) / 999 (UK) / 112 (EU)"),
    ("Fire Brigade",             "101 (India) / 911 (US)"),
    ("Tourist Police Helpline",  "1363 (India Tourism)"),
    ("Indian Embassy Abroad",    "+91-11-2301-5321 (MEA 24×7)"),
    ("Travel Insurance Hotline", "Check your policy document"),
    ("Local Hospital",           "Research before departure"),
    ("Lost Passport Helpline",   "Contact nearest Indian Consulate"),
]

# ╔══════════════════════════════════════════════════════════╗
# ║                    AI HELPERS                            ║
# ╚══════════════════════════════════════════════════════════╝
def _call_gemini(prompt: str, api_key: str) -> str:
    if GEMINI_NEW_SDK:
        client = genai_new.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    else:
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)
        return resp.text

def _call_groq(prompt: str, api_key: str) -> str:
    client = Groq(api_key=api_key)
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
    )
    return chat.choices[0].message.content

def ai_generate(prompt: str) -> Optional[str]:
    provider = st.session_state.api_provider
    key      = st.session_state.api_key
    try:
        if provider == "Gemini" and GEMINI_AVAILABLE and key:
            return _call_gemini(prompt, key)
        if provider == "Groq" and GROQ_AVAILABLE and key:
            return _call_groq(prompt, key)
    except Exception as e:
        st.warning(f"⚠️ AI call failed ({e}). Falling back to Demo Mode.")
    return None

def _parse_json_block(text: str) -> Optional[dict]:
    """Extract the first JSON object/array from a text string."""
    try:
        match = re.search(r"```json\s*([\s\S]*?)```", text)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if match:
            return json.loads(match.group(1))
    except (json.JSONDecodeError, AttributeError):
        pass
    return None

# ── Recommendation engine ──────────────────────────────────
def get_recommendations(prefs: dict) -> list:
    vibe = prefs.get("vibe", "Cultural")
    if not st.session_state.demo_mode:
        prompt = f"""
You are a travel expert. Recommend 3 destinations for a traveller with these preferences:
Vibe: {vibe}, Budget: {prefs.get('budget')}, Duration: {prefs.get('duration')} days,
Party: {prefs.get('party')}, Interests: {', '.join(prefs.get('interests', []))}.

Return ONLY a JSON array like:
```json
[
  {{
    "city": "City, Country",
    "emoji": "🌟",
    "score": 95,
    "why": "One sentence reason",
    "tags": ["tag1","tag2","tag3"],
    "season": "Best months",
    "avg_daily_usd": 80
  }}
]
```
"""
        raw = ai_generate(prompt)
        if raw:
            result = _parse_json_block(raw)
            if isinstance(result, list) and len(result) > 0:
                return result

    return MOCK_DESTINATIONS.get(vibe, MOCK_DESTINATIONS["Cultural"])

# ── Itinerary engine ───────────────────────────────────────
def _build_itinerary_prompt(
    prefs: dict,
    day_override: Optional[int] = None,
    swap_instruction: Optional[str] = None,
) -> str:
    days   = prefs.get("duration", 3)
    dest   = prefs.get("destination", "a popular destination")
    budget = prefs.get("budget", "Moderate")
    party  = prefs.get("party", "Solo")
    pace   = prefs.get("pace", "Moderate")
    ints   = ", ".join(prefs.get("interests", ["Food", "History"]))

    day_spec  = f"only Day {day_override}" if day_override else f"all {days} days"
    swap_note = (
        f"\nSPECIAL INSTRUCTION for this regeneration: {swap_instruction}"
        if swap_instruction else ""
    )

    return f"""
You are an expert travel planner specialising in personalised itineraries.
Create a detailed day-wise itinerary for {day_spec} in {dest}.
Budget level: {budget}. Travel party: {party}. Pace: {pace}. Interests: {ints}.{swap_note}

Rules:
- Group geographically nearby attractions on the same day (geographic clustering).
- Each day has exactly 4 slots: Morning Sightseeing, Lunch, Afternoon Leisure, Evening & Dining.
- Provide realistic cost estimates in USD and INR (use approx ×83 for USD→INR).

Return ONLY valid JSON — no extra text — like this structure:
```json
{{
  "Day 1": {{
    "theme": "Theme Title",
    "cluster": "Neighbourhood or Zone Name",
    "slots": [
      {{"time":"Morning",   "icon":"🌅","label":"Morning Sightseeing","activity":"...","cost_usd":10,"cost_inr":830}},
      {{"time":"Lunch",     "icon":"🍜","label":"Lunch",              "activity":"...","cost_usd":12,"cost_inr":1000}},
      {{"time":"Afternoon", "icon":"🏛️","label":"Afternoon Leisure",  "activity":"...","cost_usd":8, "cost_inr":660}},
      {{"time":"Evening",   "icon":"🌆","label":"Evening & Dining",   "activity":"...","cost_usd":20,"cost_inr":1660}}
    ]
  }}
}}
```
"""

def generate_itinerary(
    prefs: dict,
    day_override: Optional[int] = None,
    swap_instruction: Optional[str] = None,
) -> dict:
    if not st.session_state.demo_mode:
        prompt = _build_itinerary_prompt(prefs, day_override, swap_instruction)
        raw = ai_generate(prompt)
        if raw:
            result = _parse_json_block(raw)
            if isinstance(result, dict) and len(result) > 0:
                return result

    # Demo fallback — build N days from the rotating template
    days = prefs.get("duration", 3)
    base = {}
    template_keys = list(MOCK_ITINERARY_TEMPLATE.keys())
    for i in range(1, days + 1):
        key = f"Day {i}"
        tpl_key = template_keys[(i - 1) % len(template_keys)]
        tpl = MOCK_ITINERARY_TEMPLATE[tpl_key]
        base[key] = {
            "theme":   tpl["theme"],
            "cluster": tpl["cluster"],
            "slots":   [dict(s) for s in tpl["slots"]],
        }
    return base

# ╔══════════════════════════════════════════════════════════╗
# ║                    PDF GENERATOR                         ║
# ╚══════════════════════════════════════════════════════════╝
def generate_pdf(prefs: dict, itinerary: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"],
        fontSize=24, textColor=colors.HexColor("#0077b6"),
        spaceAfter=6, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#555"),
        spaceAfter=4, alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "SectionStyle", parent=styles["Heading1"],
        fontSize=14, textColor=colors.white,
        backColor=colors.HexColor("#0077b6"),
        spaceBefore=10, spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    day_style = ParagraphStyle(
        "DayStyle", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#0077b6"),
        spaceBefore=12, spaceAfter=4, fontName="Helvetica-Bold",
    )
    normal_style = ParagraphStyle(
        "NormalStyle", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#333"), spaceAfter=4,
    )
    footer_style = ParagraphStyle(
        "FooterStyle", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#888"), alignment=TA_CENTER,
    )

    story = []

    # ── Cover ─────────────────────────────────────────────
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("✈️ Personalized Travel Itinerary", title_style))
    dest = prefs.get("destination") or prefs.get("vibe", "Your Destination")
    story.append(Paragraph(f"🌍 {dest}", subtitle_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        subtitle_style,
    ))
    story.append(HRFlowable(
        width="100%", thickness=2, color=colors.HexColor("#0077b6")
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Trip Overview ──────────────────────────────────────
    story.append(Paragraph("Trip Overview", section_style))
    story.append(Spacer(1, 0.2 * cm))
    overview_data = [
        ["Destination",  dest],
        ["Duration",     f"{prefs.get('duration', '?')} days"],
        ["Travel Dates", f"{prefs.get('start_date', '?')} to {prefs.get('end_date', '?')}"],
        ["Budget Level", prefs.get("budget", "?")],
        ["Travel Party", prefs.get("party", "?")],
        ["Pace",         prefs.get("pace", "?")],
        ["Interests",    ", ".join(prefs.get("interests", []))],
    ]
    tbl = Table(overview_data, colWidths=[5 * cm, 11 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#e8f4f8")),
        ("TEXTCOLOR",     (0, 0), (0, -1), colors.HexColor("#0077b6")),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1),
         [colors.HexColor("#f8fbff"), colors.HexColor("#ffffff")]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#d0e8f0")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.6 * cm))

    # ── Day-by-day ─────────────────────────────────────────
    story.append(Paragraph("Day-by-Day Itinerary", section_style))
    story.append(Spacer(1, 0.2 * cm))

    for day_key, day_data in itinerary.items():
        story.append(Paragraph(
            f"{day_key} — {day_data.get('theme', '')}  "
            f"[Cluster: {day_data.get('cluster', '')}]",
            day_style,
        ))

        slot_rows = [["Time Slot", "Activity", "USD", "INR"]]
        day_total_usd = 0
        day_total_inr = 0
        for slot in day_data.get("slots", []):
            c_usd = slot.get("cost_usd", 0)
            c_inr = slot.get("cost_inr", 0)
            day_total_usd += c_usd
            day_total_inr += c_inr
            slot_rows.append([
                f"{slot.get('icon','')} {slot.get('label','')}",
                slot.get("activity", ""),
                f"${c_usd}",
                f"Rs.{c_inr:,}",
            ])
        slot_rows.append(["", "Day Total", f"${day_total_usd}", f"Rs.{day_total_inr:,}"])

        st_tbl = Table(slot_rows, colWidths=[3.5 * cm, 9 * cm, 2 * cm, 2.5 * cm])
        st_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#0077b6")),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -2),
             [colors.HexColor("#f0f9ff"), colors.HexColor("#ffffff")]),
            ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#d0e8f0")),
            ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#c0d8e8")),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(st_tbl)
        story.append(Spacer(1, 0.4 * cm))

    story.append(PageBreak())

    # ── Emergency Contacts ─────────────────────────────────
    story.append(Paragraph("Emergency Contact Checklist", section_style))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Keep this page handy during your travels. Fill in personal contacts before departure.",
        normal_style,
    ))

    ec_data = [["Service / Contact", "Number / Information"]] + list(EMERGENCY_CONTACTS)
    ec_data += [
        ["Personal Doctor",               "________________________"],
        ["Travel Insurance Policy No.",   "________________________"],
        ["Hotel / Accommodation Contact", "________________________"],
        ["Emergency Contact at Home",     "________________________"],
        ["Nearest Indian Consulate",      "________________________"],
    ]
    ec_tbl = Table(ec_data, colWidths=[7 * cm, 9 * cm])
    ec_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#e76f51")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1),
         [colors.HexColor("#fff5f0"), colors.HexColor("#ffffff")]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#f0c0b0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(ec_tbl)
    story.append(Spacer(1, 1 * cm))

    # ── PDF Footer ─────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0077b6")))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Generated by Personalized Travel Itinerary Planner | "
        "Skill Wallet Capstone Project 4 | "
        "Keshav Rathore - Medi-Caps University - EN23CS301508 | "
        "Platform ID: 6ac33976fb8fc7965cd9236d",
        footer_style,
    ))

    doc.build(story)
    return buf.getvalue()

# ╔══════════════════════════════════════════════════════════╗
# ║                       SIDEBAR                            ║
# ╚══════════════════════════════════════════════════════════╝
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0 0.5rem'>
            <span style='font-size:2.5rem'>✈️</span>
            <h2 style='color:#00b4d8;margin:0.3rem 0 0;font-size:1.1rem'>Travel Planner</h2>
            <p style='color:#7fb8d8;font-size:0.78rem;margin:0'>Capstone Project 4</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        # ── AI Configuration ───────────────────────────────
        st.markdown("### ⚙️ AI Configuration")
        provider_options = ["Demo Mode", "Gemini", "Groq"]
        current_idx = (
            provider_options.index(st.session_state.api_provider)
            if st.session_state.api_provider in provider_options else 0
        )
        provider = st.selectbox(
            "AI Provider",
            provider_options,
            index=current_idx,
            help="Demo Mode uses built-in mock data — no API key required.",
        )
        st.session_state.api_provider = provider
        st.session_state.demo_mode    = (provider == "Demo Mode")

        if provider != "Demo Mode":
            key_label = "Gemini API Key" if provider == "Gemini" else "Groq API Key"
            key = st.text_input(
                key_label,
                value=st.session_state.api_key,
                type="password",
                placeholder="Paste your API key here…",
            )
            st.session_state.api_key = key
            if not key:
                st.warning("⚠️ No API key — falling back to Demo Mode.")
                st.session_state.demo_mode = True
            else:
                st.success("✅ API key set.")
        else:
            st.info("🎭 **Demo Mode** — rich mock data, no API key needed!")

        st.divider()

        # ── Preferences Form ───────────────────────────────
        st.markdown("### 🗺️ Trip Preferences")
        with st.form("preferences_form", clear_on_submit=False):
            dest_type = st.radio(
                "Do you have a specific destination?",
                ["Yes — specific city", "No — suggest by vibe"],
                horizontal=True,
            )

            destination = ""
            vibe = "Cultural"
            if dest_type == "Yes — specific city":
                destination = st.text_input(
                    "🏙️ Destination City / Country",
                    placeholder="e.g. Paris, France",
                )
            else:
                vibe = st.selectbox(
                    "🌊 Travel Vibe",
                    ["Beach", "Mountains", "Cultural", "Urban"],
                )

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "📅 Start Date",
                    value=date.today() + timedelta(days=30),
                    min_value=date.today(),
                )
            with col2:
                duration = st.number_input(
                    "⏱️ Duration (days)",
                    min_value=1, max_value=30, value=3, step=1,
                )

            budget = st.select_slider(
                "💰 Budget Level",
                options=["Budget", "Moderate", "Luxury"],
                value="Moderate",
            )
            party = st.selectbox(
                "👥 Travel Party",
                ["Solo", "Couple", "Family", "Friends"],
            )
            pace = st.select_slider(
                "⚡ Travel Pace",
                options=["Relaxed", "Moderate", "Fast-Paced"],
                value="Moderate",
            )
            interests = st.multiselect(
                "❤️ Interests (select all that apply)",
                ["Food", "Adventure", "History", "Nightlife", "Shopping",
                 "Wellness", "Photography", "Art"],
                default=["Food", "History"],
            )

            submitted = st.form_submit_button(
                "🚀 Plan My Trip!", use_container_width=True
            )

        if submitted:
            end_date = start_date + timedelta(days=int(duration) - 1)
            st.session_state.preferences = {
                "destination": destination if dest_type == "Yes — specific city" else "",
                "vibe":        vibe if dest_type != "Yes — specific city" else "Cultural",
                "start_date":  str(start_date),
                "end_date":    str(end_date),
                "duration":    int(duration),
                "budget":      budget,
                "party":       party,
                "pace":        pace,
                "interests":   interests,
            }
            st.session_state.recommendations = []
            st.session_state.itinerary       = {}
            st.session_state.budget_tracker  = {}
            st.success("✅ Preferences saved! Explore the tabs →")

        # ── Author badge ───────────────────────────────────
        st.divider()
        st.markdown("""
        <div style='font-size:0.78rem;color:#7fb8d8;line-height:1.8'>
            👨‍💻 <b style='color:#e0f0ff'>Keshav Rathore</b><br>
            🎓 Medi-Caps University<br>
            🆔 EN23CS301508<br>
            🏷️ Platform: <code style='color:#90caf9'>6ac33976fb8fc7965cd9236d</code>
        </div>
        """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════╗
# ║            TAB 1 — SMART RECOMMENDATIONS                ║
# ╚══════════════════════════════════════════════════════════╝
def tab_recommendations():
    prefs = st.session_state.preferences

    if not prefs:
        st.markdown("""
        <div class='card' style='text-align:center;padding:2.5rem'>
            <div style='font-size:3.5rem'>🌍</div>
            <h3 style='color:#0077b6;margin:0.8rem 0 0.4rem'>Welcome, Wanderer!</h3>
            <p style='color:#555;max-width:420px;margin:0 auto'>
                Fill in your trip preferences in the sidebar and click
                <b>🚀 Plan My Trip!</b> to unlock your personalised travel experience.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    if prefs.get("destination"):
        st.markdown(f"""
        <div class='card'>
            <h3>📍 Destination Locked In: <span style='color:#0077b6'>{prefs['destination']}</span></h3>
            <p style='color:#555;margin:0'>
                Great choice! Head to the <b>📅 Itinerary</b> tab to generate your personalised day-by-day plan.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("## 🌟 Smart Destination Recommendations")
    st.markdown(
        f"Curated for your **{prefs.get('vibe')} vibe** · **{prefs.get('budget')} budget** · "
        f"**{prefs.get('duration')} days** · interests: **{', '.join(prefs.get('interests', ['travel']))}**"
    )

    if not st.session_state.recommendations:
        with st.spinner("🔍 Matching destinations to your vibe…"):
            st.session_state.recommendations = get_recommendations(prefs)

    recs = st.session_state.recommendations
    cols = st.columns(min(len(recs), 3))

    for i, dest in enumerate(recs[:3]):
        with cols[i]:
            tags_html = " ".join(f"<span>{t}</span>" for t in dest.get("tags", []))
            est_total_usd = dest.get("avg_daily_usd", 60) * prefs.get("duration", 3)
            est_total_inr = est_total_usd * 83

            st.markdown(f"""
            <div class='dest-card'>
                <div style='font-size:3.2rem'>{dest.get('emoji','🌍')}</div>
                <h2>{dest.get('city','')}</h2>
                <div style='font-size:1.4rem;color:#f4a261;margin:0.3rem 0'>
                    {'⭐' * (dest.get('score', 80) // 20)}
                    <span style='font-size:0.88rem;color:#777'>
                        &nbsp;{dest.get('score', 80)}/100
                    </span>
                </div>
                <p style='font-size:0.9rem;color:#555;margin:0.5rem 0 0.8rem'>
                    {dest.get('why','')}
                </p>
                <div class='tags'>{tags_html}</div>
                <div style='margin-top:0.9rem;font-size:0.85rem;color:#333;line-height:1.8'>
                    📅 Best Season: <b>{dest.get('season','Year-round')}</b><br>
                    💰 Est. Total: <b>${est_total_usd:,}</b>
                    (~₹{est_total_inr:,.0f})
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"Select {dest.get('city','').split(',')[0]} →",
                key=f"sel_{i}",
                use_container_width=True,
            ):
                st.session_state.preferences["destination"] = dest.get("city", "")
                st.session_state.recommendations = []
                st.session_state.itinerary       = {}
                st.success(
                    f"✅ {dest.get('city','')} selected! Head to the Itinerary tab."
                )
                st.rerun()

# ╔══════════════════════════════════════════════════════════╗
# ║           TAB 2 — DAY-BY-DAY ITINERARY                 ║
# ╚══════════════════════════════════════════════════════════╝
def _compute_budget_tracker(itinerary: dict) -> dict:
    tracker = {}
    running = 0
    for day_key, day_data in itinerary.items():
        day_total = sum(s.get("cost_usd", 0) for s in day_data.get("slots", []))
        running  += day_total
        tracker[day_key] = {"day_total": day_total, "cumulative": running}
    return tracker

def tab_itinerary():
    prefs = st.session_state.preferences
    if not prefs:
        st.info("👈 Fill in your preferences in the sidebar first.")
        return

    dest = prefs.get("destination") or prefs.get("vibe", "your destination")
    st.markdown(f"## 📅 Day-by-Day Itinerary — {dest}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🎯 Generate Itinerary", use_container_width=True, type="primary"):
            with st.spinner("✨ Building your perfect trip plan…"):
                itinerary = generate_itinerary(prefs)
                st.session_state.itinerary      = itinerary
                st.session_state.budget_tracker = _compute_budget_tracker(itinerary)
            st.success("✅ Itinerary generated!")
            st.rerun()
    with col2:
        if st.session_state.itinerary:
            if st.button("🔄 Regenerate All Days", use_container_width=True):
                with st.spinner("🔄 Refreshing your plan…"):
                    itinerary = generate_itinerary(prefs)
                    st.session_state.itinerary      = itinerary
                    st.session_state.budget_tracker = _compute_budget_tracker(itinerary)
                st.rerun()

    if not st.session_state.itinerary:
        st.markdown("""
        <div class='card' style='text-align:center;padding:2.5rem;margin-top:1rem'>
            <div style='font-size:3rem'>🗺️</div>
            <h3 style='color:#0077b6'>Ready to Build Your Plan!</h3>
            <p style='color:#555'>Click <b>🎯 Generate Itinerary</b> above to craft your personalised day-by-day trip.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    itinerary = st.session_state.itinerary
    tracker   = st.session_state.budget_tracker

    # ── Budget Summary ─────────────────────────────────────
    if tracker:
        last_day  = list(tracker.keys())[-1]
        total_usd = tracker[last_day]["cumulative"]
        total_inr = total_usd * 83
        budget_level = prefs.get("budget", "Moderate")
        daily_cap    = {"Budget": 50, "Moderate": 120, "Luxury": 300}.get(budget_level, 120)
        budget_cap   = daily_cap * prefs.get("duration", 3)
        pct = min(100, int((total_usd / max(budget_cap, 1)) * 100))
        bar_color = (
            "#2d6a4f" if pct < 70
            else ("#f4a261" if pct < 90 else "#e76f51")
        )

        st.markdown(f"""
        <div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem'>
                <span style='font-size:1rem;font-weight:600;color:#0077b6'>
                    💰 Total Estimated Trip Cost
                </span>
                <span style='font-size:1.15rem;font-weight:700;color:#0077b6'>
                    ${total_usd:,} USD &nbsp;|&nbsp; ₹{total_inr:,.0f} INR
                </span>
            </div>
            <div class='budget-bar-wrap'>
                <div class='budget-bar-fill' style='width:{pct}%;background:{bar_color}'></div>
            </div>
            <div style='display:flex;justify-content:space-between;font-size:0.82rem;color:#555;margin-top:0.3rem'>
                <span>Budget utilised: <b style='color:{bar_color}'>{pct}%</b> of {budget_level} estimate</span>
                <span>Budget cap (~{budget_level}): <b>${budget_cap:,}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Day-by-day Cards ───────────────────────────────────
    for day_key, day_data in itinerary.items():
        day_info = tracker.get(day_key, {})
        day_t    = day_info.get("day_total", 0)
        cum_t    = day_info.get("cumulative", 0)

        with st.expander(
            f"📅 {day_key} — {day_data.get('theme', '')}  "
            f"| 📍 {day_data.get('cluster', '')}  "
            f"| 💵 Day: ${day_t}  |  Cumulative: ${cum_t}",
            expanded=True,
        ):
            slots_html = ""
            for slot in day_data.get("slots", []):
                slots_html += f"""
                <div class='slot-row'>
                    <span class='slot-icon'>{slot.get('icon','')}</span>
                    <span class='slot-label'>{slot.get('label','')}</span>
                    <span class='slot-content'>{slot.get('activity','')}</span>
                    <span class='slot-cost'>
                        ${slot.get('cost_usd',0)} / ₹{slot.get('cost_inr',0):,}
                    </span>
                </div>
                """
            st.markdown(f"""
            <div class='day-card'>
                <h3>🗓️ {day_key} &nbsp;
                    <small style='font-size:0.82rem;color:#888;font-weight:400'>
                        📍 Geographic Cluster: {day_data.get('cluster','')}
                    </small>
                </h3>
                {slots_html}
                <div style='margin-top:0.6rem;font-size:0.85rem;color:#0077b6;font-weight:600'>
                    Day Subtotal: ${day_t} USD / ₹{day_t * 83:,} INR
                </div>
            </div>
            """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════╗
# ║          TAB 3 — VIBE CUSTOMISATION & SWAP              ║
# ╚══════════════════════════════════════════════════════════╝
def tab_customise():
    prefs     = st.session_state.preferences
    itinerary = st.session_state.itinerary

    if not itinerary:
        st.markdown("""
        <div class='card' style='text-align:center;padding:2rem'>
            <div style='font-size:2.5rem'>🎨</div>
            <h3 style='color:#0077b6'>Generate an Itinerary First</h3>
            <p style='color:#555'>Head to <b>📅 Itinerary</b> tab, generate your plan, then come back here to customise!</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("## 🎨 Vibe Customization & Dynamic Activity Swap")
    st.markdown(
        "Modify individual day slots without wiping your entire itinerary. "
        "Each regeneration targets only the selected day."
    )

    # ── Single-Day Slot Swap ───────────────────────────────
    st.markdown("### 🔀 Single-Day Activity Swap")
    day_keys     = list(itinerary.keys())
    selected_day = st.selectbox("📅 Select Day to Customise", day_keys)
    day_data     = itinerary[selected_day]

    st.markdown(
        f"**Current plan for _{selected_day}_ — {day_data.get('theme', '')}**  "
        f"| 📍 Cluster: {day_data.get('cluster', '')}"
    )

    col_preview = st.columns(2)
    for idx, slot in enumerate(day_data.get("slots", [])):
        with col_preview[idx % 2]:
            st.markdown(f"""
            <div class='card' style='padding:0.8rem 1rem;margin:0.3rem 0'>
                <b>{slot.get('icon','')} {slot.get('label','')}</b><br>
                <span style='font-size:0.9rem;color:#444'>{slot.get('activity','')}</span><br>
                <span style='font-size:0.82rem;color:#2d6a4f'>
                    💵 ${slot.get('cost_usd',0)} / ₹{slot.get('cost_inr',0):,}
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        slot_to_swap = st.selectbox(
            "🎯 Which time slot to modify?",
            [f"{s.get('icon','')} {s.get('label','')}" for s in day_data.get("slots", [])],
        )
    with col2:
        swap_presets = [
            "Swap museum for outdoor market",
            "Find vegetarian / vegan lunch spot",
            "Replace with an adventure activity",
            "Add a luxury shopping experience",
            "Change to a relaxed café & reading time",
            "Suggest a hidden local gem",
            "Add a photography-friendly spot",
            "Make it family-friendly",
            "Custom instruction…",
        ]
        swap_preset = st.selectbox("⚡ Quick Swap Templates", swap_presets)

    custom_swap = ""
    if swap_preset == "Custom instruction…":
        custom_swap = st.text_input(
            "✏️ Describe your preferred activity",
            placeholder="e.g. I'd prefer a rooftop bar with live jazz instead of the evening restaurant",
        )

    swap_instruction = custom_swap.strip() if custom_swap.strip() else swap_preset

    if st.button(
        f"🔀 Apply Swap & Regenerate {selected_day}",
        use_container_width=True,
        type="primary",
    ):
        day_num = int(selected_day.split()[-1])
        full_instruction = f"For slot '{slot_to_swap}': {swap_instruction}"
        with st.spinner(f"🔄 Regenerating {selected_day}…"):
            new_data = generate_itinerary(
                prefs,
                day_override=day_num,
                swap_instruction=full_instruction,
            )
        if new_data:
            target_key = f"Day {day_num}"
            matched = new_data.get(target_key) or new_data.get(list(new_data.keys())[0])
            if matched:
                st.session_state.itinerary[selected_day] = matched
                # Recompute tracker
                st.session_state.budget_tracker = _compute_budget_tracker(
                    st.session_state.itinerary
                )
                st.success(f"✅ {selected_day} updated with your preference!")
                st.rerun()

    st.divider()

    # ── Whole-Trip Vibe Shift ──────────────────────────────
    st.markdown("### 🌈 Whole-Trip Vibe Shift")
    st.markdown(
        "Change the overall tone of your trip. This updates preferences and clears the current "
        "itinerary — head to **📅 Itinerary** to regenerate."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧘 Make it More Relaxed", use_container_width=True):
            st.session_state.preferences["pace"] = "Relaxed"
            st.session_state.itinerary = {}
            st.success("Pace → Relaxed. Regenerate in Tab 2!")
    with col2:
        if st.button("⚡ Crank Up the Adventure", use_container_width=True):
            st.session_state.preferences["pace"] = "Fast-Paced"
            ints = st.session_state.preferences.get("interests", [])
            if "Adventure" not in ints:
                ints.append("Adventure")
            st.session_state.preferences["interests"] = ints
            st.session_state.itinerary = {}
            st.success("Pace → Fast-Paced + Adventure added. Regenerate in Tab 2!")
    with col3:
        if st.button("🍽️ Focus on Food & Culture", use_container_width=True):
            ints = st.session_state.preferences.get("interests", [])
            for item in ["Food", "History", "Art"]:
                if item not in ints:
                    ints.append(item)
            st.session_state.preferences["interests"] = ints
            st.session_state.itinerary = {}
            st.success("Interests updated! Regenerate in Tab 2.")

# ╔══════════════════════════════════════════════════════════╗
# ║           TAB 4 — TRIP MANAGEMENT & PDF                 ║
# ╚══════════════════════════════════════════════════════════╝
def tab_trips():
    st.markdown("## 💾 Trip Management & Offline PDF Export")

    prefs     = st.session_state.preferences
    itinerary = st.session_state.itinerary

    # ── Save current trip ──────────────────────────────────
    st.markdown("### 📁 Save Current Trip")
    if not itinerary:
        st.info("ℹ️ Generate an itinerary in **📅 Itinerary** tab before saving.")
    else:
        with st.form("save_trip_form"):
            default_name = (
                f"{prefs.get('destination') or prefs.get('vibe','Trip')} "
                f"— {prefs.get('start_date', str(date.today()))}"
            )
            trip_name = st.text_input(
                "Trip Name",
                value=default_name,
                placeholder="My Dream Vacation",
            )
            save_btn = st.form_submit_button(
                "💾 Save Trip to History", use_container_width=True
            )
        if save_btn:
            if trip_name.strip():
                try:
                    trip_id = db_save_trip(
                        trip_name.strip(),
                        prefs.get("destination") or prefs.get("vibe", ""),
                        prefs,
                        itinerary,
                    )
                    st.success(f"✅ Trip saved! Reference ID: `{trip_id}`")
                except Exception as e:
                    st.error(f"❌ Could not save trip: {e}")
            else:
                st.warning("Please enter a trip name.")

    st.divider()

    # ── PDF Export ─────────────────────────────────────────
    st.markdown("### 📄 Export Offline PDF Travel Guide")
    if not itinerary:
        st.info("ℹ️ Generate an itinerary first to enable PDF export.")
    else:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("""
            **Your PDF will include:**
            - 🗺️ Trip overview & preference summary
            - 📅 Full day-by-day itinerary with activity details
            - 💰 Per-activity cost breakdown in USD & INR
            - 🆘 Emergency contact checklist (pre-filled + personal fields)
            - ✅ Branded footer with project & author details
            """)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(
                "📥 Generate & Download PDF",
                use_container_width=True,
                type="primary",
            ):
                with st.spinner("📄 Preparing your offline travel guide…"):
                    try:
                        pdf_bytes = generate_pdf(prefs, itinerary)
                        dest_slug = (
                            (prefs.get("destination") or prefs.get("vibe", "trip"))
                            .replace(" ", "_")
                            .replace(",", "")
                        )
                        fname = f"itinerary_{dest_slug}_{date.today()}.pdf"
                        st.download_button(
                            label="⬇️ Download PDF Now",
                            data=pdf_bytes,
                            file_name=fname,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        st.success("✅ PDF ready! Click the download button.")
                    except Exception as e:
                        st.error(f"❌ PDF generation failed: {e}")

    st.divider()

    # ── Trip History ───────────────────────────────────────
    st.markdown("### 🕰️ Saved Trip History")
    trips = db_list_trips()

    if not trips:
        st.markdown("""
        <div class='card' style='text-align:center;padding:2rem'>
            <div style='font-size:2.5rem'>📭</div>
            <h4 style='color:#0077b6;margin:0.5rem 0'>No Saved Trips Yet</h4>
            <p style='color:#555;margin:0'>Save a trip above to build your travel archive.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"**{len(trips)} trip(s) saved in your archive:**")
        for trip in trips:
            created_str = trip["created_at"][:16].replace("T", " ")
            with st.expander(
                f"✈️ {trip['name']}  |  📍 {trip['destination']}  |  🕐 {created_str}  |  ID: `{trip['id']}`"
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(
                        "📂 Load Trip",
                        key=f"load_{trip['id']}",
                        use_container_width=True,
                    ):
                        lp, li = db_load_trip(trip["id"])
                        if lp and li:
                            st.session_state.preferences    = lp
                            st.session_state.itinerary      = li
                            st.session_state.budget_tracker = _compute_budget_tracker(li)
                            st.success(f"✅ '{trip['name']}' loaded!")
                            st.rerun()
                        else:
                            st.error("Could not load trip data.")
                with col2:
                    if st.button(
                        "🗑️ Delete Trip",
                        key=f"del_{trip['id']}",
                        use_container_width=True,
                    ):
                        db_delete_trip(trip["id"])
                        st.warning(f"Trip `{trip['id']}` deleted.")
                        st.rerun()
                with col3:
                    if st.button(
                        "📄 Export PDF",
                        key=f"pdf_{trip['id']}",
                        use_container_width=True,
                    ):
                        t_prefs, t_itin = db_load_trip(trip["id"])
                        if t_prefs and t_itin:
                            try:
                                pdf_bytes = generate_pdf(t_prefs, t_itin)
                                st.download_button(
                                    label="⬇️ Download",
                                    data=pdf_bytes,
                                    file_name=f"trip_{trip['id']}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_{trip['id']}",
                                    use_container_width=True,
                                )
                            except Exception as e:
                                st.error(f"PDF error: {e}")

# ╔══════════════════════════════════════════════════════════╗
# ║                      MAIN APP                            ║
# ╚══════════════════════════════════════════════════════════╝
def main():
    # ── Hero Banner ────────────────────────────────────────
    st.markdown("""
    <div class='hero-banner'>
        <h1>✈️ Personalized Travel Itinerary Planner</h1>
        <p>
            AI-powered trip planning &nbsp;·&nbsp; Smart destination matching
            &nbsp;·&nbsp; Day-wise geo-clustered itineraries &nbsp;·&nbsp; Offline PDF export
        </p>
    </div>
    """, unsafe_allow_html=True)

    render_sidebar()

    # ── Status chips ───────────────────────────────────────
    prefs = st.session_state.preferences
    mode_badge = (
        "🎭 Demo Mode"
        if st.session_state.demo_mode
        else f"🤖 {st.session_state.api_provider} AI"
    )

    if prefs:
        dest_display = prefs.get("destination") or prefs.get("vibe", "Not set")
        itinerary_badge = (
            f"✅ {len(st.session_state.itinerary)} days planned"
            if st.session_state.itinerary
            else "⏳ No itinerary yet"
        )
        st.markdown(f"""
        <div style='display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem'>
            <span class='metric-chip'>📍 {dest_display}</span>
            <span class='metric-chip'>📅 {prefs.get('duration','?')} days</span>
            <span class='metric-chip'>💰 {prefs.get('budget','?')}</span>
            <span class='metric-chip'>👥 {prefs.get('party','?')}</span>
            <span class='metric-chip'>⚡ {prefs.get('pace','?')}</span>
            <span class='metric-chip'>{mode_badge}</span>
            <span class='metric-chip'>{itinerary_badge}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='margin-bottom:1rem'>
            <span class='metric-chip'>{mode_badge}</span>
            <span class='metric-chip'>👈 Set preferences in sidebar</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌟 Destinations",
        "📅 Itinerary",
        "🎨 Customise",
        "💾 Trips & PDF",
    ])
    with tab1:
        tab_recommendations()
    with tab2:
        tab_itinerary()
    with tab3:
        tab_customise()
    with tab4:
        tab_trips()

    # ── Footer ─────────────────────────────────────────────
    st.markdown("""
    <div class='footer'>
        ✈️ <b>Personalized Travel Itinerary Planner</b>
        &nbsp;|&nbsp; Skill Wallet Capstone Project 4
        &nbsp;|&nbsp; Generative AI · Intelligent SaaS Trip Planning<br>
        👨‍💻 <b>Keshav Rathore</b> &nbsp;·&nbsp; Medi-Caps University
        &nbsp;·&nbsp; EN23CS301508
        &nbsp;|&nbsp; Platform ID:
        <code style='color:#fefae0;background:rgba(255,255,255,0.15);
        padding:0.1rem 0.4rem;border-radius:4px'>6ac33976fb8fc7965cd9236d</code>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
