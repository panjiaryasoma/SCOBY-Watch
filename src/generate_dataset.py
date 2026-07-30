"""Generate the complete synthetic SCOBY Watch dataset."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import (
    BATCHES_PER_RECIPE,
    DATASET_PATH,
    DAYS_PER_BATCH,
    RANDOM_STATE,
    RECIPES,
)
from .rule_engine import classify_kombucha_status


def get_rates_by_profile(
    profile: str,
    rng: np.random.RandomState,
) -> tuple[float, float]:
    """Return pH and Brix daily decline rates for one profile."""
    if profile == "fast":
        return rng.uniform(0.15, 0.21), rng.uniform(0.55, 0.80)
    if profile == "slow":
        return rng.uniform(0.06, 0.10), rng.uniform(0.22, 0.36)
    if profile == "sweet":
        return rng.uniform(0.10, 0.15), rng.uniform(0.35, 0.50)
    if profile == "low_sugar":
        return rng.uniform(0.11, 0.16), rng.uniform(0.45, 0.65)
    return rng.uniform(0.10, 0.15), rng.uniform(0.38, 0.55)


def generate_dataset(
    recipes: list[dict[str, Any]] | None = None,
    batches_per_recipe: int = BATCHES_PER_RECIPE,
    days_per_batch: int = DAYS_PER_BATCH,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """Generate 7 recipes × 50 batches × 14 daily observations.

    ``RandomState`` intentionally reproduces the original notebook's
    ``np.random.seed(42)`` sequence.
    """
    recipes = RECIPES if recipes is None else recipes
    rng = np.random.RandomState(random_state)
    rows: list[dict[str, Any]] = []

    for recipe in recipes:
        for batch_num in range(1, batches_per_recipe + 1):
            batch_id = f"KB-{recipe['recipe_id']}-{batch_num:03d}"

            sugar_actual = rng.normal(recipe["sugar_g_per_l"], 4)
            starter_actual = rng.normal(recipe["starter_ml"], 12)
            base_temp = rng.normal(25, 2)
            base_humidity = rng.normal(68, 7)

            if rng.rand() < 0.06:
                base_temp = rng.normal(31, 1.0)

            initial_ph = rng.normal(4.65, 0.18)
            initial_brix = np.clip(
                (sugar_actual / 8.0) + rng.normal(0, 0.6),
                6.0,
                14.0,
            )

            ph_drop_rate, brix_drop_rate = get_rates_by_profile(
                recipe["profile"],
                rng,
            )

            if recipe["starter_ml"] > 180:
                ph_drop_rate *= 1.15
                brix_drop_rate *= 1.12
            elif recipe["starter_ml"] < 120:
                ph_drop_rate *= 0.85
                brix_drop_rate *= 0.88

            for day in range(1, days_per_batch + 1):
                daily_temp = np.clip(
                    base_temp + rng.normal(0, 0.75),
                    15,
                    35,
                )
                humidity = np.clip(
                    base_humidity + rng.normal(0, 4),
                    40,
                    90,
                )
                ph = np.clip(
                    initial_ph - (ph_drop_rate * day) + rng.normal(0, 0.07),
                    2.4,
                    5.0,
                )
                brix = np.clip(
                    initial_brix
                    - (brix_drop_rate * day)
                    + rng.normal(0, 0.30),
                    1.5,
                    14.0,
                )

                rule_result = classify_kombucha_status(
                    temperature_c=float(daily_temp),
                    humidity_percent=float(humidity),
                    ph=float(ph),
                    brix=float(brix),
                    fermentation_day=day,
                )

                rows.append(
                    {
                        "batch_id": batch_id,
                        "recipe_id": recipe["recipe_id"],
                        "recipe_name": recipe["recipe_name"],
                        "tea_type": recipe["tea_type"],
                        "sugar_g_per_l": round(float(sugar_actual), 2),
                        "starter_ml": round(float(starter_actual), 2),
                        "water_volume_l": recipe["water_volume_l"],
                        "day": day,
                        "room_temp_c": round(float(daily_temp), 2),
                        "humidity_percent": round(float(humidity), 2),
                        "ph": round(float(ph), 2),
                        "brix": round(float(brix), 2),
                        "expected_status": rule_result["status"],
                        "recommendation": rule_result["recommendation"],
                        "rule_triggered": rule_result["rule_triggered"],
                        "risk_flag": rule_result["risk_flag"],
                    }
                )

    return pd.DataFrame(rows)


def save_dataset(
    df: pd.DataFrame,
    output_path: Path = DATASET_PATH,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DATASET_PATH)
    parser.add_argument("--random-state", type=int, default=RANDOM_STATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = generate_dataset(random_state=args.random_state)
    output = save_dataset(df, args.output)

    print(f"Dataset shape: {df.shape}")
    print(f"Unique recipes: {df['recipe_id'].nunique()}")
    print(f"Unique batches: {df['batch_id'].nunique()}")
    print("Status distribution:")
    print(df["expected_status"].value_counts().to_string())
    print(f"Saved dataset: {output}")


if __name__ == "__main__":
    main()
