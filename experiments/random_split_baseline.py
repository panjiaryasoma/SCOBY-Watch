"""Reproduce the notebook's initial random-row ML baseline.

This experiment is retained for archival completeness. The authoritative
paper evaluation remains GroupShuffleSplit by batch_id.
"""

from __future__ import annotations

from io import StringIO

from src.config import RESULTS_DIR
from src.train_models import (
    build_label_distribution,
    encode_dataset,
    load_dataset,
    save_evaluation_outputs,
    train_split,
)


def build_summary_text(run: dict, overlap_count: int) -> str:
    buffer = StringIO()
    buffer.write("INITIAL RANDOM-ROW ML BASELINE\n")
    buffer.write("=" * 70 + "\n")
    buffer.write(f"Train shape: {run['split']['X_train'].shape}\n")
    buffer.write(f"Test shape: {run['split']['X_test'].shape}\n")
    buffer.write(
        f"Train unique batch: "
        f"{run['split']['train_groups'].nunique()}\n"
    )
    buffer.write(
        f"Test unique batch: "
        f"{run['split']['test_groups'].nunique()}\n"
    )
    buffer.write(f"Overlapping batch_id: {overlap_count}\n\n")
    buffer.write("MODEL COMPARISON\n")
    buffer.write(run["results"].to_string(index=False))
    buffer.write("\n\n")
    buffer.write(f"Best model: {run['best']['name']}\n")
    buffer.write(
        "\nMethodological note: the random-row split may place "
        "observations from the same batch in both train and test sets. "
        "It is retained only to reproduce the notebook's early baseline.\n"
    )
    return buffer.getvalue()


def main() -> None:
    df = load_dataset()
    data, encoders = encode_dataset(df)

    run = train_split(data, encoders, mode="random")

    output_paths = save_evaluation_outputs(
        mode="random",
        results=run["results"],
        best=run["best"],
        reports=run["reports"],
        split=run["split"],
        target_names=run["target_names"],
    )

    label_distribution = build_label_distribution(data, run["split"])
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    label_csv = (
        RESULTS_DIR
        / "scoby_watch_random_split_label_distribution.csv"
    )
    label_distribution.to_csv(label_csv)

    label_txt = RESULTS_DIR / "RANDOM SPLIT LABEL DISTRIBUTION.txt"
    label_txt.write_text(
        label_distribution.to_string() + "\n",
        encoding="utf-8",
    )

    overlap = set(
        run["split"]["train_groups"].unique()
    ).intersection(
        run["split"]["test_groups"].unique()
    )

    summary_text = build_summary_text(
        run,
        overlap_count=len(overlap),
    )
    summary_txt = RESULTS_DIR / "RANDOM ROW SPLIT BASELINE.txt"
    summary_txt.write_text(summary_text, encoding="utf-8")

    print(summary_text)
    print("Saved outputs:")
    for name, path in output_paths.items():
        print(f"- {name}: {path}")
    print(f"- label_distribution_csv: {label_csv.resolve()}")
    print(f"- label_distribution_txt: {label_txt.resolve()}")
    print(f"- summary_txt: {summary_txt.resolve()}")


if __name__ == "__main__":
    main()
