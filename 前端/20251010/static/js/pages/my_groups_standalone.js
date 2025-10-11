// 檔案路徑: static/js/pages/my_groups_standalone.js (這是一個新檔案)

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

    // 渲染群組列表到畫面上
    function renderGroupList(groups, currentUser) {
        const groupListElement = document.getElementById('group-list-container');
        if (!groupListElement) return;

        groupListElement.innerHTML = ''; // 清空現有內容

        if (!groups || groups.length === 0) {
            groupListElement.innerHTML = '<p>您尚未加入任何群組。</p>';
            return;
        }

        groups.forEach(group => {
            // 從 userProfile 中找到對應這個 group 的角色
            const membership = currentUser.group_memberships.find(m => m.group_id === group.id);
            const role = membership ? membership.role : 'MEMBER';
            const roleText = role === 'ADMIN' ? '管理員' : '一般成員';
            const roleClass = role === 'ADMIN' ? 'role-leader' : 'role-member';
            
            const groupElement = document.createElement('li');
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
            // 從 localStorage 獲取先前儲存的使用者資訊
            const currentUser = JSON.parse(localStorage.getItem('userProfile'));
            if (!currentUser) {
                 throw new Error('無法獲取使用者資訊');
            }

            const response = await fetchWithAuth('/api/me/groups/');
            if (!response.ok) {
                throw new Error('無法獲取群組列表');
            }
            const groupsData = await response.json();
            
            // 使用從 API 獲取的群組列表 和 localStorage 的使用者資訊來渲染畫面
            renderGroupList(groupsData.results || groupsData, currentUser);

        } catch (error) {
            console.error('初始化我的群組頁面失敗:', error);
            const container = document.getElementById('group-list-container');
            if(container) container.innerHTML = '<p style="color: red;">載入群組列表失敗，請稍後再試。</p>';
        }
    }

    document.addEventListener('DOMContentLoaded', initializePage);

})();