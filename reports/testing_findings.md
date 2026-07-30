# Testing Findings — SCOBY Watch

**Project:** SCOBY Watch  
**System type:** Simulation-First IoT and Hybrid Decision Support Framework  
**Tested components:** dataset generator, rule engine, hybrid decision layer, serialized model contract, and Flask API  
**Status:** All automated tests completed successfully  
**Runtime:** Python 3.12.7  
**Test framework:** pytest 8.4.2  
**Final result:** 34 passed, 24 warnings, 0 failed  

---

## 1. Testing Purpose

Testing was performed to ensure that the main SCOBY Watch components remain
consistent after the notebook code was separated into reusable modules under
`src/`.

The main testing objectives were to:

- ensure that the synthetic dataset can be regenerated deterministically;
- ensure that the dataset structure satisfies the research contract;
- ensure that Rule Model v1.1 produces the correct status for main conditions
  and boundary values;
- ensure that the Hybrid Decision Layer applies the correct priority order;
- ensure that the final split by `batch_id` does not contain batch leakage;
- ensure that the saved model, encoders, and feature order remain compatible;
- ensure that the Flask API returns responses that satisfy the contract;
- ensure that invalid requests are rejected before inference;
- ensure that all tests can be executed automatically using `pytest`.

These tests verify software-implementation consistency. The results do not
demonstrate biological fermentation validity, food safety, or physical-sensor
accuracy.

---

## 2. Test-Suite Structure

The test suite is stored under:

```text
tests/
├── conftest.py
├── test_api.py
├── test_dataset.py
├── test_hybrid_decision.py
├── test_model_contract.py
└── test_rule_engine.py
```

Scope of each file:

| Test file | Number of tests | Scope |
|---|---:|---|
| `tests/test_api.py` | 5 | Flask endpoints, model loading, valid prediction, missing fields, and invalid JSON |
| `tests/test_dataset.py` | 5 | dataset dimensions, determinism, ranges, batch trends, and integrity summary |
| `tests/test_hybrid_decision.py` | 9 | temperature priority, confidence threshold, agreement, and conflict handling |
| `tests/test_model_contract.py` | 4 | group split, model artifacts, feature order, and reference prediction |
| `tests/test_rule_engine.py` | 11 | Rule Model v1.1 paths, boundary conditions, rule priority, and recommendation fallback |
| **Total** | **34** | **All major project contracts** |

---

## 3. Dataset Testing

Test file:

```text
tests/test_dataset.py
```

Reproduction command:

```powershell
python -m pytest tests/test_dataset.py -v
```

Result:

```text
5 passed in 1.39s
```

### 3.1 Dataset-Dimension Contract

The tests verify that the generated dataset contains:

| Component | Required value |
|---|---:|
| Rows | 4,900 |
| Columns | 16 |
| Recipes | 7 |
| Batches | 350 |
| Observations per batch | 14 |
| Missing values | 0 |
| Duplicate rows | 0 |

Related tests:

```text
test_generated_dataset_matches_fixed_contract
test_validate_integrity_returns_expected_summary
```

### 3.2 Generator Determinism

The following test ensures that calling the generator with
`random_state=42` produces identical DataFrames:

```text
test_generated_dataset_is_deterministic
```

This contract is important because the dataset, split, training, and
evaluation results must be reproducible.

### 3.3 Simulation Ranges

The test verifies that all generated values remain within the configured
ranges:

| Variable | Minimum | Maximum |
|---|---:|---:|
| Temperature | 15 °C | 35 °C |
| Humidity | 40% | 90% |
| pH | 2.40 | 5.00 |
| Brix | 1.50 | 14.00 |

Related test:

```text
test_generated_values_stay_inside_configured_ranges
```

### 3.4 Batch Trends

The test ensures that all 350 batches have:

- a negative pH slope;
- a negative Brix slope.

Related test:

```text
test_every_batch_has_decreasing_ph_and_brix_trends
```

Passing this test shows that the generator preserves the intended synthetic
fermentation trends. It does not demonstrate that the trajectories are
identical to real biological fermentation.

---

## 4. Rule-Engine Testing

Test file:

```text
tests/test_rule_engine.py
```

Reproduction command:

```powershell
python -m pytest tests/test_rule_engine.py -v
```

Result:

```text
11 passed in 0.03s
```

### 4.1 Main Rule Paths

Parameterized tests verify the following paths:

