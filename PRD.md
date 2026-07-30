# SCOBY Watch
## As-Built Product Requirements Document

| Field | Value |
|---|---|
| Document version | 1.3 |
| Product status | Completed research prototype; repository structure, English documentation, CI configuration, release metadata, and supplementary evidence assembled; GitHub publication and clean-clone validation pending |
| Release target | Public reproducibility repository after clean-clone validation |
| Document type | As-built PRD |
| Product owner | Panji Arya Soma |
| Academic supervisor and reviewer | Anas Nasrulloh |
| Last updated | 2026-07-30 |
| Primary implementation mode | Simulation-first |
| Primary language | English |
| License | MIT |

---

## 1. Document Purpose

This Product Requirements Document records the requirements, implemented behavior, design boundaries, evidence, and release criteria of the completed SCOBY Watch prototype.

Because the product has already been implemented, this document is an **as-built PRD**. It describes what the prototype currently does, why each major component exists, what has been validated, what remains outside the claim boundary, and what must be packaged before the project is released as a reproducible GitHub repository.

This document is not a replacement for the research manuscript. The manuscript explains the scientific motivation, methodology, results, and limitations. This PRD functions as the product and engineering source of truth for repository organization, implementation review, and future development.

---

## 2. Product Summary

SCOBY Watch is a simulation-first Internet of Things and hybrid decision-support framework for kombucha fermentation readiness assessment.

The system integrates:

1. Wokwi-based ESP32 sensor simulation.
2. MQTT-based JSON data transmission.
3. Node-RED middleware and dashboard visualization.
4. A Flask application programming interface.
5. A deterministic rule-based readiness model.
6. A supervised machine-learning baseline.
7. A confidence-aware hybrid decision layer.
8. A synthetic multi-recipe fermentation dataset.
9. Scripted dataset, model, hybrid-decision, API, and integration validation evidence.
10. Modular reusable source code extracted from the Colab notebook.
11. Historical random-row and final group-aware experiment scripts.
12. Automated contract tests for the dataset, rule engine, hybrid layer, model artifacts, and Flask API.
13. English technical documentation, findings reports, and notebook-style text-evidence exporters.
14. GitHub Actions configuration for Python 3.12 testing on Ubuntu.
15. Repository line-ending and binary-artifact rules through `.gitattributes`.
16. MIT licensing and machine-readable citation metadata through `CITATION.cff`.

The implemented end-to-end data path is:

```text
Wokwi ESP32
    ↓
MQTT broker
    ↓
Node-RED
    ↓
Flask POST /predict
    ↓
Rule-based model + ML baseline
    ↓
Hybrid decision layer
    ↓
Node-RED dashboard
```

The prototype is intended to validate software architecture, data flow, decision logic, model-serving integration, uncertainty handling, and dashboard behavior before calibrated physical sensors and empirical fermentation labels are available.

---

## 3. Problem Statement

Small-scale kombucha makers commonly assess fermentation readiness using intermittent visual inspection, aroma, taste, pH readings, sweetness estimation, and elapsed fermentation time.

These practices are useful but may be:

- subjective;
- intermittent;
- difficult to document consistently;
- difficult to compare across recipes and batches;
- unable to provide continuous trend visualization;
- unable to expose conflicts between deterministic rules and predictive outputs;
- expensive to prototype with physical pH and Brix sensors before the software workflow is stable.

SCOBY Watch addresses the engineering problem of validating a readiness-oriented monitoring and decision-support pipeline before physical sensor deployment.

It does not attempt to solve laboratory validation, microbial safety, regulatory approval, or commercial process control.

---

## 4. Product Vision

Provide a reproducible, transparent, simulation-first framework that allows developers, researchers, and kombucha makers to inspect simulated fermentation variables, obtain readiness-oriented rule and ML outputs, understand why the final decision was produced, and identify uncertain or conflicting cases that require manual inspection.

The product should prefer an explicit manual fallback over an unjustified automatic decision.

---

## 5. Goals

### G-01. Validate the end-to-end IoT data path

The system shall demonstrate that simulated ESP32 sensor data can be transmitted through MQTT, parsed and routed by Node-RED, evaluated by a Flask service, and returned to dashboard widgets.

### G-02. Provide transparent readiness-oriented rule output

The system shall produce a deterministic status, recommendation, triggered rule, and risk flag from the current simulated fermentation conditions.

### G-03. Validate an ML-serving pipeline

The system shall train, serialize, load, and serve a machine-learning baseline that approximates deterministic rule-generated labels under a batch-aware train-test split.

### G-04. Handle uncertainty and disagreement conservatively

The hybrid layer shall route low-confidence or conflicting outputs to `manual_check`, while preserving `temperature_warning` priority.

### G-05. Support reproducibility

The project shall provide the dataset, generation logic, model configuration, trained artifacts, API code, Node-RED flow, Wokwi files, validation outputs, and documentation needed for independent inspection.

### G-06. Preserve an explicit claim boundary

The system and documentation shall consistently identify the prototype as readiness-oriented decision support, not food-safety certification or biological validation.

---

## 6. Non-Goals

The current release shall not claim or provide:

1. Food-safety certification.
2. Microbial safety confirmation.
3. Pathogen testing.
4. Microbial enumeration.
5. Alcohol testing.
6. Titratable acidity testing.
7. Laboratory-confirmed fermentation outcomes.
8. Consumer health suitability.
9. Commercial product-quality certification.
10. Calibrated physical pH probe validation.
11. Validated digital refractometer or Brix sensor measurements.
12. Sensory-panel validation.
13. Mold or contamination detection.
14. Production deployment.
15. Persistent historical database storage.
16. Authenticated or encrypted MQTT transport.
17. Mobile-first dashboard support.
18. Guaranteed real-world model generalization.
19. Automatic replacement of human inspection or expert judgment.
20. Proof that machine learning is superior to direct rule execution.

---

