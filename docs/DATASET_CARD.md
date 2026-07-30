# Dataset Card — SCOBY Watch Synthetic Fermentation Dataset

## 1. Summary

The SCOBY Watch dataset is a synthetic dataset designed to test the complete
kombucha-fermentation monitoring and decision-support workflow.

The dataset is used to:

- validate the dataset generator;
- test Rule Model v1.1;
- train machine-learning baselines;
- compare random-row and group-aware splits;
- test model serialization;
- test the Flask API;
- test the Hybrid Decision Layer;
- support Node-RED and dashboard integration.

The dataset is not produced from physical measurements, laboratory
experiments, or commercial fermentation observations.

---

## 2. Dataset Identity

| Field | Value |
|---|---|
| Name | SCOBY Watch Synthetic Fermentation Dataset |
| Type | Synthetic multivariate time-series-like tabular dataset |
| Domain | Kombucha fermentation readiness-oriented monitoring |
| Recipe profiles | 7 |
| Batches per recipe | 50 |
| Total batches | 350 |
| Days per batch | 14 |
| Total observations | 4,900 |
| Columns | 16 |
| Random state | 42 |
| Target | `expected_status` |
| Primary format | CSV |

---

## 3. Dataset Structure

| Column | Conceptual type | Description |
|---|---|---|
| `batch_id` | identifier | Unique synthetic batch identifier |
| `recipe_id` | categorical | Recipe ID from `R1` to `R7` |
| `recipe_name` | categorical | Recipe name |
| `tea_type` | categorical | Synthetic tea type |
| `sugar_g_per_l` | numeric | Initial sugar concentration per liter |
| `starter_ml` | numeric | Starter volume |
| `water_volume_l` | numeric | Water volume |
| `day` | integer | Fermentation day |
| `room_temp_c` | numeric | Synthetic room temperature |
| `humidity_percent` | numeric | Synthetic humidity |
| `ph` | numeric | Synthetic pH value |
| `brix` | numeric | Synthetic Brix value |
| `expected_status` | target | Rule-generated status label |
| `recommendation` | text | Rule-generated recommendation |
| `rule_triggered` | categorical | Rule that generated the label |
| `risk_flag` | categorical | Rule-generated risk category |

---

## 4. Recipe Profiles

| ID | Recipe | Tea type | Sugar | Starter | Profile |
|---|---|---|---:|---:|---|
| R1 | Standard Black Tea | `black_tea` | 80 g/L | 150 mL | normal |
| R2 | High Sugar Black Tea | `black_tea` | 100 g/L | 150 mL | sweet |
| R3 | Low Sugar Black Tea | `black_tea` | 60 g/L | 150 mL | low_sugar |
| R4 | Green Tea Standard | `green_tea` | 80 g/L | 150 mL | normal |
| R5 | High Starter Ratio | `black_tea` | 80 g/L | 220 mL | fast |
| R6 | Low Starter Ratio | `black_tea` | 80 g/L | 90 mL | slow |
| R7 | Oolong Mixed Tea | `oolong_mixed` | 85 g/L | 150 mL | normal |

The profiles are designed to produce varied pH and Brix trajectories while
remaining inside the configured simulation boundaries.

---

## 5. Generation Method

The main generator is located at:

```text
src/generate_dataset.py
```

Shared configuration is located at:

```text
src/config.py
```

Conceptual generation flow:

```text
recipe profile
→ batch-level variation
→ initial pH and Brix
→ profile-specific decline rates
→ starter-ratio adjustment
→ daily temperature and humidity noise
→ daily pH and Brix trajectories
→ value clipping
→ Rule Model v1.1 labeling
```

The generator uses a fixed random state:

```text
random_state = 42
```

This allows the dataset to be regenerated deterministically.

---

## 6. Simulation Boundaries

| Variable | Minimum | Maximum |
|---|---:|---:|
| `room_temp_c` | 15.00 | 35.00 |
| `humidity_percent` | 40.00 | 90.00 |
| `ph` | 2.40 | 5.00 |
| `brix` | 1.50 | 14.00 |

The values are clipped to the configured ranges. Therefore, remaining inside
those ranges does not prove that real sensors will have the same
distribution, noise, or error characteristics.

---

## 7. Labels

The `expected_status` target is produced by Rule Model v1.1.

Available labels:

```text
balanced
manual_check
still_sweet
temperature_warning
too_early
too_sour
```

The labels do not come from:

- fermentation experts;
- sensory panels;
- alcohol measurements;
- titratable-acidity measurements;
- microbial testing;
- pathogen testing;
- laboratory inspection.

Therefore, the machine-learning model trained on this dataset learns to
approximate rule-generated labels.

---

## 8. Quality Checks

Automated tests and validation scripts inspect:

- row and column counts;
- recipe and batch counts;
- observations per batch;
- missing values;
- duplicate rows;
- sensor ranges;
- pH slopes by batch;
- Brix slopes by batch;
- status distributions;
- rule distributions;
- status-transition samples.

Final contract:

```text
rows = 4,900
columns = 16
recipes = 7
batches = 350
observations per batch = 14
missing values = 0
duplicate rows = 0
```

All 350 batches have negative pH and Brix slopes in the current validation
results.

---

## 9. Intended Use

The dataset is suitable for:

- synthetic-data-generation demonstrations;
- tabular machine-learning pipeline testing;
- group-aware split testing;
- rule-label approximation testing;
- model-serialization testing;
- API and hybrid-logic testing;
- reproducible machine-learning education;
- IoT-integration testing before physical sensors are available.

---

## 10. Out-of-Scope Use

The dataset must not be used as evidence of:

- food safety;
- consumption readiness;
- microbiological safety;
- commercial quality;
- effectiveness of a specific kombucha recipe;
- sensor calibration;
- real fermentation prediction;
- biological validity across environments;
- medical or nutritional recommendations.

---

## 11. Biases and Risks

The dataset inherits assumptions from:

- the seven selected recipe profiles;
- the pH and Brix decline ranges;
- Gaussian noise;
- value clipping;
- base-temperature distributions;
- temperature-warning scenarios;
- Rule Model v1.1 priority order.

The primary risk is that users may interpret synthetic data as biological
ground truth. Documentation must always state that the target is generated by
deterministic rules.

---

## 12. Dataset Reproduction

From the repository root:

```powershell
python -m src.generate_dataset
```

Validation:

```powershell
python -m src.validate_dataset
python -m pytest tests/test_dataset.py -v
```

Main output:

```text
data/
└── scoby_watch_simulated_dataset.csv
```

Validation outputs:

```text
data/validation/
```

---

## 13. Versioning and Changes

Any change to the following should be treated as a new dataset version:

- recipe profiles;
- trajectory formulas;
- random state;
- clipping boundaries;
- rule engine;
- number of batches;
- number of days.

Existing model artifacts must not be used with a new dataset version without
retraining and reevaluation.
