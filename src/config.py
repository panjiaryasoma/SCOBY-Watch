"""Shared paths, constants, recipes, and model configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
VALIDATION_DIR = DATA_DIR / "validation"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"

DATASET_PATH = DATA_DIR / "scoby_watch_simulated_dataset.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.20
BATCHES_PER_RECIPE = 50
DAYS_PER_BATCH = 14
CONFIDENCE_THRESHOLD = 0.70

TARGET_COLUMN = "expected_status"
CATEGORICAL_COLUMNS = [
    "recipe_id",
    "recipe_name",
    "tea_type",
    "risk_flag",
]
FEATURE_COLUMNS = [
    "recipe_id_encoded",
    "tea_type_encoded",
    "sugar_g_per_l",
    "starter_ml",
    "water_volume_l",
    "day",
    "room_temp_c",
    "humidity_percent",
    "ph",
    "brix",
]

EXPECTED_DATASET_COLUMNS = [
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

RECIPES: list[dict[str, Any]] = [
    {
        "recipe_id": "R1",
        "recipe_name": "Standard Black Tea",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "profile": "normal",
    },
    {
        "recipe_id": "R2",
        "recipe_name": "High Sugar Black Tea",
        "tea_type": "black_tea",
        "sugar_g_per_l": 100,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "profile": "sweet",
    },
    {
        "recipe_id": "R3",
        "recipe_name": "Low Sugar Black Tea",
        "tea_type": "black_tea",
        "sugar_g_per_l": 60,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "profile": "low_sugar",
    },
    {
        "recipe_id": "R4",
        "recipe_name": "Green Tea Standard",
        "tea_type": "green_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "profile": "normal",
    },
    {
        "recipe_id": "R5",
        "recipe_name": "High Starter Ratio",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 220,
        "water_volume_l": 1.0,
        "profile": "fast",
    },
    {
        "recipe_id": "R6",
        "recipe_name": "Low Starter Ratio",
        "tea_type": "black_tea",
        "sugar_g_per_l": 80,
        "starter_ml": 90,
        "water_volume_l": 1.0,
        "profile": "slow",
    },
    {
        "recipe_id": "R7",
        "recipe_name": "Oolong Mixed Tea",
        "tea_type": "oolong_mixed",
        "sugar_g_per_l": 85,
        "starter_ml": 150,
        "water_volume_l": 1.0,
        "profile": "normal",
    },
]