| Condition | Expected status | Rule |
|---|---|---|
| `temperature > 30` | `temperature_warning` | `R1_high_temperature_warning` |
| `temperature < 18` | `manual_check` | `R2_low_temperature_slow_fermentation` |
| `pH > 4.2` | `too_early` | `R3_early_acidity_stage` |
| `pH < 3.0` or `Brix < 5.0` | `too_sour` | `R4_R5_over_acidic_or_low_sweetness` |
| early day and pH in the active range | `manual_check` | `R9_early_day_manual_check` |
| `Brix > 8.0` in the active pH range | `still_sweet` | `R6_sweet_fermentation_stage` |
| day ≥ 7 within the balanced window | `balanced` | `R10_balanced_ready_window` |
| day < 7 within the balanced window | `balanced` | `R7_balanced_but_early` |

### 4.2 Boundary Values

The tests ensure that exact boundary values:

```text
temperature = 30.0
temperature = 18.0
```

do not trigger the strict conditions:

```text
temperature > 30
temperature < 18
```

Related test:

```text
test_rule_boundaries_do_not_trigger_strict_temperature_conditions
```

### 4.3 Extended Over-Fermentation Priority

The test verifies that the condition:

```text
day > 14
and
(pH < 3.2 or Brix < 5.0)
```

produces:

```text
too_sour
R11_extended_over_fermentation
```

Related test:

```text
test_extended_overfermentation_rule_has_priority_after_temperature
```

### 4.4 Recommendation Fallback

Unknown statuses still produce a manual recommendation through:

```text
test_final_recommendation_has_manual_fallback
```

Therefore, the rule engine does not return an empty recommendation when it
receives a status outside the primary mapping.

---

## 5. Hybrid Decision-Layer Testing

Test file:

```text
tests/test_hybrid_decision.py
```

Reproduction command:

```powershell
python -m pytest tests/test_hybrid_decision.py -v
```

Result:

```text
9 passed in 0.56s
```

### 5.1 Temperature-Warning Priority

The test ensures that a `temperature_warning` from the rule engine cannot be
replaced by an ordinary ML prediction.

```text
test_temperature_warning_overrides_ml_prediction
```

Required result:

```text
rule_status = temperature_warning
ml_status = balanced
final_status = temperature_warning
```

### 5.2 Confidence Threshold

Final threshold:

```text
0.70
```

The test checks three low or unavailable confidence values:

```text
None
0.0
0.6999
```

All three must produce:

```text
final_status = manual_check
```

The test also ensures that the exact value `0.70` is not considered below the
threshold.

Related tests:

```text
test_low_or_missing_confidence_falls_back_to_manual_check
test_confidence_exactly_at_threshold_is_not_low_confidence
```

### 5.3 Agreement

When the rule and ML produce the same status and confidence meets the
threshold, the final status must preserve the shared status.

```text
test_rule_and_ml_agreement_preserves_status
```

### 5.4 Conflict Involving `too_sour`

Both directions are tested:

```text
rule = too_sour, ML = balanced
rule = balanced, ML = too_sour
```

Both must produce:

```text
final_status = manual_check
```

Related test:

```text
test_conflict_involving_too_sour_requires_manual_check
```

### 5.5 General Conflict

A normal disagreement such as:

```text
rule = still_sweet
ML = balanced
```

must also produce:

```text
manual_check
```

Related test:

```text
test_ordinary_disagreement_requires_manual_check
```

Passing these tests confirms that the hybrid layer is not a majority-vote
ensemble. The system uses a conservative priority order and explicit fallback.

---

## 6. Model-Contract Testing

Test file:

```text
tests/test_model_contract.py
```

Reproduction command:

```powershell
python -m pytest tests/test_model_contract.py -v
```

Result:

```text
4 passed, 18 warnings in 2.20s
```

### 6.1 Group-Aware Split

The test verifies the final split:

| Component | Value |
|---|---:|
| Training rows | 3,920 |
| Test rows | 980 |
| Training batches | 280 |
| Test batches | 70 |
| Batch overlap | 0 |
| Number of features | 10 |

Related test:

```text
test_group_split_is_batch_aware_and_reproducible
```

The test also performs the split twice and confirms that the training and
test indices are identical.

### 6.2 Serialized Artifact Contract

The test verifies that:

- the model is a `GradientBoostingClassifier`;
- the model has `predict`;
- the model has `predict_proba`;
- the feature list contains exactly 10 features;
- the recipe encoder contains `R1` through `R7`;
- the tea-type encoder contains three categories;
- the target encoder contains six statuses.

Related test:

```text
test_serialized_artifacts_match_model_contract
```

### 6.3 Feature Order

