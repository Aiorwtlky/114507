// 檔案路徑: static/js/pages/edit_announcement.js

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

    // 從 URL 中獲取公告 ID
    const pathParts = window.location.pathname.split('/');
    const announcementId = pathParts[pathParts.length - 1];

    /**
     * 1. 載入既有公告資料並預填表單
     */
    async function loadAnnouncementForEditing() {
        if (!announcementId || isNaN(announcementId)) {
            alert('錯誤：無效的公告 ID');
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/announcements/${announcementId}/`);
            if (!response.ok) throw new Error('無法載入公告資料');
            
            const ann = await response.json();

            // 從 content 中分離出主旨 (h3) 和真實內容
            const contentHtml = new DOMParser().parseFromString(ann.content, 'text/html');
            const subjectTag = contentHtml.querySelector('h3');
            let subject = '';
            if (subjectTag) {
                subject = subjectTag.textContent;
                subjectTag.remove(); // 從內容中移除主旨，避免重複
            }
            const mainContent = contentHtml.body.innerHTML;

            // 預填表單
            document.getElementById('subject').value = subject;
            tinymce.get('content').setContent(mainContent); // 使用 TinyMCE API 來設定內容
            document.getElementById('publish-status').textContent = `此公告已於 ${new Date(ann.publish_date).toLocaleString()} 發布。`;
            
            // 預填頁首資訊 (需要額外 API 請求)
            const [userRes, groupRes] = await Promise.all([
                fetchWithAuth('/api/auth/profile/'),
                fetchWithAuth(`/api/groups/${ann.group}/`)
            ]);
            if (userRes.ok && groupRes.ok) {
                const currentUser = await userRes.json();
                const group = await groupRes.json();
                document.getElementById('publisher-unit').textContent = group.description || '總公司';
                document.getElementById('group-context-name').textContent = group.name;
                document.getElementById('publisher-avatar').src = currentUser.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
                document.getElementById('publisher-name').textContent = currentUser.first_name || currentUser.username;
            }

        } catch (error) {
            console.error("載入編輯資料失敗:", error.message);
            alert('無法載入公告資料，請稍後再試。');
        }
    }

    /**
     * 2. 處理表單提交 (儲存變更)
     */
    async function handleFormUpdate(event) {
        event.preventDefault();
        const saveButton = document.querySelector('button[type="submit"]');
        saveButton.disabled = true;
        saveButton.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 儲存中...`;

        const subject = document.getElementById('subject').value;
        const content = tinymce.get('content').getContent();
        const fullContent = `<h3>${subject}</h3>${content}`;

        try {
            const response = await fetchWithAuth(`/api/announcements/${announcementId}/`, {
                method: 'PATCH', // 使用 PATCH 只更新有變更的欄位
                body: JSON.stringify({ content: fullContent })
            });
            if (response.ok) {
                alert('公告更新成功！');
                window.location.href = '/group_leader_view';
            } else {
                const errorData = await response.json();
                alert(`更新失敗：${JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error('更新公告時發生錯誤:', error.message);
        } finally {
            saveButton.disabled = false;
            saveButton.innerHTML = `<i class="fa-solid fa-save"></i> 儲存變更`;
        }
    }

    /**
     * 3. 處理刪除按鈕
     */
    async function handleFormDelete() {
        if (!confirm('您確定要永久刪除這篇公告嗎？此操作無法復原。')) {
            return;
        }
        
        const deleteButton = document.getElementById('deleteButton');
        deleteButton.disabled = true;
        deleteButton.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 刪除中...`;

        try {
            const response = await fetchWithAuth(`/api/announcements/${announcementId}/`, {
                method: 'DELETE'
            });
            if (response.ok) { // 狀態碼 204 No Content
                alert('公告已成功刪除！');
                window.location.href = '/group_leader_view';
            } else {
                alert(`刪除失敗：伺服器回應 ${response.status}`);
            }
        } catch (error) {
            console.error('刪除公告時發生錯誤:', error.message);
        } finally {
            deleteButton.disabled = false;
            deleteButton.innerHTML = `<i class="fa-solid fa-trash"></i> 刪除公告`;
        }
    }

    // 頁面初始化
    document.addEventListener('DOMContentLoaded', function() {
      tinymce.init({
        selector: '#content',
        plugins: 'lists link image table code help wordcount',
        toolbar: 'undo redo | blocks | bold italic | bullist numlist | link image | table | code | help',
        language: 'zh_TW',
        height: 400,
        menubar: false,
        content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 16px; }',
        setup: function(editor) {
            // 確保 TinyMCE 初始化完成後，才去載入資料
            editor.on('init', function() {
                loadAnnouncementForEditing();
            });
        }
      });

      // 綁定表單提交與刪除事件
      const form = document.getElementById('announcementForm');
      if (form) form.addEventListener('submit', handleFormUpdate);
      
      const deleteButton = document.getElementById('deleteButton');
      if (deleteButton) deleteButton.addEventListener('click', handleFormDelete);
    });

})();