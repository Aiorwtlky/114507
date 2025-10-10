// 檔案路徑: static/js/pages/edit-profile.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    const profileForm = document.getElementById('editProfileForm');

    /**
     * 執行一個帶有認證標頭的 fetch 請求
     */
    async function fetchWithAuth(endpoint, options = {}) {
        // (這段程式碼和 profile.js 裡的一模一樣)
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
     * 1. 將 API 資料預填入表單
     */
    async function loadProfileForEditing() {
        try {
            const response = await fetchWithAuth('/api/auth/profile/');
            if (!response.ok) throw new Error('無法載入資料');
            const data = await response.json();
            const profile = data.personnelprofile || {};
            
            // 更新側邊欄 (因為編輯頁也需要顯示)
            document.getElementById('sidebar-avatar').src = profile.avatar || '/static/images/user-placeholder.svg';
            document.getElementById('sidebar-username').textContent = data.first_name || data.username;
            document.getElementById('sidebar-user-role').textContent = data.is_staff ? '管理員' : '一般成員';

            // 預填表單
            document.getElementById('avatarPreview').src = profile.avatar || '/static/img/user-placeholder.svg';
            document.getElementById('name').value = data.first_name || '';
            document.getElementById('username').value = data.username || '';
            document.getElementById('emp_id').value = profile.personnel_number || '';
            const genderRadio = document.querySelector(`input[name="gender"][value="${profile.gender}"]`);
            if (genderRadio) genderRadio.checked = true;
            document.getElementById('email').value = data.email || '';
            document.getElementById('phone').value = profile.phone || '';
            document.getElementById('license_number').value = profile.license_number || '';
            document.getElementById('license_type').value = profile.license_type || '普通小型車';
            document.getElementById('driving_years').value = profile.driving_experience || 0;
        } catch (error) {
            console.error("載入編輯資料失敗:", error.message);
        }
    }

    /**
     * 2. 處理表單提交
     */
    async function handleProfileUpdate(event) {
        event.preventDefault();
        const saveButton = document.querySelector('.btn-edit-profile');
        saveButton.disabled = true;
        saveButton.querySelector('span').textContent = '儲存中...';
        const formData = new FormData(profileForm);
        try {
            const response = await fetchWithAuth('/api/auth/profile/', {
                method: 'PATCH',
                body: formData,
            });
            if (response.ok) {
                alert('個人資料更新成功！');
                window.location.href = '/profile';
            } else {
                const errorData = await response.json();
                let errorMessage = '更新失敗：\n';
                for (const field in errorData) {
                    errorMessage += `${field}: ${errorData[field].join(', ')}\n`;
                }
                alert(errorMessage);
            }
        } catch (error) {
            console.error('更新個人資料時發生錯誤:', error);
        } finally {
            saveButton.disabled = false;
            saveButton.querySelector('span').textContent = '儲存變更';
        }
    }

    /**
     * 3. 圖片預覽
     */
    const avatarUpload = document.getElementById('avatarUpload');
    if (avatarUpload) {
        avatarUpload.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => { document.getElementById('avatarPreview').src = e.target.result; };
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }

    // 頁面初始化
    document.addEventListener('DOMContentLoaded', () => {
        loadProfileForEditing();
        profileForm.addEventListener('submit', handleProfileUpdate);

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
    });

})();