## 7. Users and Stakeholders

### 7.1 Primary user

A small-scale or home kombucha maker who wants to inspect simulated fermentation conditions and receive a readiness-oriented recommendation.

### 7.2 Technical user

A student, researcher, or developer who wants to reproduce the synthetic dataset, train the baseline models, inspect the rule logic, run the API, import the Node-RED flow, and test the Wokwi-to-dashboard pipeline.

### 7.3 Academic reviewer

A reviewer who needs to inspect the project assumptions, leakage-aware evaluation, model configuration, hybrid conflict handling, supplementary evidence, and limits of the claims.

### 7.4 Product owner

Panji Arya Soma, responsible for conceptualization, methodology, data generation, software implementation, model training, analysis, visualization, documentation, and repository release.

### 7.5 Academic supervisor and reviewer

Anas Nasrulloh, responsible for supervision, validation review, academic guidance, methodological refinement, and manuscript review.

---

## 8. Product Scope

### 8.1 In scope

- Synthetic kombucha fermentation dataset generation.
- Seven recipe profiles.
- Fourteen daily observations per simulated batch.
- Deterministic rule-based labeling.
- Five supervised ML baselines.
- Batch-aware train-test separation.
- Gradient Boosting model serialization.
- Rule and ML inference through Flask.
- Confidence-aware hybrid arbitration.
- MQTT ingestion through Node-RED.
- Manual test payload injection.
- Dashboard gauges, trend charts, and decision fields.
- Scripted normal, edge-case, warning, low-confidence, and conflict validation.
- Supplementary reproducibility and implementation evidence.
- Modular extraction of the complete notebook workflow into reusable Python modules.
- Historical random-row and final group-aware experiment scripts.
- Automated dataset, rule, hybrid, model-contract, and API tests.
- Technical documentation under `docs/`.
- Findings reports under `reports/`.
- Notebook-style TXT evidence generation.
- GitHub Actions configuration for cross-platform regression testing.
- Repository line-ending and binary-artifact handling through `.gitattributes`.
- MIT licensing and `CITATION.cff` metadata.
- Public GitHub repository packaging.

### 8.2 Out of scope for the current release

- Physical sensor hardware.
- Real fermentation dataset collection.
- Database integration.
- Cloud production hosting.
- Secure message transport.
- Automated deployment.
- Laboratory and microbiological validation.
- Probability calibration.
- Confidence-threshold sensitivity analysis.
- Statistical confidence intervals for model performance.
- Mobile application development.
- Automated retraining.

---

