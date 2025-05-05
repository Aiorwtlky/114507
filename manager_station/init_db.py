import pymysql
import datetime

# 建立連線（修改密碼、資料庫名稱為你的設定）
def init_db():
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='car_server_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with db.cursor() as cursor:
        # 建立 devices 資料表（若尚未建立）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                device_serial VARCHAR(64) PRIMARY KEY,
                manufacturer VARCHAR(100) NOT NULL,
                manufacturer_address TEXT NOT NULL,
                software_version VARCHAR(50) NOT NULL,
                car_brand VARCHAR(50),
                car_plate VARCHAR(50),
                vehicle_type VARCHAR(50),
                driver_position VARCHAR(10),
                install_date DATETIME,
                last_online DATETIME,
                status VARCHAR(20),
                bind_status TINYINT DEFAULT 0
            )
        ''')

        # 建立 tokens 資料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                token VARCHAR(64) PRIMARY KEY,
                device_serial VARCHAR(64) NOT NULL,
                created_at DATETIME NOT NULL,
                used TINYINT DEFAULT 0,
                FOREIGN KEY (device_serial) REFERENCES devices(device_serial)
            )
        ''')

        # 建立 drivers 資料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                driver_id INT AUTO_INCREMENT PRIMARY KEY,
                driver_name VARCHAR(100) NOT NULL
            )
        ''')

        # 插入預設設備資料（若尚未存在）
        device_serial = "mdgcs001"
        manufacturer = "北商資管114507"
        manufacturer_address = "臺北市中正區濟南路321號行政大樓4樓資研討室4"
        software_version = "V1.0.0"
        install_date = datetime.datetime.now()
        last_online = install_date
        status = "offline"

        try:
            cursor.execute('''
                INSERT INTO devices (device_serial, manufacturer, manufacturer_address, software_version,
                                      car_brand, car_plate, vehicle_type, driver_position,
                                      install_date, last_online, status, bind_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                device_serial,
                manufacturer,
                manufacturer_address,
                software_version,
                None,
                None,
                None,
                None,
                install_date,
                last_online,
                status,
                0
            ))
            print(f"✅ 成功新增設備：{device_serial}")
        except pymysql.err.IntegrityError:
            print(f"⚠️ 設備 {device_serial} 已經存在，跳過新增")

    db.commit()
    db.close()
    print("✅ 資料表 devices、tokens 與 drivers 建立完成！")

if __name__ == '__main__':
    init_db()