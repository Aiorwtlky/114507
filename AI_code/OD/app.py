from flask import Flask, render_template, Response, request
import cv2
from tracker import MultiObjectTracker

app = Flask(__name__)

cap = cv2.VideoCapture(0)
tracker = MultiObjectTracker()

# 預設框 (你可以按 /init_tracking 送框起始追蹤)
default_boxes = []

def gen_frames():
    global tracker, cap

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (640, 360))

        if tracker.tracking:
            success, boxes = tracker.update(frame)
            if success:
                tracker.draw_boxes(frame, boxes)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/init_tracking', methods=['POST'])
def init_tracking():
    global tracker, cap
    data = request.json
    boxes = data.get('boxes', [])
    boxes_tuples = [(box['x'], box['y'], box['w'], box['h']) for box in boxes]

    success, frame = cap.read()
    if success:
        frame = cv2.resize(frame, (640, 360))
        tracker.init_trackers(frame, boxes_tuples)
        return {'status': 'tracking started'}
    else:
        return {'status': 'failed to read frame'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
