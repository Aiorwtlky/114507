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
        response = requests.request(method, url, timeout=30, **kwargs)
        if response.status_code == 401 and 'refresh_token' in session:
            refresh_response = requests.post(f"{API_BASE_URL}/token/refresh/", json={'refresh': session['refresh_token']})
            if refresh_response.status_code == 200:
                new_tokens = refresh_response.json()
                session['access_token'] = new_tokens['access']
                if 'refresh' in new_tokens:
                    session['refresh_token'] = new_tokens['refresh']
                headers['Authorization'] = f'Bearer {session["access_token"]}'
                kwargs['headers'] = headers
                response = requests.request(method, url, timeout=30, **kwargs)
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
        # 如果已登入，直接導向儀表板
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 【新增】從 URL 中獲取 'next' 參數
        next_url = request.args.get('next')

        if not username or not password:
            flash('帳號和密碼為必填欄位。', 'error')
            return redirect(url_for('login', next=next_url)) # 保持 next 參數

        try:
            response = requests.post(f"{API_BASE_URL}/token/", json={"username": username, "password": password})
            if response.status_code == 200:
                tokens = response.json()
                session['access_token'], session['refresh_token'] = tokens['access'], tokens['refresh']
                session.permanent = True

                # ---  【關鍵修改】登入成功後的跳轉邏輯  ---
                if next_url:
                    flash('登入成功！', 'success')
                    return redirect(next_url) # 如果有 next 參數，就跳轉到該網址

                # 如果沒有 next 參數，才執行原本的判斷
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
                return redirect(url_for('login', next=next_url))
        except requests.exceptions.RequestException:
            flash('無法連接後端伺服器。', 'error')
            return redirect(url_for('login', next=next_url))

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
        
        files = {}
        if 'photo' in files_data and files_data['photo'].filename != '':
            files['avatar'] = (files_data['photo'].filename, files_data['photo'].read(), files_data['photo'].content_type)

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

        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register/",
                files=files,
                data=data
            )
            if response.status_code == 201:
                flash('註冊成功！請登入。', 'success')
                return redirect(url_for('login'))
            else:
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
        files_data = request.files

        files = {}
        if 'photo' in files_data and files_data['photo'].filename != '':
            files['avatar'] = (files_data['photo'].filename, files_data['photo'].read(), files_data['photo'].content_type)
        
        data = {
            "first_name": form_data.get('name'),
            "email": form_data.get('email'),
            "phone": form_data.get('phone'),
            "license_type": form_data.get('license'),
            "driving_experience": form_data.get('experience'),
        }

        if form_data.get('password'):
            data['password'] = form_data.get('password')

        response, error = make_api_request('PATCH', '/auth/profile/', files=files, data=data)

        if error or not response.ok:
            flash(f"更新個人資料失敗: {response.text}", 'error')
            return redirect(url_for('edit_profile'))
        else:
            flash('個人資料更新成功！', 'success')
            return redirect(url_for('dashboard'))
    
    response, error = make_api_request('GET', '/auth/profile/')
    if error or not response.ok:
        flash('無法讀取您的資料，請重新登入。', 'error')
        return redirect(url_for('login'))
        
    profile_data = response.json()
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
    profile_data = api_calls['profile'][0].json()
    
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

    next_page = request.args.get('next_page', 'leader_view')

    if request.method == 'POST':
        next_page = request.form.get('next_page', 'leader_view')

        response, error = make_api_request('POST', f'/groups/{group_id}/invitations/')
        if error or not response.ok:
            flash(f"生成邀請碼失敗: {response.json() if response and response.text else '網路錯誤'}", 'error')
            return render_template("invite_member.html", group=group_data, invite_code=None, next_page=next_page)
        
        invite_data = response.json()
        flash('邀請碼已成功生成！', 'success')
        return render_template("invite_member.html", group=group_data, invite_code=invite_data, next_page=next_page)

    return render_template("invite_member.html", group=group_data, invite_code=None, next_page=next_page)

@app.route("/trip_report/<int:trip_id>")
def trip_report(trip_id):
    return "Not Implemented Yet"

