from __future__ import annotations

import pytest

from src.rule_engine import (
    classify_kombucha_status,
    generate_final_recommendation,
)


@pytest.mark.parametrize(
    ("temperature", "ph", "brix", "day", "expected_status", "expected_rule"),
    [
        (30.1, 3.5, 7.0, 7, "temperature_warning", "R1_high_temperature_warning"),
        (17.9, 3.5, 7.0, 7, "manual_check", "R2_low_temperature_slow_fermentation"),
        (25.0, 4.21, 9.0, 3, "too_early", "R3_early_acidity_stage"),
        (25.0, 2.99, 7.0, 9, "too_sour", "R4_R5_over_acidic_or_low_sweetness"),
        (25.0, 3.5, 7.0, 3, "manual_check", "R9_early_day_manual_check"),
        (25.0, 3.5, 8.01, 7, "still_sweet", "R6_sweet_fermentation_stage"),
        (25.0, 3.5, 7.0, 7, "balanced", "R10_balanced_ready_window"),
        (25.0, 3.5, 7.0, 6, "balanced", "R7_balanced_but_early"),
    ],
)
def test_rule_engine_main_paths(
    temperature,
    ph,
    brix,
    day,
    expected_status,
    expected_rule,
):
    result = classify_kombucha_status(
        temperature_c=temperature,
        humidity_percent=68,
        ph=ph,
        brix=brix,
        fermentation_day=day,
    )

    assert result["status"] == expected_status
    assert result["rule_triggered"] == expected_rule
    assert result["recommendation"]
    assert result["risk_flag"] in {"normal", "caution", "warning"}


def test_rule_boundaries_do_not_trigger_strict_temperature_conditions():
    result_at_30 = classify_kombucha_status(
        temperature_c=30.0,
        humidity_percent=68,
        ph=3.5,
        brix=7.0,
        fermentation_day=7,
    )
    result_at_18 = classify_kombucha_status(
        temperature_c=18.0,
        humidity_percent=68,
        ph=3.5,
        brix=7.0,
        fermentation_day=7,
    )

    assert result_at_30["status"] == "balanced"
    assert result_at_18["status"] == "balanced"


def test_extended_overfermentation_rule_has_priority_after_temperature():
    result = classify_kombucha_status(
        temperature_c=25.0,
        humidity_percent=68,
        ph=3.1,
        brix=4.9,
        fermentation_day=15,
    )

    assert result["status"] == "too_sour"
    assert result["rule_triggered"] == "R11_extended_over_fermentation"


def test_final_recommendation_has_manual_fallback():
    recommendation = generate_final_recommendation("unknown_status")

    assert "Manual inspection" in recommendation
