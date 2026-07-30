from __future__ import annotations

import pandas as pd

from src.validate_dataset import (
    build_batch_trend_check,
    build_range_issues,
    validate_integrity,
)


EXPECTED_COLUMNS = [
    "batch_id",
    "recipe_id",
    "recipe_name",
    "tea_type",
    "sugar_g_per_l",
    "starter_ml",
    "water_volume_l",
    "day",
    "room_temp_c",
    "humidity_percent",
    "ph",
    "brix",
    "expected_status",
    "recommendation",
    "rule_triggered",
    "risk_flag",
]


def test_generated_dataset_matches_fixed_contract(generated_dataset):
    df = generated_dataset

    assert df.shape == (4900, 16)
    assert list(df.columns) == EXPECTED_COLUMNS
    assert df["recipe_id"].nunique() == 7
    assert df["batch_id"].nunique() == 350
    assert df.isna().sum().sum() == 0
    assert df.duplicated().sum() == 0

    rows_per_batch = df.groupby("batch_id").size()
    assert rows_per_batch.eq(14).all()


def test_generated_dataset_is_deterministic():
    from src.generate_dataset import generate_dataset

    first = generate_dataset(random_state=42)
    second = generate_dataset(random_state=42)

    pd.testing.assert_frame_equal(first, second)


def test_generated_values_stay_inside_configured_ranges(generated_dataset):
    issues = build_range_issues(generated_dataset)

    assert int(issues["count"].sum()) == 0
    assert generated_dataset["room_temp_c"].between(15, 35).all()
    assert generated_dataset["humidity_percent"].between(40, 90).all()
    assert generated_dataset["ph"].between(2.4, 5.0).all()
    assert generated_dataset["brix"].between(1.5, 14.0).all()


def test_every_batch_has_decreasing_ph_and_brix_trends(generated_dataset):
    trend = build_batch_trend_check(generated_dataset)

    assert len(trend) == 350
    assert trend["ph_trend_ok"].all()
    assert trend["brix_trend_ok"].all()


def test_validate_integrity_returns_expected_summary(generated_dataset):
    summary = validate_integrity(generated_dataset)

    assert summary == {
        "rows": 4900,
        "columns": 16,
        "missing_values": 0,
        "duplicate_rows": 0,
        "unique_recipes": 7,
        "unique_batches": 350,
        "minimum_rows_per_batch": 14,
        "maximum_rows_per_batch": 14,
    }