@app.route("/group_settings/<int:group_id>", methods=['GET', 'POST'])
def group_settings(group_id):
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update':
            # 處理更新邏輯
            payload = {
                "name": request.form.get('group_name'),
                "description": request.form.get('description')
            }
            response, error = make_api_request('PATCH', f'/groups/{group_id}/', json=payload)
            if error or not response.ok:
                flash('群組資訊更新失敗！', 'error')
            else:
                flash('群組資訊已更新。', 'success')
            return redirect(url_for('group_settings', group_id=group_id))

        elif action == 'delete':
            # 處理刪除邏輯
            response, error = make_api_request('DELETE', f'/groups/{group_id}/')
            if error or not response.ok:
                flash('刪除群組失敗！', 'error')
                return redirect(url_for('group_settings', group_id=group_id))
            else:
                flash('群組已成功刪除。', 'success')
                return redirect(url_for('admin_logic_redirect'))

    # GET 請求：獲取群組資料並顯示頁面
    group_res, error = make_api_request('GET', f'/groups/{group_id}/')
    if error or not group_res.ok:
        flash('無法讀取群組資料。', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template("group_settings.html", group=group_res.json())

@app.route("/member_dashboard/<int:member_id>")
def member_dashboard(member_id):
    return f"這裡是成員 {member_id} 的儀表板 (尚未實作)"

@app.route("/member_videos/<int:member_id>")
def member_videos(member_id):
    return f"這裡是成員 {member_id} 的影片列表 (尚未實作)"


# ---  【最終修正版】公告相關路由  ---

@app.route("/create_announcement/<int:group_id>", methods=['GET', 'POST'])
def create_announcement(group_id):
    """處理「建立」新公告的請求。"""
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('公告內容不得為空。', 'error')
            # 重新導向回建立頁面，並附帶 group_id
            return redirect(url_for('create_announcement', group_id=group_id))

        response, error = make_api_request('POST', f'/groups/{group_id}/announcements/', json={'content': content})

        if error or not response.ok:
            flash('新增公告失敗！', 'error')
        else:
            flash('公告已成功發布！', 'success')
        return redirect(url_for('group_leader_view', group_id=group_id))

    # GET 請求：獲取必要的資料以渲染頁面
    group_res, err_g = make_api_request('GET', f'/groups/{group_id}/')
    profile_res, err_p = make_api_request('GET', '/auth/profile/')
    if err_g or not group_res.ok or err_p or not profile_res.ok:
        flash('無法讀取資料，或您沒有權限。', 'error')
        return redirect(request.referrer or url_for('dashboard'))
        
    # 傳遞 is_edit=False 來告訴樣板這是「建立」模式
    return render_template('create_announcement.html', 
                           group=group_res.json(), 
                           profile=profile_res.json(), 
                           is_edit=False,
                           announcement=None) # 建立模式下沒有舊公告資料

@app.route('/edit_announcement/<int:announcement_id>', methods=['GET', 'POST'])
def edit_announcement(announcement_id):
    """處理「編輯」現有公告的請求。"""
    if request.method == 'POST':
        content = request.form.get('content')
        group_id = request.form.get('group_id')
        if not content:
            flash('公告內容不得為空。', 'error')
            return redirect(url_for('edit_announcement', announcement_id=announcement_id))

        response, error = make_api_request('PUT', f'/announcements/{announcement_id}/', json={'content': content})
        
        if error or not response.ok:
            flash('更新公告失敗！', 'error')
        else:
            flash('公告已成功更新。', 'success')
        return redirect(url_for('group_leader_view', group_id=group_id))

    # GET 請求：獲取公告現有內容，並顯示編輯頁面
    ann_res, error = make_api_request('GET', f'/announcements/{announcement_id}/')
    if error or not ann_res.ok:
        flash('無法讀取公告資料。', 'error')
        return redirect(request.referrer or url_for('dashboard'))
    
    announcement_data = ann_res.json()
    group_id = announcement_data.get('group')

    # 同時獲取群組和個人資料
    group_res, _ = make_api_request('GET', f'/groups/{group_id}/')
    profile_res, _ = make_api_request('GET', '/auth/profile/')

    # 傳遞 is_edit=True 來告訴樣板這是「編輯」模式
    return render_template('create_announcement.html', 
                           group=group_res.json(), 
                           profile=profile_res.json(), 
                           is_edit=True,
                           announcement=announcement_data)

@app.route('/delete_announcement/<int:announcement_id>', methods=['POST'])
def delete_announcement(announcement_id):
    """代理前端請求，刪除一則公告"""
    ann_res, err = make_api_request('GET', f'/announcements/{announcement_id}/')
    if err or not ann_res.ok:
        flash('找不到該公告或權限不足。', 'error')
        return redirect(request.referrer or url_for('dashboard'))
    
    group_id = ann_res.json().get('group')

    response, error = make_api_request('DELETE', f'/announcements/{announcement_id}/')
    if error or not response.ok:
        flash('刪除公告失敗！', 'error')
    else:
        flash('公告已成功刪除。', 'success')
    
    return redirect(url_for('group_leader_view', group_id=group_id))



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

@app.route('/promote_member/<int:group_id>/<int:user_id>', methods=['POST'])
def promote_member(group_id, user_id):
    """代理前端請求，呼叫後端 API 來提升成員權限"""
    response, error = make_api_request(
        'PATCH', 
        f'/groups/{group_id}/members/{user_id}/role/', 
        json={'role': 'ADMIN'}
    )
    if error or not response.ok:
        flash('權限更新失敗！請確認您的權限。', 'error')
    else:
        flash('成員權限已成功提升為管理員！', 'success')
    
    return redirect(url_for('group_leader_view', group_id=group_id))

@app.route('/remove_member/<int:group_id>/<int:user_id>', methods=['POST'])
def remove_member(group_id, user_id):
    """代理前端請求，呼叫後端 API 來移除成員"""
    response, error = make_api_request('DELETE', f'/groups/{group_id}/members/{user_id}/')

    if error or not response.ok:
        error_msg = '移除成員失敗！'
        if response is not None and response.status_code == 403:
            error_msg = f"移除失敗：{response.json().get('error', '權限不足')}"
        flash(error_msg, 'error')
    else:
        flash('成員已成功移除。', 'success')
    
    return redirect(url_for('group_leader_view', group_id=group_id))

@app.route("/my_groups")
def my_groups_standalone():
    """
    獨立的「我的群組」頁面，讓使用者可以查看所有已加入的群組。
    """
    response, error = make_api_request('GET', '/me/groups/')

    if error or not response.ok:
        flash('無法讀取您的群組列表，請稍後再試。', 'error')
        return redirect(url_for('dashboard'))
    
    my_groups_data = response.json().get('results', [])
    
    return render_template('my_groups_standalone.html', my_groups=my_groups_data)

@app.route("/all_reports")
def all_reports():
    """
    【新增】獲取使用者所有過往行程並顯示頁面。
    """
    # 呼叫後端 API 獲取行程列表
    response, error = make_api_request('GET', '/trips/')

    if error or not response.ok:
        flash('無法讀取您的過往行程，請稍後再試。', 'error')
        return redirect(url_for('dashboard'))
    
    # 從 API 回應中解析出行程列表 (後端預設有分頁，我們先取第一頁的結果)
    trips_data = response.json().get('results', [])
    
    # 將行程資料傳遞給範本進行渲染
    return render_template('all_reports.html', trips=trips_data)


@app.route("/group_detail/<int:group_id>")
def group_detail(group_id):
    """
    【新增】顯示單一群組的詳細資訊頁面 (待辦)。
    這是一個暫存的路由，避免啟動時出錯。
    """
    # 這裡的邏輯未來需要擴充，例如呼叫 API 獲取群組資料
    flash(f'群組詳細資料頁面 (ID: {group_id}) 尚在開發中。', 'info')
    return redirect(url_for('dashboard'))

@app.route("/chat")
def chat():
    """渲染 AI 智慧客服的頁面"""
    if 'access_token' not in session:
        flash('請先登入才能使用 AI 客服。', 'warning')
        # 【修改】告訴登入頁面，成功後要跳轉回現在這個 chat 頁面
        return redirect(url_for('login', next=request.path))
        
    return render_template("chat.html")

# 【新增】作為前端 JS 和後端 API 之間安全橋樑的代理路由
@app.route('/api/proxy/chatbot', methods=['POST'])
def chatbot_proxy():
    """
    代理前端對 Chatbot API 的請求。
    這樣做可以避免將 access_token 暴露在瀏覽器端，更安全。
    """
    if 'access_token' not in session:
        return jsonify({'error': 'Not Authenticated'}), 401

    # 從前端 JS 獲取對話歷史
    messages = request.json.get('messages', [])
    if not messages:
        return jsonify({'error': 'Messages are required'}), 400

    # 使用伺服器端的 make_api_request 函式來安全地呼叫後端
    response, error = make_api_request('POST', '/chatbot/', json={'messages': messages})

    if error or not response.ok:
        return jsonify({'error': 'Failed to get response from AI service'}), 502 # Bad Gateway

    # 將後端 API 的真實回應直接回傳給前端 JS
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

