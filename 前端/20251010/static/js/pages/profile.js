// 檔案路徑: static/js/pages/profile.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

    /**
     * 執行一個帶有認證標頭的 fetch 請求
     */
    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            alert('您尚未登入或登入已逾時，將跳轉至登入頁面。');
            window.location.href = '/login';
            throw new Error('Not Authenticated');
        }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) {
            headers.append('Content-Type', 'application/json');
        }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            alert('您的登入已過期，請重新登入。');
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    /**
     * 將 API 回傳的資料填入 HTML
     */
    function populateProfileData(userData) {
        const profile = userData.personnelprofile || {};
        const genderMap = { 'MALE': '男', 'FEMALE': '女', 'UNSPECIFIED': '不願透漏' };

        // 更新側邊欄
        document.getElementById('sidebar-avatar').src = profile.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('sidebar-username').textContent = userData.first_name || userData.username;
        document.getElementById('sidebar-user-role').textContent = userData.is_staff ? '管理員' : '一般成員';

        // 更新 Profile 頁面內容
        document.getElementById('profile-header-username').textContent = `${userData.username} 的個人資料`;
        document.getElementById('profile-header-last-login').textContent = userData.last_login ? new Date(userData.last_login).toLocaleString() : 'N/A';
        document.getElementById('profile-avatar').src = profile.avatar || '/static/img/user-placeholder.svg';
        document.getElementById('profile-first-name').textContent = userData.first_name || '尚未設定';
        document.getElementById('profile-username').textContent = userData.username;
        document.getElementById('profile-personnel-number').textContent = profile.personnel_number || 'N/A';
        document.getElementById('profile-gender').textContent = genderMap[profile.gender] || '尚未設定';
        document.getElementById('profile-email').textContent = userData.email || '尚未設定';
        document.getElementById('profile-phone').textContent = profile.phone || '尚未設定';
        document.getElementById('profile-license-number').textContent = profile.license_number || '尚未設定';
        document.getElementById('profile-license-type').textContent = profile.license_type || '尚未設定';
        document.getElementById('profile-driving-experience').textContent = `${profile.driving_experience || 0} 年`;
    }

    /**
     * 頁面載入後執行的主函式
     */
    async function initializeProfilePage() {
        try {
            const response = await fetchWithAuth('/api/auth/profile/');
            if (!response.ok) throw new Error('無法獲取個人資料');
            const userData = await response.json();
            populateProfileData(userData);
        } catch (error) {
            console.error("載入個人資料失敗:", error.message);
        }

        // 綁定登出按鈕
        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('您確定要登出嗎？')) {
                    localStorage.clear();
                    window.location.href = '/logout';
                }
            });
        }
    }

    document.addEventListener('DOMContentLoaded', initializeProfilePage);

})();