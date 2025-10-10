// 檔案路徑: static/js/pages/reset_password.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

    async function handleFormSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const password = document.getElementById('password').value;
        const passwordConfirm = document.getElementById('password_confirm').value;
        const messageDiv = document.getElementById('messageDiv');
        
        // 1. 前端基本驗證
        if (password !== passwordConfirm) {
            alert('新密碼與確認密碼不相符！');
            return;
        }
        if (password.length < 8) {
            alert('密碼長度至少需要 8 個字元！');
            return;
        }

        // 2. 從 URL 獲取 token
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        if (!token) {
            alert('錯誤：無效的重設連結，找不到 token。');
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = '儲存中...';
        messageDiv.style.display = 'none';

        // 3. 發送 API 請求到後端的確認端點
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/password-reset/confirm/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: token,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                messageDiv.className = 'flash-message flash-success';
                messageDiv.textContent = '密碼已成功重設！即將跳轉至登入頁面...';
                messageDiv.style.display = 'block';
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                // 顯示後端回傳的錯誤（例如 token 過期或無效）
                messageDiv.className = 'flash-message flash-error';
                messageDiv.textContent = data.detail || data.token || data.password || '密碼重設失敗，請重試。';
                messageDiv.style.display = 'block';
                submitButton.disabled = false;
                submitButton.textContent = '儲存新密碼';
            }

        } catch (error) {
            console.error('密碼重設確認失敗:', error);
            messageDiv.className = 'flash-message flash-error';
            messageDiv.textContent = '發生未知錯誤，請稍後再試。';
            messageDiv.style.display = 'block';
            submitButton.disabled = false;
            submitButton.textContent = '儲存新密碼';
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('resetPasswordForm');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
        }
    });

})();