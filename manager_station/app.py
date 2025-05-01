# app.py
from flask import Flask, render_template
from flask_cors import CORS
from routes.driver_manage import manage_bp
import threading
import webbrowser

app = Flask(__name__)
CORS(app)

app.register_blueprint(manage_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = 9523
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    print(f"🚀 Flask 啟動中，port = {port}")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
