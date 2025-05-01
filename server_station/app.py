from flask import Flask, render_template
from flask_cors import CORS
from routes.device import device_bp
from routes.qr import qr_bp
from routes.bind import bind_bp
from routes.reset import reset_bp
from routes.qr_driver import qr_driver_token_bp  # 新增這行
import threading
import webbrowser
import requests

app = Flask(__name__)
CORS(app)

# Blueprint 註冊
app.register_blueprint(device_bp)
app.register_blueprint(qr_bp)
app.register_blueprint(bind_bp)
app.register_blueprint(reset_bp)
app.register_blueprint(qr_driver_token_bp)  # 註冊駕駛 QR blueprint

@app.route('/')
def index():
    qr_base64 = None
    try:
        res = requests.get("http://127.0.0.1:307/generate_qr/work")
        if res.status_code == 200:
            qr_base64 = res.json().get('qr_base64')
    except Exception as e:
        print(f"❌ 無法取得上班 QR：{e}")
    return render_template('index.html', qr_base64=qr_base64)

@app.route('/work_state')
def work_state():
    qr_base64 = None
    try:
        res = requests.get("http://127.0.0.1:307/generate_qr/off")
        if res.status_code == 200:
            qr_base64 = res.json().get('qr_base64')
    except Exception as e:
        print(f"❌ 無法取得下班 QR：{e}")
    return render_template('work_state.html', qr_base64=qr_base64)


if __name__ == '__main__':
    port = 307
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    print(f"\U0001F680 Flask 啟動中，port = {port}")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
