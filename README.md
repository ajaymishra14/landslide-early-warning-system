# Updated project

Start with **UPGRADE-GUIDE.md** for the new features, setup, Android configuration and deployment limits. See **OBSERVATIONAL-DATA.md** for audited-data validation and candidate training. Earlier design documents below describe intended capabilities; use the upgrade guide for the implemented scope.

# AI-Based Landslide Prediction & Early Warning System (NER-LEWS)
### Autonomous Geotechnical Risk Prediction & Early Warning Command Platform

A complete, production-grade AI-powered geotechnical command center and autonomous early warning platform for vulnerable hill communities across India's **North Eastern Region (NER)**: Assam, Meghalaya, Arunachal Pradesh, Mizoram, Manipur, Nagaland, Tripura, and Sikkim.

---

## 🌟 Key Capabilities

1. **Physics-Informed AI/ML Engine:**
   - Evaluates geotechnical slope stability using the **Mohr-Coulomb failure criterion** and **Caine/Guzzetti Himalayan Intensity-Duration (I-D) thresholds**.
   - Generates calibrated risk scores ($0 - 100$), failure probabilities, risk categories (`LOW`, `MODERATE`, `HIGH`, `SEVERE`), and model confidence scores.
   - Computes SHAP-based feature importance attributions explaining exactly why a slope is at risk.

2. **Autonomous Early Warning System:**
   - Evaluates dynamic environmental readings against **configurable thresholds** (`LOW < 25`, `MODERATE 25–50`, `HIGH 50–75`, `SEVERE > 75`).
   - Generates Standard Operating Procedure (SOP) directives for Incident Commanders, DDMA officers, and Border Roads Organisation (BRO) crews.
   - Built-in audio warning chimes and persistent crisis dispatch tickers for emergency response centers.

3. **High-Resolution GIS Interactive Map:**
   - Live Leaflet map with custom Tactical Dark, Satellite Imagery, and Topographic contours.
   - Color-coded hazard markers with pulsing animations for Severe and High alert zones.
   - Landslide Hazard Zonation (LHZ) buffer rings and Geological Survey of India (GSI) historical incident pins.
   - Slide-over Location Inspector with real-time sensor graphs.

4. **Interactive "What-If" Scenario Simulator:**
   - Real-time sliders allowing judges and emergency planners to simulate cloudbursts, monsoon deluges, and slope saturations.
   - Instant re-calculation of risk scores, radar/gauge meters, factor rankings, and AI geotechnical explanations.

5. **Historical Analysis & Trends:**
   - Catalog of historical North Eastern landslide disasters (2022 Tupul Manipur railway tragedy, 2022 Dima Hasao Assam collapse, 2024 Aizawl quarry failure, 2023 Chungthang Sikkim disaster).
   - Time-series progression curves (Rainfall vs. Risk Score over time).
   - ML model performance report (**ROC-AUC: 0.9940, F1: 0.9504**).

6. **Pluggable Environmental Data Provider:**
   - Live Open-Meteo Weather API integration (real-world precipitation and soil moisture).
   - Dynamic physical sensor simulator fallback for offline demonstrations or simulated sensor networks.

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run unit and API tests
pytest tests/ -v

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/docs`
Health check: `http://localhost:8000/health`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run build   # Production bundle (FastAPI will serve this automatically)
npm run dev     # Or run Vite dev server on port 5173
```
Open `http://localhost:5173` (or `http://localhost:8000` for the unified server).

---

## 🐳 Docker Deployment

The system includes a production multi-stage `Dockerfile` and `docker-compose.yml`:

```bash
# Build and run complete stack (PostgreSQL + Unified FastAPI/React)
docker compose up --build
```
Access the platform at: `http://localhost:8000`

---

## 🌐 Cloud Deployment (Render)

The project includes `render.yaml` infrastructure-as-code for instant zero-config deployment:
1. Connect repository to [Render](https://render.com).
2. Apply Blueprint using `render.yaml`.
3. Render will provision the PostgreSQL database and Dockerized web service automatically.

---

## 🏛 Project Structure

```
landslide-early-warning-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST API endpoints (locations, predict, alerts, etc.)
│   │   ├── core/                # Config, logging, settings
│   │   ├── database/            # SQLAlchemy models, sessions, seed scripts
│   │   ├── models/              # Relational schemas (locations, alerts, predictions)
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Alert engine, prediction service, weather providers
│   │   ├── ml/                  # Feature engineering, dataset, training, inference
│   │   └── main.py              # Application entrypoint & SPA static server
│   ├── tests/                   # Pytest test suite (14 test cases)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Common, dashboard, map, predict, history, admin
│   │   ├── pages/               # Top-level application views
│   │   ├── services/            # REST API client
│   │   ├── types/               # TypeScript interfaces
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── Dockerfile                   # Production multi-stage Dockerfile
├── docker-compose.yml           # Multi-container orchestration (App + PostgreSQL)
├── render.yaml                  # Render Blueprint specification
└── .env.example
```
