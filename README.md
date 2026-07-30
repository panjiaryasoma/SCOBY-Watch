# SCOBY Watch

**A Simulation-First IoT and Hybrid Decision Support Framework for Kombucha Fermentation Readiness Assessment**

SCOBY Watch is a research and engineering prototype that connects synthetic
kombucha-fermentation data, an ESP32 simulation, MQTT, Node-RED, a Flask API,
a deterministic rule engine, a machine-learning baseline, and a
confidence-aware hybrid decision layer.

The project was built to validate the complete software workflow before
calibrated physical pH and Brix sensors and empirical fermentation labels are
available.

> **Important:** SCOBY Watch is a readiness-oriented decision-support
> prototype. It is not a food-safety certification system and does not
> validate microbial safety, health suitability, or commercial product
> quality.

---

## Key Results

| Item | Result |
|---|---:|
| Recipe profiles | 7 |
| Simulated batches | 350 |
| Observations per batch | 14 |
| Total observations | 4,900 |
| Dataset columns | 16 |
| Final split | GroupShuffleSplit by `batch_id` |
| Training observations | 3,920 |
| Test observations | 980 |
| Training batches | 280 |
| Test batches | 70 |
| Batch overlap | 0 |
| Selected model | Gradient Boosting |
| Accuracy | 0.995918 |
| Weighted F1-score | 0.995921 |
| Automated tests | 34 passed |
| Test failures | 0 |

The near-perfect model result measures approximation of deterministic
rule-generated labels. It does not demonstrate independent biological
understanding.

---

## System Architecture

```text
Wokwi ESP32
    ↓
MQTT broker
    ↓
Node-RED
    ↓
Flask POST /predict
    ↓
Rule Model v1.1 + ML baseline
    ↓
Hybrid Decision Layer
    ↓
Node-RED dashboard
```

The current prototype uses:

```text
MQTT broker : broker.emqx.io
Port        : 1883
Topic       : scobywatch/panji/sensor
QoS         : 0
Flask API   : http://127.0.0.1:5000
```

The public MQTT broker and Flask development service are prototype choices,
not production deployment recommendations.

---

## Decision Outputs

The system supports six final statuses:

```text
too_early
still_sweet
balanced
too_sour
temperature_warning
manual_check
```

The Hybrid Decision Layer applies the following order:

1. Preserve `temperature_warning` from the rule engine.
2. Return `manual_check` when ML confidence is below `0.70`.
3. Preserve the shared status when the rule and ML outputs agree.
4. Return `manual_check` for a conflict involving `too_sour`.
5. Return `manual_check` for any other disagreement.

The hybrid layer is not a majority-vote ensemble.

---

## Repository Structure

