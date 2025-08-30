from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect(url_for("loading", to="home"))
    return render_template("loading.html", target=url_for("register_real"))

@app.route("/register-real")
def register_real():
    return render_template("register.html")

@app.route("/loading")
def loading():
    target = request.args.get("to", "/")
    return render_template("loading.html", target=target)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/report")
def report():
    return render_template("dashboard.html")

@app.route("/all_reports")
def all_reports():
    return render_template("all_reports.html")

@app.route("/announcements")
def announcements():
    return render_template("announcements.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/admin_chat")
def admin_chat():
    return render_template("admin_chat.html")

@app.route('/create_group')
def create_group():
    # 這裡未來可以從資料庫載入好友列表
    return render_template('create_group.html')

@app.route('/create_group_step2')
def create_group_step2():
    # 這裡未來可以從資料庫載入好友列表
    return render_template('create_group_step2.html')

@app.route('/safety_report')
def safety_report():
    # 在這裡您可以從資料庫傳入真實數據
    # 目前我們先直接渲染靜態頁面
    return render_template('safety_report.html')

# 在您的 app.py 中新增這個路由
@app.route('/admin_dashboard')
def admin_dashboard():
    # 這裡未來會從資料庫撈取真實的駕駛員資料
    # 現在我們先用假資料
    dummy_drivers = [
        # ... 您的駕駛員資料 ...
    ]
    return render_template('admin_dashboard.html') # 確保檔名正確

@app.errorhandler(404)
def not_found(_):
    return redirect(url_for("home"))


@app.route("/trip_report")
def trip_report():
    trip = {
        "id": "2025-07-23-A13",
        "title": "本次行程報告",
        "start_time": "2025-07-23 09:30",
        "end_time": "2025-07-23 15:45",
        "path": [
            {"lat": 25.06328, "lng": 121.56516},
            {"lat": 25.06010, "lng": 121.57088},
            {"lat": 25.05602, "lng": 121.56831},
            {"lat": 25.05052, "lng": 121.56415},
            {"lat": 25.04413, "lng": 121.56144},
            {"lat": 25.03764, "lng": 121.55972}
        ]
    }
    return render_template("trip_report_leaflet.html", trip=trip)

from datetime import datetime

@app.route("/coaching")
def coaching():
    # 假資料：之後換成你DB查詢
    trips = [
        {"date":"2025-07-23","score":89,"violations":[
            {"type":"turn_signal","pts":1,"time":"14:30","loc":"林森忠孝路口"},
            {"type":"drowsy","pts":2,"time":"14:34","loc":"忠孝東路二段"},
            {"type":"phone","pts":4,"time":"14:40","loc":"忠孝東五段"},
        ]},
        {"date":"2025-07-20","score":87,"violations":[
            {"type":"speed","pts":2,"time":"10:21","loc":"民權東路三段"},
        ]},
        {"date":"2025-07-18","score":95,"violations":[
            {"type":"turn_signal","pts":1,"time":"09:12","loc":"重慶北路"},
        ]},
        {"date":"2025-07-15","score":72,"violations":[
            {"type":"drowsy","pts":4,"time":"11:48","loc":"中山高速公路"},
            {"type":"phone","pts":4,"time":"12:03","loc":"民族西路"},
        ]},
    ]

    # ---- 簡易規則建議引擎 ----
    # 需求注意：分數<85 或 存在嚴重違規(pts>=4) 或 疲勞次數>=2
    def needs_attention(t):
        severe = any(v["pts"]>=4 for v in t["violations"])
        drowsy_cnt = sum(1 for v in t["violations"] if v["type"]=="drowsy")
        return (t["score"]<85) or severe or (drowsy_cnt>=2)

    # 問題統計
    issue_map = {
        "turn_signal":"轉彎未打方向燈",
        "drowsy":"疲勞/閉眼",
        "phone":"分心使用手機",
        "speed":"超速",
    }
    from collections import Counter
    all_issues = Counter()
    for t in trips:
        for v in t["violations"]:
            all_issues[issue_map.get(v["type"], v["type"])] += 1

    # 產生一段總結（之後可換成 LLM）
    bad_days = [t for t in trips if needs_attention(t)]
    summary = {
        "bad_count": len(bad_days),
        "avg_score": round(sum(t["score"] for t in trips)/len(trips),1),
        "top_issues": [k for k,_ in all_issues.most_common(3)],
        "tips": []
    }
    if "疲勞/閉眼" in summary["top_issues"]:
        summary["tips"].append("每駕駛 90 分鐘休息 10 分鐘；連續閉眼>2 次自動語音提醒。")
    if "分心使用手機" in summary["top_issues"]:
        summary["tips"].append("建議啟用駕駛中來電自動回覆；語音助理取代手動操作。")
    if "轉彎未打方向燈" in summary["top_issues"]:
        summary["tips"].append("在轉向角>5° 且速<30km/h時，HUD 彈出方向燈提示。")
    if "超速" in summary["top_issues"]:
        summary["tips"].append("超速>10% 持續 5s 以上觸發蜂鳴；區間測速路段前 200m 提醒。")

    # 標記每日是否需注意
    for t in trips:
        t["needs_attention"] = needs_attention(t)
        t["date_obj"] = datetime.strptime(t["date"], "%Y-%m-%d")

    # 按日期新到舊
    trips.sort(key=lambda x: x["date"], reverse=True)

    return render_template("coaching.html", trips=trips, summary=summary)



if __name__ == "__main__":
    app.run(debug=True)
