// 檔案路徑: static/js/pages/announcements.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

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
     * 更新 UI 的函式
     */
    function updateUI(announcementData) {
        // 從公告內容中提取 H3 作為主旨
        const contentHtml = new DOMParser().parseFromString(announcementData.content, 'text/html');
        const subjectTag = contentHtml.querySelector('h3');
        let subject = '無主旨';
        if (subjectTag) {
            subject = subjectTag.textContent;
            subjectTag.remove(); // 從內容中移除主旨標籤，避免重複顯示
        }
        
        document.getElementById('announcement-subject').textContent = subject;
        document.getElementById('announcement-publisher').textContent = announcementData.publisher;
        document.getElementById('announcement-date').textContent = new Date(announcementData.publish_date).toLocaleDateString();
        // 後端 API 目前沒有直接回傳群組名稱，我們先用 ID 代替
        document.getElementById('announcement-group').textContent = `群組 #${announcementData.group}`;
        
        // 將剩餘的 HTML 內容填入 body
        document.getElementById('announcement-body').innerHTML = contentHtml.body.innerHTML;
    }

    /**
     * 頁面載入後執行的主要函式
     */
    async function initializePage() {
        // 1. 從 URL 路徑中獲取公告 ID
        const pathParts = window.location.pathname.split('/');
        const announcementId = pathParts[pathParts.length - 1];

        if (!announcementId || isNaN(announcementId)) {
            document.getElementById('announcement-subject').textContent = '錯誤：無效的公告 ID';
            return;
        }

        // 2. 根據 ID 獲取公告詳細資料
        try {
            const response = await fetchWithAuth(`/api/announcements/${announcementId}/`);
            if (!response.ok) {
                throw new Error('找不到該公告或您沒有權限查看');
            }
            const announcementData = await response.json();
            
            // 3. 更新頁面內容
            updateUI(announcementData);

        } catch (error) {
            console.error("載入公告失敗:", error.message);
            document.getElementById('announcement-subject').textContent = '錯誤';
            document.getElementById('announcement-body').innerHTML = `<p>${error.message}</p>`;
        }
    }

    document.addEventListener('DOMContentLoaded', initializePage);

})();