// 檔案路徑: static/js/pages/group_leader_view.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

    /**
     * 執行帶有認證標頭的 fetch 請求
     */
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

    /**
     * 更新群組資訊卡片
     */
    function updateGroupInfoUI(group, members, currentUser) {
        document.getElementById('group-name').textContent = group.name;
        document.getElementById('group-description').textContent = group.description || '暫無描述';

        // 顯示管理員列表
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

        // 顯示我在此群組的身分
        const myMembership = members.find(member => member.id === currentUser.id);
        document.getElementById('my-identity-avatar').src = currentUser.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('my-identity-name').textContent = currentUser.first_name || currentUser.username;
        const myRole = myMembership?.role === 'ADMIN' ? '群組管理員' : '一般成員';
        document.getElementById('my-identity-role').innerHTML = `<i class="fa-solid fa-user-tie"></i> ${myRole}`;
    }

    /**
     * 更新群組成員表格
     */
    function updateMembersTableUI(members) {
        const tableBody = document.getElementById('members-table-body');
        tableBody.innerHTML = '';
        if (members && members.length > 0) {
            members.forEach(member => {
                const score = Math.round(member.average_score || 0);
                const joinDate = member.joined_at ? new Date(member.joined_at).toLocaleDateString() : 'N/A';
                const scoreClass = score >= 80 ? 'excellent' : (score >= 60 ? 'warning' : 'danger');

                tableBody.innerHTML += `
                    <tr>
                        <td class="avatar-col">
                            <img src="${member.personnelprofile?.avatar || '/static/images/user-placeholder.svg'}" 
                                 alt="${member.first_name || member.username}" 
                                 class="member-avatar-small">
                        </td>
                        <td>${member.personnelprofile?.personnel_number || 'N/A'}</td>
                        <td class="name-col">${member.first_name || member.username}</td>
                        <td><span class="score-badge ${scoreClass}">${score}</span></td>
                        <td>${joinDate}</td>
                        <td class="actions-col">
                            <a href="/member_dashboard/${member.id}" class="btn-action" title="查看成員"><i class="fa-solid fa-eye"></i></a>
                            <a href="/member_videos/${member.id}" class="btn-action" title="行車影片"><i class="fa-solid fa-video"></i></a>
                        </td>
                    </tr>
                `;
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">此群組尚無成員。</td></tr>';
        }
        initScoreBadges();
    }

    /**
     * 更新群組公告列表
     */
    function updateAnnouncementsListUI(announcements) {
        const announcementsList = document.getElementById('announcements-list');
        announcementsList.innerHTML = '';
        if (announcements && announcements.length > 0) {
            announcements.forEach(ann => {
                const publishDate = new Date(ann.publish_date).toLocaleDateString();
                const shortContent = ann.content.length > 30 ? ann.content.substring(0, 30) + '...' : ann.content;
                announcementsList.innerHTML += `
                    <div class="announcement-row">
                        <div class="announcement-info">
                            <a href="/announcement_detail/${ann.id}" class="announcement-title">${shortContent}</a>
                            <div class="announcement-meta">
                                <span class="meta-item"><i class="fa-solid fa-user"></i> ${ann.publisher}</span>
                                <span class="meta-item"><i class="fa-solid fa-calendar"></i> ${publishDate}</span>
                            </div>
                        </div>
                        <div class="announcement-actions">
                            <a href="/edit_announcement/${ann.id}" class="btn-action-icon" title="編輯"><i class="fa-solid fa-pencil"></i></a>
                            <button class="btn-action-icon danger" title="刪除" onclick="confirmDelete('${ann.id}', '${shortContent}')"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    </div>
                `;
            });
        } else {
            announcementsList.innerHTML = '<div style="text-align: center; padding: 2rem;">尚無任何公告。</div>';
        }
    }

    /**
     * 頁面載入後執行的主要函式
     */
    async function initializeGroupViewPage() {
        try {
            const [groupsRes, currentUserRes] = await Promise.all([
                fetchWithAuth('/api/me/groups/'),
                fetchWithAuth('/api/auth/profile/')
            ]);
            if (!groupsRes.ok || !currentUserRes.ok) throw new Error('無法獲取群組或使用者資料');
            
            const groups = await groupsRes.json();
            const currentUser = await currentUserRes.json();

            if (!groups || groups.length === 0) {
                document.getElementById('group-name').textContent = '您尚未加入任何群組';
                return;
            }
            
            const targetGroup = groups[0];
            const groupId = targetGroup.id;

            const [membersRes, announcementsRes] = await Promise.all([
                fetchWithAuth(`/api/groups/${groupId}/members/`),
                fetchWithAuth(`/api/groups/${groupId}/announcements/`)
            ]);
            if (!membersRes.ok || !announcementsRes.ok) throw new Error('無法獲取群組成員或公告');

            const members = await membersRes.json();
            const announcements = await announcementsRes.json();
            
            updateGroupInfoUI(targetGroup, members, currentUser);
            updateMembersTableUI(members);
            updateAnnouncementsListUI(announcements);

            initTrendsChart();
            initFilterControls();
            
        } catch (error) {
            console.error("載入群組管理頁面失敗:", error.message);
        }

        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('您確定要登出嗎？')) {
                    localStorage.clear();
                    window.location.href = '/logout';
                }
            });
        }
    }
    
    // ========== 1. 初始化趨勢圖表（你原本的程式碼） ==========
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

    // ========== 2. 篩選器控制（你原本的程式碼） ==========
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

    // ========== 3. 分數徽章自動上色 ==========
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

    // ========== 4. 刪除確認對話框 ==========
    window.confirmDelete = function(id, title) {
        const confirmed = confirm(`確定要刪除公告「${title}」嗎？\n\n此操作無法復原。`);
        if (confirmed) {
            console.log('確認刪除 ID:', id);
            alert('刪除功能開發中...');
            // deleteAnnouncement(id);
        } else {
            console.log('取消刪除');
        }
    };

    // ========== 5. 將事件監聽器放在 IIFE 的最尾端 ==========
    document.addEventListener('DOMContentLoaded', initializeGroupViewPage);

})();