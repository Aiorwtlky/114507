import sqlite3
import os
from routes.config import DB_PATH


def check_device_db(db_path=DB_PATH):
    abs_path = os.path.abspath(db_path)
    print(f"📂 使用的資料庫路徑：{abs_path}")

    if not os.path.exists(abs_path):
        print("❌ 資料庫檔案不存在，請確認路徑是否正確")
        return

    try:
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()

        # 檢查資料表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices'")
        if not cursor.fetchone():
            print("❌ 查無 'devices' 資料表，請確認資料庫是否初始化正確")
            return

        # 查詢欄位名稱
        cursor.execute("PRAGMA table_info(devices)")
        columns = [col[1] for col in cursor.fetchall()]
        print("📑 欄位名稱：", columns)

        # 查詢所有資料
        cursor.execute("SELECT * FROM devices")
        rows = cursor.fetchall()

        if not rows:
            print("⚠️ 'devices' 資料表為空，尚未建立任何裝置資料")
        else:
            print(f"✅ 查詢結果共 {len(rows)} 筆：")
            for row in rows:
                device_info = dict(zip(columns, row))
                for k, v in device_info.items():
                    print(f"  {k}: {v}")
                print("─" * 40)

        conn.close()

    except Exception as e:
        print(f"❌ 無法連線或讀取資料：{e}")

if __name__ == '__main__':
    check_device_db()
