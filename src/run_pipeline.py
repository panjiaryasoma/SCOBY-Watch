"""Run the complete cleaned SCOBY Watch notebook pipeline in order."""

from __future__ import annotations

import argparse

from .generate_dataset import generate_dataset, save_dataset
from .hybrid_decision import (
    load_artifacts,
    save_hybrid_outputs,
)
from .notebook_text_evidence import (
    export_all_notebook_text_evidence,
)
from .train_models import (
    encode_dataset,
    save_evaluation_outputs,
    save_group_artifacts,
    save_split_comparison,
    train_split,
)
from .validate_dataset import (
    build_batch_trend_check,
    build_range_issues,
    save_validation_outputs,
    save_validation_plots,
    validate_integrity,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-random-baseline",
        action="store_true",
        help=(
            "Skip the historical random-row baseline and run "
            "only the authoritative group split."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("[1/6] Generating dataset")
    df = generate_dataset()
    dataset_path = save_dataset(df)
    print(f"Saved: {dataset_path}")

    print("[2/6] Validating dataset")
    validate_integrity(df)
    if int(build_range_issues(df)["count"].sum()) != 0:
        raise ValueError("Out-of-range values detected.")

    trends = build_batch_trend_check(df)
    if not bool(trends["ph_trend_ok"].all()):
        raise ValueError("Non-decreasing pH trend detected.")
    if not bool(trends["brix_trend_ok"].all()):
        raise ValueError("Non-decreasing Brix trend detected.")

    save_validation_outputs(df)
    save_validation_plots(df)

    print("[3/6] Training model baselines")
    data, encoders = encode_dataset(df)
    runs = {}

    if not args.skip_random_baseline:
        random_run = train_split(
            data,
            encoders,
            mode="random",
        )
        runs["random"] = random_run
        save_evaluation_outputs(
            mode="random",
            results=random_run["results"],
            best=random_run["best"],
            reports=random_run["reports"],
            split=random_run["split"],
            target_names=random_run["target_names"],
        )

    group_run = train_split(
        data,
        encoders,
        mode="group",
    )
    runs["group"] = group_run
    save_evaluation_outputs(
        mode="group",
        results=group_run["results"],
        best=group_run["best"],
        reports=group_run["reports"],
        split=group_run["split"],
        target_names=group_run["target_names"],
    )
    save_group_artifacts(
        group_run["results"],
        group_run["best"],
        encoders,
        group_run["split"],
    )

    if "random" in runs:
        print("[4/6] Comparing split strategies")
        save_split_comparison(
            runs["random"],
            runs["group"],
        )
    else:
        print("[4/6] Random baseline skipped")

    print("[5/6] Running hybrid validation")
    model, loaded_encoders, features = load_artifacts()
    save_hybrid_outputs(
        model,
        loaded_encoders,
        features,
    )

    print("[6/6] Exporting notebook-style text evidence")
    if "random" not in runs:
        random_run = train_split(
            data,
            encoders,
            mode="random",
        )
        runs["random"] = random_run

    evidence_paths = export_all_notebook_text_evidence(
        df=df,
        data=data,
        random_run=runs["random"],
        group_run=runs["group"],
        model=model,
        label_encoders=loaded_encoders,
        features=features,
    )
    print(
        f"Notebook-style text evidence: "
        f"{len(evidence_paths)} file(s)"
    )

    print("Complete SCOBY Watch pipeline finished.")
    print(
        "Authoritative final evaluation: "
        "GroupShuffleSplit by batch_id."
    )


if __name__ == "__main__":
    main()
