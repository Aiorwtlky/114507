from flask import request, jsonify
from database import db_session
from models import EventLog
import datetime

def register_routes(app):
    @app.route("/api/events/upload", methods=["POST"])
    def upload_event():
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        try:
            event = EventLog(
                device_serial=data.get("device_serial"),
                event_time=datetime.datetime.fromisoformat(data.get("event_time")),
                camera_position=data.get("camera_position"),
                detected_objects=str(data.get("detected_objects")),
                alert_level=1,  # 預設警示等級
                image_path=data.get("image_path"),
                video_path=data.get("video_path"),
                uploaded=0
            )
            db_session.add(event)
            db_session.commit()
            return jsonify({"status": "success", "message": "Event saved"})
        except Exception as e:
            db_session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/events", methods=["GET"])
    def list_events():
        device_serial = request.args.get("device_serial")
        query = db_session.query(EventLog)
        if device_serial:
            query = query.filter(EventLog.device_serial == device_serial)
        events = query.order_by(EventLog.event_time.desc()).limit(50).all()

        result = []
        for e in events:
            result.append({
                "event_id": e.event_id,
                "device_serial": e.device_serial,
                "event_time": e.event_time.isoformat(),
                "camera_position": e.camera_position,
                "image_path": e.image_path,
                "video_path": e.video_path,
                "alert_level": e.alert_level
            })
        return jsonify(result)

    @app.route("/api/events/<int:event_id>", methods=["GET"])
    def get_event_detail(event_id):
        event = db_session.query(EventLog).filter(EventLog.event_id == event_id).first()
        if not event:
            return jsonify({"status": "error", "message": "Event not found"}), 404
        return jsonify({
            "event_id": event.event_id,
            "device_serial": event.device_serial,
            "event_time": event.event_time.isoformat(),
            "camera_position": event.camera_position,
            "detected_objects": event.detected_objects,
            "image_path": event.image_path,
            "video_path": event.video_path,
            "alert_level": event.alert_level
        })
