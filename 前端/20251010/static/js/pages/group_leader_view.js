// 檔案路徑: static/js/pages/group_leader_view.js (完整重構版)

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

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            window.location.href = '/login';
            throw new Error('Not Authenticated');
        }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) { headers.append('Content-Type', 'application/json'); }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    /**
     * 【新增】根據使用者權限，動態顯示或隱藏管理員專用的 UI 元素
     */
    function setupManagementUI(groupId) {
        // 檢查使用者是否為系統管理員，或是這個特定群組的管理員
        const membership = userProfile.group_memberships.find(m => m.group_id === parseInt(groupId));
        const isGroupAdmin = membership && membership.role === 'ADMIN';
        const canManage = userProfile.is_staff || isGroupAdmin;
        
        // 獲取所有需要權限控制的按鈕
        const inviteLink = document.getElementById('invite-member-link');
        const settingsLink = document.getElementById('group-settings-link');
        const addAnnouncementLink = document.getElementById('add-announcement-link');
        
        if (canManage) {
            // 如果有權限，則顯示這些按鈕
            if(inviteLink) inviteLink.style.display = 'inline-flex';
            if(settingsLink) settingsLink.style.display = 'block';
            if(addAnnouncementLink) addAnnouncementLink.style.display = 'inline-flex';
        } else {
            // 如果沒有權限，則隱藏這些按鈕
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
        if (admins.length > 0) {
            admins.forEach(admin => {
                leadersList.innerHTML += `<span class="leader-badge">${admin.first_name || admin.username}</span>`;
            });
        } else {
            leadersList.innerHTML = '<span class="leader-badge">尚無管理員</span>';
        }

        document.getElementById('my-identity-avatar').src = userProfile.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('my-identity-name').textContent = userProfile.first_name || userProfile.username;
        const myMembership = members.find(member => member.id === userProfile.id);
        const myRole = myMembership?.role === 'ADMIN' ? '群組管理員' : '一般成員';
        document.getElementById('my-identity-role').innerHTML = `<i class="fa-solid fa-user-tie"></i> ${myRole}`;
    }

    function updateMembersTableUI(members) {
        // (此函式內容不變，可沿用您原本的版本)
        const tableBody = document.getElementById('members-table-body');
        tableBody.innerHTML = '';
        if (members && members.length > 0) {
            members.forEach(member => {
                const score = Math.round(member.average_score || 0);
                const joinDate = member.joined_at ? new Date(member.joined_at).toLocaleDateString() : 'N/A';
                const scoreClass = score >= 80 ? 'excellent' : (score >= 60 ? 'warning' : 'danger');
                tableBody.innerHTML += `
                    <tr>
                        <td class="avatar-col"><img src="${member.personnelprofile?.avatar || '/static/images/user-placeholder.svg'}" alt="${member.first_name || member.username}" class="member-avatar-small"></td>
                        <td>${member.personnelprofile?.personnel_number || 'N/A'}</td>
                        <td class="name-col">${member.first_name || member.username}</td>
                        <td><span class="score-badge ${scoreClass}">${score}</span></td>
                        <td>${joinDate}</td>
                        <td class="actions-col">
                            <a href="/member_dashboard/${member.id}" class="btn-action" title="查看成員"><i class="fa-solid fa-eye"></i></a>
                            <a href="/member_videos/${member.id}" class="btn-action" title="行車影片"><i class="fa-solid fa-video"></i></a>
                        </td>
                    </tr>`;
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">此群組尚無成員。</td></tr>';
        }
        initScoreBadges();
    }
    
    function updateAnnouncementsListUI(announcements) {
        // (此函式內容不變，可沿用您原本的版本，但刪除按鈕需要權限判斷)
        const announcementsList = document.getElementById('announcements-list');
        announcementsList.innerHTML = '';

        const membership = userProfile.group_memberships.find(m => m.group_id === currentGroupId);
        const isGroupAdmin = membership && membership.role === 'ADMIN';
        const canManage = userProfile.is_staff || isGroupAdmin;

        if (announcements && announcements.results && announcements.results.length > 0) {
            announcements.results.forEach(ann => {
                const publishDate = new Date(ann.publish_date).toLocaleDateString();
                const shortContent = ann.content.length > 30 ? ann.content.substring(0, 30) + '...' : ann.content;

                // 只有管理員才看得到編輯和刪除按鈕
                const actionButtons = canManage ? `
                    <div class="announcement-actions">
                        <a href="/edit_announcement/${ann.id}" class="btn-action-icon" title="編輯"><i class="fa-solid fa-pencil"></i></a>
                        <button class="btn-action-icon danger" title="刪除" onclick="confirmDelete('${ann.id}', '${shortContent}')"><i class="fa-solid fa-trash"></i></button>
                    </div>` : '';

                announcementsList.innerHTML += `
                    <div class="announcement-row">
                        <div class="announcement-info">
                            <a href="/announcement_detail/${ann.id}" class="announcement-title">${shortContent}</a>
                            <div class="announcement-meta">
                                <span class="meta-item"><i class="fa-solid fa-user"></i> ${ann.publisher}</span>
                                <span class="meta-item"><i class="fa-solid fa-calendar"></i> ${publishDate}</span>
                            </div>
                        </div>
                        ${actionButtons}
                    </div>`;
            });
        } else {
            announcementsList.innerHTML = '<div style="text-align: center; padding: 2rem;">尚無任何公告。</div>';
        }
    }


    async function initializeGroupViewPage() {
        const urlParams = new URLSearchParams(window.location.search);
        let groupId = urlParams.get('group_id');

        try {
            // 如果 URL 沒有 group_id，就自動抓取使用者的第一個群組
            if (!groupId) {
                const myGroupsRes = await fetchWithAuth('/api/me/groups/');
                if (!myGroupsRes.ok) throw new Error('無法獲取您的群組列表');
                const myGroupsData = await myGroupsRes.json();
                if (myGroupsData.results && myGroupsData.results.length > 0) {
                    groupId = myGroupsData.results[0].id;
                    // 更新 URL 讓頁面刷新時行為一致
                    window.history.replaceState({}, '', `?group_id=${groupId}`);
                } else {
                    document.querySelector('.group-leader-container').innerHTML = '<h1>您尚未加入任何群組</h1>';
                    return;
                }
            }
            
            currentGroupId = parseInt(groupId);

            // 【權限控制】根據權限設定管理介面
            setupManagementUI(currentGroupId);

            const [groupRes, membersRes, announcementsRes] = await Promise.all([
                fetchWithAuth(`/api/groups/${currentGroupId}/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/members/`),
                fetchWithAuth(`/api/groups/${currentGroupId}/announcements/`)
            ]);

            if (!groupRes.ok || !membersRes.ok || !announcementsRes.ok) throw new Error('無法獲取群組詳細資料');

            const groupData = await groupRes.json();
            const membersData = await membersRes.json();
            const announcementsData = await announcementsRes.json();
            
            const members = membersData.results || membersData;

            updateGroupInfoUI(groupData, members);
            updateMembersTableUI(members);
            updateAnnouncementsListUI(announcementsData);

            // 更新所有管理按鈕的連結，確保它們都帶上正確的 group_id
            document.getElementById('invite-member-link').href = `/invite_member?group_id=${currentGroupId}`;
            document.getElementById('group-settings-link').href = `/group_settings?group_id=${currentGroupId}`;
            document.getElementById('add-announcement-link').href = `/create_announcement?group_id=${currentGroupId}`;

            initTrendsChart();
            initFilterControls();

        } catch (error) {
            console.error("載入群組管理頁面失敗:", error.message);
            document.querySelector('.group-leader-container').innerHTML = `<h1>載入群組資料時發生錯誤</h1><p>${error.message}</p>`;
        }
    }
    
    function initTrendsChart() {
        const canvas = document.getElementById('groupTrendsChart');
        if (!canvas) {
            console.warn('⚠️ 找不到 groupTrendsChart canvas');
            return;
        }

        const data = {
            labels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'],
            datasets: [{
                label: '群組平均分數',
                data: [85, 86, 87, 88, 87.5, 88.5, 89, 88.3, 88.3],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.2)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverBackgroundColor: '#0056b3',
                pointHoverBorderColor: '#fff'
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top', labels: { usePointStyle: true, padding: 15, font: { size: 13, weight: 'bold' }}},
                    tooltip: { mode: 'index', intersect: false, backgroundColor: 'rgba(0, 0, 0, 0.8)', padding: 12, cornerRadius: 8, callbacks: { label: function(context) { return '平均分數: ' + context.parsed.y + ' 分'; }}}
                },
                scales: {
                    y: { beginAtZero: false, min: 80, max: 95, ticks: { stepSize: 5, callback: function(value) { return value + '分'; }, font: { size: 12 } }, grid: { color: '#e9ecef' }},
                    x: { grid: { display: false }, ticks: { font: { size: 12 }}}
                },
                interaction: { mode: 'nearest', axis: 'x', intersect: false }
            }
        };

        new Chart(canvas, config);
        console.log('✅ 群組趨勢圖表已初始化（顯示整體平均）');
    }

    function initFilterControls() {
        const periodType = document.getElementById('periodType');
        const yearFilter = document.getElementById('yearFilter');
        const quarterFilter = document.getElementById('quarterFilter');
        const monthFilter = document.getElementById('monthFilter');
        if (!periodType) return;
        periodType.addEventListener('change', function() {
            const value = this.value;
            yearFilter.style.display = 'none';
            quarterFilter.style.display = 'none';
            monthFilter.style.display = 'none';
            if (value === 'year') {
                yearFilter.style.display = 'block';
            } else if (value === 'quarter') {
                yearFilter.style.display = 'block';
                quarterFilter.style.display = 'block';
            } else if (value === 'month') {
                yearFilter.style.display = 'block';
                monthFilter.style.display = 'block';
            }
        });
        periodType.dispatchEvent(new Event('change'));
        console.log('✅ 篩選器已初始化');
    }

    function initScoreBadges() {
        const scoreBadges = document.querySelectorAll('.score-badge');
        scoreBadges.forEach(badge => {
            const score = parseInt(badge.textContent.trim());
            badge.classList.remove('excellent', 'warning', 'danger');
            if (score >= 80) badge.classList.add('excellent');
            else if (score >= 60) badge.classList.add('warning');
            else badge.classList.add('danger');
        });
        console.log(`✅ 已為 ${scoreBadges.length} 個分數徽章設定顏色`);
    }

window.confirmDelete = async function(id, title) {
        if (confirm(`確定要刪除公告「${title}」嗎？\n\n此操作無法復原。`)) {
            try {
                const response = await fetchWithAuth(`/api/announcements/${id}/`, {
                    method: 'DELETE'
                });

                if (response.ok) { // HTTP 狀態碼 204 No Content 代表成功
                    alert('公告已成功刪除！');
                    window.location.reload(); // 重新整理頁面以更新列表
                } else {
                    try {
                        const errorData = await response.json();
                        alert(`刪除失敗：${JSON.stringify(errorData)}`);
                    } catch {
                        alert(`刪除失敗：伺服器回應狀態 ${response.status}`);
                    }
                }
            } catch (error) {
                console.error('刪除公告時發生錯誤:', error);
                alert('刪除失敗，請檢查網路連線。');
            }
        } else {
            console.log('取消刪除');
        }
    };

    document.addEventListener('DOMContentLoaded', initializeGroupViewPage);

})();