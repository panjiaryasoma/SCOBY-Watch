# SCOBY Watch Supplementary Materials

This directory contains curated supplementary material for the manuscript:

> **SCOBY Watch: A Simulation-First IoT and Hybrid Decision Support Framework for Kombucha Fermentation Readiness Assessment**

Authors:

- Panji Arya Soma
- Anas Nasrulloh

The supplementary package is intended to support implementation transparency,
technical inspection, and reproducibility. It does not provide laboratory,
microbiological, physical-sensor, or food-safety validation.

---

## 1. Purpose

The main manuscript summarizes the system design, methodology, evaluation,
results, and limitations.

This supplementary directory provides additional implementation evidence for:

- synthetic dataset generation and validation;
- pH and Brix trend inspection;
- status and rule distributions;
- batch-aware train-test separation;
- model comparison and confusion-matrix outputs;
- serialized model loading;
- Flask API behavior;
- Hybrid Decision Layer scenarios;
- Wokwi and MQTT simulation;
- Node-RED configuration and routing;
- dashboard sensor and decision outputs.

The material is curated to avoid duplicating every raw screenshot or terminal
output already available elsewhere in the repository.

---

## 2. Preferred Directory Contents

```text
supplementary/
├── README.md
├── README_SUPPLEMENTARY_FILES.txt
└── SCOBY_Watch_Simulation_and_Implementation_Evidence.pdf
```

The preferred final evidence filename is:

```text
SCOBY_Watch_Simulation_and_Implementation_Evidence.pdf
```

A previous working filename may appear as:

```text
SCOBY_Watch_Validation_Evidence_CURATED_COMPACT.pdf
```

Before public release, keep only one authoritative evidence PDF and use the
preferred final filename to avoid duplicate or ambiguous versions.

---

## 3. Evidence PDF Coverage

The curated PDF should contain representative evidence from the following
categories.

### 3.1 Dataset generation and integrity

Evidence may include:

- dataset shape: 4,900 rows and 16 columns;
- seven recipe profiles;
- 350 unique batches;
- 14 observations per batch;
- missing-value check;
- duplicate-row check;
- status distribution;
- rule-trigger distribution.

### 3.2 Sensor-range and trajectory checks

Evidence may include:

- temperature range;
- humidity range;
- pH range;
- Brix range;
- average pH trend by fermentation day;
- average Brix trend by fermentation day;
- pH and Brix trends by recipe;
- monotonic trend checks across all 350 batches.

### 3.3 Machine-learning evaluation

Evidence may include:

- initial random-row baseline;
- final `GroupShuffleSplit` configuration;
- 3,920 training rows;
- 980 test rows;
- 280 training batches;
- 70 test batches;
- zero `batch_id` overlap;
- five-model comparison;
- Gradient Boosting results;
- confusion matrix.

The authoritative evaluation is the group-aware split by `batch_id`.

### 3.4 Hybrid Decision Layer

Evidence may include:

- rule and ML agreement;
- confidence-aware fallback;
- `ml_confidence < 0.70` leading to `manual_check`;
- temperature-warning priority;
- ordinary disagreement;
- conflict involving `too_sour`;
- standard, edge, and forced-conflict scenarios.

### 3.5 Flask API

Evidence may include:

- successful model and encoder loading;
- `GET /`;
- `GET /health`;
- valid `POST /predict`;
- complete hybrid response fields;
- missing-field rejection;
- invalid-JSON rejection.

### 3.6 Wokwi and MQTT

Evidence may include:

- ESP32 simulation;
- DHT22 temperature and humidity input;
- simulated analog pH and Brix input;
- JSON payload construction;
- MQTT broker and topic configuration;
- serial or publish logs.

### 3.7 Node-RED and dashboard

Evidence may include:

- MQTT input node;
- JSON parser;
- HTTP request preparation;
- Flask `/predict` request;
- response splitting;
- debug output;
- sensor gauges;
- trend charts;
- rule, ML, confidence, final status, reason, risk, and recommendation fields.

---

## 4. Repository Reproducibility Map

The evidence PDF is not the only source of reproducibility. The corresponding
machine-readable and executable artifacts are located elsewhere in the
repository.

| Evidence category | Repository location |
|---|---|
| Synthetic dataset | `data/scoby_watch_simulated_dataset.csv` |
| Dataset validation tables | `data/validation/` |
| Notebook workflow | `notebooks/scoby_watch_dataset_ml_baseline.ipynb` |
| Reusable implementation | `src/` |
| Historical split experiments | `experiments/` |
| Serialized model artifacts | `models/` |
| Flask API | `api/app.py` |
| Node-RED flow | `node-red/` |
| Wokwi files | `wokwi/` |
| Structured evaluation outputs | `results/` |
| Notebook-style TXT evidence | `results/notebook_text_evidence/` |
| Findings reports | `reports/` |
| Automated tests | `tests/` |
| Technical documentation | `docs/` |

