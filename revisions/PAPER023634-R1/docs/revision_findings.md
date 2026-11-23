# SCOBY Watch | First reproducible experiments for IJIEEB reviewer revision

**Date:** 23 November 2026  
**Manuscript ID:** PAPER023634  
**Repository:** https://github.com/panjiaryasoma/SCOBY-Watch  
**Dataset Git blob SHA (verified exactly):** `6e7bb80c231f323507d10b6cf3f5adbfbcf812c6`  
**Git repository tree:** `593f178a4084be6d0cc403835587dabda409cf50` (main)

## What was actually executed

- Reconstructed the original 4,900-row dataset from the supplied notebook, and reconciled the notebook's recommendation text with `src/rule_engine.py`. The resulting CSV matches the GitHub repository dataset **byte-for-byte** by Git blob SHA.
- Reproduced the previously reported single group-split Gradient Boosting weighted F1 of **0.995921** (seed=42, 980 test observations).
- Ran 10 `GroupShuffleSplit` evaluations (`test_size=0.2`, seeds 42–51); each hold-out contains 70 batches/980 observations and zero batches overlap with training.
- Held classifier `random_state=42` fixed during repeated splits to isolate data-split variation. Model settings match `src/train_models.py`.
- Performed humidity feature ablation for Gradient Boosting and Random Forest across the same splits.
- Assessed hybrid decision output on the **full 980 samples per split**; extracted concrete seed-42 misclassification cases.
- Computed an exact paired McNemar test for Gradient Boosting versus Random Forest on the same seed-42 held-out cases.

## Major Issue 2: Repeated GroupShuffleSplit results

| Classifier | Weighted F1 (mean ± SD) | Accuracy (mean ± SD) |
|---|---:|---:|
| Gradient Boosting | 0.996016 ± 0.001835 | 0.996020 ± 0.001829 |
| Random Forest | 0.995406 ± 0.001752 | 0.995408 ± 0.001751 |
| Decision Tree | 0.994374 ± 0.002332 | 0.994388 ± 0.002319 |
| Logistic Regression | 0.834066 ± 0.011970 | 0.838776 ± 0.011535 |
| KNN | 0.792828 ± 0.014470 | 0.800204 ± 0.012081 |

These scores measure the ability to approximate **synthetic deterministic rule labels**. They **do not** indicate biological accuracy or validated kombucha readiness. Repeated holdout splits overlap; they are not ten independent external datasets.

McNemar exact test (seed 42, same test observations): GB correct/RF incorrect = **2**, GB incorrect/RF correct = **1**, exact p = **1.000**. No statistically supported superiority of Gradient Boosting over Random Forest is established by this test.

## Major Issue 7: Humidity ablation

| Model | Include humidity | Weighted F1 (mean ± SD) |
|---|---|---:|
| Gradient Boosting | No | 0.995709 ± 0.001852 |
| Gradient Boosting | Yes | 0.996016 ± 0.001835 |
| Random Forest | No | 0.995509 ± 0.001813 |
| Random Forest | Yes | 0.995406 ± 0.001752 |

Humidity is **not used by the rule engine to generate labels**. The small split-dependent differences in F1 should not be described as evidence of an independent causal effect of humidity on fermentation. Reporting the actual ablation is more defensible than inventing biological justifications.

## Major Issue 2 (hybrid): Full-test-set coverage

For the original seed-42 group split (`n=980`):

- ML matches rule labels: **976/980**.
- Hybrid final status equals original rule label: **978/980**. This is not an external accuracy metric; its reference is the deterministic rule system.
- Hybrid emits `manual_check` for **124/980** samples, including original rule `manual_check` cases. Newly deferred non-manual cases: **2/980**.
- Temperature warnings preserved: **24/24**.
- Low confidence cases (`confidence < 0.70`): **2**.

Across all 10 splits, mean hybrid/rule agreement = **0.997449**; mean additional deferral rate = **0.002551**. These are *system-consistency* and fallback-behavior results, not real-world safety validation.

## Major Issue 8: Actual seed-42 misclassification cases

| Batch/day | pH | Brix | Rule-generated status | ML status | Confidence | Hybrid final |
|---|---:|---:|---|---|---:|---|
| KB-R2-006, day 12 | 3.19 | 8.46 | manual_check | still_sweet | 0.8614 | manual_check |
| KB-R2-044, day 11 | 3.19 | 8.99 | manual_check | still_sweet | 0.8897 | manual_check |
| KB-R6-045, day 6 | 4.20 | 8.16 | still_sweet | too_early | 0.7430 | manual_check |
| KB-R6-045, day 8 | 4.20 | 7.90 | balanced | too_early | 0.8448 | manual_check |

Two examples fall close to the **pH 3.2** decision boundary (3.19), and two use displayed **pH 4.20** close to the high-pH boundary. All four have the hybrid fallback `manual_check`; the two that were already `manual_check` under rules are not new fallback cases. The observed errors warrant focused boundary-condition analysis, not blanket claims of model robustness.

## Major Issue 3: Generator parameter transparency

See `generator_parameter_inventory.csv` and original `src/generate_dataset.py`. Important methodological mismatch with the existing manuscript: the implementation computes `initial_ph − daily_rate × day + noise` and the analogous Brix equation, **not a recursive update based on the previous day's observed value**.

Observed day-to-day increases despite overall negative slopes:

- pH increase: **466/4550** consecutive transitions (10.24%).
- Brix increase: **625/4550** consecutive transitions (13.74%).

Therefore the paper must distinguish *overall negative batch trend/slope* from *strictly monotonic daily values*.

## Limitations and required subsequent work

1. **Major 1:** Reframe ML explicitly as a rule-approximation/software integration validation tool; do not imply biological predictive capability from synthetic rule labels.
2. **Major 4:** Literature/empirical external comparison is not yet completed. Do not fabricate references or measurements.
3. **Major 5:** MQTT→Node-RED→Flask→dashboard latency, API P50/P95/P99, loss rate and throughput were **not measured** in this artifact. Run an instrumented live/simulated pipeline to report these.
4. **Major 6:** Threshold justification remains to be verified against actual kombucha literature and the chosen readiness preference; threshold logic is a *design assumption*, not a certified food-safety threshold.
5. **Version parity:** GitHub `requirements.txt` pins scikit-learn==1.6.1, while this environment used 1.8.0. Re-run with pinned versions before final camera-ready submission if any discrepancy occurs.
6. **Statistical caveat:** Repeated random holdout test sets overlap. The exact seed-42 McNemar test is paired within one held-out split and cannot establish general validity on other data distributions.
7. **Editorial:** This bundle is supporting evidence, **not a complete revised manuscript** and not a complete point-by-point revision response. Verify all figures, tables, equations, declarations, and author profiles separately.

### Reproducibility

From inside this evidence folder, with Python, pandas, NumPy, scikit-learn, and SciPy installed:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python revision_experiments.py
```

It reads `scoby_watch_simulated_dataset.csv` and overwrites the CSV results and metadata in the folder. For the exact environment of this run: Python 3.13.5, pandas 2.2.3, NumPy 2.3.5, scikit-learn 1.8.0.

**Repository status:** no GitHub branches, commits, files, or pull requests were changed by this analysis.
