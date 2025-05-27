import os
import datetime

def get_current_timestamp():
    """取得當前時間的 ISO 8601 字串格式"""
    return datetime.datetime.now().isoformat()

def ensure_dir_exists(path):
    """確認資料夾存在，若不存在則建立"""
    if not os.path.exists(path):
        os.makedirs(path)

def save_json(filepath, data):
    """將 dict 儲存成 JSON 檔案"""
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json(filepath):
    """讀取 JSON 檔案並回傳 dict"""
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
