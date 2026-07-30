# Reproducibility Guide — SCOBY Watch

## 1. Purpose

This document explains how to reproduce the dataset, validation outputs,
baseline models, artifacts, hybrid results, API behavior, and automated tests
from a clean repository.

The guide targets Windows PowerShell and Python 3.12.

---

## 2. Prerequisites

- Git
- Python 3.12
- pip
- Node-RED
- a web browser
- internet access for the public MQTT broker
- a Wokwi account only when the online project requires it

Baseline runtime:

```text
Python 3.12.7
scikit-learn 1.6.1
pytest 8.4.2
```

---

## 3. Clone the Repository

After the public URL becomes available:

```powershell
git clone [REPOSITORY_URL]
cd scoby-watch
```

Replace `[REPOSITORY_URL]` after the repository is published.

---

## 4. Create a Virtual Environment

Create:

```powershell
py -3.12 -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy `
  -Scope Process `
  -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1
```

---

## 5. Install Dependencies

Runtime:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Development and testing:

```powershell
python -m pip install -r requirements-dev.txt
```

Verify:

```powershell
python -c "import sys, sklearn; print(sys.version); print(sklearn.__version__)"
```

Expected baseline:

```text
Python 3.12.x
scikit-learn 1.6.1
```

---

## 6. Repository Structure

```text
scoby-watch/
├── api/
├── data/
├── docs/
├── experiments/
├── models/
├── node-red/
├── notebooks/
├── reports/
├── results/
├── src/
├── supplementary/
├── tests/
└── wokwi/
```

---

## 7. Generate the Dataset

```powershell
python -m src.generate_dataset
```

Expected summary:

```text
Dataset shape: (4900, 16)
Unique recipes: 7
Unique batches: 350
```

Output:

```text
data/scoby_watch_simulated_dataset.csv
```

---

## 8. Validate the Dataset

```powershell
python -m src.validate_dataset
```

Main outputs:

```text
data/validation/
reports/
```

Automated test:

```powershell
python -m pytest tests/test_dataset.py -v
```

Expected result:

```text
5 passed
```

---

## 9. Reproduce the Random-Row Baseline

Historical notebook baseline:

```powershell
python -m experiments.random_split_baseline
```

Outputs:

```text
results/
reports/
```

The random-row split is retained for historical completeness and is not the
authoritative paper evaluation.

---

## 10. Reproduce the Group-Aware Evaluation

```powershell
python -m src.train_models --mode group
```

Expected split:

```text
training rows = 3920
test rows = 980
training batches = 280
test batches = 70
batch overlap = 0
```

Expected final model:

```text
Gradient Boosting
Accuracy = 0.995918
Weighted F1 = 0.995921
```

Outputs:

```text
models/
results/
reports/
```

---

## 11. Compare Split Strategies

```powershell
python -m experiments.compare_split_strategies
```

Outputs include:

```text
SPLIT STRATEGY COMPARISON.txt
GROUP SHUFFLE SPLIT BY batch_id.txt
TRAIN ML BASELINE MODELS WITH GROUP SPLIT.txt
TRAIN ML BASELINE MODELS WITH RANDOM SPLIT.txt
```

---

## 12. Run Hybrid Validation

```powershell
python -m src.hybrid_decision
```

Outputs:

```text
results/
├── scoby_watch_hybrid_decision_test.csv
├── scoby_watch_hybrid_edge_case_test.csv
└── scoby_watch_hybrid_forced_conflict_test.csv
```

---

## 13. Generate Notebook-Style TXT Evidence

```powershell
python -m src.notebook_text_evidence
```

Output directory:

```text
results/notebook_text_evidence/
```

The generated files cover:

- basic dataset sanity;
- sensor ranges;
- average pH and Brix;
- monotonic trends;
- status transitions;
- random-row split;
- grouped split;
- model reports;
- model loading;
- one-sample hybrid output.

---

## 14. Run the Complete Pipeline

