# SCOBY Watch Reports

This directory contains actual results, experiment interpretations,
checkpoints, and implementation limitations for SCOBY Watch.

The documents in this directory differ from those in `docs/`:

```text
docs/
└── technical and methodological reference documentation

reports/
└── actual results, interpretations, findings, and project checkpoints
```

## Report List

| Document | Purpose |
|---|---|
| `dataset_generation_findings.md` | Explains the synthetic dataset generator results and design assumptions |
| `data_quality_findings.md` | Explains integrity checks, sensor ranges, trends, status distributions, and data risks |
| `training_findings.md` | Explains the random-row baseline, GroupShuffleSplit, five models, configurations, and artifacts |
| `evaluation_findings.md` | Explains the final grouped evaluation, score interpretation, and model boundaries |
| `hybrid_decision_findings.md` | Explains agreement, low-confidence handling, warning priority, and conflict handling |
| `api_findings.md` | Explains the Flask API implementation and testing results |
| `integration_testing_findings.md` | Explains the verification of Wokwi, MQTT, Node-RED, Flask, and the dashboard |
| `testing_findings.md` | Explains the results of the 34-test automated test suite |

## Recommended Reading Order

1. `dataset_generation_findings.md`
2. `data_quality_findings.md`
3. `training_findings.md`
4. `evaluation_findings.md`
5. `hybrid_decision_findings.md`
6. `api_findings.md`
7. `integration_testing_findings.md`
8. `testing_findings.md`

## Claim Boundary

All reports must be read within the following boundary:

```text
SCOBY Watch is a simulation-first readiness-oriented decision-support
prototype. It is not a food-safety certification system.
```