The supplementary PDF should summarize representative evidence, while the
repository remains the authoritative source for code, data, model artifacts,
and generated outputs.

---

## 5. Key Reproducibility Commands

From the repository root:

```powershell
python -m src.generate_dataset
python -m src.validate_dataset
python -m src.train_models --mode group
python -m src.hybrid_decision
python -m src.notebook_text_evidence
python -m pytest tests/ -q
```

Run the complete cleaned workflow:

```powershell
python -m src.run_pipeline
```

Run historical and split-comparison experiments:

```powershell
python -m experiments.random_split_baseline
python -m experiments.compare_split_strategies
```

Detailed instructions are available in:

```text
docs/REPRODUCIBILITY.md
```

---

## 6. Current Reference Results

| Item | Result |
|---|---:|
| Recipe profiles | 7 |
| Simulated batches | 350 |
| Daily observations | 4,900 |
| Dataset columns | 16 |
| Training rows | 3,920 |
| Test rows | 980 |
| Training batches | 280 |
| Test batches | 70 |
| Batch overlap | 0 |
| Selected model | Gradient Boosting |
| Accuracy | 0.995918 |
| Weighted F1-score | 0.995921 |
| Automated tests | 34 passed |
| Test failures | 0 |

These model scores quantify approximation of deterministic rule-generated
labels. They do not establish independent biological understanding.

---

## 7. Interpretation Boundary

The supplementary material supports claims about:

- software functionality;
- dataset-generator behavior;
- rule implementation;
- batch-aware model evaluation;
- model serialization and inference;
- hybrid conflict handling;
- API integration;
- MQTT and Node-RED data flow;
- dashboard visualization.

The supplementary material does not support claims about:

- microbial safety;
- pathogen detection;
- mold detection;
- alcohol content;
- titratable acidity;
- consumer health suitability;
- calibrated physical pH sensing;
- calibrated physical Brix sensing;
- real-world biological generalization;
- commercial product quality;
- food-safety certification.

The terms `balanced`, `too_early`, `still_sweet`, and `too_sour` are
readiness-oriented prototype statuses. They are not certifications that a
beverage is safe to consume.

---

## 8. Sensor Boundary

Wokwi pH and Brix values are simulated analog inputs.

The supplementary evidence does not demonstrate:

- physical sensor calibration;
- measurement repeatability;
- probe drift;
- probe fouling;
- signal-conditioning accuracy;
- cleaning protocols;
- food-contact suitability.

Physical deployment requires separate calibration, engineering, laboratory,
and safety validation.

---

## 9. Model Boundary

The machine-learning baseline is trained on deterministic rule-generated
targets.

The model is used as a controlled surrogate for validating:

- training;
- grouped evaluation;
- serialization;
- Flask inference;
- confidence reporting;
- Node-RED integration;
- Hybrid Decision Layer behavior.

The high score does not prove that machine learning is preferable to direct
rule execution in the current synthetic setting.

---

## 10. File Hygiene

The public supplementary directory should not contain:

- obsolete evidence PDFs;
- duplicate screenshots;
- failed diagrams;
- plagiarism-check screenshots;
- raw conversation exports;
- virtual environments;
- API tokens;
- passwords;
- personal access tokens;
- local machine paths;
- temporary Office files;
- model artifacts from superseded experiments.

Raw outputs that are already reproducible from scripts should remain under
`results/` instead of being duplicated here without a clear reason.

---

## 11. Versioning

When the evidence PDF changes, update:

- the filename or release tag;
- the repository commit;
- the file inventory, if one is maintained;
- the manuscript data-availability statement when necessary.

The supplementary PDF, model artifacts, dataset, and manuscript should refer
to the same authoritative release.

---

## 12. Citation

Repository citation metadata is provided in:

```text
CITATION.cff
```

When a permanent repository URL or archived DOI becomes available, update the
citation metadata and the manuscript data-availability statement.

---

## 13. License

Repository software and documentation are released under the MIT License,
unless a specific third-party artifact states otherwise.

See:

```text
LICENSE
```

The license permits reuse under its terms. It does not imply scientific,
biological, safety, or regulatory validation.

---

## 14. Contact and Responsibility

Primary implementation and repository preparation:

```text
Panji Arya Soma
```

Academic supervision and review:

```text
Anas Nasrulloh
```

Questions about interpretation should be resolved using the manuscript,
`docs/CLAIM_BOUNDARIES.md`, and the release-matched repository artifacts.
