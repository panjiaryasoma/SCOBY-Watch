# Data Quality Findings — SCOBY Watch

**Project:** SCOBY Watch  
**Dataset:** SCOBY Watch Synthetic Fermentation Dataset  
**Validation implementation:** `src/validate_dataset.py`  
**Status:** Integrity, range, trend, and distribution checks completed  

---

## 1. Purpose

This stage verifies whether the generated dataset satisfies the required
contract before it is used for training and evaluation.

The checks cover:

- dataset dimensions;
- columns;
- missing values;
- duplicate rows;
- number of recipes;
- number of batches;
- observations per batch;
- sensor ranges;
- pH trends;
- Brix trends;
- status distribution;
- rule distribution;
- status transitions per batch.

---

## 2. Dataset Summary

| Component | Value |
|---|---:|
| Rows | 4,900 |
| Columns | 16 |
| Missing values | 0 |
| Duplicate rows | 0 |
| Unique recipes | 7 |
| Unique batches | 350 |
| Unique days | 14 |
| Minimum rows per batch | 14 |
| Maximum rows per batch | 14 |

Each recipe contains:

```text
700 observations
```

---

## 3. Columns

```text
batch_id
recipe_id
recipe_name
tea_type
sugar_g_per_l
starter_ml
water_volume_l
day
room_temp_c
humidity_percent
ph
brix
expected_status
recommendation
rule_triggered
risk_flag
```

No required columns were missing from the dataset contract.

---

## 4. Status Distribution

| Status | Count | Percentage |
|---|---:|---:|
| `too_sour` | 1,461 | 29.82% |
| `balanced` | 1,119 | 22.84% |
| `too_early` | 1,047 | 21.37% |
| `manual_check` | 592 | 12.08% |
| `still_sweet` | 444 | 9.06% |
| `temperature_warning` | 237 | 4.84% |
| **Total** | **4,900** | **100%** |

The distribution is not perfectly balanced. However, all classes are present,
and the warning class remains represented.

---

## 5. Sensor-Range Summary

| Variable | Mean | Std | Min | Median | Max |
|---|---:|---:|---:|---:|---:|
| Temperature | 25.4258 | 2.4142 | 17.54 | 25.31 | 34.30 |
| Humidity | 67.8765 | 7.9324 | 40.00 | 67.81 | 90.00 |
| pH | 3.6864 | 0.6098 | 2.40 | 3.75 | 5.00 |
| Brix | 6.5149 | 2.7214 | 1.50 | 6.76 | 13.99 |
| Sugar | 80.5575 | 11.5844 | 53.05 | 81.10 | 108.66 |
| Starter | 151.8796 | 37.6745 | 67.49 | 149.845 | 261.15 |

---

## 6. Range Issues

| Check | Violations |
|---|---:|
| Temperature < 15 | 0 |
| Temperature > 35 | 0 |
| Humidity < 40 | 0 |
| Humidity > 90 | 0 |
| pH < 2.4 | 0 |
| pH > 5.0 | 0 |
| Brix < 1.5 | 0 |
| Brix > 14 | 0 |

All values remain within the configured clipping ranges.

This confirms generator consistency, not the validity of real-world sensor
ranges.

---

## 7. Average pH Trend by Day

| Day | Average pH |
|---:|---:|
| 1 | 4.506943 |
| 2 | 4.381400 |
| 3 | 4.251971 |
| 4 | 4.117229 |
| 5 | 3.993971 |
| 6 | 3.859886 |
| 7 | 3.737086 |
| 8 | 3.610943 |
| 9 | 3.469829 |
| 10 | 3.350229 |
| 11 | 3.236314 |
| 12 | 3.131571 |
| 13 | 3.028457 |
| 14 | 2.933600 |

Average pH decreases consistently across the 14-day period.

---

## 8. Average Brix Trend by Day

| Day | Average Brix |
|---:|---:|
| 1 | 9.589286 |
| 2 | 9.107457 |
| 3 | 8.648400 |
| 4 | 8.120343 |
| 5 | 7.625114 |
| 6 | 7.128229 |
| 7 | 6.634543 |
| 8 | 6.183657 |
| 9 | 5.694000 |
| 10 | 5.251371 |
| 11 | 4.816486 |
| 12 | 4.453314 |
| 13 | 4.141486 |
| 14 | 3.815514 |

Average Brix also decreases consistently.

---

## 9. Monotonic Trend per Batch

Number of batches:

```text
350
```

Results:

```text
pH trend OK: 350
Brix trend OK: 350
Suspicious pH trend: 0
Suspicious Brix trend: 0
```

The check uses a linear slope for each batch.

All pH and Brix slopes are negative.

---

## 10. Status Transitions

The status-transition sample shows patterns such as:

```text
too_early
→ manual_check or still_sweet
→ balanced
→ manual_check or too_sour
```

Batches with high temperature can produce:

```text
temperature_warning
```

on multiple days because the temperature rule has priority.

Status transitions are not required to be monotonic because of:

- daily noise;
- temperature spikes;
- threshold boundaries;
- clipping;
- rule priority.

---

## 11. Artifacts

```text
data/validation/
├── sanity_dataset_summary.json
├── sanity_sensor_range_summary.csv
├── sanity_sensor_range_issues.csv
├── sanity_status_by_day.csv
├── sanity_status_by_recipe.csv
├── sanity_ph_by_day.csv
├── sanity_brix_by_day.csv
├── sanity_ph_by_recipe.csv
├── sanity_brix_by_recipe.csv
├── sanity_batch_trend_check.csv
├── sanity_rule_distribution.csv
└── sanity_status_transition_samples.txt
```

Plots:

```text
reports/
├── average_ph_by_day.png
├── average_brix_by_day.png
├── average_ph_by_recipe.png
├── average_brix_by_recipe.png
├── status_distribution_by_day.png
├── status_distribution_by_recipe.png
└── rule_triggered_distribution.png
```

---

## 12. Automated Test

Command:

```powershell
python -m pytest tests/test_dataset.py -v
```

Result:

```text
5 passed in 1.39s
```

---

## 13. Main Findings

- The dataset satisfies the required dimensions.
- No missing values were found.
- No duplicate rows were found.
- All batches are complete.
- All values remain within the configured ranges.
- Average pH decreases.
- Average Brix decreases.
- All batches have negative pH and Brix slopes.
- All target statuses are represented.

---

## 14. Interpretation Risks

Passing the sanity checks does not mean that:

- the trajectories are identical to real fermentation;
- physical sensors will be free from error;
- pH and Brix alone are sufficient to determine safety;
- the status distribution represents a real kombucha population;
- the simulation formulas have been biologically validated.

---

## 15. Conclusion

The dataset is considered valid for the scope of synthetic software and
integration testing.

The dataset is not yet valid as an empirical fermentation dataset.
