from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# LOAD MODEL, ENCODERS, FEATURES

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"

best_model = joblib.load(
    MODEL_DIR / "scoby_watch_best_group_split_model.pkl"
)

label_encoders = joblib.load(
    MODEL_DIR / "scoby_watch_label_encoders.pkl"
)

features = joblib.load(
    MODEL_DIR / "scoby_watch_feature_columns.pkl"
)

print("Model loaded successfully.")
print("Features:", features)


# RULE-BASED MODEL

def classify_kombucha_status(temperature_c, humidity_percent, ph, brix, fermentation_day):
    if temperature_c > 30:
        return {
            "status": "temperature_warning",
            "recommendation": "Move the batch to a cooler area and monitor closely.",
            "rule_triggered": "R1_high_temperature_warning",
            "risk_flag": "warning"
        }

    if temperature_c < 18:
        return {
            "status": "manual_check",
            "recommendation": "Temperature is too low. Fermentation may slow down. Perform manual inspection.",
            "rule_triggered": "R2_low_temperature_slow_fermentation",
            "risk_flag": "caution"
        }

    if fermentation_day > 14 and (ph < 3.2 or brix < 5.0):
        return {
            "status": "too_sour",
            "recommendation": "The batch may be over-fermented. Consider using it as starter or dilute based on taste preference.",
            "rule_triggered": "R11_extended_over_fermentation",
            "risk_flag": "caution"
        }

    if ph > 4.2:
        return {
            "status": "too_early",
            "recommendation": "Continue fermentation and check again within 24 hours.",
            "rule_triggered": "R3_early_acidity_stage",
            "risk_flag": "normal"
        }

    if ph < 3.0 or brix < 5.0:
        return {
            "status": "too_sour",
            "recommendation": "The batch may be over-fermented. Consider using it as starter or dilute based on taste preference.",
            "rule_triggered": "R4_R5_over_acidic_or_low_sweetness",
            "risk_flag": "caution"
        }

    if fermentation_day < 5 and 3.2 <= ph <= 4.2:
        return {
            "status": "manual_check",
            "recommendation": "Fermentation is still early. Perform manual inspection before making a decision.",
            "rule_triggered": "R9_early_day_manual_check",
            "risk_flag": "caution"
        }

    if 3.2 <= ph <= 4.2 and brix > 8.0:
        return {
            "status": "still_sweet",
            "recommendation": "Continue fermentation or start taste testing.",
            "rule_triggered": "R6_sweet_fermentation_stage",
            "risk_flag": "normal"
        }

    if 3.2 <= ph <= 4.2 and 5.0 <= brix <= 8.0:
        if fermentation_day >= 7:
            return {
                "status": "balanced",
                "recommendation": "Start taste testing and consider bottling if the flavor matches preference.",
                "rule_triggered": "R10_balanced_ready_window",
                "risk_flag": "normal"
            }
        else:
            return {
                "status": "balanced",
                "recommendation": "Balanced profile detected, but fermentation day is still early. Taste testing is recommended.",
                "rule_triggered": "R7_balanced_but_early",
                "risk_flag": "normal"
            }

    return {
        "status": "manual_check",
        "recommendation": "Perform manual inspection using visual check, aroma, pH, Brix, and taste evaluation before making a decision.",
        "rule_triggered": "R8_ambiguous_condition",
        "risk_flag": "caution"
    }


# FINAL RECOMMENDATION

def generate_final_recommendation(final_status):
    recommendations = {
        "too_early": "Continue fermentation and check again within 24 hours.",
        "still_sweet": "Continue fermentation or start taste testing.",
        "balanced": "Start taste testing and consider bottling if the flavor matches preference.",
        "too_sour": "The batch may be over-fermented. Consider using it as starter or dilute based on taste preference.",
        "temperature_warning": "Move the batch to a cooler area and monitor closely.",
        "manual_check": "Perform manual inspection using visual check, aroma, pH, Brix, and taste evaluation before making a decision."
    }

    return recommendations.get(
        final_status,
        "Manual inspection is recommended before making a decision."
    )


# PREPARE ML INPUT

