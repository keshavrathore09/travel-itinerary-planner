# ✈️ Personalized Travel Itinerary Planner
### Skill Wallet Capstone Project 4 — Generative AI | Intelligent SaaS Trip Planning

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![ReportLab](https://img.shields.io/badge/PDF-ReportLab-0077B6)](https://reportlab.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-4285F4?logo=google)](https://ai.google.dev)
[![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA3-FF6B35)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 👨‍💻 Author Details

| Field              | Details                        |
|--------------------|-------------------------------|
| **Name**           | Keshav Rathore                |
| **University**     | Medi-Caps University          |
| **Enrollment No.** | EN23CS301508                  |
| **Platform ID**    | `6ac33976fb8fc7965cd9236d`    |
| **Category**       | Generative AI · Intelligent SaaS Trip Planning |

---

## 🌍 Project Overview

The **Personalized Travel Itinerary Planner** is a full-stack, production-ready SaaS application that harnesses Generative AI to craft hyper-personalised travel experiences. It combines intelligent destination recommendation, geographically-optimised day-wise itinerary generation, interactive vibe customisation, and offline PDF export — all within a single, beautifully styled Streamlit interface.

The app operates in **Demo Mode** (no API key needed) with rich mock data fallback, or connects to **Google Gemini** or **Groq LLaMA3** for AI-generated, real-world plans.

---

## 🗂️ Epic Architecture Breakdown

### Epic 1 — Vibe Coding Scaffolding & Wanderlust UI
- Custom CSS with **Playfair Display** (headings) and **Inter** (body) Google Fonts
- Ocean-to-sunset gradient hero banner with glassmorphism card components
- Responsive slot-row layout for time-block activities
- Animated budget progress bar with colour-coded thresholds (green → amber → red)
- Themed sidebar with deep navy gradient and cyan accent typography
- Streamlit tab system with custom styling for seamless tab navigation

### Epic 2 — Data Persistence Schema (Local SQLite / Session State)
- **SQLite** (`trips.db`) for multi-trip persistence with full CRUD operations
- Schema: `trips(id TEXT PK, name TEXT, destination TEXT, created_at TEXT, preferences TEXT, itinerary TEXT)`
- **Streamlit Session State** for in-memory real-time state across reruns
- Complete trip history viewer with load, delete, and per-trip PDF export
- Zero external database dependencies — SQLite ships with Python standard library

### Epic 3 — Preference Capture & Smart Destination Recommendation
- Comprehensive preference form: destination / vibe toggle, travel dates, duration, budget slider, party type, pace, multi-select interests
- Secure API key input with password masking; graceful fallback to Demo Mode
- **Recommendation engine**: scores destinations against vibe × budget × season × interests
- Top-3 destination cards with emoji, score stars, highlight tags, best season, and estimated trip cost in USD & INR
- One-click destination selection that feeds directly into the itinerary generator

### Epic 4 — Day-Wise Itinerary, Route Clustering & Activity Swap
- **Geographic clustering**: attractions grouped by neighbourhood/zone per day to minimise transit fatigue
- 4 structured time slots per day: Morning Sightseeing → Lunch → Afternoon Leisure → Evening & Dining
- Itemised cost per activity in both USD and INR (live exchange approximation ×83)
- Cumulative budget tracker with animated progress bar vs. budget-level cap
- **Activity Swap engine**: modify individual slots (e.g. "swap museum for outdoor market", "find vegetarian lunch") and regenerate a single day without wiping the rest of the plan
- Whole-trip vibe shift controls (Relaxed / Fast-Paced / Food & Culture)

### Epic 5 — Trip Persistence & PDF Export
- **1-click PDF generation** using ReportLab with A4 layout
- PDF sections:
  - Cover page with destination, generation timestamp
  - Trip overview table (preferences summary)
  - Day-by-day activity tables with USD/INR costs and daily totals
  - Emergency contact checklist (Police, Ambulance, Tourist Police, Indian Embassy, Insurance, personal fields)
  - Branded footer with author & platform details
- Multi-trip history: save, load, delete, and export individual saved trips as PDF

### Epic 6 — Cloud Deployment Documentation
See **Deployment Guide** section below.

### Epic 7 — Testing & Quality Assurance
- Exception handling on all AI calls, DB operations, and PDF generation
- Demo Mode as guaranteed zero-dependency fallback
- Input validation (duration bounds, required field checks)
- Graceful UI error messages with `st.error` / `st.warning` / `st.info`

---

## 🛠️ Tech Stack

| Layer              | Technology                              |
|--------------------|-----------------------------------------|
| **Frontend**       | Streamlit 1.35+ with custom CSS         |
| **AI — Option A**  | Google Gemini 1.5 Flash (`google-generativeai`) |
| **AI — Option B**  | Groq LLaMA3-70B (`groq`)               |
| **PDF**            | ReportLab 4.1+                          |
| **Database**       | SQLite (stdlib) + Streamlit Session State |
| **Language**       | Python 3.9+                             |
| **Deployment**     | Streamlit Community Cloud               |

---

## 📁 Project Structure

```
travel-itinerary-planner/
├── app.py            # Main Streamlit application (all-in-one)
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── trips.db          # Auto-created SQLite database on first run
```

---

## 🚀 Local Setup & Running

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### Step 1 — Clone / Download
```bash
git clone https://github.com/keshavrathore09/travel-itinerary-planner.git
cd travel-itinerary-planner
```

### Step 2 — Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the App
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

### Step 5 — Configure AI (Optional)
- Select **Demo Mode** in the sidebar for a zero-API-key experience with rich mock data.
- Or select **Gemini** / **Groq** and paste your API key for real AI-generated itineraries.

#### Getting a free Gemini API key:
1. Visit [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with a Google account → **Create API Key**

#### Getting a free Groq API key:
1. Visit [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up → **Create API Key**

---

## ☁️ Deployment Guide — Streamlit Community Cloud

### Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Travel Itinerary Planner"
git remote add origin https://github.com/keshavrathore09/travel-itinerary-planner.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and log in.
2. Click **"New app"**.
3. Connect your GitHub repository.
4. Set **Main file path**: `app.py`
5. Click **"Deploy"**.

### Step 3 — Add API Keys as Secrets (Optional)
In the Streamlit Cloud dashboard → **Settings** → **Secrets**, add:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
GROQ_API_KEY   = "your-groq-api-key"
```

> **Note:** The app works fully in **Demo Mode** without any secrets — ideal for public demos.

### Important Deployment Notes
- `trips.db` is ephemeral on Streamlit Cloud (resets on restart). For persistent storage, upgrade to Streamlit Community Cloud with a connected database or use `st.secrets` with an external DB.
- All CSS, fonts, and assets are inline or CDN-loaded — no static file serving needed.
- The app has zero external database dependencies in Demo Mode.

---

## 🎮 How to Use

| Step | Action |
|------|--------|
| 1️⃣ | Open the sidebar and optionally set your AI provider |
| 2️⃣ | Fill in trip preferences (destination/vibe, dates, budget, party, interests) |
| 3️⃣ | Click **🚀 Plan My Trip!** |
| 4️⃣ | **Tab 1**: Get AI-matched destination recommendations |
| 5️⃣ | **Tab 2**: Generate your full day-by-day itinerary with cost tracking |
| 6️⃣ | **Tab 3**: Swap individual activities or shift your overall vibe |
| 7️⃣ | **Tab 4**: Save trip to history, export PDF, or load past trips |

---

## 📸 Feature Highlights

- 🌟 **Smart Recommendations** — Top-3 destinations scored by vibe, budget, season & interests
- 📅 **Geographic Clustering** — Nearby spots grouped per day to reduce travel fatigue
- 💰 **Dual-Currency Tracker** — Live USD & INR estimates with animated budget bar
- 🔀 **Single-Day Swap** — Modify one slot without regenerating the whole trip
- 📄 **Offline PDF** — Full travel guide with emergency contacts, ready for no-internet use
- 🎭 **Demo Mode** — Works out-of-the-box with zero API setup

---

## 📝 License

MIT License — free to use, modify, and distribute with attribution.

---

<div align="center">

**✈️ Personalized Travel Itinerary Planner**  
Skill Wallet Capstone Project 4 | Platform ID: `6ac33976fb8fc7965cd9236d`

Made with ❤️ by **Keshav Rathore** · Medi-Caps University · EN23CS301508

</div>