The test ensures that `prepare_ml_input()` returns features in the following
order:

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

Related test:

```text
test_feature_preparation_uses_saved_order
```

This contract prevents silent prediction errors caused by feature-order
mismatches.

### 6.4 Reference Payload

The following reference payload is tested:

```text
recipe_id = R1
tea_type = black_tea
day = 7
temperature = 24.4
humidity = 68.0
pH = 3.56
Brix = 7.71
```

Required result:

```text
ml_status = balanced
0.99 ≤ ml_confidence ≤ 1.00
```

The test does not lock the confidence to a long exact decimal value so that
it remains robust to minor dependency changes.

---

## 7. Flask API Testing

Test file:

```text
tests/test_api.py
```

Reproduction command:

```powershell
python -m pytest tests/test_api.py -v
```

Result:

```text
5 passed, 6 warnings in 1.96s
```

Testing uses Flask's `test_client()`, so the server does not need to be
started manually.

### 7.1 Root Endpoint

Test:

```text
test_root_endpoint
```

Response contract:

```json
{
  "message": "SCOBY Watch ML Hybrid API is running."
}
```

HTTP status:

```text
200 OK
```

### 7.2 Health Endpoint

Test:

```text
test_health_endpoint_reports_loaded_model
```

Response contract:

```json
{
  "status": "ok",
  "model": "GradientBoostingClassifier"
}
```

This status confirms that the model artifact is available when the
application is tested.

### 7.3 Valid Prediction

Test:

```text
test_predict_endpoint_returns_complete_hybrid_response
```

The response must contain:

- `batch_id`;
- `recipe_id`;
- `tea_type`;
- `day`;
- `room_temp_c`;
- `humidity_percent`;
- `ph`;
- `brix`;
- `rule_status`;
- `ml_status`;
- `ml_confidence`;
- `final_status`;
- `decision_reason`;
- `rule_triggered`;
- `risk_flag`;
- `recommendation`.

The reference payload produces:

```text
rule_status = balanced
ml_status = balanced
final_status = balanced
rule_triggered = R10_balanced_ready_window
risk_flag = normal
```

### 7.4 Missing Field

Test:

```text
test_predict_rejects_missing_required_fields
```

One required field, `ph`, is removed from the payload.

Required result:

```text
HTTP 400
error = Missing required fields
missing_fields contains ph
```

### 7.5 Invalid JSON

Test:

```text
test_predict_rejects_non_json_body
```

A `text/plain` request with non-JSON content must produce:

```text
HTTP 400
Request body must contain a valid JSON object.
```

Therefore, the endpoint does not forward an invalid body to the rule engine
or model.

---

## 8. Overall Test Results

Command:

```powershell
python -m pytest tests/ -q
```

Final result:

| Metric | Value |
|---|---:|
| Total tests | 34 |
| Passed | 34 |
| Failed | 0 |
| Errors | 0 |
| Pass rate | 100% |
| Warnings | 24 |
| Duration | 2.86 seconds |

Final output:

```text
34 passed, 24 warnings in 2.86s
```

Summary by group:

| Group | Passed | Warnings |
|---|---:|---:|
| API | 5 | 6 |
| Dataset | 5 | 0 |
| Hybrid decision | 9 | 0 |
| Model contract | 4 | 18 |
| Rule engine | 11 | 0 |
| **Total** | **34** | **24** |

All tests collected by `pytest` completed successfully without failures.

---

## 9. Observed Warnings

Main warning:

```text
DeprecationWarning:
Setting the shape on a NumPy array has been deprecated in NumPy 2.5.
As an alternative, create a new view using np.reshape
(with copy=False if needed).
```

The warning originates from:

```text
joblib/numpy_pickle.py
```

Warning distribution:

```text
tests/test_api.py = 6 warnings
tests/test_model_contract.py = 18 warnings
```

### 9.1 Warning Impact

The warnings do not cause:

- model-loading failure;
- encoder-loading failure;
- feature-list changes;
- endpoint failure;
- invalid prediction responses;
- test failure.

All 34 tests still pass.

### 9.2 Interpretation

The warning originates from internal `joblib` compatibility behavior when
loading NumPy-based artifacts under NumPy 2.5.

It is recorded as a dependency-compatibility issue, not as a functional
defect in SCOBY Watch logic.

The model artifact was created using scikit-learn 1.6.1. The reproduction
environment should retain the pinned dependency version or retrain the model
if major dependency versions change.

---

## 10. Mechanical and Behavioral Testing

### 10.1 Mechanical Testing

