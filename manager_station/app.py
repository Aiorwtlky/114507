# app.py
from flask import Flask, render_template
from flask_cors import CORS
from routes.driver_manage import manage_bp



app = Flask(__name__)
CORS(app)

app.register_blueprint(manage_bp)



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9523, debug=True)
