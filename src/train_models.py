"""Reproduce both notebook ML baselines: random split and group split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Literal

import joblib
import matplotlib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    GroupShuffleSplit,
    train_test_split,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from .config import (
    CATEGORICAL_COLUMNS,
    DATASET_PATH,
    FEATURE_COLUMNS,
    MODELS_DIR,
    RANDOM_STATE,
    REPORTS_DIR,
    RESULTS_DIR,
    TARGET_COLUMN,
    TEST_SIZE,
)

matplotlib.use("Agg")
from matplotlib import pyplot as plt


SplitMode = Literal["random", "group"]


def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {path}. "
            "Run `python -m src.generate_dataset` first."
        )
    return pd.read_csv(path)


def encode_dataset(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    """Fit the same encoders used by the original notebook."""
    data = df.copy()
    encoders: dict[str, LabelEncoder] = {}

    for column in CATEGORICAL_COLUMNS + [TARGET_COLUMN]:
        encoder = LabelEncoder()
        data[f"{column}_encoded"] = encoder.fit_transform(
            data[column]
        )
        encoders[column] = encoder

    return data, encoders


def random_split(
    data: pd.DataFrame,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    """Reproduce notebook cells 4–7 using stratified row splitting."""
    X = data[FEATURE_COLUMNS]
    y = data[f"{TARGET_COLUMN}_encoded"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    return {
        "method": "train_test_split",
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "train_idx": X_train.index.to_numpy(),
        "test_idx": X_test.index.to_numpy(),
        "train_groups": data.loc[X_train.index, "batch_id"],
        "test_groups": data.loc[X_test.index, "batch_id"],
    }


def group_split(
    data: pd.DataFrame,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    """Reproduce the final GroupShuffleSplit by ``batch_id``."""
    X = data[FEATURE_COLUMNS]
    y = data[f"{TARGET_COLUMN}_encoded"]
    groups = data["batch_id"]

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=test_size,
        random_state=random_state,
    )
    train_idx, test_idx = next(
        splitter.split(X, y, groups=groups)
    )

    train_groups = groups.iloc[train_idx]
    test_groups = groups.iloc[test_idx]
    overlap = set(train_groups.unique()).intersection(
        test_groups.unique()
    )
    if overlap:
        raise RuntimeError(
            f"Batch leakage detected: {sorted(overlap)[:5]}"
        )

    return {
        "method": "GroupShuffleSplit",
        "X_train": X.iloc[train_idx],
        "X_test": X.iloc[test_idx],
        "y_train": y.iloc[train_idx],
        "y_test": y.iloc[test_idx],
        "train_groups": train_groups,
        "test_groups": test_groups,
        "train_idx": train_idx,
        "test_idx": test_idx,
    }


def build_models(
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    """Return the five fixed notebook model configurations."""
    return {
        "Decision Tree": DecisionTreeClassifier(
            random_state=random_state,
            max_depth=8,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            random_state=random_state,
            max_depth=12,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            random_state=random_state,
        ),
        "KNN": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "knn",
                    KNeighborsClassifier(n_neighbors=7),
                ),
            ]
        ),
        "Logistic Regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "logreg",
                    LogisticRegression(max_iter=1500),
                ),
            ]
        ),
    }


def evaluate_models(
    models: dict[str, Any],
    split: dict[str, Any],
    target_names: np.ndarray,
) -> tuple[
    pd.DataFrame,
    dict[str, Any],
    dict[str, str],
]:
    rows: list[dict[str, float | str]] = []
    reports: dict[str, str] = {}

    for model_name, model in models.items():
        model.fit(split["X_train"], split["y_train"])
        predictions = model.predict(split["X_test"])

        rows.append(
            {
                "Model": model_name,
                "Accuracy": accuracy_score(
                    split["y_test"],
                    predictions,
                ),
                "Precision": precision_score(
                    split["y_test"],
                    predictions,
                    average="weighted",
                    zero_division=0,
                ),
                "Recall": recall_score(
                    split["y_test"],
                    predictions,
                    average="weighted",
                    zero_division=0,
                ),
                "F1-Score": f1_score(
                    split["y_test"],
                    predictions,
                    average="weighted",
                    zero_division=0,
                ),
            }
        )

        reports[model_name] = classification_report(
            split["y_test"],
            predictions,
            target_names=target_names,
            zero_division=0,
        )

    results = (
        pd.DataFrame(rows)
        .sort_values("F1-Score", ascending=False)
        .reset_index(drop=True)
    )
    best_name = str(results.iloc[0]["Model"])

    return (
        results,
        {
            "name": best_name,
            "model": models[best_name],
        },
        reports,
    )


def build_label_distribution(
    data: pd.DataFrame,
    split: dict[str, Any],
) -> pd.DataFrame:
    train_status = (
        data.loc[split["train_idx"], TARGET_COLUMN]
        .value_counts(normalize=True)
        .sort_index()
    )
    test_status = (
        data.loc[split["test_idx"], TARGET_COLUMN]
        .value_counts(normalize=True)
        .sort_index()
    )
    return pd.DataFrame(
        {
            "train_distribution": train_status,
            "test_distribution": test_status,
        }
    ).fillna(0)


def _safe_name(value: str) -> str:
    return value.lower().replace(" ", "_")


def save_evaluation_outputs(
    mode: SplitMode,
    results: pd.DataFrame,
    best: dict[str, Any],
    reports: dict[str, str],
    split: dict[str, Any],
    target_names: np.ndarray,
    results_dir: Path = RESULTS_DIR,
    reports_dir: Path = REPORTS_DIR,
) -> dict[str, Path]:
    results_dir = Path(results_dir)
    reports_dir = Path(reports_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    prefix = (
        "scoby_watch_ml_baseline"
        if mode == "random"
        else "scoby_watch_group_split_ml"
    )

    result_path = results_dir / f"{prefix}_results.csv"
    results.to_csv(result_path, index=False)

    report_path = (
        results_dir / f"{prefix}_classification_reports.txt"
    )
    with report_path.open("w", encoding="utf-8") as handle:
        for model_name, report in reports.items():
            handle.write("=" * 70 + "\n")
            handle.write(model_name + "\n")
            handle.write("=" * 70 + "\n")
            handle.write(report + "\n")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(results["Model"], results["F1-Score"])
    title_prefix = (
        "ML Baseline"
        if mode == "random"
        else "Group Split ML Baseline"
    )
    ax.set(
        title=(
            f"{title_prefix} Model Comparison Based on F1-Score"
        ),
        xlabel="Model",
        ylabel="Weighted F1-Score",
        ylim=(0, 1.05),
    )
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    comparison_path = (
        reports_dir / f"{mode}_split_model_comparison.png"
    )
    fig.savefig(comparison_path, dpi=150)
    plt.close(fig)

    best_model = best["model"]
    predictions = best_model.predict(split["X_test"])
    matrix = confusion_matrix(
        split["y_test"],
        predictions,
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(matrix)
    ax.set(
        title=(
            f"{mode.title()} Split Confusion Matrix - "
            f"{best['name']}"
        ),
        xlabel="Predicted Label",
        ylabel="True Label",
    )
    positions = np.arange(len(target_names))
    ax.set_xticks(
        positions,
        labels=target_names,
        rotation=45,
        ha="right",
    )
    ax.set_yticks(
        positions,
        labels=target_names,
    )

    for row in range(len(target_names)):
        for column in range(len(target_names)):
            ax.text(
                column,
                row,
                matrix[row, column],
                ha="center",
                va="center",
            )

    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    confusion_path = (
        reports_dir
        / f"{mode}_split_best_model_confusion_matrix.png"
    )
    fig.savefig(confusion_path, dpi=150)
    plt.close(fig)

    return {
        "results": result_path.resolve(),
        "classification_reports": report_path.resolve(),
        "comparison_chart": comparison_path.resolve(),
        "confusion_matrix": confusion_path.resolve(),
    }


def save_group_artifacts(
    results: pd.DataFrame,
    best: dict[str, Any],
    encoders: dict[str, LabelEncoder],
    split: dict[str, Any],
    models_dir: Path = MODELS_DIR,
) -> dict[str, Path]:
    """Save only the authoritative group-split model artifacts."""
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = (
        models_dir
        / "scoby_watch_best_group_split_model.pkl"
    )
    encoders_path = (
        models_dir
        / "scoby_watch_label_encoders.pkl"
    )
    features_path = (
        models_dir
        / "scoby_watch_feature_columns.pkl"
    )
    metadata_path = models_dir / "metadata.json"

    joblib.dump(best["model"], model_path)
    joblib.dump(encoders, encoders_path)
    joblib.dump(FEATURE_COLUMNS, features_path)

    metadata = {
        "best_model": best["name"],
        "random_state": RANDOM_STATE,
        "split": {
            "method": "GroupShuffleSplit",
            "n_splits": 1,
            "test_size": TEST_SIZE,
            "train_rows": int(len(split["X_train"])),
            "test_rows": int(len(split["X_test"])),
            "train_batches": int(
                split["train_groups"].nunique()
            ),
            "test_batches": int(
                split["test_groups"].nunique()
            ),
            "batch_overlap": 0,
        },
        "features": FEATURE_COLUMNS,
        "target_classes": (
            encoders[TARGET_COLUMN].classes_.tolist()
        ),
        "metrics": results.iloc[0].to_dict(),
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    return {
        "model": model_path.resolve(),
        "encoders": encoders_path.resolve(),
        "features": features_path.resolve(),
        "metadata": metadata_path.resolve(),
    }


def train_split(
    data: pd.DataFrame,
    encoders: dict[str, LabelEncoder],
    mode: SplitMode,
) -> dict[str, Any]:
    split = (
        random_split(data)
        if mode == "random"
        else group_split(data)
    )
    models = build_models()
    target_names = encoders[TARGET_COLUMN].classes_
    results, best, reports = evaluate_models(
        models,
        split,
        target_names,
    )

    return {
        "mode": mode,
        "split": split,
        "results": results,
        "best": best,
        "reports": reports,
        "target_names": target_names,
    }


def save_split_comparison(
    random_run: dict[str, Any],
    group_run: dict[str, Any],
    results_dir: Path = RESULTS_DIR,
    reports_dir: Path = REPORTS_DIR,
) -> dict[str, Path]:
    results_dir = Path(results_dir)
    reports_dir = Path(reports_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    random_results = random_run["results"].copy()
    random_results["Split Strategy"] = "Random Row Split"

    group_results = group_run["results"].copy()
    group_results["Split Strategy"] = (
        "GroupShuffleSplit by batch_id"
    )

    comparison = pd.concat(
        [random_results, group_results],
        ignore_index=True,
    )
    csv_path = (
        results_dir
        / "scoby_watch_split_strategy_comparison.csv"
    )
    comparison.to_csv(csv_path, index=False)

    pivot = comparison.pivot(
        index="Model",
        columns="Split Strategy",
        values="F1-Score",
    )
    ax = pivot.plot(kind="bar", figsize=(10, 6))
    ax.set(
        title="Random Row Split vs Group Split",
        xlabel="Model",
        ylabel="Weighted F1-Score",
        ylim=(0, 1.05),
    )
    ax.figure.tight_layout()
    chart_path = (
        reports_dir
        / "split_strategy_f1_comparison.png"
    )
    ax.figure.savefig(chart_path, dpi=150)
    plt.close(ax.figure)

    return {
        "comparison_csv": csv_path.resolve(),
        "comparison_chart": chart_path.resolve(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DATASET_PATH,
    )
    parser.add_argument(
        "--mode",
        choices=["random", "group", "both"],
        default="both",
        help=(
            "random reproduces notebook cells 4–7; "
            "group reproduces the final evaluation; "
            "both runs and compares both strategies."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataset(args.dataset)
    data, encoders = encode_dataset(df)

    runs: dict[str, dict[str, Any]] = {}

    modes = (
        ["random", "group"]
        if args.mode == "both"
        else [args.mode]
    )

    for mode in modes:
        run = train_split(
            data,
            encoders,
            mode=mode,
        )
        runs[mode] = run

        paths = save_evaluation_outputs(
            mode=mode,
            results=run["results"],
            best=run["best"],
            reports=run["reports"],
            split=run["split"],
            target_names=run["target_names"],
        )

        label_distribution = build_label_distribution(
            data,
            run["split"],
        )
        label_path = (
            RESULTS_DIR
            / f"scoby_watch_{mode}_split_label_distribution.csv"
        )
        label_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        label_distribution.to_csv(label_path)

        print("=" * 70)
        print(f"{mode.upper()} SPLIT")
        print("=" * 70)
        print(run["results"].to_string(index=False))
        print(f"Best model: {run['best']['name']}")
        print(
            f"Train shape: {run['split']['X_train'].shape}"
        )
        print(
            f"Test shape: {run['split']['X_test'].shape}"
        )

        if mode == "random":
            overlap = set(
                run["split"]["train_groups"].unique()
            ).intersection(
                run["split"]["test_groups"].unique()
            )
            print(
                "Random-row batch overlap count:",
                len(overlap),
            )
        else:
            print(
                "Train unique batches:",
                run["split"]["train_groups"].nunique(),
            )
            print(
                "Test unique batches:",
                run["split"]["test_groups"].nunique(),
            )
            print("Batch overlap count: 0")

            artifact_paths = save_group_artifacts(
                results=run["results"],
                best=run["best"],
                encoders=encoders,
                split=run["split"],
            )
            print("Saved authoritative model artifacts:")
            for name, path in artifact_paths.items():
                print(f"- {name}: {path}")

        print("Saved evaluation outputs:")
        for name, path in paths.items():
            print(f"- {name}: {path}")
        print(f"- label_distribution: {label_path.resolve()}")

    if args.mode == "both":
        comparison_paths = save_split_comparison(
            runs["random"],
            runs["group"],
        )
        print("Saved split-strategy comparison:")
        for name, path in comparison_paths.items():
            print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
