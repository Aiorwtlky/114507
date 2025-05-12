# routes/gpio.py

from flask import Blueprint, jsonify

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

gpio_bp = Blueprint('gpio', __name__)

# 腳位定義
LEFT_GPIO = 17
RIGHT_GPIO = 27
REAR_GPIO = 22

# 初始化GPIO
if GPIO_AVAILABLE:
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LEFT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(REAR_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    except Exception as e:
        print(f"⚠️ GPIO 初始化失敗：{e}")
else:
    print("⚠️ 本機未偵測到 GPIO，跳過GPIO初始化")

@gpio_bp.route('/gpio_status', methods=['GET'])
def gpio_status():
    if GPIO_AVAILABLE:
        left = not GPIO.input(LEFT_GPIO)
        right = not GPIO.input(RIGHT_GPIO)
        rear = not GPIO.input(REAR_GPIO)

        return jsonify({
            "left": left,
            "right": right,
            "rear": rear
        })
    else:
        # 本機開發環境回傳假的資料
        return jsonify({
            "left": 0,
            "right": 0,
            "rear": 0,
            "message": "⚠️ 本機無GPIO，回傳預設假數值"
        })