```powershell
python -m src.run_pipeline
```

Execution order:

```text
dataset generation
→ dataset validation
→ random-row baseline
→ group-aware baseline
→ split comparison
→ artifact saving
→ hybrid validation
→ TXT evidence generation
```

To skip the random baseline:

```powershell
python -m src.run_pipeline --skip-random-baseline
```

---

## 15. Run Automated Tests

Complete test suite:

```powershell
python -m pytest tests/ -q
```

Expected baseline:

```text
34 passed, 24 warnings
```

Tests by component:

```powershell
python -m pytest tests/test_dataset.py -v
python -m pytest tests/test_rule_engine.py -v
python -m pytest tests/test_hybrid_decision.py -v
python -m pytest tests/test_model_contract.py -v
python -m pytest tests/test_api.py -v
```

The joblib/NumPy warnings are recorded as dependency-compatibility warnings
and do not change the pass/fail result.

---

## 16. Run the Flask API

```powershell
python api/app.py
```

Health check:

```text
http://127.0.0.1:5000/health
```

Root endpoint:

```text
http://127.0.0.1:5000/
```

`/predict` must be tested using POST, not through a browser address bar.

---

## 17. Import the Node-RED Flow

1. Start Node-RED.
2. Open the Node-RED editor.
3. Select Import.
4. Choose:

```text
node-red/SCOBY Watch Flask Hybrid.json
```

5. Confirm that the HTTP Request node points to:

```text
http://127.0.0.1:5000/predict
```

6. Deploy the flow.
7. Inspect debug output and the dashboard.

---

## 18. Run Wokwi

Local files:

```text
wokwi/
├── sketch.ino
├── diagram.json
├── libraries.txt
└── wokwi-project.txt or wokwi.toml
```

Steps:

1. open the Wokwi project;
2. inspect the Wi-Fi and MQTT configuration;
3. run the simulation;
4. confirm that payloads are published to the configured topic;
5. inspect the MQTT input in Node-RED;
6. inspect the dashboard.

Replace the placeholder project URL after the public Wokwi project is
available.

---

## 19. Clean-Clone Validation

Before publication:

1. clone the repository into a new directory;
2. do not reuse the old `.venv`;
3. install dependencies only from the requirement files;
4. run the dataset generator;
5. run the dataset tests;
6. run grouped training;
7. run the complete test suite;
8. start the Flask API;
9. import the Node-RED flow;
10. run Wokwi;
11. compare results against the metadata and paper.

The repository should be described as reproducible only after this clean-clone
validation succeeds.

---

## 20. Expected Artifact Checklist

```text
data/scoby_watch_simulated_dataset.csv

models/
├── scoby_watch_best_group_split_model.pkl
├── scoby_watch_label_encoders.pkl
├── scoby_watch_feature_columns.pkl
└── metadata.json

results/
├── model-comparison CSV files
├── hybrid-validation CSV files
├── split-comparison outputs
└── notebook_text_evidence/

reports/
├── validation plots
├── classification reports
└── findings markdown
```

---

## 21. Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

Run modules from the repository root:

```powershell
python -m experiments.random_split_baseline
```

Do not run:

```powershell
python experiments/random_split_baseline.py
```

### scikit-learn Version Warning

Install the artifact baseline:

```powershell
python -m pip install scikit-learn==1.6.1
```

### SciPy Attempts to Build from Source

Use standard Python 3.12 and create a fresh virtual environment.

### `/predict` Returns Method Not Allowed

A browser address bar sends GET. Use PowerShell, Postman, Node-RED, or curl
to send POST JSON.

### Model File Not Found

Run commands from the repository root and resolve paths from the location of
`app.py`.

---

## 22. Reproducibility Boundary

Successful reproduction demonstrates that the software artifacts can be
regenerated in a compatible environment.

It does not demonstrate:

- biological validity;
- physical-sensor validity;
- food safety;
- production readiness.
