# app.py

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import requests
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7) 

API_BASE_URL = "http://127.0.0.1:8000/api"

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
            refresh_response = requests.post(f"{API_BASE_URL}/token/refresh/", json={'refresh': session['refresh_token']})
            if refresh_response.status_code == 200:
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
        return None, f"Network Error: {e}"

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
                session['access_token'], session['refresh_token'] = tokens['access'], tokens['refresh']
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
                flash('帳號或密碼錯誤。', 'error')
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_data = request.form
        api_payload = {
            "username": form_data.get('username'), "password": form_data.get('password'),
            "email": form_data.get('email'), "first_name": form_data.get('name'), "last_name": "",
            "invitation_code": form_data.get('invitation_code'), # 加入邀請碼
            "personnelprofile": {
                "personnel_number": f"EMP-{form_data.get('username')}", "phone": form_data.get('phone'),
                "license_type": form_data.get('license'), "driving_experience": form_data.get('experience'),
            }
        }
        try:
            response = requests.post(f"{API_BASE_URL}/auth/register/", json=api_payload)
            if response.status_code == 201:
                flash('註冊成功！請登入。', 'success')
                return redirect(url_for('login'))
            else:
                flash(f"註冊失敗：{json.dumps(response.json())}", 'error')
        except requests.exceptions.RequestException:
            flash('無法連接後端伺服器。', 'error')
        return redirect(url_for('register'))
    return render_template("register.html")

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if request.method == 'POST':
        form_data = request.form
        api_payload = { "first_name": form_data.get('name'), "email": form_data.get('email'), "personnelprofile": { "phone": form_data.get('phone'), "license_type": form_data.get('license'), "driving_experience": form_data.get('experience'), } }
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

@app.route("/invite_member/<int:group_id>", methods=['GET', 'POST'])
def invite_member(group_id):
    group_res, error = make_api_request('GET', f'/groups/{group_id}/')
    if error:
        flash('無法讀取群組資料。', 'error')
        return redirect(url_for('dashboard'))
    group_data = group_res.json()

    if request.method == 'POST':
        response, error = make_api_request('POST', f'/groups/{group_id}/invitations/')
        if error or not response.ok:
            flash(f"生成邀請碼失敗: {response.json() if response else '網路錯誤'}", 'error')
            return render_template("invite_member.html", group=group_data, invite_code=None)
        
        invite_data = response.json()
        flash('邀請碼已成功生成！', 'success')
        return render_template("invite_member.html", group=group_data, invite_code=invite_data)

    return render_template("invite_member.html", group=group_data, invite_code=None)

# --- (此處省略其他您已有的頁面路由，如 all_reports, trip_report, chat 等，請保留您檔案中的版本) ---
@app.route("/all_reports")
def all_reports():
    # ...
    return "Not Implemented Yet"
@app.route("/trip_report/<int:trip_id>")
def trip_report(trip_id):
    # ...
    return "Not Implemented Yet"
@app.route("/coaching")
def coaching():
    # ...
    return "Not Implemented Yet"
@app.route("/group_detail/<int:group_id>")
def group_detail(group_id):
    # ...
    return "Not Implemented Yet"
@app.route("/chat")
def chat():
    return render_template("chat.html")
@app.route("/my_groups_standalone")
def my_groups_standalone():
    # ...
    return "Not Implemented Yet"
@app.route("/past_average_standalone")
def past_average_standalone():
    # ...
    return "Not Implemented Yet"
@app.route("/group_settings")
def group_settings():
    # ...
    return "Not Implemented Yet"
@app.route("/print_report/<int:trip_id>")
def print_report(trip_id):
    # ...
    return "Not Implemented Yet"

@app.route("/create_announcement/<int:group_id>", methods=['GET', 'POST'])
def create_announcement(group_id):
    if request.method == 'POST':
        # ... (這裡先省略 POST 的邏輯) ...
        flash('公告已成功發布！', 'success')
        return redirect(url_for('group_leader_view', group_id=group_id))
    
    # 暫時先只回傳一個簡單的頁面
    return f"<h1>為群組 {group_id} 新增公告</h1><form method='post'><textarea name='content'></textarea><button type='submit'>送出</button></form>"


@app.route("/create_group", methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        form_data = request.form
        api_payload = {
            "group_number": form_data.get('group_number'),
            "name": form_data.get('name'),
            "description": form_data.get('description')
        }
        response, error = make_api_request('POST', '/groups/', json=api_payload)

        if response is not None:
            print(f"後端回應狀態碼: {response.status_code}")
            print(f"後端回應內容: {response.text}")
        if error or not response.ok:
            flash(f"建立群組失敗：{response.json() if response else error}", 'error')
            return redirect(url_for('create_group'))
        
        new_group_id = response.json().get('id')
        flash('群組建立成功！', 'success')
        return redirect(url_for('group_leader_view', group_id=new_group_id))
    return render_template("create_group.html")

@app.errorhandler(404)
def not_found(_):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
