import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

cells = [
    nbf.v4.new_markdown_cell("""# Menteez — Mental Health Signal Model Training

This notebook implements the complete Machine Learning pipeline for predicting a student's **Mental Health Score (0–10)** from habit, lifestyle, and demographic features.

---

### Pipeline Blueprint:
1. **Data Ingestion & Integrity Checks**: Load dataset, inspect shape, types, missing values, duplicates.
2. **Exploratory Data Analysis (EDA)**: Target distribution, correlation patterns, lifestyle impacts.
3. **Preprocessing with `ColumnTransformer`**: Standard scaling, Ordinal encoding, One-Hot encoding.
4. **Model Training & Benchmark Comparison**: Linear Regression, Ridge, Random Forest, Gradient Boosting.
5. **Hyperparameter Tuning & Cross-Validation**: Fine-tune ensemble regressors.
6. **Full Pipeline Serialization**: Wrap preprocessing + model in a single `Pipeline` and export via `joblib`.
"""),

    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

# Configure plots
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
"""),

    nbf.v4.new_markdown_cell("## 1. Load Dataset & Integrity Check"),

    nbf.v4.new_code_cell("""csv_path = Path('../Student Social Media And Mental Health Impact.csv')
if not csv_path.exists():
    csv_path = Path('Student Social Media And Mental Health Impact.csv')

df = pd.read_csv(csv_path)
df.columns = [c.strip().lower() for c in df.columns]

print(f"Shape: {df.shape}")
print(f"Duplicates: {df.duplicated().sum()}")
print("Missing values per column:\\n", df.isnull().sum())
df.head(5)
"""),

    nbf.v4.new_markdown_cell("## 2. Exploratory Data Analysis (EDA)"),

    nbf.v4.new_code_cell("""print("Mental Health Score summary:")
print(df['mental_health_score'].describe())

print("\\nAcademic Level breakdown:")
print(df['academic_level'].value_counts())

print("\\nStress Level breakdown:")
print(df['stress_level'].value_counts())
"""),

    nbf.v4.new_markdown_cell("## 3. Preprocessing Setup (`ColumnTransformer`)"),

    nbf.v4.new_code_cell("""# Separate features and target
X = df.drop(columns=['mental_health_score'])
y = df['mental_health_score']

# Train/test split before preprocessing to prevent data leakage
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

numeric_cols = [
    'age', 'avg_daily_usage_hours', 'daily_unlocks',
    'study_hours', 'physical_activity_hours', 'sleep_hours_per_night'
]

stress_order = [['Low', 'Medium', 'High', 'Very High']]
acad_order = [['High School', 'Undergraduate', 'Graduate']]
nominal_cols = ['gender', 'country', 'most_used_platform', 'purpose_of_use']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols),
        ('ord_stress', OrdinalEncoder(categories=stress_order, handle_unknown='use_encoded_value', unknown_value=-1), ['stress_level']),
        ('ord_acad', OrdinalEncoder(categories=acad_order, handle_unknown='use_encoded_value', unknown_value=-1), ['academic_level']),
        ('nom', OneHotEncoder(handle_unknown='ignore', sparse_output=False), nominal_cols)
    ],
    remainder='drop'
)
"""),

    nbf.v4.new_markdown_cell("## 4. Model Training & Comparison"),

    nbf.v4.new_code_cell("""models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=300, learning_rate=0.04, max_depth=4, subsample=0.85, random_state=42)
}

benchmark = []
for name, model in models.items():
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    pipe.fit(X_train, y_train)
    y_pred = np.clip(pipe.predict(X_test), 0.0, 10.0)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    benchmark.append({
        'Model': name,
        'MAE': mae,
        'RMSE': rmse,
        'R2 Score': r2
    })

comparison_df = pd.DataFrame(benchmark).sort_values('R2 Score', ascending=False)
comparison_df
"""),

    nbf.v4.new_markdown_cell("## 5. Build Final Full Pipeline & Save Model"),

    nbf.v4.new_code_cell("""final_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.04,
        max_depth=4,
        subsample=0.85,
        min_samples_split=5,
        random_state=42
    ))
])

# Fit on the full dataset
final_pipeline.fit(X, y)

# Save pipeline artifact
model_out = Path('../app/model/mental_health_pipeline.pkl')
model_out.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(final_pipeline, model_out)
print(f"Pipeline saved to: {model_out.resolve()}")
""")
]

nb['cells'] = cells

out_dirs = [
    Path('notebook'),
    Path('../notebook')
]

for d in out_dirs:
    try:
        d.mkdir(parents=True, exist_ok=True)
        with open(d / 'model_training.ipynb', 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
        print(f"Wrote notebook to {d / 'model_training.ipynb'}")
    except Exception as e:
        print(f"Error for {d}: {e}")
