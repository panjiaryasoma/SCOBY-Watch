from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def generated_dataset():
    from src.generate_dataset import generate_dataset

    return generate_dataset()


@pytest.fixture(scope="session")
def api_module():
    """Load api/app.py without requiring api/__init__.py."""
    app_path = PROJECT_ROOT / "api" / "app.py"
    if not app_path.is_file():
        pytest.fail(f"API module not found: {app_path}")

    spec = importlib.util.spec_from_file_location(
        "scoby_watch_api_app",
        app_path,
    )
    if spec is None or spec.loader is None:
        pytest.fail(f"Unable to load API module: {app_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config.update(TESTING=True)
    return module


@pytest.fixture()
def client(api_module):
    with api_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def valid_payload():
    return {
        "batch_id": "KB-TEST-001",
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
