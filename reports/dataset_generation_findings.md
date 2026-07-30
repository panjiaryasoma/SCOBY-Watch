# Dataset Generation Findings — SCOBY Watch

**Project:** SCOBY Watch  
**Component:** Synthetic fermentation dataset generator  
**Implementation:** `src/generate_dataset.py`  
**Configuration:** `src/config.py`  
**Random state:** 42  
**Status:** Completed and reproducible  

---

## 1. Purpose

This stage was designed to generate a synthetic dataset that can be used to:

- validate the rule-based labeling workflow;
- train machine-learning baselines;
- test batch-aware splitting;
- test model serialization;
- test the Flask API;
- test the Hybrid Decision Layer;
- test Node-RED integration before physical sensors are available.

The dataset was not designed as a substitute for biological or laboratory data.

---

## 2. Dataset Configuration

| Component | Value |
|---|---:|
| Recipe profiles | 7 |
| Batches per recipe | 50 |
| Total batches | 350 |
| Days per batch | 14 |
| Total observations | 4,900 |
| Total columns | 16 |
| Random state | 42 |

Observation-count formula:

```text
7 recipes × 50 batches × 14 days = 4,900 observations
```

---

## 3. Recipe Profiles

| ID | Name | Tea type | Sugar | Starter | Profile |
|---|---|---|---:|---:|---|
| R1 | Standard Black Tea | `black_tea` | 80 g/L | 150 mL | normal |
| R2 | High Sugar Black Tea | `black_tea` | 100 g/L | 150 mL | sweet |
| R3 | Low Sugar Black Tea | `black_tea` | 60 g/L | 150 mL | low_sugar |
| R4 | Green Tea Standard | `green_tea` | 80 g/L | 150 mL | normal |
| R5 | High Starter Ratio | `black_tea` | 80 g/L | 220 mL | fast |
| R6 | Low Starter Ratio | `black_tea` | 80 g/L | 90 mL | slow |
| R7 | Oolong Mixed Tea | `oolong_mixed` | 85 g/L | 150 mL | normal |

Each profile affects the pH and Brix decline rates.

---

## 4. Generation Workflow

The generator applies the following sequence:

```text
recipe configuration
→ batch-level variation
→ initial pH and Brix
→ profile-specific decline rate
→ starter-ratio adjustment
→ daily environmental noise
→ pH and Brix trajectories
→ clipping
→ Rule Model v1.1 labeling
```

Batch-level variation uses controlled random distributions for:

- actual sugar concentration;
- actual starter volume;
- base temperature;
- base humidity;
- initial pH;
- initial Brix;
- pH decline rate;
- Brix decline rate.

---

## 5. Environmental Simulation

Daily temperature is generated from the batch-level base temperature plus
daily noise.

A small subset of batches receives elevated base-temperature conditions to
produce `temperature_warning` scenarios.

Humidity is simulated as a monitoring variable. In Rule Model v1.1, humidity
is not used as a primary readiness threshold.

---

## 6. Trajectory Design

In general:

```text
pH(day) = initial_pH - pH_decline × day + noise
Brix(day) = initial_Brix - Brix_decline × day + noise
```

The generated values are then clipped.

| Variable | Minimum | Maximum |
|---|---:|---:|
| Temperature | 15 °C | 35 °C |
| Humidity | 40% | 90% |
| pH | 2.40 | 5.00 |
| Brix | 1.50 | 14.00 |

The `fast` profile has a higher decline rate, whereas the `slow` profile has
a lower decline rate.

A high starter ratio accelerates the synthetic trajectory. A low starter
ratio slows it down.

---

## 7. Rule-Based Label Generation

Each observation is assigned:

- `expected_status`;
- `recommendation`;
- `rule_triggered`;
- `risk_flag`.

Generated target classes:

```text
balanced
manual_check
still_sweet
temperature_warning
too_early
too_sour
```

The labels are produced by Rule Model v1.1, not by expert annotation or
laboratory analysis.

---

## 8. Generator Results

Final output:

```text
Dataset shape: (4900, 16)
Unique recipes: 7
Unique batches: 350
Days per batch: 14
```

Each recipe produces:

```text
700 observations
```

because:

```text
50 batches × 14 days = 700 observations
```

---

## 9. Determinism

The automated test runs the generator twice using:

```text
random_state = 42
```

Both DataFrames must be identical.

Test:

```text
test_generated_dataset_is_deterministic
```

Result:

```text
PASSED
```

Determinism is necessary so that:

- the dataset can be regenerated;
- the split can be reproduced;
- the metrics can be audited;
- the model artifacts can be inspected consistently.

---

## 10. Artifacts

Main output:

```text
data/
└── scoby_watch_simulated_dataset.csv
```

Command:

```powershell
python -m src.generate_dataset
```

Full pipeline:

```powershell
python -m src.run_pipeline
```

---

## 11. Findings

- The generator produced the required dataset dimensions.
- All recipes contain an equal number of observations.
- Every batch contains 14 observations.
- The fixed random state produces identical output.
- Rule-generated labels are available directly for model training.
- The generator supports all final statuses, including warnings and manual fallback.

---

## 12. Limitations

1. The formulas are simulation designs.
2. The noise does not come from physical sensors.
3. Calibration error is not modeled.
4. Sensor drift is not modeled.
5. Vessel-specific effects are not modeled.
6. No microbial measurements are included.
7. No alcohol measurements are included.
8. No sensory-panel annotations are included.
9. No laboratory-confirmed readiness labels are included.
10. The labels depend entirely on the rule engine.

---

## 13. Conclusion

The dataset generator satisfies the defined engineering contract and can
reproduce 4,900 observations deterministically.

The dataset is suitable for software testing, rule-label approximation,
model serving, and system-integration testing.

The dataset must not be presented as biological ground truth.
