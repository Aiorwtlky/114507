// 檔案路徑: static/js/pages/group_settings.js (這是一個新檔案)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let groupId = null;

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            alert('您尚未登入或登入已逾時。');
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
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    // 載入群組資料並填入表單
    async function loadGroupData() {
        const urlParams = new URLSearchParams(window.location.search);
        groupId = urlParams.get('group_id');
        if (!groupId) {
            alert('錯誤：未指定群組 ID。');
            document.querySelector('.settings-container').innerHTML = '<h1>錯誤：無效的群組</h1>';
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/`);
            if (response.ok) {
                const group = await response.json();
                document.getElementById('group-name-input').value = group.name;
                document.getElementById('group-description-input').value = group.description;
                // 這裡可以再擴充載入管理員列表的邏輯
            } else {
                throw new Error('無法載入群組資料');
            }
        } catch (error) {
            console.error('載入群組資料失敗:', error);
            alert('載入群組資料失敗，請稍後再試。');
        }
    }

    // 處理儲存變更
    async function handleSaveChanges(event) {
        event.preventDefault();
        const saveButton = event.target.querySelector('button[type="submit"]');
        saveButton.disabled = true;
        saveButton.textContent = '儲存中...';

        const newName = document.getElementById('group-name-input').value;
        const newDescription = document.getElementById('group-description-input').value;

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/`, {
                method: 'PATCH', // 使用 PATCH 只更新有變更的欄位
                body: JSON.stringify({
                    name: newName,
                    description: newDescription
                })
            });

            if (response.ok) {
                alert('群組設定已成功儲存！');
                // 成功後跳轉回管理頁面
                window.location.href = `/group_leader_view?group_id=${groupId}`;
            } else {
                const errorData = await response.json();
                alert(`儲存失敗：${JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error('儲存時發生錯誤:', error);
            alert('儲存失敗，請檢查網路連線。');
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = '儲存變更';
        }
    }

    // 處理刪除群組
    async function handleDeleteGroup() {
        if (!confirm('警告：確定要刪除此群組嗎？\n\n此操作將無法復原，所有相關資料將被永久移除！')) {
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/`, {
                method: 'DELETE'
            });

            if (response.status === 204) { // 204 No Content 代表成功
                alert('群組已成功刪除。');
                window.location.href = '/dashboard'; // 刪除後回到儀表板
            } else {
                alert('刪除失敗，您可能沒有權限或群組內尚有其他資料。');
            }
        } catch (error) {
            console.error('刪除時發生錯誤:', error);
            alert('刪除失敗，請檢查網路連線。');
        }
    }

    // 頁面初始化
    document.addEventListener('DOMContentLoaded', () => {
        loadGroupData();
        
        const form = document.querySelector('.settings-form');
        form.addEventListener('submit', handleSaveChanges);

        const deleteButton = document.getElementById('delete-group-btn');
        deleteButton.addEventListener('click', handleDeleteGroup);

        // 將返回按鈕的連結也動態加上 group_id
        const backButton = document.getElementById('back-to-leader-view');
        if (groupId) {
             backButton.href = `/group_leader_view?group_id=${groupId}`;
        }
    });

})();