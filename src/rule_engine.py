"""Rule Model v1.1 and final recommendation mapping."""

from __future__ import annotations

from typing import TypedDict


class RuleResult(TypedDict):
    status: str
    recommendation: str
    rule_triggered: str
    risk_flag: str


def classify_kombucha_status(
    temperature_c: float,
    humidity_percent: float,
    ph: float,
    brix: float,
    fermentation_day: int,
) -> RuleResult:
    """Return a readiness-oriented rule result.

    The function mirrors the final Rule Model v1.1 used by the notebook and
    Flask API. It is decision-support logic, not food-safety validation.
    """
    _ = humidity_percent  # Recorded for monitoring; not a primary rule threshold.

    if temperature_c > 30:
        return {
            "status": "temperature_warning",
            "recommendation": (
                "Move the batch to a cooler area and monitor closely."
            ),
            "rule_triggered": "R1_high_temperature_warning",
            "risk_flag": "warning",
        }

    if temperature_c < 18:
        return {
            "status": "manual_check",
            "recommendation": (
                "Temperature is too low. Fermentation may slow down. "
                "Perform manual inspection."
            ),
            "rule_triggered": "R2_low_temperature_slow_fermentation",
            "risk_flag": "caution",
        }

    if fermentation_day > 14 and (ph < 3.2 or brix < 5.0):
        return {
            "status": "too_sour",
            "recommendation": (
                "The batch may be over-fermented. Consider using it as starter "
                "or dilute based on taste preference."
            ),
            "rule_triggered": "R11_extended_over_fermentation",
            "risk_flag": "caution",
        }

    if ph > 4.2:
        return {
            "status": "too_early",
            "recommendation": (
                "Continue fermentation and check again within 24 hours."
            ),
            "rule_triggered": "R3_early_acidity_stage",
            "risk_flag": "normal",
        }

    if ph < 3.0 or brix < 5.0:
        return {
            "status": "too_sour",
            "recommendation": (
                "The batch may be over-fermented. Consider using it as starter "
                "or dilute based on taste preference."
            ),
            "rule_triggered": "R4_R5_over_acidic_or_low_sweetness",
            "risk_flag": "caution",
        }

    if fermentation_day < 5 and 3.2 <= ph <= 4.2:
        return {
            "status": "manual_check",
            "recommendation": (
                "Fermentation is still early. Perform manual inspection before "
                "making a decision."
            ),
            "rule_triggered": "R9_early_day_manual_check",
            "risk_flag": "caution",
        }

    if 3.2 <= ph <= 4.2 and brix > 8.0:
        return {
            "status": "still_sweet",
            "recommendation": (
                "Continue fermentation or start taste testing."
            ),
            "rule_triggered": "R6_sweet_fermentation_stage",
            "risk_flag": "normal",
        }

    if 3.2 <= ph <= 4.2 and 5.0 <= brix <= 8.0:
        if fermentation_day >= 7:
            return {
                "status": "balanced",
                "recommendation": (
                    "Start taste testing and consider bottling if the flavor "
                    "matches preference."
                ),
                "rule_triggered": "R10_balanced_ready_window",
                "risk_flag": "normal",
            }

        return {
            "status": "balanced",
            "recommendation": (
                "Balanced profile detected, but fermentation day is still early. "
                "Taste testing is recommended."
            ),
            "rule_triggered": "R7_balanced_but_early",
            "risk_flag": "normal",
        }

    return {
        "status": "manual_check",
        "recommendation": (
            "Perform manual inspection using visual check, aroma, pH, Brix, "
            "and taste evaluation before making a decision."
        ),
        "rule_triggered": "R8_ambiguous_condition",
        "risk_flag": "caution",
    }


def generate_final_recommendation(final_status: str) -> str:
    recommendations = {
        "too_early": "Continue fermentation and check again within 24 hours.",
        "still_sweet": "Continue fermentation or start taste testing.",
        "balanced": (
            "Start taste testing and consider bottling if the flavor "
            "matches preference."
        ),
        "too_sour": (
            "The batch may be over-fermented. Consider using it as starter "
            "or dilute based on taste preference."
        ),
        "temperature_warning": (
            "Move the batch to a cooler area and monitor closely."
        ),
        "manual_check": (
            "Perform manual inspection using visual check, aroma, pH, Brix, "
            "and taste evaluation before making a decision."
        ),
    }
    return recommendations.get(
        final_status,
        "Manual inspection is recommended before making a decision.",
    )
