// 檔案路徑: static/js/pages/group_leader_view.js (最終表格修正版)

(function() {
    'use strict';

    // 頁面守衛：檢查使用者是否已登入
    const userProfile = JSON.parse(localStorage.getItem('userProfile'));
    if (!userProfile) {
        alert('無法獲取使用者資訊，請重新登入。');
        window.location.href = '/login';
        return;
    }

    // --- 全域變數 ---
    const API_BASE_URL = 'http://127.0.0.1:8000';
    let currentGroupId = null;
    let groupTrendsChart = null;

    // --- 核心 API 呼叫函式 ---
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

    // --- 根據權限，動態顯示/隱藏 UI 元素 ---
    function setupUIByRole(canManage) {
        const managementElements = [
            document.getElementById('invite-member-link'),
            document.getElementById('group-settings-link'),
            document.getElementById('add-announcement-link'),
        ];
        const memberActionsHeader = document.querySelector('.members-table th.actions-col');
        const trendsCard = document.querySelector('.trends-card');

        if (canManage) {
            managementElements.forEach(el => { if (el) el.style.display = 'inline-flex'; });
            if (document.getElementById('group-settings-link')) document.getElementById('group-settings-link').style.display = 'block';
            if (memberActionsHeader) memberActionsHeader.style.display = 'table-cell';
            if (trendsCard) trendsCard.style.display = 'flex';
        } else {
            managementElements.forEach(el => { if (el) el.style.display = 'none'; });
            if (memberActionsHeader) memberActionsHeader.style.display = 'none';
            if (trendsCard) trendsCard.style.display = 'none';
        }
    }

    // --- 趨勢分析圖表相關 ---
    async function fetchAndUpdateGroupTrends(startDate, endDate) {
        if (!currentGroupId || !startDate || !endDate) return;
        const summaryContainer = document.querySelector('.trends-summary');
        const chartWrapper = document.querySelector('.chart-wrapper');
        if (summaryContainer) summaryContainer.style.opacity = 0.5;
        if (chartWrapper) chartWrapper.innerHTML = '<p>載入趨勢數據中...</p>';
        try {
            const response = await fetchWithAuth(`/api/groups/${currentGroupId}/statistics/trends/?start_date=${startDate}&end_date=${endDate}`);
            if (!response.ok) throw new Error('無法獲取群組趨勢資料');
            const trendsData = await response.json();
            updateTrendsUI(trendsData);
        } catch (error) {
            console.error('獲取群組趨勢失敗:', error);
            if (chartWrapper) chartWrapper.innerHTML = '<p style="color: red;">載入趨勢數據失敗。</p>';
        } finally {
            if (summaryContainer) summaryContainer.style.opacity = 1;
        }
    }

    function updateTrendsUI(trendsData) {
        const summaryAvg = document.getElementById('summary-avg');
        const summaryChange = document.getElementById('summary-change');
        const summaryMax = document.getElementById('summary-max');
        const summaryMin = document.getElementById('summary-min');
        const chartWrapper = document.querySelector('.chart-wrapper');

        if (!trendsData || trendsData.length === 0) {
            if (summaryAvg) summaryAvg.textContent = 'N/A';
            if (summaryChange) summaryChange.textContent = '--';
            if (summaryMax) summaryMax.textContent = 'N/A';
            if (summaryMin) summaryMin.textContent = 'N/A';
            if (chartWrapper) chartWrapper.innerHTML = '<p>選定範圍內無資料可供顯示。</p>';
            if (groupTrendsChart) groupTrendsChart.destroy();
            return;
        }
        const latestData = trendsData[trendsData.length - 1] || {};
        if (summaryAvg) summaryAvg.textContent = `${parseFloat(latestData.average_score || 0).toFixed(1)}分`;
        if (summaryMax) summaryMax.textContent = `${parseFloat(latestData.max_score || 0).toFixed(1)}分`;
        if (summaryMin) summaryMin.textContent = `${parseFloat(latestData.min_score || 0).toFixed(1)}分`;
        let changeText = '--';
        if (trendsData.length >= 2) {
            const latest = trendsData[trendsData.length - 1].average_score;
            const previous = trendsData[trendsData.length - 2].average_score;
            if (previous > 0) {
                const change = ((latest - previous) / previous) * 100;
                if (isFinite(change)) {
                    summaryChange.className = `summary-value ${change >= 0 ? 'success' : 'danger'}`;
                    changeText = `${change >= 0 ? '▲' : '▼'} ${Math.abs(change).toFixed(1)}%`;
                }
            }
        }
        if (summaryChange) summaryChange.textContent = changeText;
        if (chartWrapper) chartWrapper.innerHTML = '<canvas id="groupTrendsChart"></canvas>';
        const ctx = document.getElementById('groupTrendsChart')?.getContext('2d');
        if (!ctx) return;
        if (groupTrendsChart) groupTrendsChart.destroy();
        groupTrendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendsData.map(item => item.month),
                datasets: [{
                    label: '群組每月平均分數',
                    data: trendsData.map(item => item.average_score),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    function initFilterControls() {
        const formatDate = (date) => date.toISOString().split('T')[0];
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(endDate.getMonth() - 5);
        const defaultStartDateStr = formatDate(startDate);
        const defaultEndDateStr = formatDate(endDate);
        flatpickr("#group-date-range-picker", {
            mode: "range",
            dateFormat: "Y-m-d",
            defaultDate: [defaultStartDateStr, defaultEndDateStr],
            onClose: function(selectedDates) {
                if (selectedDates.length === 2) {
                    fetchAndUpdateGroupTrends(formatDate(selectedDates[0]), formatDate(selectedDates[1]));
                }
            }
        });
        fetchAndUpdateGroupTrends(defaultStartDateStr, defaultEndDateStr);
    }

    async function initializeGroupViewPage() {
        const urlParams = new URLSearchParams(window.location.search);
        let groupId = urlParams.get('group_id');
        try {
            if (!groupId) {
                const myGroupsRes = await fetchWithAuth('/api/me/groups/');
                if (!myGroupsRes.ok) throw new Error('無法獲取您的群組列表');
                const myGroupsData = await myGroupsRes.json();
                if (myGroupsData.results && myGroupsData.results.length > 0) {
                    groupId = myGroupsData.results[0].id;
                    window.history.replaceState({}, '', `?group_id=${groupId}`);
                } else {
                    document.querySelector('.group-leader-container').innerHTML = '<h1>您尚未加入任何群組</h1>';
                    return;
                }
            }
            currentGroupId = parseInt(groupId);
            const [groupRes, membersRes, announcementsRes] = await Promise.all([
                fetchWithAuth(`/api/groups/${currentGroupId}/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/members/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/all-announcements/`)
            ]);
            if (!groupRes.ok || !membersRes.ok || !announcementsRes.ok) throw new Error('無法獲取群組詳細資料');
            const groupData = await groupRes.json();
            const membersData = await membersRes.json();
            const announcementsData = await announcementsRes.json();
            const membership = userProfile.group_memberships.find(m => m.group_id === currentGroupId);
            const isGroupAdmin = membership && membership.role === 'ADMIN';
            const canManage = userProfile.is_staff || isGroupAdmin;
            setupUIByRole(canManage);
            updateGroupInfoUI(groupData, membersData.results || membersData);
            updateMembersTableUI(membersData.results || membersData, canManage);
            updateAnnouncementsListUI(announcementsData, canManage);
            if (canManage) initFilterControls();
            document.getElementById('invite-member-link').href = `/invite_member?group_id=${currentGroupId}`;
            document.getElementById('group-settings-link').href = `/group_settings?group_id=${currentGroupId}`;
            document.getElementById('add-announcement-link').href = `/create_announcement?group_id=${currentGroupId}`;
        } catch (error) {
            console.error("載入群組管理頁面失敗:", error.message);
            document.querySelector('.group-leader-container').innerHTML = `<h1>載入群組資料時發生錯誤</h1><p>${error.message}</p>`;
        }
    }

    function updateGroupInfoUI(group, members) {
        document.getElementById('group-name').textContent = group.name;
        document.getElementById('group-description').textContent = group.description || '暫無描述';
        const leadersList = document.getElementById('group-leaders-list');
        leadersList.innerHTML = '';
        const admins = members.filter(member => member.role === 'ADMIN');
        if (admins.length > 0) {
            admins.forEach(admin => { leadersList.innerHTML += `<span class="leader-badge">${admin.first_name || admin.username}</span>`; });
        } else {
            leadersList.innerHTML = '<span class="leader-badge">尚無管理員</span>';
        }
        document.getElementById('my-identity-avatar').src = userProfile.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('my-identity-name').textContent = userProfile.first_name || userProfile.username;
        const myMembership = members.find(member => member.id === userProfile.id);
        const myRole = myMembership?.role === 'ADMIN' ? '群組管理員' : '一般成員';
        document.getElementById('my-identity-role').innerHTML = `<i class="fa-solid fa-user-tie"></i> ${myRole}`;
    }

    function updateMembersTableUI(members, canManage) {
        const tableBody = document.getElementById('members-table-body');
        tableBody.innerHTML = '';
        if (members && members.length > 0) {
            members.forEach(member => {
                const score = parseFloat(member.average_score || 0); // 改為 float
                const scoreDisplay = isNaN(score) ? 'N/A' : score.toFixed(1); // 顯示一位小數
                const joinDate = member.joined_at ? new Date(member.joined_at).toLocaleDateString() : 'N/A';
                const scoreClass = score >= 90 ? 'excellent' : (score >= 81 ? 'warning' : 'danger');
                
                // 修正連結格式
                const actionsCell = canManage ?
                    `<td class="actions-col">
                        <a href="/member_dashboard?member_id=${member.id}&group_id=${currentGroupId}" class="btn-action" title="查看成員儀表板">
                            <i class="fa-solid fa-chart-bar"></i>
                        </a>
                        <a href="/member_videos?member_id=${member.id}" class="btn-action" title="行車影片">
                            <i class="fa-solid fa-video"></i>
                        </a>
                    </td>` : '';

                tableBody.innerHTML += `
                    <tr>
                        <td class="avatar-col"><img src="${member.personnelprofile?.avatar || '/static/images/user-placeholder.svg'}" alt="${member.first_name || member.username}" class="member-avatar-small"></td>
                        <td class="name-col">${member.last_name}${member.first_name || member.username}</td>
                        <td><span class="score-badge ${scoreClass}">${scoreDisplay}</span></td>
                        <td>${joinDate}</td>
                        ${actionsCell}
                    </tr>`;
            });
        } else {
            tableBody.innerHTML = `<tr><td colspan="${canManage ? 5 : 4}" style="text-align: center; padding: 2rem;">此群組尚無成員。</td></tr>`;
        }
        // initScoreBadges 函式不再需要，因為 class 已在上面動態產生
    }

    function updateAnnouncementsListUI(announcements, canManage) {
        const announcementsList = document.getElementById('announcements-list');
        announcementsList.innerHTML = '';
        if (announcements && announcements.length > 0) {
            announcements.forEach(ann => {
                const publishDate = new Date(ann.publish_date).toLocaleDateString();
                let actionButtons = '';
                if (ann.type === 'GROUP' && canManage) {
                    const numericId = ann.id.split('-')[1]; 
                    actionButtons = `<div class="announcement-actions"><a href="/edit_announcement/${numericId}" class="btn-action-icon" title="編輯"><i class="fa-solid fa-pencil"></i></a><button class="btn-action-icon danger" title="刪除" onclick="confirmDelete('${numericId}', '${ann.content.substring(0, 20)}...')"><i class="fa-solid fa-trash"></i></button></div>`;
                }
                const typeBadge = ann.type === 'SYSTEM' ? '<span class="announcement-badge system">系統公告</span>' : '<span class="announcement-badge group">群組公告</span>';
                announcementsList.innerHTML += `<div class="announcement-row">${typeBadge}<div class="announcement-info"><a href="/announcement_detail/${ann.id}" class="announcement-title">${ann.content}</a><div class="announcement-meta"><span class="meta-item"><i class="fa-solid fa-user"></i> ${ann.publisher}</span><span class="meta-item"><i class="fa-solid fa-calendar"></i> ${publishDate}</span></div></div>${actionButtons}</div>`;
            });
        } else {
            announcementsList.innerHTML = '<div style="text-align: center; padding: 2rem;">尚無任何公告。</div>';
        }
    }

    // 這個函式不再需要，因為我們在產生表格時就直接設定好 class 了
    /*
    function initScoreBadges() { ... }
    */

    window.confirmDelete = async function(id, title) {
        if (confirm(`確定要刪除公告「${title}」嗎？此操作無法復原。`)) {
            try {
                const response = await fetchWithAuth(`/api/announcements/${id}/`, { method: 'DELETE' });
                if (response.ok) {
                    alert('公告已成功刪除！');
                    window.location.reload();
                } else {
                    alert(`刪除失敗：伺服器回應狀態 ${response.status}`);
                }
            } catch (error) {
                alert('刪除失敗，請檢查網路連線。');
            }
        }
    };

    document.addEventListener('DOMContentLoaded', initializeGroupViewPage);

})();