# Experiments

## Run

From the repository root:

```powershell
python -m experiments.random_split_baseline
python -m experiments.compare_split_strategies
```

## Generated text evidence

`random_split_baseline.py` generates:

```text
results/
├── RANDOM ROW SPLIT BASELINE.txt
├── RANDOM SPLIT LABEL DISTRIBUTION.txt
└── scoby_watch_ml_baseline_classification_reports.txt
```

`compare_split_strategies.py` generates:

```text
results/
├── SPLIT STRATEGY COMPARISON.txt
├── GROUP SHUFFLE SPLIT BY batch_id.txt
├── CHECK LABEL DISTRIBUTION AFTER GROUP SPLIT.txt
├── TRAIN ML BASELINE MODELS WITH GROUP SPLIT.txt
└── TRAIN ML BASELINE MODELS WITH RANDOM SPLIT.txt
```

CSV and PNG comparison artifacts are generated alongside these files.

The GroupShuffleSplit result remains the authoritative paper evaluation.
