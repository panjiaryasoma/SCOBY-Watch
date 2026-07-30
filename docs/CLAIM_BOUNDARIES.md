# Claim Boundaries — SCOBY Watch

## 1. Purpose

This document defines the boundaries that must be preserved across:

- the README;
- the paper;
- the repository;
- presentations;
- posters;
- demonstrations;
- API documentation;
- dataset documentation;
- model documentation.

Its purpose is to prevent a simulation-first prototype from being
misrepresented as biological or food-safety evidence.

---

## 2. Supported Claims

SCOBY Watch can be described as:

- a simulation-first IoT prototype;
- a readiness-oriented decision-support framework;
- a synthetic dataset generator;
- a deterministic rule-based monitoring prototype;
- a leakage-aware ML baseline;
- a batch-aware evaluation implementation;
- a Flask model-serving prototype;
- a confidence-aware Hybrid Decision Layer;
- an MQTT and Node-RED integration demonstration;
- a dashboard-visualization prototype;
- a reproducibility-oriented engineering artifact.

---

## 3. Unsupported Claims

SCOBY Watch must not be described as:

- a food-safety certification system;
- a microbial-safety detector;
- a pathogen detector;
- a mold detector;
- an alcohol measurement system;
- a titratable-acidity measurement system;
- a laboratory-validated fermentation predictor;
- a clinical or nutritional recommendation system;
- a commercial quality-control system;
- a calibrated pH sensor product;
- a calibrated Brix sensor product;
- a production-ready IoT platform;
- a replacement for expert inspection;
- a guarantee that kombucha is safe to consume.

---

## 4. Dataset Boundary

The dataset is:

- synthetic;
- generated using controlled formulas and noise;
- labeled by deterministic rules;
- not an empirical observation set;
- not laboratory ground truth;
- not sensory-panel ground truth.

Safe claim:

```text
The dataset supports pipeline, rule, model, and integration testing.
```

Unsafe claim:

```text
The dataset represents real biological fermentation behavior.
```

---

## 5. Model Boundary

The model approximates rule-generated labels.

Safe claim:

```text
The model achieved high rule-label approximation performance under a
batch-aware split.
```

Unsafe claim:

```text
The model understands kombucha fermentation biology.
```

High accuracy and weighted F1 do not prove:

- biological intelligence;
- real-world generalization;
- calibrated confidence;
- superiority over direct rule execution.

---

## 6. Sensor Boundary

Wokwi provides simulated sensor values.

Safe claim:

```text
The project validates the software data path using simulated pH, Brix,
temperature, and humidity values.
```

Unsafe claim:

```text
The system has validated physical pH and Brix sensors.
```

The following have not yet been tested:

- calibration;
- drift;
- fouling;
- cleaning;
- signal conditioning;
- food-contact suitability;
- measurement repeatability.

---

## 7. System Boundary

The system demonstrates that:

- a payload can be constructed;
- MQTT can forward the payload;
- Node-RED can process the payload;
- Flask can provide inference;
- the dashboard can display the output.

The system does not demonstrate:

- production uptime;
- network resilience;
- cybersecurity;
- concurrent-load capacity;
- message ordering;
- delayed-message handling;
- duplicate-message handling;
- database durability.

---

## 8. Hybrid-Layer Boundary

The Hybrid Decision Layer improves transparency and conservative fallback at
the software-logic level.

The hybrid layer does not prove:

- safety optimization;
- clinical-risk reduction;
- laboratory-risk reduction;
- calibrated abstention;
- an empirically optimal threshold.

The 0.70 threshold is a predefined conservative heuristic.

---

## 9. Recommendation Boundary

Recommendations such as:

```text
Start taste testing and consider bottling.
```

must be interpreted as readiness-oriented prototype output.

The recommendation is not:

- permission to consume;
- a safety certificate;
- medical instruction;
- a replacement for contamination inspection;
- a replacement for sanitation practices;
- a replacement for expert evaluation.

---

## 10. Food-Safety Boundary

SCOBY Watch does not test:

- pathogens;
- mold;
- microbial counts;
- ethanol;
- contamination;
- toxins;
- food-contact materials;
- sanitation effectiveness.

pH and Brix alone are not sufficient to establish that a beverage is safe.

---

## 11. Seven Validity Categories

### 11.1 Construct Validity

Readiness status comes from rules, not sensory or laboratory outcomes.

### 11.2 Internal Validity

The results depend on formulas, random seed, noise, clipping, and rule order.

### 11.3 External Validity

Seven recipes do not represent all recipes, cultures, climates, vessels, and
practices.

### 11.4 Model Validity

The metrics measure rule-label approximation.

### 11.5 Sensor Validity

The sensors remain simulated and are not physically calibrated.

### 11.6 System Validity

The architecture remains a local prototype using a public MQTT broker.

### 11.7 Safety Validity

No laboratory or food-safety testing has been performed.

---

## 12. Recommended Language

Use:

```text
simulation-first
readiness-oriented
decision-support
prototype
rule-label approximation
software-integration validation
manual-inspection fallback
```

Avoid without qualification:

```text
safe
certified
accurate for real fermentation
production-ready
biologically validated
automatically determines consumption safety
```

---

## 13. Public Repository Notice

The public README should include:

```text
SCOBY Watch is a simulation-first readiness-oriented decision-support
prototype. It is not a food-safety certification system and does not validate
microbial safety, health suitability, or commercial quality.
```

---

## 14. Future Validation Requirements

Stronger claims would require:

- calibrated physical sensors;
- an empirical fermentation dataset;
- a structured sensory protocol;
- laboratory measurements;
- probability calibration;
- threshold-sensitivity analysis;
- external validation;
- deployment testing;
- qualified food-science collaboration.

Until those stages are completed, the current claim boundaries must be
preserved.
