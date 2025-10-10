// 檔案路徑: static/js/auth.js

(function(window) {
    'use strict';

    // 你的 Django 後端 API 基礎地址
    const API_BASE_URL = 'http://127.0.0.1:8000';

    const Auth = {
        /**
         * 獲取儲存在 localStorage 中的 access token
         * @returns {string|null}
         */
        getAccessToken: () => localStorage.getItem('accessToken'),

        /**
         * 執行一個帶有認證標頭的 fetch 請求
         * @param {string} endpoint - API 的端點，例如 /api/auth/profile/
         * @param {object} options - fetch 的設定選項，例如 method, body
         * @returns {Promise<Response>}
         */
        fetchWithAuth: async (endpoint, options = {}) => {
            const token = Auth.getAccessToken();

            // 如果沒有 token，直接踢回登入頁
            if (!token) {
                alert('您尚未登入或登入已逾時，將跳轉至登入頁面。');
                window.location.href = '/login'; // 假設登入頁在 /login
                throw new Error('Not Authenticated');
            }

            const headers = options.headers || new Headers();
            headers.append('Authorization', `Bearer ${token}`);
            
            // FormData 不需要手動設定 Content-Type，瀏覽器會自動處理
            if (!(options.body instanceof FormData)) {
                headers.append('Content-Type', 'application/json');
            }

            const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

            // 如果 token 過期 (401)，也踢回登入頁
            if (response.status === 401) {
                alert('您的登入已過期，請重新登入。');
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                window.location.href = '/login';
                throw new Error('Token Expired');
            }

            return response;
        },

        /**
         * 登出功能
         */
        logout: () => {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            // 導向登出成功頁面
            window.location.href = '/logout';
        }
    };

    // 將 Auth 物件掛載到 window 上，讓其他 JS 檔案可以使用，例如 window.Auth.fetchWithAuth(...)
    window.Auth = Auth;

})(window);