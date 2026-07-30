# `src/` complete notebook extraction

This folder reproduces the full logical sequence of
`SCOBY WATCH DATASET + ML BASELINE.ipynb`, including the initial
random-row ML baseline and the final batch-aware grouped evaluation.

## Files

| File | Notebook responsibility |
|---|---|
| `config.py` | Shared paths, recipe profiles, columns, seeds, and thresholds |
| `rule_engine.py` | Rule Model v1.1 and final recommendation mapping |
| `generate_dataset.py` | Recipe profiles, fermentation rates, synthetic trajectories, labels, and CSV export |
| `validate_dataset.py` | Basic sanity, range checks, trends, status distributions, transitions, rule distributions, tables, and plots |
| `train_models.py` | Encoding, initial random split, final group split, five classifiers, reports, charts, confusion matrices, model artifacts, and split comparison |
| `hybrid_decision.py` | Artifact loading, feature preparation, real ML prediction, standard cases, edge cases, and forced conflicts |
| `notebook_text_evidence.py` | Exports notebook-style TXT evidence for sanity checks, trends, model reports, artifact loading, and one-sample hybrid output |
| `run_pipeline.py` | End-to-end runner matching the notebook's complete logical order |

## Full run

From the repository root:

```powershell
python -m src.run_pipeline
```

This performs:

```text
dataset generation
→ dataset validation
→ random-row baseline
→ GroupShuffleSplit baseline
→ split-strategy comparison
→ authoritative model saving
→ hybrid scenario validation
```

## Individual stages

```powershell
python -m src.generate_dataset
python -m src.validate_dataset
python -m src.train_models --mode random
python -m src.train_models --mode group
python -m src.train_models --mode both
python -m src.hybrid_decision
python -m src.notebook_text_evidence
```

## Methodological status

The random-row baseline reproduces the notebook's early experiment and is
retained for archival completeness.

The authoritative paper result remains:

```text
GroupShuffleSplit by batch_id
Train rows: 3,920
Test rows: 980
Train batches: 280
Test batches: 70
Batch overlap: 0
```

Only the group-split winner is saved as the deployable model artifact.


## Notebook-style TXT evidence

Run:

```powershell
python -m src.notebook_text_evidence
```

Files are written to:

```text
results/notebook_text_evidence/
```

The exporter recreates the important text downloads from the Colab notebook,
including dataset sanity, sensor ranges, daily and recipe trends, monotonic
checks, status transitions, random and group model reports, model-loading
evidence, and the updated one-sample hybrid decision output.

The old `TEST HYBRID DECISION WITH ONE SAMPLE.txt` is not regenerated because
it was superseded by `TEST HYBRID DECISION WITH ONE SAMPLE UPDATED.txt`.
