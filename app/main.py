from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import MentalHealthInput, MentalHealthOutput

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "mental_health_pipeline.pkl"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Menteez API", version="1.0")

# Load the full pipeline (preprocessing + model) once at startup
if not MODEL_PATH.exists():
    alt_path = BASE_DIR / "Mental-Health-Score-main" / "app" / "model" / "mental_health_pipeline.pkl"
    if alt_path.exists():
        MODEL_PATH = alt_path

if MODEL_PATH.exists():
    pipeline = joblib.load(MODEL_PATH)
else:
    pipeline = None


def score_to_band(score: float) -> tuple[str, str]:
    if score < 4.0:
        return (
            "Struggling",
            "Your recent habits are showing real strain — consider talking to someone you trust.",
        )
    if score < 6.5:
        return (
            "Managing",
            "You're holding steady but a few habits could use attention — sleep and screen time stand out.",
        )
    if score < 8.5:
        return (
            "Steady",
            "Your rhythm looks balanced. Small, consistent habits are paying off.",
        )
    return (
        "Thriving",
        "Your habits are supporting your wellbeing well right now.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=MentalHealthOutput)
def predict(payload: MentalHealthInput) -> MentalHealthOutput:
    if pipeline is None:
        raise HTTPException(
            status_code=500, detail="Model pipeline is not loaded."
        )

    try:
        input_df = pd.DataFrame([payload.model_dump()])
        raw_score = float(pipeline.predict(input_df)[0])
        score = max(0.0, min(10.0, raw_score))
        band, context = score_to_band(score)
        return MentalHealthOutput(
            mental_health_score=round(score, 1),
            band=band,
            context=context,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Prediction failed: {str(exc)}"
        ) from exc


# Serve frontend from the same app -> no CORS needed
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
