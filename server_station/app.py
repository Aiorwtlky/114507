# app.py
from flask import Flask, render_template
from flask_cors import CORS
from routes.device import device_bp
from routes.qr import qr_bp
from routes.bind import bind_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(device_bp)
app.register_blueprint(qr_bp)
app.register_blueprint(bind_bp)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=307, debug=True)
