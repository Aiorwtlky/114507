# app.py

# =============================================================================
# 步驟 0: 匯入所有必要的函式庫
# =============================================================================
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import requests
import os
from datetime import datetime, timedelta
import json

# =============================================================================
# 步驟 1: Flask 應用程式初始化與基本設定
# =============================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7) 

API_BASE_URL = "http://127.0.0.1:8000/api"

# =============================================================================
# 步驟 2: 統一的 API 請求輔助函式 (核心)
# =============================================================================
def make_api_request(method, endpoint, **kwargs):
    if 'access_token' not in session:
        return None, 'Not Authenticated'
    url = f"{API_BASE_URL}{endpoint}"
    headers = kwargs.get('headers', {})
    headers['Authorization'] = f'Bearer {session["access_token"]}'
    kwargs['headers'] = headers
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        if response.status_code == 401 and 'refresh_token' in session:
            print("Access token expired. Attempting to refresh...")
            refresh_response = requests.post(f"{API_BASE_URL}/token/refresh/", json={'refresh': session['refresh_token']})
            if refresh_response.status_code == 200:
                print("Token refreshed successfully.")
                new_tokens = refresh_response.json()
                session['access_token'] = new_tokens['access']
                if 'refresh' in new_tokens:
                    session['refresh_token'] = new_tokens['refresh']
                headers['Authorization'] = f'Bearer {session["access_token"]}'
                kwargs['headers'] = headers
                response = requests.request(method, url, timeout=10, **kwargs)
            else:
                session.clear()
                return None, 'Refresh Failed'
        return response, None
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None, f"Network Error: {e}"

# =============================================================================
# 步驟 3: 模板過濾器 (方便在 HTML 中格式化日期)
# =============================================================================
@app.template_filter('format_datetime')
def format_datetime(value):
    if not value: return ""
    try: return datetime.fromisoformat(value.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError): return value
