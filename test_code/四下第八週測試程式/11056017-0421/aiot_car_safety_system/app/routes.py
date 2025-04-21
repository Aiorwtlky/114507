from flask import Blueprint, jsonify, render_template, Response
from app.detector import get_detection_status, get_stream_frame, set_camera_index

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/status', methods=['GET'])
def status():
    return jsonify(get_detection_status())

@main.route('/video_feed')
def video_feed():
    return Response(get_stream_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/switch_camera/<int:index>', methods=['GET'])
def switch_camera(index):
    set_camera_index(index)
    return jsonify({"message": f"Switched to camera {index}"})
