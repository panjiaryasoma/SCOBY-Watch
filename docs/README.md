# SCOBY Watch Documentation

This directory contains the technical and methodological documentation for the
SCOBY Watch repository.

## Document List

| Document | Purpose |
|---|---|
| `DATASET_CARD.md` | Explains the origin, structure, generator, intended use, and interpretation boundaries of the synthetic dataset |
| `MODEL_CARD.md` | Explains the final model, features, configuration, metrics, intended use, risks, and claim boundaries |
| `API.md` | Explains the Flask endpoints, requests, responses, error behavior, and how to run the API |
| `REPRODUCIBILITY.md` | Explains the complete workflow from cloning the repository to regenerating the outputs |
| `SYSTEM_ARCHITECTURE.md` | Explains the Wokwi, MQTT, Node-RED, Flask, rule-engine, ML, hybrid-layer, and dashboard flow |
| `CLAIM_BOUNDARIES.md` | Defines the research, engineering, sensor, model, system, and food-safety claim boundaries |

## Relationship to Other Directories

```text
docs/
└── technical and methodological reference documentation

reports/
└── actual findings, experiment interpretations, and checkpoints

results/
└── generated CSV, TXT, and other machine-readable evidence

supplementary/
└── curated implementation and simulation evidence supporting the paper
```

## Recommended Reading Order

1. `SYSTEM_ARCHITECTURE.md`
2. `DATASET_CARD.md`
3. `MODEL_CARD.md`
4. `API.md`
5. `REPRODUCIBILITY.md`
6. `CLAIM_BOUNDARIES.md`

## Repository Status

SCOBY Watch is a simulation-first, readiness-oriented decision-support
prototype.

The permanent public repository URL and archived DOI have not yet been added.
They should be inserted after the repository is published and validated through
a clean-clone rehearsal.
