// 檔案路徑: static/js/pages/group_leader_view.js

(function() {
    'use strict';

    // 1. 移除 API_BASE_URL 和 fetchWithAuth

    // 頁面守衛
    const userProfile = JSON.parse(localStorage.getItem('userProfile'));
    if (!userProfile) {
        window.location.href = '/login';
        return;
    }

    let currentGroupId = null;
    let groupTrendsChart = null;

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

    async function fetchAndUpdateGroupTrends(startDate, endDate) {
        if (!currentGroupId || !startDate || !endDate) return;
        const summaryContainer = document.querySelector('.trends-summary');
        const chartWrapper = document.querySelector('.chart-wrapper');
        if (summaryContainer) summaryContainer.style.opacity = 0.5;
        
        try {
            // 直接使用 fetchWithAuth
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
        if (typeof flatpickr === 'undefined') return;
        const formatDate = (date) => date.toISOString().split('T')[0];
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(endDate.getMonth() - 5);
        
        flatpickr("#group-date-range-picker", {
            mode: "range",
            dateFormat: "Y-m-d",
            defaultDate: [formatDate(startDate), formatDate(endDate)],
            onClose: function(selectedDates) {
                if (selectedDates.length === 2) {
                    fetchAndUpdateGroupTrends(formatDate(selectedDates[0]), formatDate(selectedDates[1]));
                }
            }
        });
        fetchAndUpdateGroupTrends(formatDate(startDate), formatDate(endDate));
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
                    // 更新網址但不跳轉
                    const newUrl = `${window.location.pathname}?group_id=${groupId}`;
                    window.history.replaceState({}, '', newUrl);
                } else {
                    document.querySelector('.group-leader-container').innerHTML = '<h1>您尚未加入任何群組</h1>';
                    return;
                }
            }
            currentGroupId = parseInt(groupId);
            
            // 平行請求
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
            
            const inviteLink = document.getElementById('invite-member-link');
            if(inviteLink) inviteLink.href = `/invite_member?group_id=${currentGroupId}`;
            
            const settingsLink = document.getElementById('group-settings-link');
            if(settingsLink) settingsLink.href = `/group_settings?group_id=${currentGroupId}`;
            
            const addAnnounceLink = document.getElementById('add-announcement-link');
            if(addAnnounceLink) addAnnounceLink.href = `/create_announcement?group_id=${currentGroupId}`;

        } catch (error) {
            console.error("載入群組管理頁面失敗:", error.message);
            document.querySelector('.group-leader-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
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
                const score = parseFloat(member.average_score || 0);
                const scoreDisplay = isNaN(score) ? 'N/A' : score.toFixed(1);
                const joinDate = member.joined_at ? new Date(member.joined_at).toLocaleDateString() : 'N/A';
                
                let scoreClass = '';
                if (score < 80) scoreClass = 'danger';
                else if (score < 90) scoreClass = 'warning';
                else scoreClass = 'excellent';
                
                const actionsCell = canManage ?
                    `<td class="actions-col">
                        <a href="/member_dashboard?member_id=${member.id}&group_id=${currentGroupId}" class="btn-action" title="查看儀表板">
                            <i class="fa-solid fa-chart-bar"></i>
                        </a>
                        <a href="/member_videos?member_id=${member.id}" class="btn-action" title="行車影片">
                            <i class="fa-solid fa-video"></i>
                        </a>
                    </td>` : '';

                tableBody.innerHTML += `
                    <tr>
                        <td class="avatar-col"><img src="${member.personnelprofile?.avatar || '/static/images/user-placeholder.svg'}" alt="${member.first_name}" class="member-avatar-small"></td>
                        <td class="name-col">${member.last_name}${member.first_name || member.username}</td>
                        <td><span class="score-badge ${scoreClass}">${scoreDisplay}</span></td>
                        <td>${joinDate}</td>
                        ${actionsCell}
                    </tr>`;
            });
        } else {
            tableBody.innerHTML = `<tr><td colspan="${canManage ? 5 : 4}" style="text-align: center; padding: 2rem;">此群組尚無成員。</td></tr>`;
        }
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
                    actionButtons = `<div class="announcement-actions"><a href="/edit_announcement/${numericId}" class="btn-action-icon" title="編輯"><i class="fa-solid fa-pencil"></i></a><button class="btn-action-icon danger" onclick="window.confirmDelete('${numericId}', '${ann.content.substring(0, 10)}...')" title="刪除"><i class="fa-solid fa-trash"></i></button></div>`;
                }
                const typeBadge = ann.type === 'SYSTEM' ? '<span class="announcement-badge system">系統公告</span>' : '<span class="announcement-badge group">群組公告</span>';
                announcementsList.innerHTML += `<div class="announcement-row">${typeBadge}<div class="announcement-info"><a href="/announcement_detail/${ann.id}" class="announcement-title">${ann.content}</a><div class="announcement-meta"><span class="meta-item"><i class="fa-solid fa-user"></i> ${ann.publisher}</span><span class="meta-item"><i class="fa-solid fa-calendar"></i> ${publishDate}</span></div></div>${actionButtons}</div>`;
            });
        } else {
            announcementsList.innerHTML = '<div style="text-align: center; padding: 2rem;">尚無任何公告。</div>';
        }
    }

    // 全域函式供 HTML onclick 使用
    window.confirmDelete = async function(id, title) {
        if (confirm(`確定要刪除公告？`)) {
            try {
                const response = await fetchWithAuth(`/api/announcements/${id}/`, { method: 'DELETE' });
                if (response.ok) {
                    alert('公告已刪除！');
                    window.location.reload();
                } else {
                    alert('刪除失敗');
                }
            } catch (error) {
                alert('刪除失敗');
            }
        }
    };

    document.addEventListener('DOMContentLoaded', initializeGroupViewPage);

})();