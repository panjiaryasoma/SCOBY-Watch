"""ML input preparation, prediction, and hybrid-decision validation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, TypedDict

import joblib
import numpy as np
import pandas as pd

from .config import (
    CONFIDENCE_THRESHOLD,
    MODELS_DIR,
    RESULTS_DIR,
)
from .rule_engine import (
    classify_kombucha_status,
    generate_final_recommendation,
)


class MLResult(TypedDict):
    ml_status: str
    ml_confidence: float | None


def load_artifacts(
    models_dir: Path = MODELS_DIR,
) -> tuple[Any, dict[str, Any], list[str]]:
    models_dir = Path(models_dir)

    model_path = (
        models_dir
        / "scoby_watch_best_group_split_model.pkl"
    )
    encoders_path = (
        models_dir
        / "scoby_watch_label_encoders.pkl"
    )
    features_path = (
        models_dir
        / "scoby_watch_feature_columns.pkl"
    )

    missing = [
        str(path)
        for path in (
            model_path,
            encoders_path,
            features_path,
        )
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(
            f"Missing model artifacts: {missing}"
        )

    return (
        joblib.load(model_path),
        joblib.load(encoders_path),
        joblib.load(features_path),
    )


def prepare_ml_input(
    input_data: dict[str, Any],
    label_encoders: dict[str, Any],
    features: list[str],
) -> pd.DataFrame:
    recipe_id_encoded = label_encoders[
        "recipe_id"
    ].transform([input_data["recipe_id"]])[0]

    tea_type_encoded = label_encoders[
        "tea_type"
    ].transform([input_data["tea_type"]])[0]

    row = pd.DataFrame(
        [
            {
                "recipe_id_encoded": recipe_id_encoded,
                "tea_type_encoded": tea_type_encoded,
                "sugar_g_per_l": input_data[
                    "sugar_g_per_l"
                ],
                "starter_ml": input_data["starter_ml"],
                "water_volume_l": input_data[
                    "water_volume_l"
                ],
                "day": input_data["day"],
                "room_temp_c": input_data[
                    "room_temp_c"
                ],
                "humidity_percent": input_data[
                    "humidity_percent"
                ],
                "ph": input_data["ph"],
                "brix": input_data["brix"],
            }
        ]
    )

    return row[features]


def predict_ml_status(
    input_data: dict[str, Any],
    model: Any,
    label_encoders: dict[str, Any],
    features: list[str],
) -> MLResult:
    X_input = prepare_ml_input(
        input_data,
        label_encoders,
        features,
    )
    pred_encoded = model.predict(X_input)[0]
    pred_status = label_encoders[
        "expected_status"
    ].inverse_transform([pred_encoded])[0]

    confidence: float | None = None
    if hasattr(model, "predict_proba"):
        confidence = float(
            np.max(model.predict_proba(X_input)[0])
        )

    return {
        "ml_status": str(pred_status),
        "ml_confidence": confidence,
    }


def get_ml_prediction(
    model: Any,
    input_features: pd.DataFrame,
    label_encoders: dict[str, Any],
) -> MLResult:
    """Compatibility helper reproducing notebook cell 37."""
    probabilities = model.predict_proba(input_features)[0]
    max_probability = float(np.max(probabilities))
    predicted_index = int(np.argmax(probabilities))
    predicted_label = label_encoders[
        "expected_status"
    ].inverse_transform([predicted_index])[0]

    return {
        "ml_status": str(predicted_label),
        "ml_confidence": max_probability,
    }


def hybrid_decision_layer(
    rule_result: dict[str, Any],
    ml_result: MLResult,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    rule_status = str(rule_result["status"])
    ml_status = str(ml_result["ml_status"])
    ml_confidence = ml_result["ml_confidence"]

    if rule_status == "temperature_warning":
        final_status = "temperature_warning"
        decision_reason = (
            "Rule-based temperature warning has priority over ML prediction."
        )
    elif (
        ml_confidence is None
        or ml_confidence < confidence_threshold
    ):
        final_status = "manual_check"
        decision_reason = (
            "ML confidence is below threshold; manual inspection is required."
        )
    elif rule_status == ml_status:
        final_status = rule_status
        decision_reason = (
            "Rule-based and ML model agree on the same fermentation status."
        )
    elif (
        rule_status == "too_sour"
        or ml_status == "too_sour"
    ):
        final_status = "manual_check"
        decision_reason = (
            "Conflict involving too_sour status; manual inspection is required."
        )
    else:
        final_status = "manual_check"
        decision_reason = (
            "Rule-based and ML model disagree; manual inspection is required."
        )

    return {
        "rule_status": rule_status,
        "ml_status": ml_status,
        "ml_confidence": (
            None
            if ml_confidence is None
            else round(float(ml_confidence), 4)
        ),
        "final_status": final_status,
        "decision_reason": decision_reason,
        "rule_triggered": rule_result[
            "rule_triggered"
        ],
        "risk_flag": rule_result["risk_flag"],
        "recommendation": (
            generate_final_recommendation(final_status)
        ),
    }


def evaluate_input(
    input_data: dict[str, Any],
    model: Any,
    label_encoders: dict[str, Any],
    features: list[str],
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    rule_result = classify_kombucha_status(
        temperature_c=input_data["room_temp_c"],
        humidity_percent=input_data[
            "humidity_percent"
        ],
        ph=input_data["ph"],
        brix=input_data["brix"],
        fermentation_day=input_data["day"],
    )
    ml_result = predict_ml_status(
        input_data,
        model,
        label_encoders,
        features,
    )
    return hybrid_decision_layer(
        rule_result,
        ml_result,
        confidence_threshold=confidence_threshold,
    )


STANDARD_TEST_CASES = [
    {
        "case_id": "TC-001",
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 1,
        "room_temp_c": 25.0,
        "humidity_percent": 68,
        "ph": 4.6,
        "brix": 10.2,
    },
    {
        "case_id": "TC-002",
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 6,
        "room_temp_c": 25.5,
        "humidity_percent": 67,
        "ph": 3.7,
        "brix": 9.1,
    },
    {
        "case_id": "TC-003",
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 8,
        "room_temp_c": 25.2,
        "humidity_percent": 66,
        "ph": 3.5,
        "brix": 6.4,
    },
    {
        "case_id": "TC-004",
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 12,
        "room_temp_c": 26.0,
        "humidity_percent": 70,
        "ph": 2.8,
        "brix": 4.5,
    },
    {
        "case_id": "TC-005",
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 7,
        "room_temp_c": 31.5,
        "humidity_percent": 72,
        "ph": 3.6,
        "brix": 6.8,
    },
]

EDGE_TEST_SCENARIOS = [
    {
        "case_id": "TC-006",
        "description": (
            "Borderline Early Manual Check"
        ),
        "data": {
            "recipe_id": "R1",
            "tea_type": "black_tea",
            "sugar_g_per_l": 80,
            "starter_ml": 150,
            "water_volume_l": 1.0,
            "day": 4,
            "room_temp_c": 25.0,
            "humidity_percent": 68,
            "ph": 4.10,
            "brix": 7.20,
        },
    },
    {
        "case_id": "TC-007",
        "description": "Borderline Balanced",
        "data": {
            "recipe_id": "R1",
            "tea_type": "black_tea",
            "sugar_g_per_l": 80,
            "starter_ml": 150,
            "water_volume_l": 1.0,
            "day": 7,
            "room_temp_c": 25.0,
            "humidity_percent": 66,
            "ph": 3.20,
            "brix": 5.00,
        },
    },
    {
        "case_id": "TC-008",
        "description": (
            "Low Brix Over-Fermentation"
        ),
        "data": {
            "recipe_id": "R1",
            "tea_type": "black_tea",
            "sugar_g_per_l": 80,
            "starter_ml": 150,
            "water_volume_l": 1.0,
            "day": 10,
            "room_temp_c": 25.5,
            "humidity_percent": 70,
            "ph": 3.35,
            "brix": 4.90,
        },
    },
    {
        "case_id": "TC-009",
        "description": (
            "Low Temperature Manual Check"
        ),
        "data": {
            "recipe_id": "R1",
            "tea_type": "black_tea",
            "sugar_g_per_l": 80,
            "starter_ml": 150,
            "water_volume_l": 1.0,
            "day": 8,
            "room_temp_c": 17.8,
            "humidity_percent": 68,
            "ph": 3.60,
            "brix": 6.70,
        },
    },
    {
        "case_id": "TC-010",
        "description": "High Temperature Override",
        "data": {
            "recipe_id": "R1",
            "tea_type": "black_tea",
            "sugar_g_per_l": 80,
            "starter_ml": 150,
            "water_volume_l": 1.0,
            "day": 8,
            "room_temp_c": 31.2,
            "humidity_percent": 70,
            "ph": 3.50,
            "brix": 6.50,
        },
    },
]

FORCED_CONFLICT_CASES = [
    {
        "case_id": "FC-001",
        "description": (
            "Rule Balanced vs ML Still Sweet"
        ),
        "rule_result": {
            "status": "balanced",
            "recommendation": (
                "Start taste testing and consider bottling."
            ),
            "rule_triggered": (
                "R10_balanced_ready_window"
            ),
            "risk_flag": "normal",
        },
        "ml_result": {
            "ml_status": "still_sweet",
            "ml_confidence": 0.92,
        },
    },
    {
        "case_id": "FC-002",
        "description": (
            "Rule Too Sour vs ML Balanced"
        ),
        "rule_result": {
            "status": "too_sour",
            "recommendation": (
                "The batch may be too acidic or "
                "low in residual sweetness."
            ),
            "rule_triggered": (
                "R4_R5_over_acidic_or_low_sweetness"
            ),
            "risk_flag": "caution",
        },
        "ml_result": {
            "ml_status": "balanced",
            "ml_confidence": 0.89,
        },
    },
    {
        "case_id": "FC-003",
        "description": (
            "Rule Temperature Warning vs ML Balanced"
        ),
        "rule_result": {
            "status": "temperature_warning",
            "recommendation": (
                "Move the batch to a cooler area "
                "and monitor closely."
            ),
            "rule_triggered": (
                "R1_high_temperature_warning"
            ),
            "risk_flag": "warning",
        },
        "ml_result": {
            "ml_status": "balanced",
            "ml_confidence": 0.99,
        },
    },
    {
        "case_id": "FC-004",
        "description": "Low ML Confidence",
        "rule_result": {
            "status": "balanced",
            "recommendation": (
                "Start taste testing and consider bottling."
            ),
            "rule_triggered": (
                "R10_balanced_ready_window"
            ),
            "risk_flag": "normal",
        },
        "ml_result": {
            "ml_status": "balanced",
            "ml_confidence": 0.45,
        },
    },
    {
        "case_id": "FC-005",
        "description": (
            "Rule Still Sweet vs ML Too Sour"
        ),
        "rule_result": {
            "status": "still_sweet",
            "recommendation": (
                "The batch is still sweet. Continue "
                "fermentation or start taste testing."
            ),
            "rule_triggered": (
                "R6_sweet_fermentation_stage"
            ),
            "risk_flag": "normal",
        },
        "ml_result": {
            "ml_status": "too_sour",
            "ml_confidence": 0.91,
        },
    },
]


def run_standard_cases(
    model: Any,
    encoders: dict[str, Any],
    features: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for case in STANDARD_TEST_CASES:
        result = evaluate_input(
            case,
            model,
            encoders,
            features,
        )
        rows.append(
            {
                "case_id": case["case_id"],
                "day": case["day"],
                "temp": case["room_temp_c"],
                "ph": case["ph"],
                "brix": case["brix"],
                **result,
            }
        )

    return pd.DataFrame(rows)


def run_edge_cases(
    model: Any,
    encoders: dict[str, Any],
    features: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for scenario in EDGE_TEST_SCENARIOS:
        result = evaluate_input(
            scenario["data"],
            model,
            encoders,
            features,
        )
        rows.append(
            {
                "case_id": scenario["case_id"],
                "description": scenario["description"],
                **scenario["data"],
                **result,
            }
        )

    return pd.DataFrame(rows)


def run_forced_conflicts() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for case in FORCED_CONFLICT_CASES:
        result = hybrid_decision_layer(
            case["rule_result"],
            case["ml_result"],
        )
        rows.append(
            {
                "case_id": case["case_id"],
                "description": case["description"],
                **result,
            }
        )

    return pd.DataFrame(rows)


def save_hybrid_outputs(
    model: Any,
    encoders: dict[str, Any],
    features: list[str],
    results_dir: Path = RESULTS_DIR,
) -> list[Path]:
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    outputs = [
        (
            "scoby_watch_hybrid_decision_test.csv",
            run_standard_cases(
                model,
                encoders,
                features,
            ),
        ),
        (
            "scoby_watch_hybrid_edge_case_test.csv",
            run_edge_cases(
                model,
                encoders,
                features,
            ),
        ),
        (
            "scoby_watch_hybrid_forced_conflict_test.csv",
            run_forced_conflicts(),
        ),
    ]

    paths: list[Path] = []
    for filename, dataframe in outputs:
        path = results_dir / filename
        dataframe.to_csv(path, index=False)
        paths.append(path.resolve())

    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=MODELS_DIR,
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model, encoders, features = load_artifacts(
        args.models_dir
    )

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
    sample_result = evaluate_input(
        sample_input,
        model,
        encoders,
        features,
    )
    print("Single-sample hybrid result:")
    print(sample_result)

    paths = save_hybrid_outputs(
        model,
        encoders,
        features,
        args.results_dir,
    )
    print("Saved hybrid validation outputs:")
    for path in paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
