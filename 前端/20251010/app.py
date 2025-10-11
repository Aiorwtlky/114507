# app.py

from flask import Flask, render_template, redirect, url_for, request, session, flash
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

@app.template_filter('format_datetime')
def format_datetime(value):
    from datetime import datetime
    if not value: return ""
    try: return datetime.fromisoformat(value.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError): return value

@app.route("/")
def home():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    return render_template("logout.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/edit_profile_basic")
def edit_profile_basic():
    return render_template("edit_profile_basic.html")

@app.route("/change_password")
def change_password():
    return render_template("change_password.html")

@app.route('/group_leader_view')
def group_leader_view():
    return render_template('group_leader_view.html')

@app.route("/all_reports")
def all_reports():
    return render_template("all_reports.html")

@app.route("/solutions")
def solutions():
    return render_template("solutions.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")
    
@app.route('/create_group')
def create_group():
    return render_template('create_group.html')

@app.route('/trip_report')
def trip_report():
    return render_template("trip_report_leaflet.html")

@app.route('/my_groups_standalone')
def my_groups_standalone():
    return render_template('my_groups_standalone.html')

@app.route('/past_average_standalone')
def past_average_standalone():
    return render_template("past_average_standalone.html")


@app.route('/member_videos/<member_id>')
def member_videos(member_id):
    return render_template("member_videos.html", member_id=member_id)

@app.route('/group_settings')
def group_settings():
    return render_template('group_settings.html')

@app.route('/invite_member')
def invite_member():
    return render_template('invite_member.html')

@app.route('/member_dashboard/<member_id>')
def member_dashboard(member_id):
    return f"這是成員 {member_id} 的「儀表板」佔位頁面。"

@app.route('/create_announcement')
def create_announcement():
    return render_template('create_announcement.html')

@app.route('/announcement_detail/<announcement_id>')
def announcement_detail(announcement_id):
    return render_template('announcements.html', announcement_id=announcement_id)

@app.route('/edit_announcement/<announcement_id>')
def edit_announcement(announcement_id):
    return render_template('edit_announcement.html')

@app.route('/announcements')
def announcements():
    return "這是「所有公告列表」的佔位頁面。"
    
@app.route('/print_report')
def print_report():
    return "這是「列印報表」的佔位頁面。"

@app.route("/reset-password")
def reset_password():
    return render_template("reset_password.html")


@app.errorhandler(404)
def not_found(_):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)