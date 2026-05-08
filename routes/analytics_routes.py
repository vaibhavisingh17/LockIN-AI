from flask import Blueprint, jsonify

from ml.preprocessing.feature_builder import (
    generate_behavior_features
)

analytics_bp = Blueprint("analytics", __name__)


# =========================================
# USER BEHAVIOR ANALYTICS
# =========================================
@analytics_bp.route("/behavior_analysis", methods=["GET"])
def behavior_analysis():

    features = generate_behavior_features()

    return jsonify(features)