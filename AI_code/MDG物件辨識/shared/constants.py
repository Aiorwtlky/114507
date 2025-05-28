# 事件警示等級
ALERT_LEVEL_LOW = 1
ALERT_LEVEL_MEDIUM = 2
ALERT_LEVEL_HIGH = 3

# 攝影機位置定義
CAMERA_LEFT = 'left'
CAMERA_RIGHT = 'right'
CAMERA_REAR = 'rear'
CAMERA_SIDE_MIRROR = 'side_mirror'  # 側面後照鏡
CAMERA_FRONT = 'front'

# 攝影機視角
VIEW_ANGLE_SIDE = 'side_view'
VIEW_ANGLE_TOP = 'top_view' 
VIEW_ANGLE_REAR = 'rear_view'
VIEW_ANGLE_FRONT = 'front_view'

# 偵測物件類別 - 側面攝影機重點偵測
DETECT_CLASSES = ['person', 'bicycle', 'motorcycle', 'car', 'bus', 'truck']

# 內輪差高風險物件（行人、機車、自行車）
HIGH_RISK_CLASSES = ['person', 'bicycle', 'motorcycle']

# 中風險物件（其他車輛）
MEDIUM_RISK_CLASSES = ['car', 'bus', 'truck']

# 低風險或忽略物件
IGNORE_CLASSES = ['traffic light', 'stop sign', 'fire hydrant', 'bench']

# 大型車輛規格常數
LARGE_TRUCK_AXLE_LENGTH = 6.5      # 大型卡車軸距（公尺）
LARGE_BUS_AXLE_LENGTH = 6.0        # 大型巴士軸距（公尺）
TRAILER_TRUCK_AXLE_LENGTH = 15.0   # 聯結車軸距（公尺）

LARGE_VEHICLE_WIDTH = 2.5          # 大型車輛寬度（公尺）
LARGE_VEHICLE_LENGTH = 12.0        # 大型車輛長度（公尺）

# 轉向角度範圍
MIN_TURN_ANGLE = 5                 # 最小轉向角度（度）
MAX_TURN_ANGLE = 45                # 最大轉向角度（度）
DEFAULT_TURN_ANGLE = 25            # 預設轉向角度（度）

# 轉向方向
TURN_LEFT = 'left'
TURN_RIGHT = 'right'
TURN_STRAIGHT = 'straight'

# ROI 區域類型
ZONE_DANGER = 'danger'             # 內輪差危險區域
ZONE_SAFE = 'safe'                 # 車輛安全轉向區域
ZONE_WARNING = 'warning'           # 警告區域
ZONE_OUTSIDE = 'outside'           # ROI 外區域

# 警示顏色 (BGR 格式)
COLOR_DANGER = (0, 0, 255)         # 紅色 - 危險
COLOR_WARNING = (0, 255, 255)      # 黃色 - 警告
COLOR_SAFE = (0, 255, 0)           # 綠色 - 安全
COLOR_NORMAL = (255, 255, 255)     # 白色 - 正常
COLOR_VEHICLE = (255, 255, 0)      # 青色 - 車輛標記

# 影片與截圖存放路徑
DEFAULT_EVENT_IMAGE_DIR = './events/images/'
DEFAULT_EVENT_VIDEO_DIR = './events/videos/'

# 檔案格式
VIDEO_FORMAT = '.mp4'
IMAGE_FORMAT = '.jpg'
CONFIG_FORMAT = '.json'

# 錄影設定
DEFAULT_RECORDING_DURATION = 10    # 預設錄影時長（秒）
MAX_RECORDING_DURATION = 30        # 最大錄影時長（秒）
VIDEO_FPS = 30                     # 影片幀率

# 偵測信心度閾值
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
HIGH_CONFIDENCE_THRESHOLD = 0.7
LOW_CONFIDENCE_THRESHOLD = 0.3

# 攝影機解析度預設值
SIDE_CAMERA_WIDTH = 1280           # 側面攝影機寬度
SIDE_CAMERA_HEIGHT = 720           # 側面攝影機高度
DEFAULT_PIXELS_PER_METER = 60      # 像素/公尺比例

# 校正相關常數
CALIBRATION_POINT_RADIUS = 8       # 校正點半徑
CALIBRATION_POINT_COLOR = (0, 255, 255)  # 校正點顏色
GRID_LINE_COLOR = (100, 100, 100)  # 網格線顏色
GRID_SPACING = 50                  # 網格間距（像素）

# 系統設定
DEBUG_MODE = True                  # 偵錯模式
SHOW_FPS = True                    # 顯示FPS
SHOW_DETECTION_INFO = True         # 顯示偵測資訊
SHOW_VEHICLE_OUTLINE = True        # 顯示車輛輪廓

# 事件觸發條件
MIN_DANGER_ZONE_TIME = 0.5         # 在危險區域最小停留時間（秒）
MIN_OBJECT_SIZE = 100              # 最小物件大小（像素）
MAX_TRACKING_DISTANCE = 50         # 最大追蹤距離（像素）

# 日誌等級
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'

# 側面攝影機特定設定
SIDE_VIEW_DEFAULT_REAR_AXLE_X = 200   # 預設後軸X座標
SIDE_VIEW_DEFAULT_REAR_AXLE_Y = 400   # 預設後軸Y座標
SIDE_VIEW_VEHICLE_ORIENTATION = 0     # 車輛朝向（度，0為向右）

# 內輪差計算相關
INNER_WHEEL_SAFETY_MARGIN = 0.5    # 內輪差安全邊距（公尺）
OUTER_WHEEL_SAFETY_MARGIN = 0.3    # 外輪差安全邊距（公尺）

# 警示音設定
ALERT_SOUND_ENABLED = True
ALERT_SOUND_VOLUME = 0.8
DANGER_ALERT_FREQUENCY = 4         # 危險警示頻率（Hz）
WARNING_ALERT_FREQUENCY = 2        # 警告警示頻率（Hz）