def prepare_ml_input(input_data):
    recipe_id_encoded = label_encoders["recipe_id"].transform([input_data["recipe_id"]])[0]
    tea_type_encoded = label_encoders["tea_type"].transform([input_data["tea_type"]])[0]

    row = pd.DataFrame([{
        "recipe_id_encoded": recipe_id_encoded,
        "tea_type_encoded": tea_type_encoded,
        "sugar_g_per_l": input_data["sugar_g_per_l"],
        "starter_ml": input_data["starter_ml"],
        "water_volume_l": input_data["water_volume_l"],
        "day": input_data["day"],
        "room_temp_c": input_data["room_temp_c"],
        "humidity_percent": input_data["humidity_percent"],
        "ph": input_data["ph"],
        "brix": input_data["brix"]
    }])

    return row[features]


# ML PREDICTION

def get_ml_prediction(input_features):
    probs = best_model.predict_proba(input_features)[0]

    max_prob = np.max(probs)
    pred_idx = np.argmax(probs)

    predicted_label = label_encoders["expected_status"].inverse_transform([pred_idx])[0]

    return {
        "ml_status": predicted_label,
        "ml_confidence": float(max_prob)
    }


# HYBRID DECISION LAYER

def hybrid_decision_layer(rule_result, ml_result, confidence_threshold=0.70):
    rule_status = rule_result["status"]
    ml_status = ml_result["ml_status"]
    ml_confidence = ml_result["ml_confidence"]

    if rule_status == "temperature_warning":
        final_status = "temperature_warning"
        decision_reason = "Rule-based temperature warning has priority over ML prediction."

    elif ml_confidence < confidence_threshold:
        final_status = "manual_check"
        decision_reason = "ML confidence is below threshold; manual inspection is required."

    elif rule_status == ml_status:
        final_status = rule_status
        decision_reason = "Rule-based and ML model agree on the same fermentation status."

    elif rule_status == "too_sour" or ml_status == "too_sour":
        final_status = "manual_check"
        decision_reason = "Conflict involving too_sour status; manual inspection is required."

    else:
        final_status = "manual_check"
        decision_reason = "Rule-based and ML model disagree; manual inspection is required."

    return {
        "rule_status": rule_status,
        "ml_status": ml_status,
        "ml_confidence": round(ml_confidence, 4),
        "final_status": final_status,
        "decision_reason": decision_reason,
        "rule_triggered": rule_result["rule_triggered"],
        "risk_flag": rule_result["risk_flag"],
        "recommendation": generate_final_recommendation(final_status)
    }


# ROUTES

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "SCOBY Watch ML Hybrid API is running."
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": type(best_model).__name__
    })


@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json(silent=True)

        if not isinstance(input_data, dict):
            return jsonify({
                "error": "Request body must contain a valid JSON object."
            }), 400

        required_fields = [
            "batch_id",
            "recipe_id",
            "tea_type",
            "sugar_g_per_l",
            "starter_ml",
            "water_volume_l",
            "day",
            "room_temp_c",
            "humidity_percent",
            "ph",
            "brix"
        ]

        missing_fields = [field for field in required_fields if field not in input_data]

        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        rule_result = classify_kombucha_status(
            temperature_c=float(input_data["room_temp_c"]),
            humidity_percent=float(input_data["humidity_percent"]),
            ph=float(input_data["ph"]),
            brix=float(input_data["brix"]),
            fermentation_day=int(input_data["day"])
        )

        ml_features = prepare_ml_input(input_data)
        ml_result = get_ml_prediction(ml_features)

        hybrid_result = hybrid_decision_layer(rule_result, ml_result)

        response = {
            "batch_id": input_data["batch_id"],
            "recipe_id": input_data["recipe_id"],
            "tea_type": input_data["tea_type"],
            "day": input_data["day"],
            "room_temp_c": input_data["room_temp_c"],
            "humidity_percent": input_data["humidity_percent"],
            "ph": input_data["ph"],
            "brix": input_data["brix"],

            "rule_status": hybrid_result["rule_status"],
            "ml_status": hybrid_result["ml_status"],
            "ml_confidence": hybrid_result["ml_confidence"],
            "final_status": hybrid_result["final_status"],
            "decision_reason": hybrid_result["decision_reason"],
            "rule_triggered": hybrid_result["rule_triggered"],
            "risk_flag": hybrid_result["risk_flag"],
            "recommendation": hybrid_result["recommendation"]
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)