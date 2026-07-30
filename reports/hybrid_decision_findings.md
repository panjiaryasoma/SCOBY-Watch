# Hybrid Decision Findings — SCOBY Watch

**Project:** SCOBY Watch  
**Component:** Hybrid Decision Layer  
**Confidence threshold:** 0.70  
**Status:** Standard, edge, and forced-conflict testing completed  

---

## 1. Purpose

The Hybrid Decision Layer combines:

- `rule_status`;
- `ml_status`;
- `ml_confidence`;
- `rule_triggered`;
- `risk_flag`.

Its purpose is to prevent ML from becoming the sole decision authority and
to provide a manual fallback when the output is not sufficiently reliable.

---

## 2. Decision Order

```text
1. temperature_warning priority
2. low-confidence fallback
3. agreement
4. conflict involving too_sour
5. general conflict
```

The hybrid layer is not a majority-voting mechanism.

---

## 3. Temperature-Warning Priority

Condition:

```text
rule_status = temperature_warning
```

Result:

```text
final_status = temperature_warning
```

The ML model must not replace the warning with an ordinary readiness status.

---

## 4. Low-Confidence Fallback

Condition:

```text
ml_confidence < 0.70
```

Result:

```text
final_status = manual_check
```

The test covers:

```text
None
0.0
0.6999
```

The exact value:

```text
0.70
```

is not considered below the threshold.

---

## 5. Agreement

When:

```text
rule_status == ml_status
and
confidence >= 0.70
```

then:

```text
final_status = shared status
```

Reference sample:

```text
rule_status = balanced
ml_status = balanced
ml_confidence ≈ 0.9998
final_status = balanced
```

---

## 6. Conflict Involving `too_sour`

Both directions are tested:

```text
rule = too_sour, ML = balanced
rule = balanced, ML = too_sour
```

Result:

```text
manual_check
```

The reason is that the disagreement concerns possible over-fermentation risk.

---

## 7. General Conflict

Example:

```text
rule = still_sweet
ML = balanced
```

Result:

```text
manual_check
```

The system does not silently choose one output over the other.

---

## 8. Recommendation Mapping

| Final status | Recommendation intent |
|---|---|
| `too_early` | continue fermentation |
| `still_sweet` | continue fermentation or begin taste testing |
| `balanced` | begin taste testing and consider bottling |
| `too_sour` | possible over-fermentation |
| `temperature_warning` | move the batch to a cooler area |
| `manual_check` | perform a manual inspection |

The recommendation is a readiness-oriented output.

---

## 9. Test Scenarios

Stored outputs:

```text
results/
├── scoby_watch_hybrid_decision_test.csv
├── scoby_watch_hybrid_edge_case_test.csv
└── scoby_watch_hybrid_forced_conflict_test.csv
```

The scenarios cover:

- early fermentation;
- sweet stage;
- balanced stage;
- too-sour condition;
- high temperature;
- low temperature;
- borderline values;
- low confidence;
- ordinary disagreement;
- conflict involving `too_sour`.

---

## 10. Automated Test

Command:

```powershell
python -m pytest tests/test_hybrid_decision.py -v
```

Result:

```text
9 passed in 0.56s
```

---

## 11. Findings

- Warning priority works as intended.
- Confidence fallback works as intended.
- The 0.70 boundary is handled correctly.
- Agreement preserves the shared status.
- Conflicts involving `too_sour` are routed to manual checking.
- General conflicts are routed to manual checking.
- A decision reason is available.
- A recommendation is available.

---

## 12. Limitations

1. The 0.70 threshold is heuristic.
2. Confidence is not calibrated.
3. No sensitivity analysis has been performed.
4. No empirical risk model is available.
5. No human-factor evaluation has been performed.
6. Manual checking does not guarantee food safety.
7. The hybrid logic has not been tested in a real-world deployment.

---

## 13. Conclusion

The Hybrid Decision Layer successfully applies conservative fallback behavior
and provides an explicit decision trace.

Its primary value is transparency and conflict handling at the software level.

The layer does not demonstrate reduced biological risk or improved food safety.
