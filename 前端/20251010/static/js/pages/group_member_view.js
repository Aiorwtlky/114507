// 檔案路徑: static/js/pages/group_member_view.js (這是一個新檔案)

(function() {
    'use strict';

    const userProfile = JSON.parse(localStorage.getItem('userProfile'));
    if (!userProfile) { window.location.href = '/login'; return; }
    
    const API_BASE_URL = 'http://127.0.0.1:8000';
    let currentGroupId = null;

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) { window.location.href = '/login'; throw new Error('Not Authenticated'); }
        const headers = new Headers(options.headers || {});
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) { headers.append('Content-Type', 'application/json'); }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.clear(); window.location.href = '/login'; throw new Error('Token Expired'); }
        return response;
    }

    // --- UI 更新函式 (精簡版) ---
    function updateGroupInfoUI(group, members) { /* ... (與 leader 版相同) ... */ }
    function updateMembersTableUI(members) { /* ... (與 leader 版相同，但無操作按鈕) ... */ }
    function updateAnnouncementsListUI(announcements) { /* ... (與 leader 版相同，但無管理按鈕) ... */ }

    // --- 頁面初始化 ---
    async function initializePage() {
        const urlParams = new URLSearchParams(window.location.search);
        let groupId = urlParams.get('group_id');
        try {
            if (!groupId) { /* ... (邏輯與 leader 版相同) ... */ }
            currentGroupId = parseInt(groupId);
            
            const [groupRes, membersRes, announcementsRes] = await Promise.all([
                fetchWithAuth(`/api/groups/${currentGroupId}/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/members/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/all-announcements/`)
            ]);
            if (!groupRes.ok || !membersRes.ok || !announcementsRes.ok) throw new Error('無法獲取群組資料');
            
            const groupData = await groupRes.json();
            const membersData = await membersRes.json();
            const announcementsData = await announcementsRes.json();
            
            updateGroupInfoUI(groupData, membersData.results || []);
            updateMembersTableUI(membersData.results || []);
            updateAnnouncementsListUI(announcementsData);
        } catch (error) {
            console.error("載入群組頁面失敗:", error.message);
            document.querySelector('.group-leader-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
        }
    }
    
    // (為了讓您方便複製貼上，這裡補上所有省略的程式碼)
    function updateGroupInfoUI(group, members) {
        document.getElementById('group-name').textContent = group.name;
        document.getElementById('group-description').textContent = group.description || '暫無描述';
        const leadersList = document.getElementById('group-leaders-list');
        leadersList.innerHTML = '';
        const admins = members.filter(member => member.role === 'ADMIN');
        if (admins.length > 0) { admins.forEach(admin => { leadersList.innerHTML += `<span class="leader-badge">${admin.first_name || admin.username}</span>`; }); }
        else { leadersList.innerHTML = '<span class="leader-badge">尚無管理員</span>'; }
        document.getElementById('my-identity-avatar').src = userProfile.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('my-identity-name').textContent = userProfile.first_name || userProfile.username;
        const myMembership = members.find(member => member.id === userProfile.id);
        const myRole = myMembership?.role === 'ADMIN' ? '群組管理員' : '一般成員';
        document.getElementById('my-identity-role').innerHTML = `<i class="fa-solid fa-user-tie"></i> ${myRole}`;
    }
    function updateMembersTableUI(members) {
        const tableBody = document.getElementById('members-table-body');
        tableBody.innerHTML = '';
        if (members && members.length > 0) {
            members.forEach(member => {
                const score = Math.round(member.average_score || 0);
                const joinDate = member.joined_at ? new Date(member.joined_at).toLocaleDateString() : 'N/A';
                const scoreClass = score >= 80 ? 'excellent' : (score >= 60 ? 'warning' : 'danger');
                tableBody.innerHTML += `<tr><td class="avatar-col"><img src="${member.personnelprofile?.avatar || '/static/images/user-placeholder.svg'}" alt="${member.first_name || member.username}" class="member-avatar-small"></td><td>${member.personnelprofile?.personnel_number || 'N/A'}</td><td class="name-col">${member.first_name || member.username}</td><td><span class="score-badge ${scoreClass}">${score}</span></td><td>${joinDate}</td></tr>`;
            });
        } else { tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem;">此群組尚無成員。</td></tr>'; }
    }
    function updateAnnouncementsListUI(announcements) {
        const announcementsList = document.getElementById('announcements-list');
        announcementsList.innerHTML = '';
        if (announcements && announcements.length > 0) {
            announcements.forEach(ann => {
                const publishDate = new Date(ann.publish_date).toLocaleDateString();
                const typeBadge = ann.type === 'SYSTEM' ? '<span class="announcement-badge system">系統公告</span>' : '<span class="announcement-badge group">群組公告</span>';
                announcementsList.innerHTML += `<div class="announcement-row">${typeBadge}<div class="announcement-info"><a href="#" class="announcement-title">${ann.content}</a><div class="announcement-meta"><span class="meta-item"><i class="fa-solid fa-user"></i> ${ann.publisher}</span><span class="meta-item"><i class="fa-solid fa-calendar"></i> ${publishDate}</span></div></div></div>`;
            });
        } else { announcementsList.innerHTML = '<div style="text-align: center; padding: 2rem;">尚無任何公告。</div>'; }
    }
    async function initializePage() {
        const urlParams = new URLSearchParams(window.location.search);
        let groupId = urlParams.get('group_id');
        try {
            if (!groupId) {
                const myGroupsRes = await fetchWithAuth('/api/me/groups/');
                if (!myGroupsRes.ok) throw new Error('無法獲取您的群組列表');
                const myGroupsData = await myGroupsRes.json();
                if (myGroupsData.results && myGroupsData.results.length > 0) { groupId = myGroupsData.results[0].id; window.history.replaceState({}, '', `?group_id=${groupId}`); }
                else { document.querySelector('.group-leader-container').innerHTML = '<h1>您尚未加入任何群組</h1>'; return; }
            }
            currentGroupId = parseInt(groupId);
            const [groupRes, membersRes, announcementsRes] = await Promise.all([
                fetchWithAuth(`/api/groups/${currentGroupId}/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/members/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/all-announcements/`)
            ]);
            if (!groupRes.ok || !membersRes.ok || !announcementsRes.ok) throw new Error('無法獲取群組資料');
            const [groupData, membersData, announcementsData] = await Promise.all([groupRes.json(), membersRes.json(), announcementsRes.json()]);
            updateGroupInfoUI(groupData, membersData.results || []);
            updateMembersTableUI(membersData.results || []);
            updateAnnouncementsListUI(announcementsData);
        } catch (error) { console.error("載入群組頁面失敗:", error.message); document.querySelector('.group-leader-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`; }
    }
    document.addEventListener('DOMContentLoaded', initializePage);
})();