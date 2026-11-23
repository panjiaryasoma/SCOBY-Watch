"""IJIEEB PAPER023634 R1: repeated group splits, humidity ablation, hybrid coverage.
Run from the repository root:
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python revisions/PAPER023634-R1/scripts/revision_experiments.py
All output is generated using the original repository dataset and source modules.
Results evaluate approximation of deterministic synthetic rule-generated labels, not biology.
"""
from __future__ import annotations

import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parents[3]
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.config import DATASET_PATH, FEATURE_COLUMNS, TARGET_COLUMN
from src.train_models import encode_dataset, build_models
from src.hybrid_decision import hybrid_decision_layer

BASE = ROOT / "revisions" / "PAPER023634-R1"
RESULTS = BASE / "results"
FIGURES = BASE / "figures"
SEEDS = list(range(42, 52))
MODEL_SEED = 42
THRESHOLD = 0.70

def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATASET_PATH)
    data, encoders = encode_dataset(df)
    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN + "_encoded"]
    groups = data["batch_id"]
    labels = encoders[TARGET_COLUMN]

    records, ablations, hybrid_records, error_cases = [], [], [], []
    seed42 = None
    for seed in SEEDS:
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=seed)
        train_idx, test_idx = next(splitter.split(X, y, groups))
        train_groups = set(groups.iloc[train_idx])
        test_groups = set(groups.iloc[test_idx])
        assert not train_groups.intersection(test_groups), "batch leakage"
        assert len(train_idx) == 3920 and len(test_idx) == 980, "unexpected split sizes"
        y_test = y.iloc[test_idx].to_numpy()
        fitted = {}

        for name, model in build_models(MODEL_SEED).items():
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            predictions = model.predict(X.iloc[test_idx])
            fitted[name] = (model, predictions)
            records.append({
                "seed": seed, "model": name, "n_train": len(train_idx),
                "n_test": len(test_idx), "train_batches": len(train_groups),
                "test_batches": len(test_groups), "batch_leakage": 0,
                "accuracy": accuracy_score(y_test, predictions),
                "weighted_precision": precision_score(y_test, predictions, average="weighted", zero_division=0),
                "weighted_recall": recall_score(y_test, predictions, average="weighted", zero_division=0),
                "weighted_f1": f1_score(y_test, predictions, average="weighted", zero_division=0)
            })

        for name in ("Gradient Boosting", "Random Forest"):
            for include_humidity in (True, False):
                if include_humidity:
                    _, pred = fitted[name]
                else:
                    features = [f for f in FEATURE_COLUMNS if f != "humidity_percent"]
                    model = build_models(MODEL_SEED)[name]
                    model.fit(X.iloc[train_idx][features], y.iloc[train_idx])
                    pred = model.predict(X.iloc[test_idx][features])
                ablations.append({
                    "seed": seed, "model": name, "include_humidity": include_humidity,
                    "weighted_f1": f1_score(y_test, pred, average="weighted", zero_division=0),
                    "accuracy": accuracy_score(y_test, pred)
                })

        gb, gb_pred = fitted["Gradient Boosting"]
        confidences = gb.predict_proba(X.iloc[test_idx]).max(axis=1)
        truth_labels = data.iloc[test_idx][TARGET_COLUMN].to_numpy()
        predicted_labels = labels.inverse_transform(gb_pred)
        decisions = []
        for true_label, prediction, confidence, (_, row) in zip(
            truth_labels, predicted_labels, confidences, data.iloc[test_idx].iterrows()
        ):
            rule = {
                "status": str(true_label),
                "rule_triggered": str(row["rule_triggered"]),
                "risk_flag": str(row["risk_flag"])
            }
            ml = {"ml_status": str(prediction), "ml_confidence": float(confidence)}
            decision = hybrid_decision_layer(rule, ml, confidence_threshold=THRESHOLD)
            decisions.append(decision["final_status"])
        final = np.asarray(decisions)
        agree = truth_labels == predicted_labels
        warning = truth_labels == "temperature_warning"
        deferrals = (final == "manual_check") & (truth_labels != "manual_check")
        hybrid_records.append({
            "seed": seed, "n_test": len(test_idx), "ml_matches_rule": int(agree.sum()),
            "ml_disagreements": int((~agree).sum()),
            "ml_rule_agreement_rate": float(agree.mean()),
            "hybrid_final_matches_rule": int((final == truth_labels).sum()),
            "hybrid_final_agreement_rate": float((final == truth_labels).mean()),
            "hybrid_manual_check": int((final == "manual_check").sum()),
            "hybrid_manual_check_rate": float((final == "manual_check").mean()),
            "additional_manual_check_deferrals": int(deferrals.sum()),
            "additional_manual_check_deferral_rate": float(deferrals.mean()),
            "warning_cases": int(warning.sum()),
            "warnings_preserved": int(((final == "temperature_warning") & warning).sum()),
            "low_confidence_cases": int((confidences < THRESHOLD).sum())
        })
        if seed == 42:
            seed42 = (y_test, gb_pred, fitted["Random Forest"][1])
            for pos, index in enumerate(test_idx):
                if agree[pos]:
                    continue
                row = data.iloc[index]
                error_cases.append({
                    "row_index": int(index), "batch_id": str(row["batch_id"]),
                    "day": int(row["day"]), "ph": float(row["ph"]),
                    "brix": float(row["brix"]), "room_temp_c": float(row["room_temp_c"]),
                    "humidity_percent": float(row["humidity_percent"]),
                    "rule_label": str(truth_labels[pos]),
                    "ml_label": str(predicted_labels[pos]),
                    "ml_confidence": float(confidences[pos]),
                    "hybrid_final": str(final[pos]),
                    "rule_triggered": str(row["rule_triggered"])
                })
        print(f"Seed {seed}: GB F1={f1_score(y_test, gb_pred, average='weighted'):.6f}")

    raw = pd.DataFrame(records)
    raw.to_csv(RESULTS / "repeated_group_splits_raw.csv", index=False)
    summary = raw.groupby("model", as_index=False).agg(
        accuracy_mean=("accuracy", "mean"), accuracy_sd=("accuracy", "std"),
        f1_mean=("weighted_f1", "mean"), f1_sd=("weighted_f1", "std"),
        precision_mean=("weighted_precision", "mean"),
        recall_mean=("weighted_recall", "mean"),
        f1_min=("weighted_f1", "min"), f1_max=("weighted_f1", "max")
    ).sort_values("f1_mean", ascending=False)
    summary.to_csv(RESULTS / "repeated_group_splits_summary.csv", index=False)
    pd.DataFrame(ablations).to_csv(RESULTS / "humidity_ablation_raw.csv", index=False)
    ablation_summary = pd.DataFrame(ablations).groupby(["model", "include_humidity"], as_index=False).agg(
        f1_mean=("weighted_f1", "mean"), f1_sd=("weighted_f1", "std"),
        accuracy_mean=("accuracy", "mean")
    )
    ablation_summary.to_csv(RESULTS / "humidity_ablation_summary.csv", index=False)
    pd.DataFrame(hybrid_records).to_csv(RESULTS / "hybrid_full_test_coverage.csv", index=False)
    pd.DataFrame(error_cases).to_csv(RESULTS / "seed42_gradient_boosting_error_cases.csv", index=False)

    truth, gb_pred, rf_pred = seed42
    gb_correct = gb_pred == truth
    rf_correct = rf_pred == truth
    gb_only = int((gb_correct & ~rf_correct).sum())
    rf_only = int((~gb_correct & rf_correct).sum())
    p_value = (
        float(binomtest(min(gb_only, rf_only), n=gb_only + rf_only, p=0.5).pvalue)
        if gb_only + rf_only else 1.0
    )
    metadata = {
        "n_rows": int(len(df)), "n_batches": int(groups.nunique()),
        "seeds": SEEDS, "model_random_state_fixed": MODEL_SEED,
        "n_splits": len(SEEDS),
        "classification_ground_truth": "deterministic rule-generated labels; no independent biological ground truth",
        "mcnemar_seed42": {
            "both_correct": int((gb_correct & rf_correct).sum()),
            "gradient_boosting_only_correct": gb_only,
            "random_forest_only_correct": rf_only,
            "both_wrong": int((~gb_correct & ~rf_correct).sum()),
            "p_exact": p_value
        },
        "scikit_learn_version": sklearn.__version__,
        "numpy_version": np.__version__, "pandas_version": pd.__version__,
        "python_version": platform.python_version(),
        "note": "Repeated test sets overlap across random seeds; not independent external validation."
    }
    (RESULTS / "experiment_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    chart = summary.sort_values("f1_mean", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(chart["model"], chart["f1_mean"], xerr=chart["f1_sd"], capsize=3)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Weighted F1 (mean ± SD across 10 batch-disjoint splits)")
    fig.tight_layout()
    fig.savefig(FIGURES / "model_repeated_group_f1_300dpi.png", dpi=300)
    plt.close(fig)
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