## 9. As-Built System Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│ Simulation Layer                                             │
│ Wokwi ESP32 + DHT22 + analog pH/Brix inputs                  │
└──────────────────────────────┬───────────────────────────────┘
                               │ JSON payload
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ Messaging Layer                                              │
│ MQTT broker: broker.emqx.io:1883                             │
│ Topic: scobywatch/panji/sensor                               │
│ QoS: 0                                                       │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ Middleware Layer                                             │
│ Node-RED                                                     │
│ - MQTT input                                                 │
│ - JSON parser                                                │
│ - Manual inject payload                                      │
│ - Flask request preparation                                  │
│ - API response splitting                                     │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP POST
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ Decision Service                                             │
│ Local Flask API: http://127.0.0.1:5000                      │
│ - GET /health                                                │
│ - POST /predict                                              │
│ - Rule-based inference                                       │
│ - ML inference                                               │
│ - Hybrid decision logic                                      │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ Visualization Layer                                          │
│ Node-RED dashboard                                           │
│ - Sensor gauges                                              │
│ - Sensor trend charts                                        │
│ - Batch metadata                                             │
│ - Rule, ML, confidence, final status, and recommendation      │
└──────────────────────────────────────────────────────────────┘
```

---

## 10. Data Requirements

### 10.1 Dataset composition

The synthetic dataset shall contain:

- 7 recipe profiles;
- 50 batches per recipe;
- 350 unique batches;
- 14 daily observations per batch;
- 4,900 rows;
- 16 columns.

### 10.2 Dataset columns

| Column | Description |
|---|---|
| `batch_id` | Unique simulated batch identifier |
| `recipe_id` | Recipe profile code |
| `recipe_name` | Human-readable recipe name |
| `tea_type` | Simulated tea category |
| `sugar_g_per_l` | Simulated initial sugar concentration |
| `starter_ml` | Simulated starter volume |
| `water_volume_l` | Water volume |
| `day` | Fermentation day |
| `room_temp_c` | Simulated ambient temperature |
| `humidity_percent` | Simulated ambient humidity |
| `ph` | Simulated acidity indicator |
| `brix` | Simulated residual-sweetness proxy |
| `expected_status` | Deterministic rule-generated target label |
| `recommendation` | Rule-generated recommendation |
| `rule_triggered` | Identifier of the rule that produced the label |
| `risk_flag` | Rule-generated risk category |

### 10.3 Recipe profiles

| ID | Recipe name | Tea type | Sugar | Starter | Profile |
|---|---|---|---:|---:|---|
| R1 | Standard Black Tea | black_tea | 80 g/L | 150 mL | normal |
| R2 | High Sugar Black Tea | black_tea | 100 g/L | 150 mL | sweet |
| R3 | Low Sugar Black Tea | black_tea | 60 g/L | 150 mL | low_sugar |
| R4 | Green Tea Standard | green_tea | 80 g/L | 150 mL | normal |
| R5 | High Starter Ratio | black_tea | 80 g/L | 220 mL | fast |
| R6 | Low Starter Ratio | black_tea | 80 g/L | 90 mL | slow |
| R7 | Oolong Mixed Tea | oolong_mixed | 85 g/L | 150 mL | normal |

### 10.4 Simulated value boundaries

| Variable | Minimum | Maximum |
|---|---:|---:|
| Temperature | 15 °C | 35 °C |
| Humidity | 40% | 90% |
| pH | 2.40 | 5.00 |
| Brix | 1.50 | 14.00 |

### 10.5 Dataset quality acceptance criteria

The generated dataset shall satisfy:

- exactly 4,900 rows;
- exactly 16 columns;
- no missing values;
- no duplicate rows;
- exactly 7 recipes;
- exactly 350 batches;
- exactly 14 rows per batch;
- no value outside the configured clipping range;
- decreasing pH trend at batch level;
- decreasing Brix trend at batch level;
- explicit status and triggered-rule distribution outputs.

---

## 11. Rule-Based Readiness Requirements

### 11.1 Inputs

The rule model shall accept:

- temperature;
- humidity;
- pH;
- Brix;
- fermentation day.

Humidity is recorded and displayed as an environmental variable. It is not currently used as a primary readiness threshold.

### 11.2 Outputs

The rule model shall return:

- `status`;
- `recommendation`;
- `rule_triggered`;
- `risk_flag`.

### 11.3 Status vocabulary

The supported statuses are:

- `too_early`;
- `still_sweet`;
- `balanced`;
- `too_sour`;
- `temperature_warning`;
- `manual_check`.

### 11.4 Implemented rules

| Priority | Condition | Status | Rule identifier |
|---:|---|---|---|
| 1 | `temperature > 30` | `temperature_warning` | `R1_high_temperature_warning` |
| 2 | `temperature < 18` | `manual_check` | `R2_low_temperature_slow_fermentation` |
| 3 | `day > 14` and (`pH < 3.2` or `Brix < 5.0`) | `too_sour` | `R11_extended_over_fermentation` |
| 4 | `pH > 4.2` | `too_early` | `R3_early_acidity_stage` |
| 5 | `pH < 3.0` or `Brix < 5.0` | `too_sour` | `R4_R5_over_acidic_or_low_sweetness` |
| 6 | `day < 5` and `3.2 ≤ pH ≤ 4.2` | `manual_check` | `R9_early_day_manual_check` |
| 7 | `3.2 ≤ pH ≤ 4.2` and `Brix > 8.0` | `still_sweet` | `R6_sweet_fermentation_stage` |
| 8 | `3.2 ≤ pH ≤ 4.2`, `5.0 ≤ Brix ≤ 8.0`, and `day ≥ 7` | `balanced` | `R10_balanced_ready_window` |
| 9 | `3.2 ≤ pH ≤ 4.2`, `5.0 ≤ Brix ≤ 8.0`, and `day < 7` | `balanced` with early manual taste guidance | `R7_balanced_but_early` |
| Fallback | No previous rule matches | `manual_check` | `R8_ambiguous_condition` |

### 11.5 Rule-model claim boundary

The rule model represents transparent decision-support logic. It does not represent microbiological validation, food-safety certification, or validated biological readiness.

---

## 12. Machine-Learning Requirements

### 12.1 ML purpose

The ML component shall not be presented as a replacement for the deterministic rule engine.

Its current purpose is to act as a controlled rule-label approximation baseline for validating:

- feature preparation;
- model training;
- serialization;
- deserialization;
- Flask inference;
- confidence reporting;
- Node-RED integration;
- hybrid disagreement handling;
- future replacement by models trained on empirical labels.

### 12.2 Features

The final model shall use:

1. encoded `recipe_id`;
2. encoded `tea_type`;
3. `sugar_g_per_l`;
4. `starter_ml`;
5. `water_volume_l`;
6. `day`;
7. `room_temp_c`;
8. `humidity_percent`;
9. `ph`;
10. `brix`.

### 12.3 Target

The target shall be encoded from `expected_status`.

### 12.4 Leakage-aware split

The final evaluation shall use `GroupShuffleSplit` grouped by `batch_id`.

Configuration:

```text
n_splits = 1
test_size = 0.20
random_state = 42
```

Required split result:

- training rows: 3,920;
- test rows: 980;
- training batches: 280;
- test batches: 70;
- overlapping `batch_id`: 0.

The earlier random row split may remain in the notebook only as a clearly labeled initial baseline. It shall not be presented as the final evaluation.

### 12.5 Candidate algorithms

| Model | Configuration |
|---|---|
| Decision Tree | `max_depth=8`, `random_state=42` |
| Random Forest | `n_estimators=150`, `max_depth=12`, `random_state=42` |
| Gradient Boosting | `learning_rate=0.1`, `n_estimators=100`, `max_depth=3`, `subsample=1.0`, `max_features=None`, `random_state=42` |
| KNN | `n_neighbors=7`, preceded by `StandardScaler` |
| Logistic Regression | `max_iter=1500`, preceded by `StandardScaler` |

No hyperparameter optimization was performed in the completed baseline experiment. The serialized estimators were created with scikit-learn 1.6.1; the release environment shall pin a compatible scikit-learn version because pickle/joblib compatibility is not guaranteed across versions.

### 12.6 Selection criterion

The implemented comparison reports:

- accuracy;
- weighted precision;
- weighted recall;
- weighted F1-score;
- classification report;
- confusion matrix.

The selected model is Gradient Boosting.

Final recorded performance:

```text
Accuracy:          0.995918
Weighted F1-score: 0.995921
```

### 12.6.1 Inspected serialized model contract

The uploaded model artifact confirms:

```text
Estimator:       GradientBoostingClassifier
Training library: scikit-learn 1.6.1
Input features:  10
Output classes:  6
Random state:    42
```

A representative valid payload using recipe `R1`, day 7, temperature `24.4`, humidity `68.0`, pH `3.56`, and Brix `7.71` was inspected directly against the serialized model. The model returned `balanced` with a top-class probability of approximately `0.9998`. This inspection confirms artifact compatibility with the feature list and encoders; it is not an additional evaluation result and shall not replace the reported grouped test metrics.


### 12.7 Interpretation requirement

The high score shall be interpreted as successful approximation of deterministic rule-generated labels under a batch-aware split.

It shall not be interpreted as:

- independent biological understanding;
- proof of real fermentation prediction;
- proof that ML is superior to direct rule execution;
- evidence of food-safety validity.

---

## 13. Hybrid Decision Requirements

### 13.1 Inputs

The hybrid layer shall accept:

- `rule_status`;
- `ml_status`;
- `ml_confidence`;
- `rule_triggered`;
- `risk_flag`;
- rule-generated recommendation context.

### 13.2 Decision sequence

The hybrid layer shall apply the following ordered logic:

1. If the rule result is `temperature_warning`, preserve `temperature_warning`.
2. If ML confidence is below `0.70`, return `manual_check`.
3. If the rule and ML statuses agree, return the shared status.
4. If either component returns `too_sour` while the other disagrees, return `manual_check`.
5. For any other disagreement, return `manual_check`.

The hybrid layer is not a majority-vote ensemble.

### 13.3 Confidence threshold

The `0.70` confidence cutoff is a predefined conservative readiness-oriented heuristic.

A top-class score below `0.70` leaves more than `0.30` of the model-reported probability mass outside the selected class and therefore triggers manual inspection.

The threshold was not empirically optimized. Probability calibration and threshold-sensitivity analysis are future requirements before deployment.

### 13.4 Outputs

The hybrid layer shall return:

- `rule_status`;
- `ml_status`;
- `ml_confidence`;
- `final_status`;
- `decision_reason`;
- `rule_triggered`;
- `risk_flag`;
- `recommendation`.

### 13.5 Recommendation mapping

| Final status | Recommendation intent |
|---|---|
| `too_early` | Continue fermentation and check again |
| `still_sweet` | Continue fermentation or begin taste testing |
| `balanced` | Begin taste testing and consider bottling |
| `too_sour` | Treat as possible over-fermentation; consider starter use or dilution based on preference |
| `temperature_warning` | Move the batch to a cooler area and monitor closely |
| `manual_check` | Perform visual, aroma, pH, Brix, and taste inspection before deciding |

### 13.6 Hybrid acceptance criteria

The scripted validation shall demonstrate:

- rule and ML agreement;
- low-confidence fallback;
- ordinary disagreement fallback;
- conflict involving `too_sour`;
- high-temperature rule override;
- low-temperature manual fallback;
- representative outputs for all six statuses;
- readable `decision_reason`;
- final-status-specific recommendation.

---

## 14. Flask API Requirements

### 14.1 Service environment

The current implementation runs as a local Flask development service:

```text
http://127.0.0.1:5000
```

Cross-origin requests are enabled through `flask-cors`. The three serialized artifacts are loaded at module import, so they are not deserialized again for every request.

### 14.2 Required endpoints

#### `GET /health`

The endpoint shall confirm that the service is available and that the model is loaded.

Observed behavior includes:

```json
{
  "status": "ok"
}
```

and identification of the loaded `GradientBoostingClassifier`.

#### `POST /predict`

The endpoint shall accept one fermentation payload and return the rule, ML, and hybrid outputs.

### 14.3 Request fields

The endpoint checks for the following required fields:

```text
batch_id
recipe_id
tea_type
sugar_g_per_l
starter_ml
water_volume_l
day
room_temp_c
humidity_percent
ph
brix
```

The expected request contract includes:

```json
{
  "batch_id": "KB-WOKWI-001",
  "recipe_id": "R1",
  "tea_type": "black_tea",
  "sugar_g_per_l": 80,
  "starter_ml": 150,
  "water_volume_l": 1.0,
  "day": 7,
  "room_temp_c": 24.4,
  "humidity_percent": 68.0,
  "ph": 3.56,
  "brix": 7.71
}
```

A missing required field produces HTTP 400 with `missing_fields`. Other exceptions are currently caught by a broad handler and returned as HTTP 500.

### 14.4 Response fields

The response shall expose the current input values and at least:

- `rule_status`;
- `ml_status`;
- `ml_confidence`;
- `final_status`;
- `risk_flag`;
- `rule_triggered`;
- `decision_reason`;
- `recommendation`.

### 14.5 Artifact requirements

The API resolves the repository root from the location of `api/app.py`, then loads the following files from `models/` once when the module is imported:

- `scoby_watch_best_group_split_model.pkl`;
- `scoby_watch_label_encoders.pkl`;
- `scoby_watch_feature_columns.pkl`.

The inspected artifacts contain:

- model type: `GradientBoostingClassifier`;
- model class indices: `[0, 1, 2, 3, 4, 5]`;
- ten input features;
- recipe encoder classes: `R1` through `R7`;
- tea-type encoder classes: `black_tea`, `green_tea`, and `oolong_mixed`;
- target classes: `balanced`, `manual_check`, `still_sweet`, `temperature_warning`, `too_early`, and `too_sour`.

The exact ordered feature list is:

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

### 14.6 API boundaries

The current Flask service:

- is local;
- is not production-hosted;
- resolves model artifacts from the repository-level `models/` directory;
- does not use a production WSGI server;
- has no persistent storage;
- enables CORS;
- does not provide authenticated access;
- validates that the request body is a JSON object;
- validates required-field presence;
- does not yet enforce complete numeric ranges or categorical enums before inference;
- may return unknown encoder categories or malformed values through a generic HTTP 500 handler;
- has not been evaluated for production throughput, concurrency, or uptime.

Development execution has been verified using Flask debug mode. The public repository configuration shall default to `debug=False` or use an environment variable so that the interactive debugger is not unintentionally exposed.

Repository hardening shall add explicit schema validation, structured 4xx errors for invalid categories and numeric ranges, a production WSGI command, controlled CORS configuration, and production-safe logging.

---

## 15. MQTT and Node-RED Requirements

### 15.1 MQTT configuration

| Field | Value |
|---|---|
| Broker | `broker.emqx.io` |
| Port | `1883` |
| Topic | `scobywatch/panji/sensor` |
| QoS | `0` |

### 15.2 Input paths

Node-RED shall support:

1. Live payloads received through MQTT.
2. Manual inject payloads for deterministic local testing.

### 15.3 Processing flow

The implemented Node-RED flow shall:

1. receive a JSON payload;
2. parse the payload into a JavaScript object;
3. set `Content-Type: application/json`;
4. send an HTTP `POST` request to `/predict`;
5. parse the response object;
6. safely convert numeric and text fields;
7. route output fields to dashboard widgets;
8. expose the raw hybrid API response through a debug node.

### 15.4 Dashboard widgets

The dashboard shall display:

#### Sensor values

- temperature gauge;
- humidity gauge;
- pH gauge;
- Brix gauge.

#### Trend charts

- temperature trend;
- humidity trend;
- pH trend;
- Brix trend.

#### Batch metadata

- batch ID;
- recipe and tea type;
- fermentation day.

#### Decision fields

- rule status;
- ML status;
- ML confidence;
- final status;
- risk flag;
- triggered rule;
- decision reason;
- recommendation.

### 15.5 Node-RED claim boundary

The dashboard demonstrates real-time prototype integration. It is desktop-oriented, local, and not validated as a production user interface.

---

## 16. Wokwi Simulation Requirements

The Wokwi project shall simulate:

- ESP32 execution;
- DHT22-based temperature and humidity readings;
- analog pH input;
- analog Brix input;
- Wi-Fi connectivity;
- JSON payload construction;
- MQTT publishing.

The pH and Brix inputs represent simulated analog values. They shall not be described as readings from calibrated physical probes or refractometers.

---

## 17. Functional Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-01 | Generate seven recipe profiles | Met |
| FR-02 | Generate 350 batches and 4,900 daily rows | Met |
| FR-03 | Generate pH and Brix trajectories with bounded noise | Met |
| FR-04 | Produce deterministic status, rule, risk, and recommendation fields | Met |
| FR-05 | Export the generated dataset to CSV | Met |
| FR-06 | Run dataset sanity and range checks | Met |
| FR-07 | Verify pH and Brix trend behavior | Met |
| FR-08 | Evaluate five baseline classifiers | Met |
| FR-09 | Preserve the initial random-row baseline as an explicit historical experiment | Met |
| FR-10 | Use batch-aware group splitting for final evaluation | Met |
| FR-11 | Save the selected model, encoders, feature order, and metadata | Met |
| FR-12 | Expose `/`, `/health`, and `/predict` | Met |
| FR-13 | Return rule, ML, confidence, hybrid, reason, risk, and recommendation fields | Met |
| FR-14 | Route low-confidence output to `manual_check` | Met |
| FR-15 | Preserve temperature-warning priority | Met |
| FR-16 | Route disagreements to `manual_check` | Met |
| FR-17 | Receive Wokwi payloads through MQTT | Met |
| FR-18 | Route payloads through Node-RED to Flask | Met |
| FR-19 | Display gauges, trends, metadata, and decision fields | Met |
| FR-20 | Provide normal, edge, warning, low-confidence, and forced-conflict evidence | Met |
| FR-21 | Extract the complete notebook workflow into reusable `src/` modules | Met |
| FR-22 | Provide separate experiment scripts for random-row and split-strategy comparison | Met |
| FR-23 | Provide automated contract tests for dataset, rule, hybrid, model, and API behavior | Met |
| FR-24 | Produce notebook-style TXT evidence from reusable source code | Met |
| FR-25 | Provide dataset, model, API, architecture, reproducibility, and claim-boundary documentation | Met |
| FR-26 | Provide findings reports for generation, quality, training, evaluation, hybrid logic, API, integration, and testing | Met |
| FR-27 | Provide clone-to-run reproducibility documentation | Met |
| FR-28 | Provide MIT licensing and machine-readable citation metadata | Met |
| FR-29 | Provide a GitHub Actions workflow for Python 3.12 tests on Ubuntu | Configured; first hosted run pending |
| FR-30 | Provide `.gitattributes` rules for cross-platform text and binary artifacts | Met |
| FR-31 | Package the project as a clean GitHub repository | In progress |
| FR-32 | Perform clean-clone validation in a fresh directory and environment | Pending |
| FR-33 | Replace the temporary Google Drive data-availability link with a stable repository URL | Pending after public release |

---

## 18. Non-Functional Requirements

### NFR-01. Reproducibility

The released repository shall document:

- Python and dependency versions;
- dataset generation sequence;
- fixed random seeds;
- model configurations;
- group-split configuration;
- artifact file names;
- API startup sequence;
- Node-RED import steps;
- Wokwi execution steps;
- validation commands.

### NFR-02. Transparency

The system shall expose the rule output, ML output, confidence, triggered rule, final status, reason, and recommendation.

### NFR-03. Conservative failure behavior

Uncertain or conflicting outputs shall fall back to `manual_check` rather than silently producing a definitive readiness status.

### NFR-04. Modularity

Sensor simulation, messaging, middleware, inference, decision logic, and visualization shall remain separate components connected through JSON and HTTP/MQTT contracts.

### NFR-05. Traceability

Repository files and evidence shall make it possible to trace:

```text
input payload
→ rule result
→ ML result
→ hybrid result
→ dashboard output
```

### NFR-06. Portability

The dataset and ML experiment shall remain runnable in Google Colab. The API and Node-RED components shall be runnable locally.

### NFR-07. Security disclosure

The repository shall clearly state that the public MQTT broker and local development server are prototype choices and not secure production deployment patterns.

### NFR-08. Safe artifact handling

The repository shall warn users that `.pkl` and `.joblib` files must only be loaded from trusted sources.

### NFR-09. No hidden secrets

The public repository shall not contain:

- passwords;
- personal access tokens;
- broker credentials;
- local absolute paths;
- environment-specific secrets.

### NFR-10. Automated regression protection

The repository shall provide fast `pytest` contract tests that verify dataset integrity, deterministic rules, hybrid arbitration, group-aware splitting, serialized artifacts, feature order, and Flask API behavior without retraining all five classifiers on every test run.

The established baseline is:

```text
34 passed
0 failed
24 warnings
```

### NFR-11. Documentation separation

The repository shall preserve the following separation:

```text
docs/     = technical and methodological reference
reports/  = actual findings, interpretations, and checkpoints
results/  = machine-readable and notebook-style generated evidence
```

### NFR-12. Colab and local parity

The cleaned notebook and modular source code shall represent the same authoritative workflow. The initial random-row experiment shall remain identifiable as historical, while GroupShuffleSplit by `batch_id` remains the official evaluation.


### NFR-13. Cross-platform repository behavior

The repository shall include:

```text
.github/workflows/tests.yml
.gitattributes
```

The workflow shall run import, compilation, and automated-test checks using
Python 3.12 on an Ubuntu runner. This is intended to expose case-sensitive
path issues that may remain hidden on Windows.

The `.gitattributes` file shall normalize text line endings and classify model,
image, PDF, archive, and Office files as binary artifacts.

The workflow configuration is part of the repository. A successful hosted
execution remains a release checkpoint after the first push.

---

## 19. Validation and Evidence Requirements

### 19.1 Dataset evidence

Required evidence includes:

- dataset shape;
- column list;
- missing-value count;
- duplicate count;
- recipe count;
- batch count;
- days per batch;
- status distribution;
- sensor range checks;
- pH and Brix trends;
- rule-trigger distribution;
- sample batch transitions.

### 19.2 ML evidence

Required evidence includes:

- train and test row counts;
- train and test batch counts;
- zero batch overlap;
- model comparison table;
- classification reports;
- best-model confusion matrix;
- saved model and encoder confirmation.

### 19.3 Hybrid evidence

Required evidence includes:

- normal cases;
- edge cases;
- low-confidence case;
- high-temperature priority case;
- `too_sour` conflict case;
- ordinary disagreement case;
- final recommendation mapping.

### 19.4 Integration evidence

Required evidence includes:

- Wokwi simulation;
- MQTT publishing;
- Node-RED MQTT configuration;
- JSON parser configuration;
- Flask request preparation;
- HTTP request node;
- response splitter;
- `/health` output;
- `/predict` response;
- final Node-RED flow;
- sensor dashboard;
- hybrid-output dashboard.

### 19.5 Automated testing evidence

Required evidence includes:

- dataset shape, determinism, ranges, and batch trends;
- all primary rule paths and strict boundary behavior;
- confidence values below and exactly at the `0.70` threshold;
- temperature-warning priority;
- agreement and conflict handling;
- reproducible GroupShuffleSplit with zero batch overlap;
- model, encoder, and feature-order contracts;
- reference-payload prediction;
- valid API response;
- missing-field rejection;
- invalid-JSON rejection.

The current automated-test baseline is:

```text
34 passed
24 warnings
0 failed
```

The warnings originate from internal `joblib` and NumPy compatibility behavior while loading serialized artifacts and do not currently cause test failures.

### 19.6 Notebook-style text evidence

The repository shall be able to generate notebook-style TXT evidence for:

- basic dataset sanity;
- sensor ranges;
- average pH and Brix trends;
- per-batch monotonic checks;
- status-transition samples;
- random-row and group-aware split summaries;
- model classification reports;
- model, encoder, and feature loading;
- one-sample hybrid output.

The exporter is implemented in `src/notebook_text_evidence.py`.

### 19.7 Evidence boundary

The supplementary evidence shall be described as simulation, implementation, and reproducibility evidence.

It shall not be described as laboratory, microbial, biological, or food-safety validation.

---

## 20. Acceptance Criteria

The prototype is accepted as an engineering proof of concept when all of the following are true:

1. The dataset contains 4,900 rows and 350 complete batches.
2. There are no missing or duplicate dataset rows.
3. All generated sensor values remain within configured boundaries.
4. The average and per-batch pH/Brix trends behave as intended.
5. The final train-test split contains no overlapping batch IDs.
6. Five baseline models are evaluated using the same grouped split.
7. Gradient Boosting reproduces the recorded final metrics.
8. The model, encoders, feature order, and metadata can be saved and loaded.
9. `/health` confirms the service and model are available.
10. `/predict` returns the complete hybrid response contract.
11. Temperature warnings override ordinary readiness predictions.
12. Low-confidence and disagreement cases return `manual_check`.
13. Wokwi or manual payloads reach Node-RED.
14. Node-RED successfully forwards payloads to Flask.
15. Flask responses are routed to gauges, charts, and text fields.
16. All six final statuses can be demonstrated.
17. The complete notebook logic is available as reusable source modules.
18. Historical random-row and final grouped experiments are separated and reproducible.
19. The automated suite completes with 34 passing tests and no failures.
20. Technical documentation exists for the dataset, model, API, architecture, reproducibility, and claim boundaries.
21. Findings reports exist for generation, quality, training, evaluation, hybrid logic, API, integration, and testing.
22. Notebook-style TXT evidence can be regenerated from source code.
23. The claim boundary appears in the manuscript, dataset card, model card, API documentation, and claim-boundary document.
24. Root repository documentation, MIT licensing, and `CITATION.cff` metadata are present.
25. GitHub Actions and `.gitattributes` are present and syntactically valid.
26. The public repository can be cloned and executed using documented steps.
27. The first GitHub-hosted CI run completes successfully.
28. No secrets, caches, virtual environments, or machine-specific paths are committed.
29. The public repository URL replaces the temporary Google Drive data-availability link after verification.

Acceptance criteria 1–25 and 28 are met by the current local repository
assembly. Criteria 26, 27, and 29 remain part of the clean-clone and public
release phase.

---

## 21. Risks and Limitations

### 21.1 Construct validity

Readiness labels are deterministic rule outputs rather than expert sensory-panel or laboratory-confirmed outcomes.

### 21.2 Internal validity

The generated trajectories depend on chosen decay ranges, profile factors, Gaussian noise, clipping, and simulated temperature spikes.

### 21.3 External validity

Seven simulated recipes do not represent all tea substrates, sugar types, starter ratios, SCOBY cultures, vessels, climates, handling practices, or production environments.

### 21.4 Model validity

The ML metrics measure rule-label approximation, not biological understanding.

### 21.5 Sensor validity

Wokwi pH and Brix values are analog simulations, not calibrated measurements. The prototype does not evaluate calibration error, drift, fouling, signal conditioning, or food-contact suitability.

### 21.6 System validity

The prototype uses:

- a local Flask development server;
- a public MQTT broker;
- a desktop-oriented Node-RED dashboard;
- no persistent storage;
- no production authentication;
- no production latency, reliability, or delayed-message testing.

### 21.7 Safety validity

No microbial contamination, alcohol, titratable acidity, pathogen, consumer tasting, or food-safety testing was performed.

### 21.8 Threshold validity

The `0.70` confidence threshold is heuristic. It has not been optimized through sensitivity analysis or probability calibration.

---

## 22. Repository Release Requirements

### 22.1 Current assembled structure

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
│   ├── group and random split outputs
│   ├── hybrid-validation CSV files
│   ├── classification-report TXT files
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

The directory must be named lowercase `api/`. Windows may tolerate `API/`,
but the Ubuntu CI runner uses case-sensitive paths.

### 22.2 Repository assembly status

| Area | Status |
|---|---|
| API and model path separation | Met |
| Dataset and validation outputs | Met |
| Serialized model artifacts | Met |
| Modular `src/` pipeline | Met |
| Historical experiment scripts | Met |
| Automated tests | Met locally: 34 passed |
| English technical `docs/` package | Met |
| English findings `reports/` package | Met |
| Notebook-style TXT exporter | Met |
| Node-RED and Wokwi files | Met |
| Curated supplementary evidence package | Met |
| Root README | Met |
| MIT license | Met |
| Base `CITATION.cff` metadata | Met |
| GitHub Actions workflow configuration | Met |
| `.gitattributes` configuration | Met |
| First GitHub-hosted CI run | Pending until push |
| Notebook review against modular source | In progress |
| Final dependency review | In progress |
| Clean-clone rehearsal | Pending |
| GitHub publication | Pending |
| Permanent repository URL in citation and manuscript | Pending |
| Optional release DOI | Pending |

### 22.3 Notebook cleanup

Before publication, the notebook shall:

- use the `.ipynb` extension;
- distinguish the initial random split from the final group split;
- remove irrelevant exploratory output;
- retain the final random seed and model configurations;
- use repository-relative paths where applicable;
- include a clear run order;
- cross-reference the equivalent reusable modules under `src/`;
- be reviewed against the modular source to prevent contradictory logic.

### 22.4 Release hygiene

The release shall contain one authoritative version of each major artifact:

- dataset;
- notebook;
- modular source;
- experiment scripts;
- automated tests;
- model artifacts;
- API;
- Node-RED flow;
- Wokwi project;
- generated validation outputs;
- English technical documentation;
- English findings reports;
- supplementary evidence PDF;
- root README, PRD, license, citation metadata, CI workflow, and
  `.gitattributes`.

Drafts, duplicate ZIP files, failed diagrams, plagiarism screenshots,
obsolete model artifacts, raw conversation archives, virtual environments,
caches, and local machine paths shall not be included.

---

## 23. Source-of-Truth Artifacts

The as-built PRD is grounded in the completed project artifacts:

1. Final research manuscript.
2. `SCOBY WATCH DATASET + ML BASELINE.ipynb`.
3. Modular reusable source under `src/`.
4. Historical and comparison scripts under `experiments/`.
5. Flask API under `api/app.py`.
6. Serialized Gradient Boosting model, encoders, feature order, and metadata.
7. Node-RED flow.
8. Wokwi project files.
9. Generated dataset and validation outputs.
10. Hybrid standard, edge-case, and forced-conflict outputs.
11. Automated tests under `tests/`.
12. Technical documentation under `docs/`.
13. Findings reports under `reports/`.
14. Curated supplementary simulation and implementation evidence.
15. Supplementary README.
16. Project decision and development records.
17. Root `README.md`, MIT `LICENSE`, and `CITATION.cff`.
18. `.github/workflows/tests.yml` and `.gitattributes`.

The long exported project conversations are internal historical records and shall not be published in the public repository.

---

## 24. Future Development Roadmap

### Phase 2. Repository hardening

Completed:

- converted the notebook file to `.ipynb`;
- extracted reusable logic into modular Python files;
- separated historical random-row experiments from the official grouped evaluation;
- added dependency requirement files;
- added automated tests;
- added English dataset, model, API, architecture, reproducibility, and
  claim-boundary documentation;
- added English generation, quality, training, evaluation, hybrid, API,
  integration, and testing reports;
- added notebook-style TXT evidence generation;
- added a curated supplementary evidence package;
- verified the Flask API and serialized artifacts locally;
- established a 34-test local automated baseline;
- finalized the root README;
- selected the MIT license;
- added base `CITATION.cff` metadata;
- added GitHub Actions configuration for Python 3.12 on Ubuntu;
- added `.gitattributes` for cross-platform line endings and binary artifacts.

Remaining:

- ensure the API directory is lowercase `api/`;
- review the notebook against the modular source;
- complete the final dependency review;
- remove duplicate drafts, caches, and local-only files;
- push the repository and verify the first hosted CI run;
- perform a clean-clone rehearsal;
- create or verify the public Wokwi URL;
- replace temporary data-availability links with the verified repository URL;
- optionally create a release tag and archival DOI.

### Phase 3. Physical sensing pilot

- Replace analog pH simulation with a calibrated pH measurement process.
- Replace analog Brix simulation with validated manual or digital measurements.
- Evaluate calibration, drift, cleaning, and food-contact constraints.
- Collect empirical batch trajectories.

### Phase 4. Empirical model development

- Define labels through structured sensory and laboratory procedures.
- Train models on empirical observations.
- Compare rule-only, synthetic-trained, and empirical-trained baselines.
- Calibrate probabilities.
- Perform confidence-threshold sensitivity analysis.
- Evaluate temporal consistency across daily observations.

### Phase 5. Production-oriented system evaluation

- Replace the Flask development server with a production WSGI server.
- Add authenticated and encrypted messaging.
- Add persistent historical storage.
- Test delayed messages, missing data, sensor noise, network interruption, and recovery.
- Add mobile usability and richer uncertainty visualization.

### Phase 6. Safety and laboratory research

This phase requires qualified food-science and laboratory collaboration. It may include:

- microbial analysis;
- alcohol measurement;
- titratable acidity;
- contamination and pathogen protocols;
- controlled sensory studies;
- consumer-facing safety procedures.

No consumer-facing safety claim may be introduced before this phase is completed.

---

## 25. Open Release Decisions

The following items remain before the reproducibility release is complete:

1. Final public GitHub repository URL.
2. Verification of the first GitHub Actions run.
3. Final exact dependency pins, including the installed `matplotlib` version;
   scikit-learn 1.6.1 remains the artifact-creation baseline unless the model
   is retrained.
4. Final public Wokwi project URL.
5. Whether the manuscript PDF is included in the repository or distributed
   separately.
6. Whether Google Drive remains as a backup mirror.
7. Whether the current MQTT topic is retained or replaced with a generic
   public example topic.
8. Whether an archived release and DOI are created.

The following decisions are complete:

```text
License                       = MIT
Citation base metadata        = CITATION.cff present
Supplementary evidence title  = Simulation and Implementation Evidence
Flask debug default           = false
Root README                   = finalized
Model artifacts               = stored directly in the repository
README screenshots            = omitted; curated evidence is stored separately
```

---

## 26. Definition of Done

The SCOBY Watch public reproducibility release is complete when:

| Requirement | Status |
|---|---|
| Final source files are organized in the repository | Met |
| Dataset can be regenerated | Met |
| Dataset validation outputs can be regenerated | Met |
| Random-row historical baseline can be reproduced | Met |
| Grouped evaluation can be reproduced | Met |
| Model artifacts can be regenerated and loaded | Met |
| Flask starts using documented commands | Met |
| Automated suite completes with 34 passing tests locally | Met |
| English technical documentation is present | Met |
| English findings reports are present | Met |
| Notebook-style TXT evidence can be regenerated | Met |
| Supplementary evidence package is present | Met |
| Node-RED imports without broken nodes | Met in current local prototype |
| Wokwi publishes a valid payload | Met in current simulation prototype |
| End-to-end dashboard displays expected outputs | Met in current local prototype |
| Root README is finalized | Met |
| MIT license is present | Met |
| Base `CITATION.cff` metadata is present | Met |
| GitHub Actions workflow is configured | Met |
| `.gitattributes` is configured | Met |
| API directory uses the lowercase `api/` path | Must be confirmed before push |
| Notebook is reviewed against the modular source | In progress |
| Final dependency review is complete | In progress |
| First GitHub-hosted CI run succeeds | Pending |
| Repository passes a fresh clean-clone rehearsal | Pending |
| Repository is public | Pending |
| Manuscript data-availability statement points to the verified repository | Pending |
| Permanent repository URL is added to `CITATION.cff` | Pending |
| Optional archival DOI is added | Optional |

The engineering prototype and local repository assembly are complete. The
public reproducibility release remains incomplete until the lowercase path
check, hosted CI run, clean-clone rehearsal, publication, and permanent URL
updates are completed.

---

## 27. Final Product Boundary

SCOBY Watch is a completed simulation-first engineering and research prototype for kombucha fermentation readiness-oriented decision support.

It demonstrates:

- synthetic data generation;
- deterministic readiness logic;
- leakage-aware ML evaluation;
- model serving;
- conservative hybrid arbitration;
- MQTT and Node-RED integration;
- dashboard visualization;
- reproducibility-oriented evidence.

It does not certify that kombucha is safe, biologically validated, healthy, commercially acceptable, or ready for unrestricted consumer use.

Calibrated physical sensors, empirical fermentation data, laboratory confirmation, biological validation, safety protocols, and realistic deployment testing remain mandatory before any consumer-facing implementation.
---

## 28. Version History

### Version 1.3 — 2026-07-30

Version 1.3 aligns the PRD with the final local repository assembly.

Added or updated:

- finalized root `README.md`;
- MIT `LICENSE`;
- base `CITATION.cff` metadata;
- English `docs/` and `reports/` packages;
- curated supplementary evidence package;
- GitHub Actions configuration for Python 3.12 on Ubuntu;
- `.gitattributes` line-ending and binary-artifact policy;
- updated repository structure and release-readiness matrix;
- updated functional requirements and acceptance criteria;
- completed release decisions for licensing, citation base metadata,
  supplementary naming, Flask debug defaults, and model-artifact handling;
- remaining hosted CI, clean-clone, publication, permanent URL, and optional
  DOI tasks.

### Version 1.2 — 2026-07-29

Version 1.2 updated the PRD from a packaging plan to the assembled modular
repository state.

Added or updated:

- complete modular `src/` pipeline;
- `experiments/` scripts for random-row and split-strategy analysis;
- `tests/` with 34 passing local contract tests;
- notebook-style TXT evidence exporter;
- technical documentation package;
- findings package;
- repository-relative model loading;
- current API validation behavior;
- release-readiness matrix;
- updated functional requirements and acceptance criteria.
