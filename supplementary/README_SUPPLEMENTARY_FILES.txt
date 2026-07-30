SCOBY Watch Supplementary Materials

This directory contains curated supplementary material for the manuscript:

"SCOBY Watch: A Simulation-First IoT and Hybrid Decision Support Framework
for Kombucha Fermentation Readiness Assessment."

Authors:
- Panji Arya Soma
- Anas Nasrulloh

Preferred contents:
1. README.md
2. README_SUPPLEMENTARY_FILES.txt
3. SCOBY_Watch_Simulation_and_Implementation_Evidence.pdf

The evidence PDF documents representative:
- dataset-generation and integrity checks;
- pH and Brix trend checks;
- batch-aware GroupShuffleSplit evaluation;
- model comparison and confusion matrix;
- Hybrid Decision Layer scenarios;
- Flask API behavior;
- Wokwi and MQTT simulation;
- Node-RED flow and dashboard integration.

Executable and machine-readable artifacts are stored in the repository:
- data/ for the dataset and validation tables;
- src/ for reusable implementation;
- experiments/ for historical split experiments;
- models/ for serialized artifacts;
- api/ for the Flask service;
- node-red/ for the flow;
- wokwi/ for simulation files;
- results/ for generated outputs;
- reports/ for findings;
- tests/ for automated tests;
- docs/ for technical documentation.

Reference results:
- 7 recipe profiles
- 350 simulated batches
- 4,900 observations
- 3,920 training rows
- 980 test rows
- 280 training batches
- 70 test batches
- zero batch_id overlap
- Gradient Boosting accuracy: 0.995918
- Gradient Boosting weighted F1-score: 0.995921
- automated tests: 34 passed, 0 failed

These materials support software, implementation, and reproducibility claims.
They do not represent laboratory, microbiological, physical-sensor, or
food-safety validation.

SCOBY Watch is a simulation-first readiness-oriented decision-support
prototype. It is not a food-safety certification system and does not validate
microbial safety, health suitability, or commercial product quality.

For detailed instructions, see:
- docs/REPRODUCIBILITY.md
- docs/CLAIM_BOUNDARIES.md
- CITATION.cff
- LICENSE
