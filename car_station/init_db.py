import sqlite3
import datetime

# 連線到 device.db（如果沒有就建立）
conn = sqlite3.connect('device.db')

# 建立 devices 資料表
conn.execute('''
CREATE TABLE IF NOT EXISTS devices (
    device_serial TEXT PRIMARY KEY,            -- 設備序號（唯一識別）
    manufacturer TEXT NOT NULL,                -- 製造商名
    manufacturer_address TEXT NOT NULL,        -- 製造商地址
    software_version TEXT NOT NULL,             -- 軟體版本
    car_brand TEXT,                             -- 車輛廠牌（輸入）
    car_plate TEXT,                             -- 車牌號碼（輸入）
    vehicle_type TEXT,                          -- 車種（輸入）
    driver_position TEXT,                       -- 左駕/右駕（輸入）
    install_date TEXT,                          -- 安裝日期
    last_online TEXT,                           -- 最後上線時間
    status TEXT                                 -- 線上/離線狀態
);
''')

# 使用你的正式出廠資訊
device_serial = "mdgcs001"
manufacturer = "北商資管114507"
manufacturer_address = "臺北市中正區濟南路321號行政大樓4樓資研討室4"
software_version = "V1.0.0"
install_date = datetime.datetime.now().isoformat()
last_online = install_date
status = "offline"  # 預設狀態：離線

# 插入資料，如果已存在就跳過
try:
    conn.execute('''
    INSERT INTO devices (device_serial, manufacturer, manufacturer_address, software_version,
                          car_brand, car_plate, vehicle_type, driver_position,
                          install_date, last_online, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        device_serial,
        manufacturer,
        manufacturer_address,
        software_version,
        None,   # car_brand (安裝時填)
        None,   # car_plate (安裝時填)
        None,   # vehicle_type (安裝時填)
        None,   # driver_position (安裝時填)
        install_date,
        last_online,
        status
    ))
    conn.commit()
    print(f"✅ 成功新增設備：{device_serial}")
except sqlite3.IntegrityError:
    print(f"⚠️ 設備 {device_serial} 已經存在，跳過新增")

conn.close()

print("✅ 資料庫 device.db 初始化完成！")
