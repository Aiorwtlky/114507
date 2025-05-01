import pymysql

try:
    print("🚀 嘗試連線 car_server_db...")
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # 如果有設密碼請改
        database='car_server_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )
    print("✅ 成功連線到資料庫")
except Exception as e:
    print(f"❌ 錯誤：{e}")

