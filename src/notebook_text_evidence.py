"""Export notebook-style text evidence from the modular SCOBY Watch pipeline.

The original Colab notebook displayed many tables and dictionaries directly in
cell output. This module preserves those outputs as reproducible UTF-8 text
files under ``results/notebook_text_evidence``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from pprint import pformat
from typing import Any

import pandas as pd

from .config import (
    FEATURE_COLUMNS,
    MODELS_DIR,
    RESULTS_DIR,
    TARGET_COLUMN,
)
from .hybrid_decision import (
    hybrid_decision_layer,
    load_artifacts,
    predict_ml_status,
)
from .rule_engine import classify_kombucha_status
from .train_models import (
    build_label_distribution,
    encode_dataset,
    load_dataset,
    save_group_artifacts,
    train_split,
)
from .validate_dataset import (
    build_batch_trend_check,
    build_range_issues,
    build_status_transition_sample,
)


DEFAULT_EVIDENCE_DIR = RESULTS_DIR / "notebook_text_evidence"


def _write_text(
    evidence_dir: Path,
    filename: str,
    content: str,
) -> Path:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / filename
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return path.resolve()


def build_basic_sanity_text(df: pd.DataFrame) -> str:
    rows_per_recipe = (
        df.groupby("recipe_id").size().rename("count")
    )
    rows_per_batch = df.groupby("batch_id").size()
    status_distribution = (
        df["expected_status"].value_counts().rename("count")
    )
    status_percentage = (
        df["expected_status"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .rename("proportion")
    )

    return "\n".join(
        [
            f"Dataset shape: {df.shape}",
            "",
            "Columns:",
            str(df.columns.tolist()),
            "",
            "Missing values:",
            str(int(df.isna().sum().sum())),
            df.isna().sum().to_string(),
            "",
            "Duplicate rows:",
            str(int(df.duplicated().sum())),
            "",
            f"Unique recipes: {df['recipe_id'].nunique()}",
            f"Unique batches: {df['batch_id'].nunique()}",
            (
                "Unique days: "
                + str(
                    [
                        int(value)
                        for value in sorted(df["day"].unique())
                    ]
                )
            ),
            "",
            "Rows per recipe:",
            rows_per_recipe.to_string(),
            "",
            "Rows per batch summary:",
            rows_per_batch.describe().to_string(),
            "",
            "Status distribution:",
            status_distribution.to_string(),
            "",
            "Status distribution percentage:",
            status_percentage.to_string(),
        ]
    )


def build_sensor_range_text(df: pd.DataFrame) -> str:
    sensor_cols = [
        "room_temp_c",
        "humidity_percent",
        "ph",
        "brix",
        "sugar_g_per_l",
        "starter_ml",
    ]
    summary = df[sensor_cols].describe().T
    issues = build_range_issues(df)
    return (
        summary.to_string()
        + "\n\n"
        + issues.to_string(index=True)
    )


def build_average_table_text(
    df: pd.DataFrame,
    value_column: str,
    by_recipe: bool,
) -> str:
    group_columns = (
        ["recipe_id", "day"]
        if by_recipe
        else ["day"]
    )
    table = (
        df.groupby(group_columns)[value_column]
        .mean()
        .reset_index()
    )
    return table.to_string(index=True)


def build_monotonic_trend_text(df: pd.DataFrame) -> str:
    trend = build_batch_trend_check(df)
    suspicious_ph = trend.loc[~trend["ph_trend_ok"]]
    suspicious_brix = trend.loc[~trend["brix_trend_ok"]]

    return "\n".join(
        [
            f"Total batches: {len(trend)}",
            "",
            "pH trend check:",
            trend["ph_trend_ok"].value_counts().to_string(),
            "",
            "Brix trend check:",
            trend["brix_trend_ok"].value_counts().to_string(),
            "",
            "Batches with suspicious pH trend:",
            suspicious_ph.to_string(index=False),
            "",
            "Batches with suspicious Brix trend:",
            suspicious_brix.to_string(index=False),
        ]
    )


def build_rule_distribution_text(df: pd.DataFrame) -> str:
    return df["rule_triggered"].value_counts().to_string()


def export_dataset_text_evidence(
    df: pd.DataFrame,
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> list[Path]:
    outputs = {
        "BASIC DATASET SANITY CHECK.txt": (
            build_basic_sanity_text(df)
        ),
        "SENSOR RANGE CHECK.txt": (
            build_sensor_range_text(df)
        ),
        "AVERAGE pH TREND BY DAY.txt": (
            build_average_table_text(
                df,
                value_column="ph",
                by_recipe=False,
            )
        ),
        "AVERAGE BRIX TREND BY DAY.txt": (
            build_average_table_text(
                df,
                value_column="brix",
                by_recipe=False,
            )
        ),
        "AVERAGE pH TREND BY RECIPE.txt": (
            build_average_table_text(
                df,
                value_column="ph",
                by_recipe=True,
            )
        ),
        "AVERAGE BRIX TREND BY RECIPE.txt": (
            build_average_table_text(
                df,
                value_column="brix",
                by_recipe=True,
            )
        ),
        "MONOTONIC TREND CHECK PER BATCH.txt": (
            build_monotonic_trend_text(df)
        ),
        "STATUS TRANSITION SAMPLE PER BATCH.txt": (
            build_status_transition_sample(
                df,
                sample_count=10,
            )
        ),
        "RULE TRIGGERED DISTRIBUTION.txt": (
            build_rule_distribution_text(df)
        ),
    }

    return [
        _write_text(evidence_dir, filename, content)
        for filename, content in outputs.items()
    ]


def build_split_summary_text(
    df: pd.DataFrame,
    run: dict[str, Any],
    *,
    group_aware: bool,
) -> str:
    train_batches = set(
        run["split"]["train_groups"].unique()
    )
    test_batches = set(
        run["split"]["test_groups"].unique()
    )
    overlap = train_batches.intersection(test_batches)

    heading = (
        "GROUP SHUFFLE SPLIT BY batch_id"
        if group_aware
        else "RANDOM ROW SPLIT"
    )
    lines = [
        heading,
        "=" * 70,
        f"Dataset shape: {df.shape}",
        f"Unique batch: {df['batch_id'].nunique()}",
        "Expected unique batch: 350",
        f"Train shape: {run['split']['X_train'].shape}",
        f"Test shape: {run['split']['X_test'].shape}",
        f"Train unique batch: {len(train_batches)}",
        f"Test unique batch: {len(test_batches)}",
        f"Overlapping batch_id: {len(overlap)}",
    ]
    if group_aware and not overlap:
        lines.append(
            "Safe: no batch leakage between train and test."
        )
    elif overlap:
        lines.append(
            "Warning: the random-row split contains batch overlap."
        )
    return "\n".join(lines)


def build_model_reports_text(
    heading: str,
    run: dict[str, Any],
) -> str:
    sections = [heading]
    for model_name, report in run["reports"].items():
        sections.extend(
            [
                "=" * 70,
                model_name,
                "=" * 70,
                report.rstrip(),
            ]
        )
    sections.extend(
        [
            "",
            "MODEL COMPARISON",
            run["results"].to_string(index=False),
        ]
    )
    return "\n".join(sections)


def export_training_text_evidence(
    df: pd.DataFrame,
    data: pd.DataFrame,
    random_run: dict[str, Any],
    group_run: dict[str, Any],
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> list[Path]:
    group_distribution = build_label_distribution(
        data,
        group_run["split"],
    )
    random_reports = build_model_reports_text(
        "TRAIN ML BASELINE MODELS WITH RANDOM SPLIT",
        random_run,
    )
    group_reports = build_model_reports_text(
        "TRAIN ML BASELINE MODELS WITH GROUP SPLIT",
        group_run,
    )

    outputs = {
        "RANDOM ROW SPLIT.txt": build_split_summary_text(
            df,
            random_run,
            group_aware=False,
        ),
        "GROUP SHUFFLE SPLIT BY batch_id.txt": (
            build_split_summary_text(
                df,
                group_run,
                group_aware=True,
            )
        ),
        "CHECK LABEL DISTRIBUTION AFTER GROUP SPLIT.txt": (
            group_distribution.to_string()
        ),
        "TRAIN ML BASELINE MODELS WITH RANDOM SPLIT.txt": (
            random_reports
        ),
        "TRAIN ML BASELINE MODELS WITH GROUP SPLIT.txt": (
            group_reports
        ),
        # Legacy notebook download used a misleading filename even though
        # the file contained reports for all five classifiers.
        "Decision Tree.txt": random_reports,
    }

    return [
        _write_text(evidence_dir, filename, content)
        for filename, content in outputs.items()
    ]


def build_model_load_text(
    model: Any,
    label_encoders: dict[str, Any],
    features: list[str],
) -> str:
    return "\n".join(
        [
            f"Model loaded: {model}",
            f"Features: {features}",
            (
                "Available encoders: "
                f"{list(label_encoders.keys())}"
            ),
        ]
    )


def build_single_sample_hybrid_text(
    model: Any,
    label_encoders: dict[str, Any],
    features: list[str],
) -> str:
    sample_input = {
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 7,
        "room_temp_c": 25.5,
        "humidity_percent": 68,
        "ph": 3.5,
        "brix": 6.5,
    }
    rule_result = classify_kombucha_status(
        temperature_c=sample_input["room_temp_c"],
        humidity_percent=sample_input["humidity_percent"],
        ph=sample_input["ph"],
        brix=sample_input["brix"],
        fermentation_day=sample_input["day"],
    )
    ml_result = predict_ml_status(
        sample_input,
        model,
        label_encoders,
        features,
    )
    result = hybrid_decision_layer(
        rule_result,
        ml_result,
    )
    # Preserve the full raw model confidence in notebook evidence. The API
    # response intentionally rounds this value for compact transport.
    result["ml_confidence"] = ml_result["ml_confidence"]
    return pformat(
        result,
        sort_dicts=False,
        width=240,
    )


def export_model_hybrid_text_evidence(
    model: Any,
    label_encoders: dict[str, Any],
    features: list[str],
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> list[Path]:
    outputs = {
        "LOAD BEST MODEL, ENCODERS, AND FEATURES.txt": (
            build_model_load_text(
                model,
                label_encoders,
                features,
            )
        ),
        "TEST HYBRID DECISION WITH ONE SAMPLE UPDATED.txt": (
            build_single_sample_hybrid_text(
                model,
                label_encoders,
                features,
            )
        ),
    }
    return [
        _write_text(evidence_dir, filename, content)
        for filename, content in outputs.items()
    ]


def export_all_notebook_text_evidence(
    df: pd.DataFrame,
    data: pd.DataFrame,
    random_run: dict[str, Any],
    group_run: dict[str, Any],
    model: Any,
    label_encoders: dict[str, Any],
    features: list[str],
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> list[Path]:
    paths: list[Path] = []
    paths.extend(
        export_dataset_text_evidence(
            df,
            evidence_dir,
        )
    )
    paths.extend(
        export_training_text_evidence(
            df,
            data,
            random_run,
            group_run,
            evidence_dir,
        )
    )
    paths.extend(
        export_model_hybrid_text_evidence(
            model,
            label_encoders,
            features,
            evidence_dir,
        )
    )
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataset()
    data, encoders = encode_dataset(df)

    random_run = train_split(
        data,
        encoders,
        mode="random",
    )
    group_run = train_split(
        data,
        encoders,
        mode="group",
    )

    # Ensure the serialized artifacts match the group-split run.
    save_group_artifacts(
        group_run["results"],
        group_run["best"],
        encoders,
        group_run["split"],
        models_dir=MODELS_DIR,
    )
    model, loaded_encoders, features = load_artifacts(
        MODELS_DIR
    )

    paths = export_all_notebook_text_evidence(
        df=df,
        data=data,
        random_run=random_run,
        group_run=group_run,
        model=model,
        label_encoders=loaded_encoders,
        features=features,
        evidence_dir=args.evidence_dir,
    )

    print(
        f"Notebook-style text evidence saved: {len(paths)} file(s)"
    )
    for path in paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
