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
        files_data = request.files

        # --- ▼▼▼ 【關鍵修改】將資料分為 files 和 data 兩部分 ▼▼▼ ---
        
        # 1. 準備檔案部分
        files = {}
        if 'photo' in files_data and files_data['photo'].filename != '':
            files['avatar'] = (files_data['photo'].filename, files_data['photo'].read(), files_data['photo'].content_type)

        # 2. 準備文字資料部分 (key 必須與 Serializer 中的欄位名完全對應)
        data = {
            "username": form_data.get('username'),
            "password": form_data.get('password'),
            "email": form_data.get('email'),
            "first_name": form_data.get('name'),
            "invitation_code": form_data.get('invitation_code'),
            "personnel_number": f"EMP-{form_data.get('username')}",
            "phone": form_data.get('phone'),
            "license_type": form_data.get('license'),
            "driving_experience": form_data.get('experience'),
        }
        # --- ▲▲▲ 修改結束 ▲▲▲ ---

        try:
            # 【關鍵修改】不再使用 json=，而是使用 files= 和 data=
            response = requests.post(
                f"{API_BASE_URL}/auth/register/",
                files=files,
                data=data
            )
            if response.status_code == 201:
                flash('註冊成功！請登入。', 'success')
                return redirect(url_for('login'))
            else:
                # 讓錯誤訊息更好看
                error_data = response.json()
                error_messages = []
                for field, messages in error_data.items():
                    error_messages.append(f"{messages[0]}")
                flash(f"註冊失敗：{' '.join(error_messages)}", 'error')

        except requests.exceptions.RequestException as e:
            flash(f'無法連接後端伺服器: {e}', 'error')

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

    print(f"DEBUG: 準備傳給樣板的 my_groups 資料: {my_groups_data}")


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
    # 【新增】'profile' API 請求，來獲取您自己的個人資料
    api_calls = {
        'managed_groups': make_api_request('GET', '/me/groups/'),
        'group': make_api_request('GET', f'/groups/{group_id}/'),
        'members': make_api_request('GET', f'/groups/{group_id}/members/'),
        'announcements': make_api_request('GET', f'/groups/{group_id}/announcements/'),
        'profile': make_api_request('GET', '/auth/profile/')
    }
    if any(error for _, error in api_calls.values()):
        flash('無法讀取群組資料，請重新登入或確認權限。', 'error')
        return redirect(url_for('dashboard'))
    
    managed_groups = api_calls['managed_groups'][0].json().get('results', [])
    group_data = api_calls['group'][0].json()
    members_data = api_calls['members'][0].json().get('results', [])
    announcements_data = api_calls['announcements'][0].json().get('results', [])
    # 【新增】解析 profile 資料
    profile_data = api_calls['profile'][0].json()
    
    # 【新增】將 profile 傳給樣板
    return render_template('group_leader_view.html', 
                           group=group_data, 
                           members=members_data, 
                           announcements=announcements_data, 
                           managed_groups=managed_groups, 
                           current_group_id=group_id,
                           profile=profile_data)

@app.route("/invite_member/<int:group_id>", methods=['GET', 'POST'])
def invite_member(group_id):
    group_res, error = make_api_request('GET', f'/groups/{group_id}/')
    if error or not group_res.ok:
        flash('無法讀取群組資料。', 'error')
        return redirect(url_for('dashboard'))
    group_data = group_res.json()

    # 在 GET 請求中，從 URL 參數獲取 next_page
    next_page = request.args.get('next_page', 'leader_view') # 預設返回組長儀表板

    if request.method == 'POST':
        # 在 POST 請求後，從表單的隱藏欄位中獲取 next_page
        next_page = request.form.get('next_page', 'leader_view')

        response, error = make_api_request('POST', f'/groups/{group_id}/invitations/')
        if error or not response.ok:
            flash(f"生成邀請碼失敗: {response.json() if response and response.text else '網路錯誤'}", 'error')
            # 即使失敗，也要把 next_page 傳回樣板
            return render_template("invite_member.html", group=group_data, invite_code=None, next_page=next_page)
        
        invite_data = response.json()
        flash('邀請碼已成功生成！', 'success')
        # 成功後，也要把 next_page 傳回樣板
        return render_template("invite_member.html", group=group_data, invite_code=invite_data, next_page=next_page)

    # 初始 GET 請求，也要把 next_page 傳給樣板
    return render_template("invite_member.html", group=group_data, invite_code=None, next_page=next_page)

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
# 修正您現有的 group_settings，讓它能接收 group_id
@app.route("/group_settings/<int:group_id>")
def group_settings(group_id):
    # 未來我們會在這裡實作群組設定功能
    return f"這裡是群組 {group_id} 的設定頁面 (尚未實作)"

# 這個路由就是解決您目前錯誤的關鍵
@app.route("/member_dashboard/<int:member_id>")
def member_dashboard(member_id):
    # 現在先回傳一個簡單的訊息，確保頁面不會崩潰
    return f"這裡是成員 {member_id} 的儀表板 (尚未實作)"

# 這是樣板中用到的另一個路由，也需要補上
@app.route("/member_videos/<int:member_id>")
def member_videos(member_id):
    # 未來用來顯示特定成員的行車影片列表
    return f"這裡是成員 {member_id} 的影片列表 (尚未實作)"

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

@app.route("/debug/my_groups")
def debug_my_groups():
    """
    這個頁面的唯一目的，就是呼叫 /api/me/groups/
    並將後端回傳的原始 JSON 資料直接顯示在畫面上。
    """
    # 使用我們現有的 make_api_request 函式，它會自動處理認證
    response, error = make_api_request('GET', '/me/groups/')

    # 處理可能的錯誤
    if error or not response.ok:
        error_content = response.text if response is not None else "No response"
        return f"""
            <h1>API 請求失敗</h1>
            <p><b>錯誤訊息:</b> {error}</p>
            <p><b>狀態碼:</b> {response.status_code if response is not None else 'N/A'}</p>
            <p><b>後端回應內容:</b></p>
            <pre>{error_content}</pre>
        """
    
    # 如果成功，直接回傳後端給的 JSON 資料
    return jsonify(response.json())

@app.route("/debug/profile")
def debug_profile():
    """
    呼叫 /api/auth/profile/ 並將後端回傳的原始 JSON 顯示在畫面上。
    """
    response, error = make_api_request('GET', '/auth/profile/')

    if error or not response.ok:
        # (錯誤處理的部分省略，與之前的 debug 路由相同)
        return f"<h1>API 請求失敗: {error or response.status_code}</h1>"
    
    # 如果成功，直接回傳後端給的 JSON 資料
    return jsonify(response.json())

@app.route('/promote_member/<int:group_id>/<int:user_id>', methods=['POST'])
def promote_member(group_id, user_id):
    """代理前端請求，呼叫後端 API 來提升成員權限"""
    response, error = make_api_request(
        'PATCH', 
        f'/groups/{group_id}/members/{user_id}/role/', 
        json={'role': 'ADMIN'}
    )
    if error or not response.ok:
        flash('權限更新失敗！', 'error')
    else:
        flash('成員權限已成功提升為管理員！', 'success')
    
    return redirect(url_for('group_leader_view', group_id=group_id))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
