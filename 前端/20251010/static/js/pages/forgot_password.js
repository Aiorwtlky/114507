// 檔案路徑: static/js/pages/forgot_password.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

    async function handleFormSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const email = document.getElementById('email').value;
        const messageDiv = document.getElementById('messageDiv');

        submitButton.disabled = true;
        submitButton.textContent = '處理中...';
        messageDiv.style.display = 'none';
        messageDiv.className = '';

        try {
            // 注意：後端 /api/auth/password-reset/ 端點目前尚未建立
            // 所以這個請求現在會失敗，但我們先把前端邏輯寫好
            const response = await fetch(`${API_BASE_URL}/api/auth/password-reset/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });

            // 為了安全性，無論後端回應成功或失敗 (例如 email 不存在)，
            // 我們都應該顯示一個模糊的成功訊息，避免攻擊者利用此功能確認 email 是否已註冊。
            messageDiv.className = 'flash-message flash-success'; // 使用綠色的成功樣式
            messageDiv.textContent = '如果此 Email 已被註冊，您將會很快收到一封密碼重設郵件。';
            messageDiv.style.display = 'block';
            form.reset(); // 清空表單

        } catch (error) {
            // 如果是網路連線等根本性的錯誤
            console.error('密碼重設請求失敗:', error);
            messageDiv.className = 'flash-message flash-error'; // 使用紅色的錯誤樣式
            messageDiv.textContent = '無法連線至伺服器，請稍後再試。';
            messageDiv.style.display = 'block';
        } finally {
            // 無論結果如何，都恢復按鈕狀態
            submitButton.disabled = false;
            submitButton.textContent = '發送重設郵件';
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('forgotPasswordForm');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
        }
    });

})();