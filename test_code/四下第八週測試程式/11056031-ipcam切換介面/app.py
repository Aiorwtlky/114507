from flask import Flask, render_template, Response, request
import cv2

app = Flask(__name__)

# 鏡頭來源設定（替換為你實際的 IP CAM URL）
IP_CAM_SOURCES = {
    "left": "http://172.20.10.4:4747/video",
    "right": "http://192.168.1.102:8080/video",
    "rear": "http://192.168.1.103:8080/video"
}

# 初始鏡頭（可自行指定）
current_cam = IP_CAM_SOURCES["left"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_camera', methods=['POST'])
def set_camera():
    global current_cam
    cam_id = request.form.get('cam_id')
    if cam_id in IP_CAM_SOURCES:
        current_cam = IP_CAM_SOURCES[cam_id]
    return ('', 204)

def generate_frames():
    while True:
        cap = cv2.VideoCapture(current_cam)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)


