from flask import Flask, render_template, Response, request, jsonify
import cv2
from drowsy_detection import VideoFrameHandler

app = Flask(__name__)
video_handler = VideoFrameHandler()

thresholds = {
    "EAR_THRESH": 0.18,
    "WAIT_TIME": 1.0,
}

camera = cv2.VideoCapture(1)
if not camera.isOpened():
    print("[WARN] 攝影機索引 0 無法開啟，改為索引 1")
    camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise RuntimeError("❌ 無法開啟任何攝影機")

def generate_video():
    while True:
        success, frame = camera.read()
        if not success:
            print("[ERROR] 鏡頭無畫面")
            break
        frame, _ = video_handler.process(frame, thresholds)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    ear_thresh = float(request.args.get('ear_thresh', thresholds["EAR_THRESH"]))
    wait_time = float(request.args.get('wait_time', thresholds["WAIT_TIME"]))
    thresholds["EAR_THRESH"] = ear_thresh
    thresholds["WAIT_TIME"] = wait_time
    return render_template('index.html', ear_thresh=ear_thresh, wait_time=wait_time)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alarm_status')
def alarm_status():
    return jsonify({'play_alarm': video_handler.state_tracker['play_alarm']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