@app.template_filter('format_date')
def format_date(value):
    if not value: return ""
    try: return datetime.fromisoformat(value.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except (ValueError, TypeError): return value
@app.template_filter('format_time')
def format_time(value):
    if not value: return "" 
    try: return datetime.fromisoformat(value.replace('Z', '+00:00')).strftime('%H:%M')
    except (ValueError, TypeError): return value

# =============================================================================
# 步驟 4: 核心認證與基礎路由
# =============================================================================
@app.route("/")
def home():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'access_token' in session:
        profile_response, _ = make_api_request('GET', '/auth/profile/')
        if profile_response and profile_response.json().get('is_group_leader'):
            return redirect(url_for('admin_logic_redirect'))
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('帳號和密碼為必填欄位。', 'error')
            return redirect(url_for('login'))
        try:
            response = requests.post(f"{API_BASE_URL}/token/", json={"username": username, "password": password})
            if response.status_code == 200:
                tokens = response.json()
                session['access_token'] = tokens['access']
                session['refresh_token'] = tokens['refresh']
                session.permanent = True
                
                profile_response, error = make_api_request('GET', '/auth/profile/')
                if error or not profile_response.ok:
                    flash('登入成功，但無法獲取使用者身份。', 'warning')
                    return redirect(url_for('dashboard')) 
                
                profile_data = profile_response.json()
                
                if profile_data.get('is_group_leader', False):
                    flash('歡迎回來，組長！', 'success')
                    return redirect(url_for('admin_logic_redirect'))
                else:
                    flash('登入成功！', 'success')
                    return redirect(url_for('dashboard'))
            else:
                flash('帳號或密碼錯誤，請重新輸入。', 'error')
                return redirect(url_for('login'))
        except requests.exceptions.RequestException:
            flash('無法連接後端伺服器。', 'error')
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出。', 'info')
    return redirect(url_for('login'))

# =============================================================================
# 步驟 5: 使用者註冊與個人資料
# =============================================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_data = request.form
        api_payload = {
            "username": form_data.get('username'), "password": form_data.get('password'),
            "email": form_data.get('email'), "first_name": form_data.get('name'), "last_name": "",
            "personnelprofile": {
                "personnel_number": f"EMP-{form_data.get('username')}",
                "phone": form_data.get('phone'), "license_type": form_data.get('license'),
                "driving_experience": form_data.get('experience'),
            }
        }
        try:
            response = requests.post(f"{API_BASE_URL}/auth/register/", json=api_payload)
            if response.status_code == 201:
                flash('註冊成功！請使用您的新帳號登入。', 'success')
                return redirect(url_for('login'))
            else:
                flash(f"註冊失敗：{json.dumps(response.json())}", 'error')
        except requests.exceptions.RequestException:
            flash('無法連接後端伺服器，註冊失敗。', 'error')
        return redirect(url_for('register'))
    return render_template("register.html")

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if request.method == 'POST':
        form_data = request.form
        api_payload = {
            "first_name": form_data.get('name'), "email": form_data.get('email'),
            "personnelprofile": {
                "phone": form_data.get('phone'), "license_type": form_data.get('license'),
                "driving_experience": form_data.get('experience'),
            }
        }
        if form_data.get('password'): api_payload['password'] = form_data.get('password')
        response, error = make_api_request('PATCH', '/auth/profile/', json=api_payload)
        if error or not response.ok: flash('更新個人資料失敗。', 'error')
        else: flash('個人資料更新成功！', 'success')
        return redirect(url_for('edit_profile'))
    
    response, error = make_api_request('GET', '/auth/profile/')
    if error:
        flash('無法讀取您的資料，請重新登入。', 'error')
        return redirect(url_for('login'))
    profile_data = response.json() if response and response.ok else {}
    return render_template("edit_profile.html", user_data=profile_data)

# =============================================================================
# 步驟 6: 一般使用者核心頁面
# =============================================================================
@app.route("/dashboard")
def dashboard():
    api_calls = {
        'trips': make_api_request('GET', '/trips/?page_size=5'),
        'profile': make_api_request('GET', '/auth/profile/'),
        'my_groups': make_api_request('GET', '/me/groups/'),
        'trends': make_api_request('GET', '/statistics/trends/')
    }
    if any(error for _, error in api_calls.values()):
        flash('您的登入已失效或發生錯誤，請重新登入。', 'error')
        return redirect(url_for('login'))

    trips_data = api_calls['trips'][0].json().get('results', [])
    profile_data = api_calls['profile'][0].json()
    my_groups_data = api_calls['my_groups'][0].json().get('results', [])
    trends_data = api_calls['trends'][0].json()

    return render_template('dashboard.html', trips=trips_data, profile=profile_data, my_groups=my_groups_data, trends_data=trends_data)

@app.route("/all_reports")
def all_reports():
    page = request.args.get('page', 1, type=int)
    response, error = make_api_request('GET', f'/trips/?page={page}')
    if error:
        flash('無法讀取行程資料，請重新登入。', 'error')
        return redirect(url_for('login'))
    data = response.json() if response and response.ok else {}
    return render_template('all_reports.html', trips=data.get('results', []), next_page_exists=bool(data.get('next')), prev_page_exists=bool(data.get('previous')), current_page=page)

@app.route("/trip_report/<int:trip_id>")
def trip_report(trip_id):
    trip_res, err_trip = make_api_request('GET', f'/trips/{trip_id}/')
    if err_trip:
        flash(f'無法讀取行程 {trip_id} 的報告。', 'error')
        return redirect(url_for('dashboard'))
    return render_template("trip_report_leaflet.html", trip=trip_res.json())

@app.route("/coaching")
def coaching():
    response, error = make_api_request('GET', '/trips/?page_size=100')
    if error:
        flash('無法讀取 AI 教練資料。', 'error')
        return redirect(url_for('dashboard'))
    trips = response.json().get('results', [])
    if not trips:
        return render_template("coaching.html", trips=[], summary={"avg_score": 0, "tips": ["尚無行程資料可供分析。"]})
    valid_scores = [float(t['score']) for t in trips if t.get('score') is not None]
    avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0
    all_suggestions = [t.get('ai_suggestion') for t in trips if t.get('ai_suggestion')]
    summary = {"avg_score": avg_score, "tips": all_suggestions or ["表現良好！"]}
    return render_template("coaching.html", trips=trips, summary=summary)

# =============================================================================
# 步驟 7: 管理者 (組長) 核心頁面
# =============================================================================
@app.route("/admin/redirect")
def admin_logic_redirect():
    profile_res, error = make_api_request('GET', '/auth/profile/')
    if error or not profile_res.ok or not profile_res.json().get('is_group_leader'):
        flash('您沒有權限訪問此區域。', 'error')
        return redirect(url_for('dashboard'))

    my_groups_res, err_groups = make_api_request('GET', '/me/groups/')
    if err_groups:
        flash('無法獲取您的群組列表。', 'error')
        return redirect(url_for('create_group'))

    my_groups = my_groups_res.json().get('results', [])
    if my_groups:
        return redirect(url_for('group_leader_view', group_id=my_groups[0]['id']))
    else:
        flash('您目前尚未管理任何群組，請先建立一個。', 'info')
        return redirect(url_for('create_group'))

@app.route('/group_leader_view/<int:group_id>')
def group_leader_view(group_id):
    api_calls = {
        'managed_groups': make_api_request('GET', '/me/groups/'),
        'group': make_api_request('GET', f'/groups/{group_id}/'),
        'members': make_api_request('GET', f'/groups/{group_id}/members/'),
        'announcements': make_api_request('GET', f'/groups/{group_id}/announcements/')
    }
    if any(error for _, error in api_calls.values()):
        flash('無法讀取群組資料，請重新登入或確認權限。', 'error')
        return redirect(url_for('dashboard'))
    
    managed_groups = api_calls['managed_groups'][0].json().get('results', [])
    group_data = api_calls['group'][0].json()
    members_data = api_calls['members'][0].json().get('results', [])
    announcements_data = api_calls['announcements'][0].json().get('results', [])
    
    return render_template('group_leader_view.html', group=group_data, members=members_data, announcements=announcements_data, managed_groups=managed_groups, current_group_id=group_id)

# =============================================================================
# 步驟 8: 聊天機器人代理路由
# =============================================================================
@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/api/chatbot/", methods=['POST'])
def chatbot_proxy():
    if 'access_token' not in session: return jsonify({"error": "Not Authenticated"}), 401
    chat_history = request.json.get('messages', [])
    if not chat_history: return jsonify({"error": "Messages are required"}), 400
    response, error = make_api_request('POST', '/chatbot/', json={"messages": chat_history})
    if error or not response.ok: return jsonify({"error": "Failed to connect to AI assistant"}), 502
    return jsonify(response.json()), response.status_code

# =============================================================================
# 步驟 9: 其他獨立頁面與佔位路由
# =============================================================================
@app.route("/my_groups_standalone")
def my_groups_standalone():
    response, error = make_api_request('GET', '/me/groups/')
    if error:
        flash('無法讀取您的群組資料。', 'error')
        return redirect(url_for('login'))
    my_groups = response.json().get('results', []) if response.ok else []
    return render_template("my_groups_standalone.html", my_groups=my_groups)

@app.route("/past_average_standalone")
def past_average_standalone():
    response, error = make_api_request('GET', '/statistics/trends/')
    if error:
        flash('無法讀取您的統計資料。', 'error')
        return redirect(url_for('login'))
    trends = response.json() if response.ok else []
    total_average = 0
    if trends:
        scores = [item['average_score'] for item in trends if 'average_score' in item]
        if scores: total_average = round(sum(scores) / len(scores), 0)
    return render_template("past_average_standalone.html", average_score=total_average)

@app.route("/group_settings")
def group_settings():
    return render_template("group_settings.html") 

@app.route("/create_group", methods=['GET', 'POST'])
def create_group():
    # 處理 POST 請求 (當使用者提交表單時)
    if request.method == 'POST':
        form_data = request.form
        api_payload = {
            "group_number": form_data.get('group_number'),
            "name": form_data.get('name'),
            "description": form_data.get('description')
        }

        # 呼叫後端的「建立群組」API
        response, error = make_api_request('POST', '/groups/', json=api_payload)

        if error or not response.ok:
            flash(f"建立群組失敗：{response.json() if response else error}", 'error')
            return redirect(url_for('create_group'))
        
        # 建立成功後，獲取新群組的 ID
        new_group_id = response.json().get('id')
        flash('群組建立成功！', 'success')
        
        # 跳轉到新建立的群組的組長儀表板頁面
        return redirect(url_for('group_leader_view', group_id=new_group_id))

    # 處理 GET 請求 (當使用者第一次訪問頁面時)
    return render_template("create_group.html")

@app.route("/print_report/<int:trip_id>")
def print_report(trip_id):
    pdf_url = f"{API_BASE_URL}/trips/{trip_id}/report/"
    return render_template("print_report.html", trip_id=trip_id, pdf_url=pdf_url)

# =============================================================================
# 錯誤處理與啟動點
# =============================================================================
@app.errorhandler(404)
def not_found(_):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)