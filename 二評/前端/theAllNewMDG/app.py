# ---------------------------------------------------------------- #
# 步驟 0: 匯入必要的函式庫
# ---------------------------------------------------------------- #
from flask import Flask, render_template, redirect, url_for, request, session, flash
import requests
import os
from datetime import datetime
from collections import Counter
import json # 用於解析可能的 JSON 字串

# ---------------------------------------------------------------- #
# 步驟 1: Flask 應用程式初始化與基本設定
# ---------------------------------------------------------------- #
app = Flask(__name__)

# 設定 Session 密鑰 (SECRET_KEY) 以啟用 session 功能
# 在生產環境中，建議從環境變數讀取此值
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# 定義後端 API 的基礎 URL
API_BASE_URL = "http://140.131.114.182:8000/api"

# ---------------------------------------------------------------- #
# 步驟 2: 統一的 API 請求輔助函式 (核心)
# ---------------------------------------------------------------- #

def make_api_request(method, endpoint, **kwargs):
    """
    一個封裝了自動刷新 token 邏輯的 API 請求函式。
    所有對後端的請求都應透過此函式。
    """
    # 檢查 session 中是否有 token
    if 'access_token' not in session:
        return None, 'Not Authenticated'

    url = f"{API_BASE_URL}{endpoint}"
    headers = kwargs.get('headers', {})
    headers['Authorization'] = f'Bearer {session["access_token"]}'
    kwargs['headers'] = headers

    try:
        # 第一次嘗試發送請求
        response = requests.request(method, url, timeout=10, **kwargs)

        # 如果 token 過期 (401 Unauthorized)
        if response.status_code == 401 and 'refresh_token' in session:
            print("Access token expired. Attempting to refresh...")
            refresh_url = f"{API_BASE_URL}/token/refresh/"
            refresh_data = {'refresh': session['refresh_token']}
            
            refresh_response = requests.post(refresh_url, json=refresh_data, timeout=5)

            # 如果刷新成功
            if refresh_response.status_code == 200:
                print("Token refreshed successfully.")
                new_tokens = refresh_response.json()
                session['access_token'] = new_tokens['access']
                
                # 有些設定會一併刷新 refresh token
                if 'refresh' in new_tokens:
                    session['refresh_token'] = new_tokens['refresh']

                # 用新的 token 重新發送原始請求
                headers['Authorization'] = f'Bearer {session["access_token"]}'
                kwargs['headers'] = headers
                response = requests.request(method, url, timeout=10, **kwargs)
            else:
                # 如果連 refresh token 都過期了，就清除 session
                print(f"Refresh token failed. Status: {refresh_response.status_code}")
                session.clear()
                return None, 'Refresh Failed'
        
        return response, None

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None, f"Network Error: {e}"

# ---------------------------------------------------------------- #
# 步驟 3: 核心功能與 API 串接路由
# ---------------------------------------------------------------- #

