// 檔案路徑: static/js/pages/group_leader_view.js (最終完整版)

(function() {
    'use strict';

    const userProfile = JSON.parse(localStorage.getItem('userProfile'));
    if (!userProfile) {
        alert('無法獲取使用者資訊，請重新登入。');
        window.location.href = '/login';
        return; 
    }
    
    const API_BASE_URL = 'http://127.0.0.1:8000';
    let currentGroupId = null;
    let groupTrendsChart = null;

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) { window.location.href = '/login'; throw new Error('Not Authenticated'); }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) { headers.append('Content-Type', 'application/json'); }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.clear(); window.location.href = '/login'; throw new Error('Token Expired'); }
        return response;
    }

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
        const summaryValues = document.querySelectorAll('.summary-value');
        const chartWrapper = document.querySelector('.chart-wrapper');

        if (!trendsData || trendsData.length === 0) {
            if (summaryValues.length >= 4) {
                summaryValues[0].textContent = 'N/A';
                summaryValues[1].textContent = '--';
                summaryValues[2].textContent = 'N/A';
                summaryValues[3].textContent = 'N/A';
            }
            if (chartWrapper) chartWrapper.innerHTML = '<p>選定範圍內無資料可供顯示。</p>';
            if (groupTrendsChart) groupTrendsChart.destroy();
            return;
        }

        const scores = trendsData.map(item => item.average_score);
        const totalAverage = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const maxScore = Math.max(...trendsData.map(item => item.max_score));
        const minScore = Math.min(...trendsData.map(item => item.min_score));
        
        let changeText = '--';
        if (scores.length >= 2) {
            const latest = scores[scores.length - 1];
            const previous = scores[scores.length - 2];
            const change = ((latest - previous) / previous) * 100;
            if (isFinite(change) && change !== 0) {
                summaryValues[1].className = `summary-value ${change > 0 ? 'success' : 'danger'}`;
                changeText = `${change > 0 ? '▲' : '▼'} ${Math.abs(change).toFixed(1)}%`;
            }
        }
        
        if (summaryValues.length >= 4) {
            summaryValues[0].textContent = `${totalAverage.toFixed(1)}分`;
            summaryValues[1].textContent = changeText;
            summaryValues[2].textContent = `${maxScore.toFixed(1)}分`;
            summaryValues[3].textContent = `${minScore.toFixed(1)}分`;
        }

        if (chartWrapper) chartWrapper.innerHTML = '<canvas id="groupTrendsChart"></canvas>';
        const ctx = document.getElementById('groupTrendsChart')?.getContext('2d');
        if (!ctx) return;
        
        const labels = trendsData.map(item => item.month);
        
        if (groupTrendsChart) groupTrendsChart.destroy();

        groupTrendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '群組每月平均分數', data: scores,
                    borderColor: '#007bff', backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    fill: true, tension: 0.4
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
                    const newStartDate = formatDate(selectedDates[0]);
                    const newEndDate = formatDate(selectedDates[1]);
                    fetchAndUpdateGroupTrends(newStartDate, newEndDate);
                }
            }
        });
        
        fetchAndUpdateGroupTrends(defaultStartDateStr, defaultEndDateStr);
    }

    // (以下所有其他函式維持不變)
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
                } else { document.querySelector('.group-leader-container').innerHTML = '<h1>您尚未加入任何群組</h1>'; return; }
            }
            currentGroupId = parseInt(groupId);
            const [groupRes, membersRes, announcementsRes] = await Promise.all([
                fetchWithAuth(`/api/groups/${currentGroupId}/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/members/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/announcements/`)
            ]);
            if (!groupRes.ok || !membersRes.ok || !announcementsRes.ok) throw new Error('無法獲取群組詳細資料');
            const groupData = await groupRes.json();
            const membersData = await membersRes.json();
            const announcementsData = await announcementsRes.json();
            updateGroupInfoUI(groupData, membersData.results || membersData);
            updateMembersTableUI(membersData.results || membersData);
            updateAnnouncementsListUI(announcementsData);
            setupManagementUI(currentGroupId);
            document.getElementById('invite-member-link').href = `/invite_member?group_id=${currentGroupId}`;
            document.getElementById('group-settings-link').href = `/group_settings?group_id=${currentGroupId}`;
            document.getElementById('add-announcement-link').href = `/create_announcement?group_id=${currentGroupId}`;
            initFilterControls();
        } catch (error) {
            console.error("載入群組管理頁面失敗:", error.message);
            document.querySelector('.group-leader-container').innerHTML = `<h1>載入群組資料時發生錯誤</h1><p>${error.message}</p>`;
        }
    }
    function setupManagementUI(groupId) {
        const membership = userProfile.group_memberships.find(m => m.group_id === groupId);
        const isGroupAdmin = membership && membership.role === 'ADMIN';
        const canManage = userProfile.is_staff || isGroupAdmin;
        const inviteLink = document.getElementById('invite-member-link');
        const settingsLink = document.getElementById('group-settings-link');
        const addAnnouncementLink = document.getElementById('add-announcement-link');
        if (canManage) {
            if(inviteLink) inviteLink.style.display = 'inline-flex';
            if(settingsLink) settingsLink.style.display = 'block';
            if(addAnnouncementLink) addAnnouncementLink.style.display = 'inline-flex';
        } else {
            if(inviteLink) inviteLink.style.display = 'none';
            if(settingsLink) settingsLink.style.display = 'none';
            if(addAnnouncementLink) addAnnouncementLink.style.display = 'none';
        }
    
    }
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
                tableBody.innerHTML += `<tr><td class="avatar-col"><img src="${member.personnelprofile?.avatar || '/static/images/user-placeholder.svg'}" alt="${member.first_name || member.username}" class="member-avatar-small"></td><td>${member.personnelprofile?.personnel_number || 'N/A'}</td><td class="name-col">${member.first_name || member.username}</td><td><span class="score-badge ${scoreClass}">${score}</span></td><td>${joinDate}</td><td class="actions-col"><a href="/member_dashboard/${member.id}" class="btn-action" title="查看成員"><i class="fa-solid fa-eye"></i></a><a href="/member_videos/${member.id}" class="btn-action" title="行車影片"><i class="fa-solid fa-video"></i></a></td></tr>`;
            });
        } else { tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">此群組尚無成員。</td></tr>'; }
        initScoreBadges();
    }
    function updateAnnouncementsListUI(announcements) {
        const announcementsList = document.getElementById('announcements-list');
        announcementsList.innerHTML = '';
        const membership = userProfile.group_memberships.find(m => m.group_id === currentGroupId);
        const isGroupAdmin = membership && membership.role === 'ADMIN';
        const canManage = userProfile.is_staff || isGroupAdmin;
        if (announcements && announcements.results && announcements.results.length > 0) {
            announcements.results.forEach(ann => {
                const publishDate = new Date(ann.publish_date).toLocaleDateString();
                const shortContent = ann.content.length > 30 ? ann.content.substring(0, 30) + '...' : ann.content;
                const actionButtons = canManage ? `<div class="announcement-actions"><a href="/edit_announcement/${ann.id}" class="btn-action-icon" title="編輯"><i class="fa-solid fa-pencil"></i></a><button class="btn-action-icon danger" title="刪除" onclick="confirmDelete('${ann.id}', '${shortContent}')"><i class="fa-solid fa-trash"></i></button></div>` : '';
                announcementsList.innerHTML += `<div class="announcement-row"><div class="announcement-info"><a href="/announcement_detail/${ann.id}" class="announcement-title">${shortContent}</a><div class="announcement-meta"><span class="meta-item"><i class="fa-solid fa-user"></i> ${ann.publisher}</span><span class="meta-item"><i class="fa-solid fa-calendar"></i> ${publishDate}</span></div></div>${actionButtons}</div>`;
            });
        } else { announcementsList.innerHTML = '<div style="text-align: center; padding: 2rem;">尚無任何公告。</div>'; }
    }
    function initScoreBadges() {
        const scoreBadges = document.querySelectorAll('.score-badge');
        scoreBadges.forEach(badge => {
            const score = parseInt(badge.textContent.trim());
            if (isNaN(score)) return;
            badge.classList.remove('excellent', 'warning', 'danger');
            if (score >= 80) badge.classList.add('excellent');
            else if (score >= 60) badge.classList.add('warning');
            else badge.classList.add('danger');
        });
    }
    window.confirmDelete = async function(id, title) {
        if (confirm(`確定要刪除公告「${title}」嗎？此操作無法復原。`)) {
            try {
                const response = await fetchWithAuth(`/api/announcements/${id}/`, { method: 'DELETE' });
                if (response.ok) { alert('公告已成功刪除！'); window.location.reload(); }
                else { alert(`刪除失敗：伺服器回應狀態 ${response.status}`); }
            } catch (error) { alert('刪除失敗，請檢查網路連線。'); }
        }
    };

    document.addEventListener('DOMContentLoaded', initializeGroupViewPage);

})();