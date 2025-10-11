// 檔案路徑: static/js/pages/my_groups_standalone.js (完整修正版)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

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

    // ▼▼▼【核心修改 1】新增一個專門用來更新側邊欄的函式 ▼▼▼
    function updateSidebarUI(currentUser) {
        if (!currentUser) return;
        
        const sidebarAvatar = document.getElementById('sidebar-avatar');
        const sidebarUsername = document.getElementById('sidebar-username');
        const sidebarUserRole = document.getElementById('sidebar-user-role');

        if (sidebarAvatar) {
            sidebarAvatar.src = currentUser.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
        }
        if (sidebarUsername) {
            sidebarUsername.textContent = currentUser.first_name || currentUser.username;
        }
        if (sidebarUserRole) {
            // 保持與 dashboard.js 一致的角色顯示邏輯
            sidebarUserRole.textContent = currentUser.is_staff ? '系統管理員' : (currentUser.is_group_admin ? '群組管理員' : '一般成員');
        }
    }

    // 渲染群組列表到畫面上
    function renderGroupList(groups, currentUser) {
        const groupListElement = document.getElementById('group-list-container');
        if (!groupListElement) return;

        groupListElement.innerHTML = '';

        if (!groups || groups.length === 0) {
            groupListElement.innerHTML = '<li><p>您尚未加入任何群組。</p></li>';
            return;
        }

        groups.forEach(group => {
            const membership = currentUser.group_memberships.find(m => m.group_id === group.id);
            const role = membership ? membership.role : 'MEMBER';
            const roleText = role === 'ADMIN' ? '管理員' : '一般成員';
            const roleClass = role === 'ADMIN' ? 'role-leader' : 'role-member';
            
            const groupElement = document.createElement('li');
            // 點擊群組後應前往該群組的總覽頁
            groupElement.innerHTML = `
                <a href="/group_leader_view?group_id=${group.id}">${group.name}</a>
                <span class="group-role ${roleClass}">${roleText}</span>
            `;
            groupListElement.appendChild(groupElement);
        });
    }

    // 頁面初始化函式
    async function initializePage() {
        try {
            const currentUser = JSON.parse(localStorage.getItem('userProfile'));
            if (!currentUser) {
                 throw new Error('無法獲取使用者資訊');
            }

            // ▼▼▼【核心修改 2】在頁面初始化時，立刻呼叫更新側邊欄的函式 ▼▼▼
            updateSidebarUI(currentUser);

            const response = await fetchWithAuth('/api/me/groups/');
            if (!response.ok) {
                throw new Error('無法獲取群組列表');
            }
            const groupsData = await response.json();
            
            renderGroupList(groupsData.results || groupsData, currentUser);

        } catch (error) {
            console.error('初始化我的群組頁面失敗:', error);
            const container = document.getElementById('group-list-container');
            if(container) container.innerHTML = '<li><p style="color: red;">載入群組列表失敗，請稍後再試。</p></li>';
        }
    }

    document.addEventListener('DOMContentLoaded', initializePage);

})();