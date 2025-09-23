from flask import Flask
from blueprints.main import main_bp
from blueprints.trip import trip_bp
from blueprints.gpio import gpio_bp
from blueprints.camera import camera_bp
from blueprints.device_info import device_info_bp
from blueprints.gps import gps_bp
from blueprints.video import video_bp
from models import db, init_database
from config import APP_CONFIG
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = APP_CONFIG['SECRET_KEY']
    
    # SQLite 資料庫設定
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "mdg_car.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化資料庫
    db.init_app(app)
    
    # 註冊藍圖
    app.register_blueprint(main_bp)
    app.register_blueprint(trip_bp, url_prefix='/trip')
    app.register_blueprint(gpio_bp, url_prefix='/api')
    app.register_blueprint(camera_bp, url_prefix='/camera')
    app.register_blueprint(device_info_bp, url_prefix='/device_info')
    app.register_blueprint(gps_bp, url_prefix='/gps')
    app.register_blueprint(video_bp, url_prefix='/video')
    
    # 建立資料庫表格
    init_database(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=APP_CONFIG['DEBUG'], 
        host=APP_CONFIG['HOST'], 
        port=APP_CONFIG['PORT']
    )