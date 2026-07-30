from __future__ import annotations

import pytest

from src.hybrid_decision import hybrid_decision_layer


def make_rule(
    status: str,
    risk_flag: str = "normal",
    rule_triggered: str = "R_TEST",
):
    return {
        "status": status,
        "recommendation": "Rule recommendation.",
        "rule_triggered": rule_triggered,
        "risk_flag": risk_flag,
    }


def test_temperature_warning_overrides_ml_prediction():
    result = hybrid_decision_layer(
        make_rule(
            "temperature_warning",
            risk_flag="warning",
            rule_triggered="R1_high_temperature_warning",
        ),
        {"ml_status": "balanced", "ml_confidence": 0.99},
    )

    assert result["final_status"] == "temperature_warning"
    assert "priority" in result["decision_reason"].lower()


@pytest.mark.parametrize("confidence", [None, 0.0, 0.6999])
def test_low_or_missing_confidence_falls_back_to_manual_check(confidence):
    result = hybrid_decision_layer(
        make_rule("balanced"),
        {"ml_status": "balanced", "ml_confidence": confidence},
    )

    assert result["final_status"] == "manual_check"
    assert "confidence" in result["decision_reason"].lower()


def test_confidence_exactly_at_threshold_is_not_low_confidence():
    result = hybrid_decision_layer(
        make_rule("balanced"),
        {"ml_status": "balanced", "ml_confidence": 0.70},
    )

    assert result["final_status"] == "balanced"


def test_rule_and_ml_agreement_preserves_status():
    result = hybrid_decision_layer(
        make_rule("still_sweet"),
        {"ml_status": "still_sweet", "ml_confidence": 0.95},
    )

    assert result["final_status"] == "still_sweet"
    assert result["ml_confidence"] == 0.95
    assert "agree" in result["decision_reason"].lower()


@pytest.mark.parametrize(
    ("rule_status", "ml_status"),
    [
        ("too_sour", "balanced"),
        ("balanced", "too_sour"),
    ],
)
def test_conflict_involving_too_sour_requires_manual_check(
    rule_status,
    ml_status,
):
    result = hybrid_decision_layer(
        make_rule(rule_status, risk_flag="caution"),
        {"ml_status": ml_status, "ml_confidence": 0.95},
    )

    assert result["final_status"] == "manual_check"
    assert "too_sour" in result["decision_reason"]


def test_ordinary_disagreement_requires_manual_check():
    result = hybrid_decision_layer(
        make_rule("still_sweet"),
        {"ml_status": "balanced", "ml_confidence": 0.95},
    )

    assert result["final_status"] == "manual_check"
    assert "disagree" in result["decision_reason"].lower()