@app.route("/")
def home():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('帳號和密碼為必填欄位。', 'error')
            return redirect(url_for('login'))

        login_data = {"username": username, "password": password}
        login_url = f"{API_BASE_URL}/token/"
        try:
            response = requests.post(login_url, json=login_data, timeout=5)
            if response.status_code == 200:
                tokens = response.json()
                session['access_token'] = tokens['access']
                session['refresh_token'] = tokens['refresh']
                session.permanent = True
                flash('登入成功！', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('帳號或密碼錯誤，請重新輸入。', 'error')
                return redirect(url_for('login'))
        except requests.exceptions.RequestException as e:
            flash(f'無法連接後端伺服器，請稍後再試。', 'error')
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出。', 'info')
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    response, error = make_api_request('GET', '/trips/')

    if error:
        flash('您的登入已失效或發生錯誤，請重新登入。', 'error')
        return redirect(url_for('login'))

    if response and response.status_code == 200:
        # 後端回傳的是分頁後的資料，我們要取 'results'
        trips_data = response.json().get('results', [])
        return render_template('dashboard.html', trips=trips_data)
    else:
        status_code = response.status_code if response else 'N/A'
        flash(f'讀取儀表板資料失敗，錯誤碼: {status_code}', 'error')
        return render_template('dashboard.html', trips=[]) # 傳入空列表避免模板出錯

@app.route("/coaching")
def coaching():
    response, error = make_api_request('GET', '/trips/')

    if error:
        flash('您的登入已失效或發生錯誤，請重新登入。', 'error')
        return redirect(url_for('login'))

    if not (response and response.status_code == 200):
        status_code = response.status_code if response else 'N/A'
        flash(f'讀取 AI 教練資料失敗，錯誤碼: {status_code}', 'error')
        return render_template("coaching.html", trips=[], summary={})

    trips_from_api = response.json().get('results', [])
    
    # --- 根據真實數據進行分析 ---
    if not trips_from_api:
        return render_template("coaching.html", trips=[], summary={"avg_score": 0, "top_issues": [], "tips": ["尚無行程資料可供分析。"]})
    
    # 轉換與清理資料
    for trip in trips_from_api:
        # 將分數從字串轉為數字以便計算
        try:
            trip['score'] = float(trip.get('score', 0)) if trip.get('score') is not None else 0
        except (ValueError, TypeError):
            trip['score'] = 0
        
        # 處理日期，只取 YYYY-MM-DD
        try:
            trip['date_obj'] = datetime.fromisoformat(trip['start_time'].replace('Z', '+00:00'))
            trip['date'] = trip['date_obj'].strftime('%Y-%m-%d')
        except (ValueError, TypeError, AttributeError):
            trip['date_obj'] = datetime.now()
            trip['date'] = 'N/A'

    # 計算平均分數
    valid_scores = [t['score'] for t in trips_from_api if t['score'] > 0]
    avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0

    # 提取所有 AI 建議
    all_suggestions = [trip.get('ai_suggestion') for trip in trips_from_api if trip.get('ai_suggestion')]

    summary = {
        "avg_score": avg_score,
        "top_issues": ["數據分析中..."], # 這裡可以根據後端提供的事件來統計
        "tips": all_suggestions if all_suggestions else ["恭喜您，目前所有行程表現良好！"]
    }
    
    trips_from_api.sort(key=lambda x: x.get('date_obj'), reverse=True)

    return render_template("coaching.html", trips=trips_from_api, summary=summary)

@app.route("/trip_report/<int:trip_id>")
def trip_report(trip_id):
    endpoint = f'/trips/{trip_id}/'
    response, error = make_api_request('GET', endpoint)

    if error:
        flash('您的登入已失效或發生錯誤，請重新登入。', 'error')
        return redirect(url_for('login'))

    if not (response and response.status_code == 200):
        status_code = response.status_code if response else 'N/A'
        flash(f'無法讀取行程 {trip_id} 的詳細報告，錯誤碼: {status_code}', 'error')
        return redirect(url_for('dashboard'))
    
    trip_details = response.json()
    
    # 模擬地圖路徑，因為後端尚未提供此欄位
    # 未來應從 trip_details 中的 route_logs 欄位生成
    trip_details['path'] = [
        {"lat": 25.06328, "lng": 121.56516}, {"lat": 25.06010, "lng": 121.57088},
        {"lat": 25.05602, "lng": 121.56831}, {"lat": 25.05052, "lng": 121.56415}
    ]
    
    return render_template("trip_report_leaflet.html", trip=trip_details)


# ---------------------------------------------------------------- #
# 您原有的其他靜態頁面路由 (維持不變)
# ---------------------------------------------------------------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    # 這裡未來應串接 POST /api/register/
    if request.method == "POST":
        return redirect(url_for("loading", to="home"))
    return render_template("loading.html", target=url_for("register_real"))

@app.route("/register-real")
def register_real():
    return render_template("register.html")

# ... (保留您其他的靜態路由，例如 /group_leader_view, /all_reports 等)
# ... 為了簡潔，此處省略，但您應將它們保留在您的檔案中
@app.route('/group_leader_view')
def group_leader_view():
    return render_template('group_leader_view.html')

@app.route("/all_reports")
def all_reports():
    return render_template("all_reports.html")

# ... (以及所有其他靜態路由)


# ---------------------------------------------------------------- #
# 錯誤處理與啟動點
# ---------------------------------------------------------------- #
@app.errorhandler(404)
def not_found(_):
    return render_template('404.html'), 404 # 建議有一個 404 頁面

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7307, debug=True)
