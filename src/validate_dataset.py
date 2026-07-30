"""Reproduce the complete dataset sanity and visualization section."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

from .config import (
    DATASET_PATH,
    EXPECTED_DATASET_COLUMNS,
    REPORTS_DIR,
    VALIDATION_DIR,
)

matplotlib.use("Agg")
from matplotlib import pyplot as plt


def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {path}. "
            "Run `python -m src.generate_dataset` first."
        )
    return pd.read_csv(path)


def validate_integrity(df: pd.DataFrame) -> dict[str, int]:
    missing_columns = [
        column for column in EXPECTED_DATASET_COLUMNS if column not in df
    ]
    if missing_columns:
        raise ValueError(f"Dataset is missing columns: {missing_columns}")

    rows_per_batch = df.groupby("batch_id").size()
    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_recipes": int(df["recipe_id"].nunique()),
        "unique_batches": int(df["batch_id"].nunique()),
        "minimum_rows_per_batch": int(rows_per_batch.min()),
        "maximum_rows_per_batch": int(rows_per_batch.max()),
    }

    expected = {
        "rows": 4900,
        "columns": 16,
        "missing_values": 0,
        "duplicate_rows": 0,
        "unique_recipes": 7,
        "unique_batches": 350,
        "minimum_rows_per_batch": 14,
        "maximum_rows_per_batch": 14,
    }

    mismatches = {
        key: {
            "observed": summary[key],
            "expected": expected[key],
        }
        for key in expected
        if summary[key] != expected[key]
    }
    if mismatches:
        raise ValueError(f"Dataset integrity check failed: {mismatches}")

    return summary


def build_range_summary(df: pd.DataFrame) -> pd.DataFrame:
    sensor_cols = [
        "room_temp_c",
        "humidity_percent",
        "ph",
        "brix",
        "sugar_g_per_l",
        "starter_ml",
    ]
    return df[sensor_cols].describe().T


def build_range_issues(df: pd.DataFrame) -> pd.DataFrame:
    issues = {
        "temp_below_15": int((df["room_temp_c"] < 15).sum()),
        "temp_above_35": int((df["room_temp_c"] > 35).sum()),
        "humidity_below_40": int((df["humidity_percent"] < 40).sum()),
        "humidity_above_90": int((df["humidity_percent"] > 90).sum()),
        "ph_below_2_4": int((df["ph"] < 2.4).sum()),
        "ph_above_5_0": int((df["ph"] > 5.0).sum()),
        "brix_below_1_5": int((df["brix"] < 1.5).sum()),
        "brix_above_14": int((df["brix"] > 14.0).sum()),
    }
    return pd.DataFrame(issues.items(), columns=["check", "count"])


def build_batch_trend_check(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for batch_id, batch_df in df.groupby("batch_id"):
        batch_df = batch_df.sort_values("day")
        ph_slope = float(
            np.polyfit(batch_df["day"], batch_df["ph"], 1)[0]
        )
        brix_slope = float(
            np.polyfit(batch_df["day"], batch_df["brix"], 1)[0]
        )
        rows.append(
            {
                "batch_id": batch_id,
                "recipe_id": batch_df["recipe_id"].iloc[0],
                "ph_slope": ph_slope,
                "brix_slope": brix_slope,
                "ph_trend_ok": ph_slope < 0,
                "brix_trend_ok": brix_slope < 0,
            }
        )

    return pd.DataFrame(rows)


def build_status_transition_sample(
    df: pd.DataFrame,
    sample_count: int = 10,
) -> str:
    blocks: list[str] = []
    sample_batches = df["batch_id"].drop_duplicates().head(sample_count)

    for batch_id in sample_batches:
        batch_df = df[df["batch_id"] == batch_id].sort_values("day")
        table = batch_df[
            [
                "day",
                "room_temp_c",
                "ph",
                "brix",
                "expected_status",
                "rule_triggered",
            ]
        ].to_string(index=False)
        blocks.extend(
            [
                "=" * 80,
                f"Batch: {batch_id}",
                (
                    f"Recipe: {batch_df['recipe_id'].iloc[0]} - "
                    f"{batch_df['recipe_name'].iloc[0]}"
                ),
                table,
            ]
        )

    return "\n".join(blocks) + "\n"


def build_validation_tables(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame | pd.Series]:
    status_by_day = pd.crosstab(
        df["day"],
        df["expected_status"],
    )
    status_by_recipe = pd.crosstab(
        df["recipe_id"],
        df["expected_status"],
    )

    return {
        "sanity_status_by_day.csv": status_by_day,
        "sanity_status_by_day_percent.csv": (
            pd.crosstab(
                df["day"],
                df["expected_status"],
                normalize="index",
            )
            * 100
        ).round(2),
        "sanity_status_by_recipe.csv": status_by_recipe,
        "sanity_status_by_recipe_percent.csv": (
            pd.crosstab(
                df["recipe_id"],
                df["expected_status"],
                normalize="index",
            )
            * 100
        ).round(2),
        "sanity_ph_by_day.csv": (
            df.groupby("day")["ph"].mean().reset_index()
        ),
        "sanity_brix_by_day.csv": (
            df.groupby("day")["brix"].mean().reset_index()
        ),
        "sanity_ph_by_recipe.csv": (
            df.groupby(["recipe_id", "day"])["ph"]
            .mean()
            .reset_index()
        ),
        "sanity_brix_by_recipe.csv": (
            df.groupby(["recipe_id", "day"])["brix"]
            .mean()
            .reset_index()
        ),
        "sanity_batch_trend_check.csv": build_batch_trend_check(df),
        "sanity_rule_distribution.csv": (
            df["rule_triggered"].value_counts()
        ),
        "sanity_status_distribution.csv": (
            df["expected_status"].value_counts()
        ),
        "sanity_status_distribution_percent.csv": (
            df["expected_status"].value_counts(normalize=True) * 100
        ).round(2),
    }


def save_validation_outputs(
    df: pd.DataFrame,
    validation_dir: Path = VALIDATION_DIR,
) -> list[Path]:
    validation_dir = Path(validation_dir)
    validation_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    summary = validate_integrity(df)
    summary_path = validation_dir / "sanity_dataset_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    paths.append(summary_path.resolve())

    range_summary_path = validation_dir / "sanity_sensor_range_summary.csv"
    build_range_summary(df).to_csv(range_summary_path)
    paths.append(range_summary_path.resolve())

    range_issues_path = validation_dir / "sanity_sensor_range_issues.csv"
    build_range_issues(df).to_csv(range_issues_path, index=False)
    paths.append(range_issues_path.resolve())

    tables = build_validation_tables(df)
    for filename, table in tables.items():
        path = validation_dir / filename
        if isinstance(table, pd.DataFrame):
            keep_index = filename not in {
                "sanity_ph_by_day.csv",
                "sanity_brix_by_day.csv",
                "sanity_ph_by_recipe.csv",
                "sanity_brix_by_recipe.csv",
                "sanity_batch_trend_check.csv",
            }
            table.to_csv(path, index=keep_index)
        else:
            table.to_csv(path)
        paths.append(path.resolve())

    transitions_path = (
        validation_dir / "sanity_status_transition_samples.txt"
    )
    transitions_path.write_text(
        build_status_transition_sample(df),
        encoding="utf-8",
    )
    paths.append(transitions_path.resolve())

    return paths


def save_validation_plots(
    df: pd.DataFrame,
    reports_dir: Path = REPORTS_DIR,
) -> list[Path]:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    ph_by_day = df.groupby("day")["ph"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ph_by_day["day"], ph_by_day["ph"], marker="o")
    ax.set(
        title="Average pH Trend by Fermentation Day",
        xlabel="Fermentation Day",
        ylabel="Average pH",
    )
    ax.grid(True)
    fig.tight_layout()
    path = reports_dir / "average_ph_by_day.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path.resolve())

    brix_by_day = df.groupby("day")["brix"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(brix_by_day["day"], brix_by_day["brix"], marker="o")
    ax.set(
        title="Average Brix Trend by Fermentation Day",
        xlabel="Fermentation Day",
        ylabel="Average Brix",
    )
    ax.grid(True)
    fig.tight_layout()
    path = reports_dir / "average_brix_by_day.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path.resolve())

    ph_by_recipe = (
        df.groupby(["recipe_id", "day"])["ph"]
        .mean()
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    for recipe_id in sorted(df["recipe_id"].unique()):
        subset = ph_by_recipe[
            ph_by_recipe["recipe_id"].eq(recipe_id)
        ]
        ax.plot(
            subset["day"],
            subset["ph"],
            marker="o",
            label=recipe_id,
        )
    ax.set(
        title="Average pH Trend by Recipe",
        xlabel="Fermentation Day",
        ylabel="Average pH",
    )
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    path = reports_dir / "average_ph_by_recipe.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path.resolve())

    brix_by_recipe = (
        df.groupby(["recipe_id", "day"])["brix"]
        .mean()
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    for recipe_id in sorted(df["recipe_id"].unique()):
        subset = brix_by_recipe[
            brix_by_recipe["recipe_id"].eq(recipe_id)
        ]
        ax.plot(
            subset["day"],
            subset["brix"],
            marker="o",
            label=recipe_id,
        )
    ax.set(
        title="Average Brix Trend by Recipe",
        xlabel="Fermentation Day",
        ylabel="Average Brix",
    )
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    path = reports_dir / "average_brix_by_recipe.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path.resolve())

    status_by_day = pd.crosstab(
        df["day"],
        df["expected_status"],
    )
    ax = status_by_day.plot(
        kind="bar",
        stacked=True,
        figsize=(11, 6),
    )
    ax.set(
        title="Fermentation Status Distribution by Day",
        xlabel="Fermentation Day",
        ylabel="Count",
    )
    ax.legend(
        title="Status",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    ax.figure.tight_layout()
    path = reports_dir / "status_distribution_by_day.png"
    ax.figure.savefig(path, dpi=150)
    plt.close(ax.figure)
    paths.append(path.resolve())

    status_by_recipe = pd.crosstab(
        df["recipe_id"],
        df["expected_status"],
    )
    ax = status_by_recipe.plot(
        kind="bar",
        stacked=True,
        figsize=(11, 6),
    )
    ax.set(
        title="Fermentation Status Distribution by Recipe",
        xlabel="Recipe ID",
        ylabel="Count",
    )
    ax.legend(
        title="Status",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    ax.figure.tight_layout()
    path = reports_dir / "status_distribution_by_recipe.png"
    ax.figure.savefig(path, dpi=150)
    plt.close(ax.figure)
    paths.append(path.resolve())

    rule_distribution = df["rule_triggered"].value_counts()
    ax = rule_distribution.plot(kind="bar", figsize=(10, 5))
    ax.set(
        title="Rule Triggered Distribution",
        xlabel="Rule Triggered",
        ylabel="Count",
    )
    ax.tick_params(axis="x", rotation=45)
    ax.figure.tight_layout()
    path = reports_dir / "rule_triggered_distribution.png"
    ax.figure.savefig(path, dpi=150)
    plt.close(ax.figure)
    paths.append(path.resolve())

    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument(
        "--validation-dir",
        type=Path,
        default=VALIDATION_DIR,
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=REPORTS_DIR,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataset(args.dataset)

    summary = validate_integrity(df)
    range_issues = build_range_issues(df)
    if int(range_issues["count"].sum()) != 0:
        raise ValueError(
            "Generated values fall outside configured boundaries."
        )

    trend_df = build_batch_trend_check(df)
    if not bool(trend_df["ph_trend_ok"].all()):
        raise ValueError(
            "At least one batch has a non-decreasing pH trend."
        )
    if not bool(trend_df["brix_trend_ok"].all()):
        raise ValueError(
            "At least one batch has a non-decreasing Brix trend."
        )

    table_paths = save_validation_outputs(
        df,
        args.validation_dir,
    )
    plot_paths = save_validation_plots(
        df,
        args.reports_dir,
    )

    print("Dataset integrity:")
    for key, value in summary.items():
        print(f"- {key}: {value}")
    print("Range issues: 0")
    print(f"Validation files: {len(table_paths)}")
    print(f"Validation plots: {len(plot_paths)}")


if __name__ == "__main__":
    main()
