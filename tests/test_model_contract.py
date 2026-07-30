from __future__ import annotations

from pathlib import Path

from sklearn.ensemble import GradientBoostingClassifier

from src.generate_dataset import generate_dataset
from src.hybrid_decision import (
    load_artifacts,
    predict_ml_status,
    prepare_ml_input,
)
from src.train_models import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    encode_dataset,
    group_split,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"

EXPECTED_TARGET_CLASSES = {
    "balanced",
    "manual_check",
    "still_sweet",
    "temperature_warning",
    "too_early",
    "too_sour",
}


def test_group_split_is_batch_aware_and_reproducible():
    df = generate_dataset()
    encoded, _ = encode_dataset(df)

    first = group_split(encoded)
    second = group_split(encoded)

    assert first["X_train"].shape == (3920, 10)
    assert first["X_test"].shape == (980, 10)
    assert first["train_groups"].nunique() == 280
    assert first["test_groups"].nunique() == 70

    train_batches = set(first["train_groups"].unique())
    test_batches = set(first["test_groups"].unique())
    assert train_batches.isdisjoint(test_batches)

    assert first["train_idx"].tolist() == second["train_idx"].tolist()
    assert first["test_idx"].tolist() == second["test_idx"].tolist()


def test_serialized_artifacts_match_model_contract():
    model, encoders, features = load_artifacts(MODELS_DIR)

    assert isinstance(model, GradientBoostingClassifier)
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    assert features == FEATURE_COLUMNS
    assert len(features) == 10

    assert set(encoders["recipe_id"].classes_) == {
        "R1", "R2", "R3", "R4", "R5", "R6", "R7"
    }
    assert set(encoders["tea_type"].classes_) == {
        "black_tea",
        "green_tea",
        "oolong_mixed",
    }
    assert set(encoders[TARGET_COLUMN].classes_) == EXPECTED_TARGET_CLASSES


def test_feature_preparation_uses_saved_order():
    _, encoders, features = load_artifacts(MODELS_DIR)

    payload = {
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 7,
        "room_temp_c": 24.4,
        "humidity_percent": 68.0,
        "ph": 3.56,
        "brix": 7.71,
    }
    prepared = prepare_ml_input(payload, encoders, features)

    assert prepared.shape == (1, 10)
    assert prepared.columns.tolist() == FEATURE_COLUMNS


def test_reference_payload_is_predicted_as_balanced():
    model, encoders, features = load_artifacts(MODELS_DIR)

    payload = {
        "recipe_id": "R1",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "day": 7,
        "room_temp_c": 24.4,
        "humidity_percent": 68.0,
        "ph": 3.56,
        "brix": 7.71,
    }

    result = predict_ml_status(payload, model, encoders, features)

    assert result["ml_status"] == "balanced"
    assert result["ml_confidence"] is not None
    assert 0.99 <= result["ml_confidence"] <= 1.0
