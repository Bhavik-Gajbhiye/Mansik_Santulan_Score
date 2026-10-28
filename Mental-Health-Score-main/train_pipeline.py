"""
Menteez ML Training Pipeline
Trains a complete scikit-learn Pipeline (preprocessing + GradientBoosting/RandomForest Regressor)
on student habit data and saves the pipeline for FastAPI serving.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler


def load_and_prep_data(csv_path: str | Path) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(csv_path)
    # Standardize columns to lowercase matching Pydantic schema
    df.columns = [c.strip().lower() for c in df.columns]

    # Deduplicate and clean
    df = df.drop_duplicates().reset_index(drop=True)

    X = df.drop(columns=["mental_health_score"])
    y = df["mental_health_score"]
    return X, y


def build_preprocessor() -> ColumnTransformer:
    numeric_cols = [
        "age",
        "avg_daily_usage_hours",
        "daily_unlocks",
        "study_hours",
        "physical_activity_hours",
        "sleep_hours_per_night",
    ]

    stress_order = [["Low", "Medium", "High", "Very High"]]
    acad_order = [["High School", "Undergraduate", "Graduate"]]

    nominal_cols = ["gender", "country", "most_used_platform", "purpose_of_use"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            (
                "ord_stress",
                OrdinalEncoder(
                    categories=stress_order,
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
                ["stress_level"],
            ),
            (
                "ord_acad",
                OrdinalEncoder(
                    categories=acad_order,
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
                ["academic_level"],
            ),
            (
                "nom",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                nominal_cols,
            ),
        ],
        remainder="drop",
    )
    return preprocessor


def train_pipeline(csv_path: str | Path, model_save_paths: list[Path]):
    print(f"Loading data from {csv_path}...")
    X, y = load_and_prep_data(csv_path)
    print(f"Data shape: {X.shape}, Target range: [{y.min()}, {y.max()}]")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessor = build_preprocessor()

    base_model = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.04,
        max_depth=4,
        subsample=0.85,
        min_samples_split=5,
        random_state=42,
    )

    full_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("regressor", base_model),
        ]
    )

    print("Fitting full pipeline...")
    full_pipeline.fit(X_train, y_train)

    y_pred = full_pipeline.predict(X_test)
    y_pred_clipped = np.clip(y_pred, 0.0, 10.0)

    mae = mean_absolute_error(y_test, y_pred_clipped)
    rmse = root_mean_squared_error(y_test, y_pred_clipped)
    r2 = r2_score(y_test, y_pred_clipped)

    print("\n--- Model Evaluation on Test Set ---")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r2:.4f}")

    # Test with sample input row
    sample_row = pd.DataFrame(
        [
            {
                "age": 21,
                "gender": "Female",
                "country": "India",
                "academic_level": "Undergraduate",
                "most_used_platform": "Instagram",
                "purpose_of_use": "Entertainment",
                "avg_daily_usage_hours": 4.5,
                "daily_unlocks": 55,
                "study_hours": 5.0,
                "physical_activity_hours": 1.5,
                "sleep_hours_per_night": 7.5,
                "stress_level": "Medium",
            }
        ]
    )
    sample_pred = full_pipeline.predict(sample_row)[0]
    print(f"\nSample prediction for balanced student: {sample_pred:.2f} / 10")

    for save_path in model_save_paths:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(full_pipeline, save_path)
        print(f"Saved pipeline to: {save_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    csv_file = base_dir / "Student Social Media And Mental Health Impact.csv"
    if not csv_file.exists():
        csv_file = (
            base_dir.parent / "Student Social Media And Mental Health Impact.csv"
        )

    targets = [
        base_dir / "app" / "model" / "mental_health_pipeline.pkl",
        base_dir.parent / "app" / "model" / "mental_health_pipeline.pkl",
    ]

    train_pipeline(csv_file, targets)
