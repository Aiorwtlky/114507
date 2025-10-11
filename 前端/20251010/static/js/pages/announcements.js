// 檔案路徑: static/js/pages/announcements.js (這是一個新檔案)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) { window.location.href = '/login'; throw new Error('Not Authenticated'); }
        const headers = new Headers(options.headers || {});
        headers.append('Authorization', `Bearer ${token}`);
        headers.append('Content-Type', 'application/json');
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.clear(); window.location.href = '/login'; throw new Error('Token Expired'); }
        return response;
    }
    
    // 將 API 回傳的資料填入 HTML 元素中
    function updateUI(annData) {
        document.getElementById('announcement-subject').textContent = annData.subject;
        document.getElementById('announcement-publisher').textContent = annData.publisher;
        document.getElementById('announcement-date').textContent = new Date(annData.publish_date).toLocaleDateString();
        document.getElementById('announcement-group').textContent = annData.group_name;
        // 將內容中的換行符號轉換為 <br>
        document.getElementById('announcement-body').innerHTML = `<p>${annData.content.replace(/\n/g, '<br>')}</p>`;
    }

    async function initializePage() {
        const pathParts = window.location.pathname.split('/');
        const annId = pathParts[pathParts.length - 1]; 

        if (!annId) {
            document.querySelector('.announcement-detail-container').innerHTML = '<h1>錯誤：未指定公告 ID</h1>';
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/announcements/detail/${annId}/`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '無法載入公告資料。');
            }
            const data = await response.json();
            updateUI(data);

        } catch (error) {
            console.error('載入公告詳情失敗:', error);
            document.querySelector('.announcement-detail-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
        }
    }
    document.addEventListener('DOMContentLoaded', initializePage);

})();