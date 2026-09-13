# CropGuard AI

**AI-powered Early Crop Disease & Pest Surveillance System**

Prototype for **Smart India Hackathon 2026**  
Problem: *Early detection and management of crop diseases and pest infestations*

> This is a **local hackathon MVP**. It is not a government system, is not officially approved, and does not show live government surveillance data.

---

## Problem statement

Farmers often notice disease and pests only after visible damage has spread. Extension staff cannot visit every farm. Weather, crop stage, variety and local history all change outbreak risk. Incorrect pesticide use raises cost and residue concerns. Officers need a geographic view of emerging problems, plus follow-up after advice is given.

CropGuard AI supports a shift from **reactive spraying** to **early detection → risk prediction → IPM action → expert validation → monitoring**.

---

## Features

- Farmer image screening (JPG/PNG) with confidence bands  
- Labelled **Demo Mode** if no trained model or weather API is available  
- Open-Meteo weather with automatic fallback  
- Transparent prototype **risk score** (weather + stage + soil + local history)  
- IPM advisories from a JSON knowledge base (**no invented pesticide doses or brands**)  
- SQLite case store, expert review, lab referral records, follow-up timeline  
- Maharashtra hotspot map (Folium) with DBSCAN clustering  
- Officer dashboard: KPIs, charts, surveillance table  
- English / मराठी / हिन्दी UI strings  
- Optional browser text-to-speech for the advisory  

---

## Architecture (MVP vs future)

**This MVP:** one Streamlit app + SQLite + JSON/CSV config.

**Intended later scale:** Farmer app → API gateway → image processing → CV model → risk engine (weather, crop, soil, history) → PostGIS → GIS hotspots → advisory engine → expert validation → agriculture dashboard.

Everything above is collapsed into `streamlit run app.py` for the hackathon.

---

## Tech stack

Python, Streamlit, optional PyTorch/torchvision, OpenCV/NumPy, Pandas, scikit-learn, Plotly, Folium, Requests, SQLite, JSON/CSV.

No React, Flutter, Kubernetes, Postgres, Redis, or paid APIs are required.

---

## Installation

```text
python -m venv .venv
```

**Windows**

```text
.venv\Scripts\activate
pip install -r requirements-streamlit.txt
```

**Linux / macOS**

```text
source .venv/bin/activate
pip install -r requirements-streamlit.txt
```

PyTorch is optional. If `pip install torch` is slow or fails, the app still runs in **Demo Mode** (image screening uses a labelled demo predictor).

A lighter install without PyTorch:

```text
pip install streamlit numpy pandas scikit-learn plotly folium streamlit-folium requests Pillow opencv-python-headless
```

---

## Running locally

From the project folder:

```text
streamlit run app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

---

## Demo Mode

On startup the sidebar shows **Demo Mode: ON**.

The app works **without internet**, without a `.pt` model, and without a remote database.

Simulated records are labelled:

**SIMULATED DEMO DATA — NOT REAL GOVERNMENT SURVEILLANCE DATA**

### Hackathon walkthrough

1. Open CropGuard AI.  
2. Go to **Farmer Detection**.  
3. Crop **Tomato**, stage **Fruiting**, location **Nashik**.  
4. Upload any tomato/leaf JPG or PNG.  
5. Demo screening typically shows **Tomato Early Blight** at about **87%** (repeatable demo, not a trained field model).  
6. Weather loads from Open-Meteo or **demo weather**.  
7. Risk engine should show **HIGH** with contributing factors.  
8. Read the IPM advisory (no chemical dose).  
9. **Submit Case**.  
10. Open **Surveillance Dashboard** — the case appears on the table/map.  
11. Open **Expert Review**, confirm **Early Blight**.  
12. Status becomes **expert_confirmed**.  
13. Open **Follow-up**, save outcome **Improved**.

---

## Model setup

See `models/README.md`.

- Place `models/cropguard.pt` (MobileNetV2 `state_dict`, with optional `labels` / `num_classes` in the checkpoint).  
- Class names must match `data/diseases.json`.  
- Do **not** claim ImageNet or an unmatched checkpoint as crop-disease accuracy.  
- PlantVillage is a common public research dataset; do not auto-download copyrighted data. Document model name, source, license, input size and classes before any “real inference” demo.

Until a checkpoint is present, the UI shows:

**Demo prediction — replace with trained/open model for production.**

---

## Dataset information

- `data/diseases.json` — crops, varieties, classes  
- `data/crop_profiles.json` — **prototype** susceptibility and stage weights (not validated ratings)  
- `data/advisories.json` — controlled IPM text  
- `data/demo_cases.csv` — simulated Maharashtra cases used to seed SQLite  
- Uploads: `data/uploads/` (filenames only in the UI)

---

## Project structure

```text
CropGuard/
├── app.py                 # Home
├── database.py            # SQLite
├── requirements.txt
├── README.md
├── models/README.md
├── services/              # detection, weather, risk, advisory, GIS, i18n
├── pages/                 # Farmer, Risk, Expert, Dashboard, Follow-up, About
├── data/                  # JSON, CSV, uploads, cropguard.db
├── utils/
└── tests/test_mvp.py
```

---

## Tests

```text
python tests/test_mvp.py
```

Covers demo prediction, weather fallback, risk scoring, advisory JSON, SQLite insert/review, hotspots, and i18n.

---

## Limitations

- Demo predictor is not a trained field diagnostic unless you add a matching open model.  
- Risk weights need local agronomic calibration.  
- No live laboratory, SMS, or government data feed.  
- Long advisory paragraphs stay in English on purpose (safety wording); UI chrome is translated.  
- Nutrient deficiency, drought, heat and chemical injury can look like disease — experts/labs remain essential.  
- The app never invents pesticide brands, doses, concentrations or mixing instructions.

---

## Future improvements

- PlantVillage-compatible open weights with documented license  
- District-calibrated epidemiological models  
- Offline mobile capture (sync later)  
- PostGIS + official GIS layers  
- SMS/IVR for low-smartphone users  
- Human-reviewed translation of full IPM sheets  
- Active learning from expert-confirmed images (manual retraining, not auto-retrain in the field)

---

## Safety disclaimer

This prototype provides decision support and does not replace diagnosis by qualified agricultural experts or laboratories. Always follow locally approved agricultural recommendations and product labels.
