# Model Card — SCOBY Watch ML Baseline

## 1. Summary

The final SCOBY Watch model is:

```text
GradientBoostingClassifier
```

The model is used as a controlled rule-label approximation baseline.

The model is not a replacement for Rule Model v1.1 and is not an independent
biological fermentation predictor.

---

## 2. Model Identity

| Field | Value |
|---|---|
| Model | Gradient Boosting Classifier |
| Library | scikit-learn |
| Artifact baseline version | scikit-learn 1.6.1 |
| Random state | 42 |
| Training data | SCOBY Watch synthetic dataset |
| Training rows | 3,920 |
| Test rows | 980 |
| Training batches | 280 |
| Test batches | 70 |
| Batch overlap | 0 |
| Split method | GroupShuffleSplit by `batch_id` |
| Target | `expected_status` |
| Output classes | 6 |

---

## 3. Model Purpose

The model is used to validate:

- feature preparation;
- categorical encoding;
- model training;
- grouped evaluation;
- model serialization;
- model loading;
- probability output;
- Flask inference;
- Node-RED integration;
- hybrid conflict handling.

The model is not intended to prove that machine learning is superior to
direct rule execution.

---

## 4. Features

Required feature order:

```text
recipe_id_encoded
tea_type_encoded
sugar_g_per_l
starter_ml
water_volume_l
day
room_temp_c
humidity_percent
ph
brix
```

The feature order is stored in:

```text
models/scoby_watch_feature_columns.pkl
```

A feature-order mismatch can produce incorrect predictions without a clear
runtime error. Therefore, the API must always use the saved feature list.

---

## 5. Encoders

Encoder artifact:

```text
models/scoby_watch_label_encoders.pkl
```

Available encoders:

```text
recipe_id
recipe_name
tea_type
risk_flag
expected_status
```

Main categories:

```text
recipe_id:
R1, R2, R3, R4, R5, R6, R7

tea_type:
black_tea, green_tea, oolong_mixed

expected_status:
balanced
manual_check
still_sweet
temperature_warning
too_early
too_sour
```

New categories not present in the encoders do not yet have an official
inference contract.

---

## 6. Model Configuration

Gradient Boosting configuration:

```text
learning_rate = 0.1
n_estimators = 100
max_depth = 3
subsample = 1.0
max_features = None
random_state = 42
```

No hyperparameter optimization was performed for the final experiment.

Candidate models:

| Model | Main configuration |
|---|---|
| Decision Tree | `max_depth=8`, `random_state=42` |
| Random Forest | `n_estimators=150`, `max_depth=12`, `random_state=42` |
| Gradient Boosting | scikit-learn defaults with `random_state=42` |
| KNN | `n_neighbors=7`, StandardScaler |
| Logistic Regression | `max_iter=1500`, StandardScaler |

---

## 7. Evaluation Strategy

The final evaluation uses:

```text
GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)
```

Grouping variable:

```text
batch_id
```

Split contract:

```text
training rows = 3,920
test rows = 980
training batches = 280
test batches = 70
batch overlap = 0
```

The initial random-row split remains available as a historical experiment
under:

```text
experiments/random_split_baseline.py
```

The random-row split is not the authoritative paper result because
observations from the same batch can appear in both train and test subsets.

---

## 8. Final Results

| Metric | Value |
|---|---:|
| Accuracy | 0.995918 |
| Weighted F1-score | 0.995921 |

The high score is expected because the target is generated using
deterministic, nonlinear, axis-aligned threshold rules.

The result shows that the model can approximate rule-generated labels under a
batch-aware split.

The result does not demonstrate:

- biological understanding;
- real-world fermentation generalization;
- calibrated uncertainty;
- food-safety validity;
- superiority over direct rule execution.

---

## 9. Artifacts

```text
models/
├── scoby_watch_best_group_split_model.pkl
├── scoby_watch_label_encoders.pkl
├── scoby_watch_feature_columns.pkl
└── metadata.json
```

Artifact purposes:

| File | Purpose |
|---|---|
| model `.pkl` | final classifier |
| label encoders `.pkl` | categorical and target mappings |
| feature columns `.pkl` | inference feature order |
| `metadata.json` | configuration, split, classes, and metrics |

---

## 10. Usage

Loading example:

```python
from pathlib import Path
import joblib

models_dir = Path("models")

model = joblib.load(
    models_dir / "scoby_watch_best_group_split_model.pkl"
)
encoders = joblib.load(
    models_dir / "scoby_watch_label_encoders.pkl"
)
features = joblib.load(
    models_dir / "scoby_watch_feature_columns.pkl"
)
```

Do not load pickle files from untrusted sources. Pickle deserialization can
execute code.

---

## 11. Confidence

Confidence comes from:

```python
model.predict_proba(...)
```

The Hybrid Decision Layer uses the following threshold:

```text
0.70
```

Rule:

```text
confidence < 0.70
→ manual_check
```

The threshold is a conservative heuristic for a readiness-oriented
prototype.

The threshold has not been:

- calibrated;
- optimized;
- tested through sensitivity analysis;
- evaluated with a reliability diagram;
- evaluated using empirical fermentation labels.

---

## 12. Hybrid Decision Role

ML is not the sole decision authority.

The final decision considers:

1. rule status;
2. ML status;
3. ML confidence;
4. temperature-warning priority;
5. disagreements;
6. conflicts involving `too_sour`.

Possible final outputs:

```text
too_early
still_sweet
balanced
too_sour
temperature_warning
manual_check
```

---

## 13. Limitations

1. The target is generated by deterministic rules.
2. The dataset is fully synthetic.
3. Probability output is not calibrated.
4. The 0.70 threshold has not undergone sensitivity analysis.
5. No external validation has been performed.
6. No temporal model is used.
7. The sensor-noise model is not physically validated.
8. No empirical labels are available.
9. No laboratory confirmation is available.
10. No production drift monitoring is implemented.

---

## 14. Reproduction

Final grouped training:

```powershell
python -m src.train_models --mode group
```

All baselines:

```powershell
python -m src.train_models --mode both
```

Contract tests:

```powershell
python -m pytest tests/test_model_contract.py -v
```

Full pipeline:

```powershell
python -m src.run_pipeline
```

---

## 15. Model Update Policy

The model must be retrained if any of the following change:

- dataset generator;
- Rule Model v1.1;
- feature list;
- encoder categories;
- scikit-learn compatibility version;
- number of recipes;
- target labels;
- split strategy.

A new model must include updated metadata and evaluation results. The old
artifact should not be overwritten without a traceable version or commit.
