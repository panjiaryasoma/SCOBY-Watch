# Training Findings — SCOBY Watch

**Project:** SCOBY Watch  
**Dataset:** SCOBY Watch Synthetic Fermentation Dataset  
**Target:** `expected_status`  
**Final model:** Gradient Boosting  
**Random state:** 42  
**Status:** Random-row baseline and group-aware training completed  

---

## 1. Purpose

The training stage compares five classifiers and validates two split strategies:

1. random-row splitting as the initial notebook experiment;
2. GroupShuffleSplit by `batch_id` as the final evaluation strategy.

The purpose of the ML component is not to outperform the rule engine. It is
used to validate training, serialization, inference, confidence reporting,
and hybrid integration.

---

## 2. Features

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

Number of features:

```text
10
```

---

## 3. Encoding

Encoders are created for:

```text
recipe_id
recipe_name
tea_type
risk_flag
expected_status
```

Target classes:

```text
balanced
manual_check
still_sweet
temperature_warning
too_early
too_sour
```

---

## 4. Candidate Models

| Model | Configuration |
|---|---|
| Decision Tree | `max_depth=8`, `random_state=42` |
| Random Forest | `n_estimators=150`, `max_depth=12`, `random_state=42` |
| Gradient Boosting | `random_state=42`, other parameters left at defaults |
| KNN | `n_neighbors=7`, StandardScaler |
| Logistic Regression | `max_iter=1500`, StandardScaler |

No hyperparameter optimization was performed.

---

## 5. Random-Row Baseline

Method:

```text
train_test_split
test_size = 0.20
stratify = target
random_state = 42
```

Results:

| Model | Accuracy | Precision | Recall | Weighted F1 |
|---|---:|---:|---:|---:|
| Random Forest | 0.996939 | 0.996935 | 0.996939 | 0.996933 |
| Gradient Boosting | 0.996939 | 0.996960 | 0.996939 | 0.996924 |
| Decision Tree | 0.995918 | 0.995945 | 0.995918 | 0.995902 |
| Logistic Regression | 0.837755 | 0.830011 | 0.837755 | 0.831765 |
| KNN | 0.816327 | 0.809739 | 0.816327 | 0.809824 |

Random Forest is the best-performing model under the random-row split.

However, the random-row split can place observations from the same batch in
both the training and test sets. Therefore, this result is not used as the
final paper result.

---

## 6. Group-Aware Split

Final method:

```text
GroupShuffleSplit
group = batch_id
n_splits = 1
test_size = 0.20
random_state = 42
```

Split results:

| Component | Value |
|---|---:|
| Training rows | 3,920 |
| Test rows | 980 |
| Training batches | 280 |
| Test batches | 70 |
| Batch overlap | 0 |

The group split is used to prevent trajectory leakage between observations
belonging to the same batch.

---

## 7. Final Model

Final model:

```text
GradientBoostingClassifier
```

Main parameters:

```text
learning_rate = 0.1
n_estimators = 100
max_depth = 3
subsample = 1.0
max_features = None
random_state = 42
```

---

## 8. Final Group-Split Results

| Metric | Value |
|---|---:|
| Accuracy | 0.995918 |
| Weighted F1-score | 0.995921 |

Gradient Boosting produces the best result in the grouped evaluation.

---

## 9. Why Tree-Based Models Perform Highly

The target is generated using threshold rules on:

- pH;
- Brix;
- temperature;
- fermentation day.

Tree-based models can directly approximate axis-aligned, nonlinear, piecewise
decision boundaries.

The high score does not mean that the model biologically understands
fermentation.

---

## 10. Artifacts

```text
models/
├── scoby_watch_best_group_split_model.pkl
├── scoby_watch_label_encoders.pkl
├── scoby_watch_feature_columns.pkl
└── metadata.json
```

Result outputs:

```text
results/
├── scoby_watch_ml_baseline_results.csv
├── scoby_watch_group_split_ml_results.csv
├── scoby_watch_split_strategy_comparison.csv
└── classification-report TXT files
```

---

## 11. Reproduction

Random baseline:

```powershell
python -m experiments.random_split_baseline
```

Group split:

```powershell
python -m src.train_models --mode group
```

Both modes:

```powershell
python -m src.train_models --mode both
```

Split comparison:

```powershell
python -m experiments.compare_split_strategies
```

---

## 12. Environment

The baseline artifacts were created using:

```text
Python 3.12.x
scikit-learn 1.6.1
```

Using a different scikit-learn version may produce serialization warnings or
compatibility issues.

---

## 13. Claims That Must Not Be Made

The training results do not prove that:

- ML is better than direct rule execution;
- the model has biological understanding;
- the model can be used directly on real fermentation data;
- the confidence values are calibrated;
- the 0.70 threshold is optimal;
- the model is safe for consumption-related decisions.

---

## 14. Conclusion

The training pipeline successfully compares five classifiers, reproduces the
random-row baseline, and produces a final evaluation with zero batch overlap.

Gradient Boosting is selected as the deployable model for software-integration
validation.

The model remains a rule-label approximation baseline.
