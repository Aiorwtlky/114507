# app.py
from flask import Flask, render_template
from routes.device import device_bp

app = Flask(__name__)

app.register_blueprint(device_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=307, debug=True)