Mechanical tests ensure that the program satisfies its technical contracts:

- the dataset has the correct dimensions and columns;
- artifacts can be loaded;
- endpoints return the correct HTTP status;
- responses include the required fields;
- invalid requests are rejected;
- the split contains no batch overlap.

### 10.2 Behavioral Testing

Behavioral tests ensure that decision logic moves in the intended direction:

- temperature warnings have priority;
- confidence below 0.70 triggers manual fallback;
- agreement preserves the status;
- conflict involving `too_sour` produces `manual_check`;
- general conflict produces `manual_check`;
- boundary values follow the intended strict or inclusive operators.

Both test types are required. Mechanical tests only show that the software
runs, whereas behavioral tests ensure that it does not silently run with the
wrong logic.

---

## 11. Testing Limitations

Although all tests pass, the suite does not yet cover:

1. retraining all five models during every test run;
2. high-load testing;
3. concurrent API requests;
4. authentication and rate limiting;
5. a production WSGI server;
6. network interruptions;
7. delayed or duplicated MQTT messages;
8. public MQTT broker reliability;
9. automated execution of the full Node-RED flow;
10. automated Wokwi integration;
11. persistent database behavior;
12. physical pH sensor calibration;
13. physical Brix measurement validation;
14. microbial testing;
15. laboratory-confirmed fermentation outcomes;
16. food-safety certification;
17. probability calibration;
18. sensitivity analysis for the 0.70 threshold.

Therefore, passing the test suite demonstrates software consistency against
the defined contract, not biological validity or production readiness.

---

## 12. Main Findings

The following findings are confirmed:

- the dataset generator produces 4,900 observations deterministically;
- all 350 batches contain 14-day structures;
- synthetic sensor values remain within the configured ranges;
- all batches have decreasing pH and Brix trends;
- Rule Model v1.1 preserves the defined priority order;
- the Hybrid Decision Layer applies conservative fallback behavior;
- the `0.70` threshold uses the correct operator;
- the grouped split has zero batch overlap;
- the model, encoders, and feature list remain compatible;
- the reference payload produces the `balanced` status;
- the Flask API satisfies the root, health, and prediction contracts;
- invalid JSON and missing fields are rejected;
- all 34 tests pass.

---

## 13. Testing Artifacts

Artifact structure:

```text
tests/
├── conftest.py
├── test_api.py
├── test_dataset.py
├── test_hybrid_decision.py
├── test_model_contract.py
├── test_rule_engine.py
└── README.md

requirements-dev.txt
reports/
└── testing_findings.md
```

Artifact purposes:

| File | Purpose |
|---|---|
| `conftest.py` | dataset, API module, test-client, and valid-payload fixtures |
| `test_api.py` | verifies endpoint behavior and request validation |
| `test_dataset.py` | verifies the dataset generator and integrity contract |
| `test_hybrid_decision.py` | verifies the hybrid decision order |
| `test_model_contract.py` | verifies the split and serialized artifacts |
| `test_rule_engine.py` | verifies rule paths and boundaries |
| `requirements-dev.txt` | testing dependencies |
| `testing_findings.md` | summary of results and claim boundaries |

---

## 14. Checkpoint Status

- Dataset-contract test: completed.
- Deterministic-generation test: completed.
- Sensor-range test: completed.
- Batch-trend test: completed.
- Rule-engine test: completed.
- Boundary test: completed.
- Hybrid-decision test: completed.
- Confidence-threshold test: completed.
- Group-aware split test: completed.
- Serialized-artifact test: completed.
- Feature-order test: completed.
- Flask API test: completed.
- Invalid-request test: completed.
- Full automated suite: completed.
- Final result: 34 passed, 24 warnings, 0 failed.
- Next stage: repository documentation and clean-clone reproducibility test.

---

## 15. Conclusion

The SCOBY Watch test suite verifies the primary contracts for the dataset,
deterministic rule logic, hybrid conflict handling, batch-aware model
evaluation, serialized artifacts, and Flask API.

Final result:

```text
34 passed
0 failed
24 warnings
100% pass rate
```

The warnings originate from internal `joblib` and NumPy behavior when reading
serialized artifacts. They do not cause functional or test failures.

Based on these results, the SCOBY Watch software implementation is consistent
with the defined contracts and can proceed to repository packaging,
reproducibility documentation, and clean-clone validation.

This conclusion is limited to software-implementation validity. The test
results do not change the status of SCOBY Watch as a simulation-first,
readiness-oriented decision-support prototype rather than a food-safety
certification system.
