# SCOBY Watch Test Suite

This directory contains fast contract tests for the completed SCOBY Watch
prototype.

## Coverage

- `test_dataset.py`
  - 4,900 rows, 16 columns, 350 batches, and 14 observations per batch
  - deterministic generation
  - configured sensor ranges
  - decreasing pH and Brix batch trends

- `test_rule_engine.py`
  - main Rule Model v1.1 paths
  - strict temperature boundaries
  - extended over-fermentation priority
  - recommendation fallback

- `test_hybrid_decision.py`
  - temperature-warning priority
  - confidence threshold behavior
  - agreement
  - `too_sour` conflicts
  - ordinary disagreements

- `test_model_contract.py`
  - GroupShuffleSplit row and batch counts
  - zero batch overlap
  - serialized artifact classes and feature order
  - reference payload prediction

- `test_api.py`
  - `/`
  - `/health`
  - valid `/predict`
  - missing-field validation
  - invalid JSON validation

## Run

From the repository root:

```powershell
python -m pytest tests -v
```

The test suite intentionally does not retrain all five baseline models on every
run. Full training reproducibility remains available through:

```powershell
python -m src.train_models
```
