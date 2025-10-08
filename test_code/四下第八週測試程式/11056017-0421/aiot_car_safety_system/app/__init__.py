from flask import Flask

def create_app():
    # 🔧 指定 template_folder 正確的資料夾
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    from .routes import main
    app.register_blueprint(main)

    return app
