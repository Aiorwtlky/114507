// 檔案路徑: static/js/pages/group_settings.js (功能增強版)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let groupId = null;
    let groupOwnerId = null; // 用來存放群組建立者的 ID

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

    function renderMemberList(members) {
        const listContainer = document.getElementById('leaders-management-list');
        listContainer.innerHTML = ''; // 清空舊內容

        if (!members || members.length === 0) {
            listContainer.innerHTML = '<p class="info-text">此群組尚無成員可管理。</p>';
            return;
        }

        members.forEach(member => {
            const isOwner = member.id === groupOwnerId;
            const isAdmin = member.role === 'ADMIN';

            let roleBadge = '';
            if (isOwner) {
                roleBadge = '<span class="role-badge owner"><i class="fa-solid fa-crown"></i> 建立者</span>';
            } else if (isAdmin) {
                roleBadge = '<span class="role-badge admin"><i class="fa-solid fa-shield-halved"></i> 管理員</span>';
            }

            let actionButton = '';
            // 只有非建立者的成員才能被變更權限
            if (!isOwner) {
                if (isAdmin) {
                    //套用新的 btn-demote 樣式並加入圖示 
                    actionButton = `<button class="btn btn-sm btn-demote" data-user-id="${member.id}" data-action="demote"><i class="fa-solid fa-arrow-down"></i> 移除管理員</button>`;
                } else {
                    //套用新的 btn-promote 樣式並加入圖示 
                    actionButton = `<button class="btn btn-sm btn-promote" data-user-id="${member.id}" data-action="promote"><i class="fa-solid fa-arrow-up"></i> 擢升為管理員</button>`;
                }
            }

            const memberRow = `
                <div class="member-row">
                    <div class="member-info">
                        <img src="${member.personnelprofile?.avatar || '/static/images/user-placeholder.svg'}" alt="${member.first_name}" class="member-avatar">
                        <span class="member-name">${member.first_name || member.username}</span>
                        ${roleBadge}
                    </div>
                    <div class="member-actions">
                        ${actionButton}
                    </div>
                </div>
            `;
            listContainer.innerHTML += memberRow;
        });
    }

    async function loadGroupData() {
        const urlParams = new URLSearchParams(window.location.search);
        groupId = urlParams.get('group_id');
        if (!groupId) {
            alert('錯誤：未指定群組 ID。');
            document.querySelector('.settings-container').innerHTML = '<h1>錯誤：無效的群組</h1>';
            return;
        }
        
        // 動態設定返回按鈕的連結
        document.getElementById('back-to-leader-view').href = `/group_leader_view?group_id=${groupId}`;

        try {
            // 使用 Promise.all 同時發送兩個請求，加快載入速度
            const [groupRes, membersRes] = await Promise.all([
                fetchWithAuth(`/api/groups/${groupId}/`),
                fetchWithAuth(`/api/groups/${groupId}/members/`)
            ]);

            if (!groupRes.ok || !membersRes.ok) {
                throw new Error('無法載入群組或成員資料');
            }
            
            const group = await groupRes.json();
            const membersData = await membersRes.json();
            const members = membersData.results || membersData;

            // 填入表單
            document.getElementById('group-name-input').value = group.name;
            document.getElementById('group-description-input').value = group.description;
            
            // 儲存群組建立者 ID，用於 UI 判斷
            groupOwnerId = group.created_by;

            // 渲染成員列表
            renderMemberList(members);

        } catch (error) {
            console.error('載入群組資料失敗:', error);
            alert('載入群組資料失敗，請稍後再試。');
        }
    }
    
    // 【核心新增】處理變更角色的函式 
    async function handleRoleChange(event) {
        const button = event.target.closest('button[data-action]');
        if (!button) return;

        const userId = button.dataset.userId;
        const action = button.dataset.action;
        const newRole = action === 'promote' ? 'ADMIN' : 'MEMBER';
        const actionText = action === 'promote' ? '擢升' : '降級';
        
        if (!confirm(`確定要${actionText}這位成員嗎？`)) {
            return;
        }

        button.disabled = true;
        button.textContent = '處理中...';

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/members/${userId}/role/`, {
                method: 'PATCH',
                body: JSON.stringify({ role: newRole })
            });

            if (response.ok) {
                alert('成員角色已成功更新！');
                loadGroupData(); // 重新載入所有資料以更新 UI
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || JSON.stringify(errorData));
            }
        } catch (error) {
            console.error(`變更角色失敗:`, error);
            alert(`操作失敗：${error.message}`);
            button.disabled = false;
            button.textContent = action === 'promote' ? '擢升為管理員' : '降為一般成員';
        }
    }

    // 處理儲存變更 (維持不變)
    async function handleSaveChanges(event) {
        event.preventDefault();
        const saveButton = event.target.querySelector('button[type="submit"]');
        saveButton.disabled = true;
        saveButton.textContent = '儲存中...';

        const newName = document.getElementById('group-name-input').value;
        const newDescription = document.getElementById('group-description-input').value;

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/`, {
                method: 'PATCH',
                body: JSON.stringify({
                    name: newName,
                    description: newDescription
                })
            });

            if (response.ok) {
                alert('群組設定已成功儲存！');
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

    // 處理刪除群組 (維持不變)
    async function handleDeleteGroup() {
        if (!confirm('警告：確定要刪除此群組嗎？\n\n此操作將無法復原，所有相關資料將被永久移除！')) {
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/`, {
                method: 'DELETE'
            });

            if (response.status === 204) {
                alert('群組已成功刪除。');
                window.location.href = '/dashboard';
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
        
        document.getElementById('settings-form').addEventListener('submit', handleSaveChanges);
        document.getElementById('delete-group-btn').addEventListener('click', handleDeleteGroup);
        
        // 【核心新增】使用事件委派來監聽成員列表中的按鈕點擊 
        document.getElementById('leaders-management-list').addEventListener('click', handleRoleChange);
    });

})();