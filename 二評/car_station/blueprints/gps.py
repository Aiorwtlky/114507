# blueprints/gps.py（臨時空殼）
from flask import Blueprint, render_template, jsonify

gps_bp = Blueprint('gps', __name__)

@gps_bp.route('/status')
def gps_view():
    """GPS 狀態頁面（暫時停用）"""
    return jsonify({
        'status': 'disabled',
        'message': 'GPS 功能暫時停用'
    })

@gps_bp.route('/api/location')
def get_location():
    """取得 GPS 位置（暫時停用）"""
    return jsonify({
        'status': 'disabled',
        'latitude': None,
        'longitude': None
    })