# app.py
from flask import Flask, render_template, Response
import cv2
from detectors.inward_turn import detect_inward
from detectors.face_detect import VideoFrameHandler
import time

app = Flask(__name__)

cam_inward = cv2.VideoCapture(0)
cam_face = cv2.VideoCapture(0)

video_handler = VideoFrameHandler()

def generate_inward():
    prev_time = time.time()
    while True:
        success, frame = cam_inward.read()
        if not success:
            break

        frame = detect_inward(frame)

        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time)
        prev_time = curr_time

        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def generate_face():
    prev_time = time.time()
    while True:
        success, frame = cam_face.read()
        if not success:
            break

        thresholds = {
            "EAR_THRESH": 0.18,
            "WAIT_TIME": 1.0
        }

        frame, play_alarm = video_handler.process(frame, thresholds)

        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time)
        prev_time = curr_time

        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inward-turn')
def inward_turn():
    return render_template('inward_turn.html')

@app.route('/face-detect')
def face_detect():
    return render_template('face_detect.html')

@app.route('/demo')
def demo_page():
    return render_template('demo.html')

@app.route('/video_feed_inward')
def video_feed_inward():
    return Response(generate_inward(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_face')
def video_feed_face():
    return Response(generate_face(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
