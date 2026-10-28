# Menteez — Student Wellness Analytics & Mental Health Signal

**Menteez** is an editorial wellness web application designed for students. By entering routine daily lifestyle and digital habits (screen time, phone unlocks, sleep, study hours, physical activity, and stress), students receive an instant, non-clinical predicted **Mental Health Signal Score (0–10)** powered by a trained scikit-learn Machine Learning pipeline served via FastAPI.

---

## 🎨 Visual Design System

The application features a warm, calming pastel wellness aesthetic:
- **Background**: Soft Cream (`#F3E7DC` / `#F6ECE3`)
- **Card Accents**: Lavender (`#C9CBEF`), Sage Mint (`#BFE3D0`), Peach (`#F1D6C4`), Yellow (`#F0D876`)
- **Typography**: Display serif (*Fraunces*) + Modern sans-serif (*Plus Jakarta Sans*, *Inter*)
- **Visual Elements**:
  - Circular Donut Progress Ring (0–10 score mapped to 0–100%)
  - Segmented stress control pills (Low, Medium, High, Very High)
  - Ambient floating pastel blobs and minimalist single-line botanical / meditation art doodles
  - Bubble cluster factor badges (Mood, Sleep, Calm)
  - 4-Petal rounded diamond branding

---

## 📁 Repository Structure

```
menteez/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app (API routes + static frontend mounting)
│   ├── schemas.py                       # Pydantic v2 schemas (MentalHealthInput, MentalHealthOutput)
│   ├── model/
│   │   └── mental_health_pipeline.pkl   # Serialized scikit-learn Pipeline (preprocessing + GradientBoosting)
│   └── static/
│       ├── favicon.svg                  # Brand logo mark
│       ├── index.html                   # High-fidelity pastel UI
│       ├── style.css                    # Design system styling & responsive layout
│       └── script.js                    # Form validation, API calls, donut ring animation
├── notebook/
│   └── model_training.ipynb             # ML training walkthrough (EDA, benchmark, tuning, export)
├── train_pipeline.py                    # Standalone reproducible model training script
├── Student Social Media And Mental Health Impact.csv  # Dataset (5,000 student records)
├── requirements.txt                     # Python dependencies
└── README.md                            # Documentation
```

---

## 🚀 Quick Start (Local Run)

### 1. Clone & Setup Environment
```bash
# Create virtual environment (optional)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. (Optional) Train/Re-train the ML Pipeline
```bash
python train_pipeline.py
```

### 3. Run FastAPI Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at: **`http://localhost:8000`**

---

## 🌐 API Reference

### 1. `GET /health`
Returns service status.
```json
{
  "status": "ok"
}
```

### 2. `POST /predict`
Evaluates student habits and returns score, band, and supportive feedback.

**Sample Request Body:**
```json
{
  "age": 21,
  "gender": "Female",
  "country": "India",
  "academic_level": "Undergraduate",
  "most_used_platform": "Instagram",
  "purpose_of_use": "Entertainment",
  "avg_daily_usage_hours": 4.5,
  "daily_unlocks": 60,
  "study_hours": 5.0,
  "physical_activity_hours": 1.5,
  "sleep_hours_per_night": 7.5,
  "stress_level": "Medium"
}
```

**Sample Response (200 OK):**
```json
{
  "mental_health_score": 7.1,
  "band": "Steady",
  "context": "Your rhythm looks balanced. Small, consistent habits are paying off."
}
```

---

## ☁️ Deployment (Render / Cloud)

Menteez is pre-configured as a single unified service (FastAPI serves both API and static frontend from the same origin, eliminating CORS issues).

- **Environment**: Python 3.11+
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## ⚠️ Disclaimer
*Built for informational and habit-awareness purposes only — this is not a clinical diagnosis. If you are experiencing distress, please reach out to a trusted counselor or healthcare professional.*