```text
scoby-watch/
├── .github/
│   └── workflows/
│       └── tests.yml
├── api/
│   └── app.py
├── data/
│   ├── scoby_watch_simulated_dataset.csv
│   └── validation/
├── docs/
│   ├── README.md
│   ├── DATASET_CARD.md
│   ├── MODEL_CARD.md
│   ├── API.md
│   ├── REPRODUCIBILITY.md
│   ├── SYSTEM_ARCHITECTURE.md
│   └── CLAIM_BOUNDARIES.md
├── experiments/
│   ├── __init__.py
│   ├── README.md
│   ├── random_split_baseline.py
│   └── compare_split_strategies.py
├── models/
│   ├── scoby_watch_best_group_split_model.pkl
│   ├── scoby_watch_label_encoders.pkl
│   ├── scoby_watch_feature_columns.pkl
│   └── metadata.json
├── node-red/
│   └── SCOBY Watch Flask Hybrid.json
├── notebooks/
│   └── SCOBY WATCH DATASET + ML BASELINE.ipynb
├── reports/
│   ├── README.md
│   ├── dataset_generation_findings.md
│   ├── data_quality_findings.md
│   ├── training_findings.md
│   ├── evaluation_findings.md
│   ├── hybrid_decision_findings.md
│   ├── api_findings.md
│   ├── integration_testing_findings.md
│   └── testing_findings.md
├── results/
│   ├── model and split results
│   ├── hybrid-validation outputs
│   └── notebook_text_evidence/
├── src/
│   ├── __init__.py
│   ├── README.md
│   ├── config.py
│   ├── rule_engine.py
│   ├── generate_dataset.py
│   ├── validate_dataset.py
│   ├── train_models.py
│   ├── hybrid_decision.py
│   ├── notebook_text_evidence.py
│   └── run_pipeline.py
├── supplementary/
│   ├── README.md
│   ├── README_SUPPLEMENTARY_FILES.txt
│   └── SCOBY Watch Simulation and Implementation Evidence.pdf
├── tests/
│   ├── README.md
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_dataset.py
│   ├── test_hybrid_decision.py
│   ├── test_model_contract.py
│   └── test_rule_engine.py
├── wokwi/
│   ├── diagram.json
│   ├── libraries.txt
│   ├── sketch.ino
│   └── wokwi-project.txt
├── .gitattributes
├── .gitignore
├── CITATION.cff
├── LICENSE
├── PRD.md
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

---

## Requirements

Recommended baseline:

```text
Python 3.12
scikit-learn 1.6.1
```

The serialized model was created with scikit-learn 1.6.1. Loading the model
with a different version may produce compatibility warnings or invalid
results.

Install the runtime dependencies from the repository root:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install development and test dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

---

## Quick Start

### 1. Create a virtual environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

When PowerShell blocks script activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Generate the dataset

```powershell
python -m src.generate_dataset
```

Expected summary:

```text
Dataset shape: (4900, 16)
Unique recipes: 7
Unique batches: 350
```

### 3. Validate the dataset

```powershell
python -m src.validate_dataset
```

### 4. Train the authoritative grouped baseline

```powershell
python -m src.train_models --mode group
```

### 5. Run hybrid validation

```powershell
python -m src.hybrid_decision
```

### 6. Generate notebook-style text evidence

```powershell
python -m src.notebook_text_evidence
```

### 7. Run the complete pipeline

```powershell
python -m src.run_pipeline
```

The complete run performs:

```text
dataset generation
→ dataset validation
→ random-row historical baseline
→ group-aware final evaluation
→ split comparison
→ model artifact saving
→ hybrid validation
→ notebook-style TXT evidence
```

---

## Experiments

The initial notebook used a stratified random-row split. It is preserved for
archival and methodological comparison:

```powershell
python -m experiments.random_split_baseline
```

Compare random-row and group-aware strategies:

```powershell
python -m experiments.compare_split_strategies
```

The official paper result remains the GroupShuffleSplit evaluation based on
`batch_id`.

Run experiment files as modules from the repository root. Executing them as
plain file paths may prevent Python from locating the sibling `src` package.

---

## Automated Testing

Run the complete test suite:

```powershell
python -m pytest tests/ -q
```

Current baseline:

```text
34 passed
24 warnings
0 failed
```

Test coverage includes:

- dataset dimensions and deterministic generation;
- sensor ranges;
- per-batch pH and Brix trends;
- Rule Model v1.1 paths and boundary behavior;
- confidence threshold behavior;
- temperature-warning priority;
- agreement and conflict handling;
- grouped split and zero batch overlap;
- model, encoder, and feature-order contracts;
- Flask root, health, and prediction endpoints;
- invalid JSON and missing-field handling.

The current warnings originate from internal `joblib` and NumPy behavior
while loading serialized artifacts. They do not currently cause test
failures.

---


## Continuous Integration

The repository includes:

```text
.github/workflows/tests.yml
```

The workflow runs on:

```text
Ubuntu
Python 3.12
```

It is triggered by:

- pushes;
- pull requests;
- manual workflow dispatch.

The workflow performs:

```text
repository checkout
→ Python 3.12 setup
→ pip dependency caching
→ requirements-dev.txt installation
→ import and compilation checks
→ pytest tests/ -q
```

The expected test baseline is:

```text
34 passed
0 failed
```

The workflow configuration is complete. Its first GitHub-hosted execution
remains pending until the repository is pushed.

The repository also includes `.gitattributes` to normalize line endings and
mark model, image, PDF, archive, and Office files as binary artifacts.

---


## Flask API

Start the API from the repository root:

```powershell
python api/app.py
```

Available endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service information |
| GET | `/health` | Model health check |
| POST | `/predict` | Rule, ML, and hybrid inference |

### Health check

Open:

```text
http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "model": "GradientBoostingClassifier",
  "status": "ok"
}
```

### Prediction example

PowerShell:

```powershell
$body = @{
    batch_id           = "KB-TEST-001"
    recipe_id          = "R1"
    tea_type           = "black_tea"
    sugar_g_per_l      = 80
    starter_ml         = 150
    water_volume_l     = 1.0
    day                = 7
    room_temp_c        = 24.4
    humidity_percent   = 68.0
    ph                 = 3.56
    brix               = 7.71
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Representative result:

```text
rule_status   = balanced
ml_status     = balanced
ml_confidence = 0.9998
final_status  = balanced
```

Opening `/predict` directly in a browser address bar sends GET and therefore
returns `405 Method Not Allowed`. The endpoint requires POST JSON.

---

## Node-RED

Import the flow from:

```text
node-red/SCOBY Watch Flask Hybrid.json
```

Confirm that the HTTP Request node points to:

```text
http://127.0.0.1:5000/predict
```

The flow supports:

- MQTT input;
- manual inject payloads;
- JSON parsing;
- Flask requests;
- raw debug output;
- sensor gauges;
- trend charts;
- rule, ML, confidence, and final-decision fields.

---

## Wokwi

The `wokwi/` folder contains the ESP32 simulation files:

```text
sketch.ino
diagram.json
libraries.txt
```

It may also contain a local configuration file or a text file containing the
public Wokwi project URL.

The simulated pH and Brix values are not calibrated physical measurements.

---

## Documentation

Technical reference:

```text
docs/
├── DATASET_CARD.md
├── MODEL_CARD.md
├── API.md
├── REPRODUCIBILITY.md
├── SYSTEM_ARCHITECTURE.md
└── CLAIM_BOUNDARIES.md
```

Actual findings and checkpoints:

```text
reports/
├── dataset_generation_findings.md
├── data_quality_findings.md
├── training_findings.md
├── evaluation_findings.md
├── hybrid_decision_findings.md
├── api_findings.md
├── integration_testing_findings.md
└── testing_findings.md
```

---

## Reproducibility Notes

Before publishing a release:

1. Clone the repository into a new directory.
2. Create a new Python 3.12 virtual environment.
3. Install dependencies only from the requirement files.
4. Regenerate the dataset.
5. Run the grouped training pipeline.
6. Run all automated tests.
7. Start the Flask API.
8. Import the Node-RED flow.
9. Run the Wokwi simulation.
10. Compare the outputs with the documented metadata and findings.

The repository should not be described as fully reproducible until this
clean-clone rehearsal succeeds.

---

## Limitations

SCOBY Watch currently does not provide:

- empirical fermentation labels;
- physical pH or Brix sensor validation;
- microbial testing;
- alcohol testing;
- titratable-acidity testing;
- pathogen or contamination detection;
- probability calibration;
- confidence-threshold sensitivity analysis;
- production authentication;
- encrypted MQTT communication;
- persistent historical storage;
- production WSGI deployment;
- high-load or concurrency validation;
- food-safety certification.

---

## Safety and Claim Boundary

The terms `balanced`, `too_early`, `still_sweet`, and `too_sour` describe
readiness-oriented prototype statuses.

They do not establish that a beverage is safe to consume.

Users must not treat:

```text
pH
Brix
model confidence
rule agreement
dashboard status
```

as substitutes for sanitation, contamination inspection, laboratory testing,
or qualified food-safety guidance.

---

## Citation

Citation metadata is provided in:

```text
CITATION.cff
```

GitHub can use this file to display a **Cite this repository** option after
the repository is published.

The repository URL, archived release DOI, and preferred paper citation should
be added after they become available.

---

## License

This repository is released under the MIT License.

See:

```text
LICENSE
```

The license permits reuse of the software and documentation under its terms.
It does not grant scientific validity to modified versions or remove the
project's safety and claim boundaries.

---

## Authors

**Panji Arya Soma**  
Conceptualization, methodology, synthetic data generation, software
implementation, model training, analysis, visualization, documentation, and
repository preparation.

**Anas Nasrulloh**  
Academic supervision, validation review, methodological guidance, refinement,
and manuscript review.

---

## Project Status

Completed:

- simulation-first prototype;
- synthetic dataset generator;
- Rule Model v1.1;
- five-model baseline comparison;
- GroupShuffleSplit evaluation;
- serialized model artifacts;
- Flask API;
- Hybrid Decision Layer;
- Wokwi, MQTT, Node-RED, and dashboard integration;
- modular source extraction;
- automated tests with a 34-test local baseline;
- English technical documentation;
- English findings reports;
- notebook-style evidence generation;
- curated supplementary evidence package;
- root `README.md`;
- MIT `LICENSE`;
- base `CITATION.cff` metadata;
- GitHub Actions workflow configuration;
- `.gitattributes` line-ending and binary-file configuration.

Remaining before the reproducibility release is considered complete:

- rename the local `API/` directory to lowercase `api/` if it has not already
  been renamed;
- push the repository and verify the first GitHub Actions run;
- perform a clean-clone rehearsal in a fresh directory and virtual environment;
- complete the final dependency review;
- add the permanent public GitHub URL;
- verify or publish the public Wokwi URL;
- create an optional release tag and archival DOI;
- update the manuscript data-availability statement with the verified
  repository URL.
