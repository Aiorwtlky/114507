# flask_server.py

from flask import Flask, render_template, send_from_directory, abort
import os
import json

app = Flask(__name__, static_url_path='/static')

# 路徑設定
EVENTS_DIR = 'events'  # 原始事件資料夾路徑
@app.route('/')
def index():
    event_cards = []

    for folder in sorted(os.listdir(EVENTS_DIR), reverse=True):
        folder_path = os.path.join(EVENTS_DIR, folder)
        print(f"🔍 檢查資料夾：{folder_path}")  # ✅ 加這行除錯

        if not os.path.isdir(folder_path):
            continue

        meta_path = os.path.join(folder_path, 'meta.json')
        print(f"➡️ 讀取 meta.json：{meta_path}")  # ✅ 加這行

        if not os.path.exists(meta_path):
            print("⚠️ meta.json 不存在，跳過")
            continue

        with open(meta_path, 'r', encoding='utf-8') as f:
            try:
                meta = json.load(f)
                meta["folder"] = folder
                event_cards.append(meta)
                print(f"✅ 成功加入事件：{meta['timestamp']}")
            except json.JSONDecodeError:
                print("❌ JSON 解析失敗，跳過")

    print(f"📦 最終事件筆數：{len(event_cards)}")
    return render_template('index.html', events=event_cards)


@app.route('/detail/<folder>')
def detail(folder):
    folder_path = os.path.join(EVENTS_DIR, folder)
    meta_path = os.path.join(folder_path, 'meta.json')

    if not os.path.exists(meta_path):
        abort(404)

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
        meta["folder"] = folder

    return render_template('detail.html', event=meta)


@app.route('/events/<folder>/<filename>')
def serve_event_file(folder, filename):
    # 讓 Flask 可以讀取 alert.jpg、clip.mp4 等檔案
    return send_from_directory(os.path.join(EVENTS_DIR, folder), filename)

if __name__ == '__main__':
    app.run(debug=True)
