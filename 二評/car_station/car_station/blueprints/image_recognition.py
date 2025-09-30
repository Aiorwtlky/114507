# blueprints/image_recognition.py
from flask import Blueprint, jsonify
from utils.db_helper import LocalEventHelper

recognition_bp = Blueprint('recognition', __name__)

@recognition_bp.route('/test')
def test_recognition():
    return jsonify({"status": "ok", "message": "Recognition blueprint working"})

@recognition_bp.route('/trip/<int:trip_id>/events/summary')
def get_trip_events_summary(trip_id):
    """取得行程事件摘要"""
    summary = LocalEventHelper.get_trip_events_summary(trip_id)
    return jsonify({
        "status": "success",
        "trip_id": trip_id,
        **summary
    })