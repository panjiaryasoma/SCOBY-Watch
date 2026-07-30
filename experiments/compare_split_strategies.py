"""Compare the notebook's random-row split and final group-aware split."""

from __future__ import annotations

from io import StringIO

from src.config import RESULTS_DIR
from src.train_models import (
    build_label_distribution,
    encode_dataset,
    load_dataset,
    save_split_comparison,
    train_split,
)


def split_summary(name: str, run: dict) -> str:
    train_batches = set(run["split"]["train_groups"].unique())
    test_batches = set(run["split"]["test_groups"].unique())
    overlap = train_batches.intersection(test_batches)

    buffer = StringIO()
    buffer.write(name + "\n")
    buffer.write("=" * 70 + "\n")
    buffer.write(f"Train shape: {run['split']['X_train'].shape}\n")
    buffer.write(f"Test shape: {run['split']['X_test'].shape}\n")
    buffer.write(f"Train unique batch: {len(train_batches)}\n")
    buffer.write(f"Test unique batch: {len(test_batches)}\n")
    buffer.write(f"Overlapping batch_id: {len(overlap)}\n\n")
    buffer.write(run["results"].to_string(index=False))
    buffer.write("\n\n")
    buffer.write(f"Best model: {run['best']['name']}\n")
    return buffer.getvalue()


def model_reports_text(name: str, run: dict) -> str:
    buffer = StringIO()
    buffer.write(name + "\n")
    for model_name, report in run["reports"].items():
        buffer.write("=" * 70 + "\n")
        buffer.write(model_name + "\n")
        buffer.write("=" * 70 + "\n")
        buffer.write(report)
        buffer.write("\n")
    buffer.write("MODEL COMPARISON\n")
    buffer.write(run["results"].to_string(index=False))
    buffer.write("\n")
    return buffer.getvalue()


def main() -> None:
    df = load_dataset()
    data, encoders = encode_dataset(df)

    random_run = train_split(data, encoders, mode="random")
    group_run = train_split(data, encoders, mode="group")

    random_summary = split_summary("RANDOM ROW SPLIT", random_run)
    group_summary = split_summary(
        "GROUP SHUFFLE SPLIT BY batch_id",
        group_run,
    )

    interpretation = (
        "INTERPRETATION\n"
        + "=" * 70
        + "\n"
        + "The random-row split is retained as an historical baseline. "
          "Rows from the same fermentation batch may appear in both "
          "subsets, creating a batch-leakage risk.\n"
        + "The GroupShuffleSplit result is the authoritative evaluation "
          "used by the paper because every batch_id is assigned "
          "exclusively to either train or test.\n"
    )

    complete_text = (
        random_summary
        + "\n"
        + group_summary
        + "\n"
        + interpretation
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    comparison_txt = RESULTS_DIR / "SPLIT STRATEGY COMPARISON.txt"
    comparison_txt.write_text(complete_text, encoding="utf-8")

    group_split_txt = (
        RESULTS_DIR / "GROUP SHUFFLE SPLIT BY batch_id.txt"
    )
    group_split_txt.write_text(group_summary, encoding="utf-8")

    group_distribution = build_label_distribution(
        data,
        group_run["split"],
    )
    group_distribution_txt = (
        RESULTS_DIR
        / "CHECK LABEL DISTRIBUTION AFTER GROUP SPLIT.txt"
    )
    group_distribution_txt.write_text(
        group_distribution.to_string() + "\n",
        encoding="utf-8",
    )

    group_models_txt = (
        RESULTS_DIR
        / "TRAIN ML BASELINE MODELS WITH GROUP SPLIT.txt"
    )
    group_models_txt.write_text(
        model_reports_text(
            "TRAIN ML BASELINE MODELS WITH GROUP SPLIT",
            group_run,
        ),
        encoding="utf-8",
    )

    random_models_txt = (
        RESULTS_DIR
        / "TRAIN ML BASELINE MODELS WITH RANDOM SPLIT.txt"
    )
    random_models_txt.write_text(
        model_reports_text(
            "TRAIN ML BASELINE MODELS WITH RANDOM SPLIT",
            random_run,
        ),
        encoding="utf-8",
    )

    output_paths = save_split_comparison(
        random_run,
        group_run,
    )

    print(complete_text)
    print("Saved outputs:")
    for name, path in output_paths.items():
        print(f"- {name}: {path}")
    print(f"- comparison_txt: {comparison_txt.resolve()}")
    print(f"- group_split_txt: {group_split_txt.resolve()}")
    print(
        f"- group_distribution_txt: "
        f"{group_distribution_txt.resolve()}"
    )
    print(f"- group_models_txt: {group_models_txt.resolve()}")
    print(f"- random_models_txt: {random_models_txt.resolve()}")


if __name__ == "__main__":
    main()
