// 檔案路徑: static/js/pages/member_dashboard.js (最終完整版)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let memberId = null;
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
        headers.append('Content-Type', 'application/json');
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    /**
     * 安全地格式化分數，如果分數無效則回傳佔位符
     */
    function formatScore(score) {
        const numericScore = parseFloat(score);
        if (typeof numericScore === 'number' && !isNaN(numericScore)) {
            return numericScore.toFixed(2);
        }
        return '--';
    }

    function updateUI(memberData, tripsData, trendsData, groupData) {
        const profile = memberData.personnelprofile || {};
        
        // --- 更新成員資訊卡片 (動態化) ---
        document.getElementById('member-avatar').src = profile.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('member-name').textContent = memberData.first_name ? `${memberData.last_name}${memberData.first_name}` : memberData.username;
        
        // 從群組資料和成員資料中找到對應的身分
        if (groupData) {
            document.getElementById('member-group').textContent = groupData.name || '未知群組';
        }
        const membership = memberData.group_memberships?.find(m => m.group_id == groupId);
        if (membership) {
            document.getElementById('member-role').textContent = membership.role === 'ADMIN' ? '群組管理員' : '群組成員';
        }

        // --- 更新過往行程列表 (加入分數格式化與顏色) ---
        const tripsList = document.getElementById('past-trips-list');
        tripsList.innerHTML = '';
        if (tripsData.results && tripsData.results.length > 0) {
            tripsData.results.slice(0, 10).forEach(trip => { // 增加顯示數量到 10 筆
                const score = parseFloat(trip.score);
                const scoreDisplay = formatScore(trip.score);
                const scoreClass = score <= 80 ? 'danger' : (score <= 90 ? 'warning' : 'excellent');

                tripsList.innerHTML += `
                    <li>
                        <a href="/trip_report?trip_id=${trip.id}" class="trip-link">
                            <div class="trip-info">
                                <span class="trip-date-group">${new Date(trip.start_time).toLocaleDateString()} ‧ ${trip.group}</span>
                                <span class="trip-time-route">${trip.name || '未命名行程'}</span>
                            </div>
                            <div class="trip-score ${scoreClass}">${scoreDisplay}</div>
                        </a>
                    </li>
                `;
            });
        } else {
            tripsList.innerHTML = '<li><p>此成員尚無行程記錄。</p></li>';
        }
        
        // --- 動態設定「查看全部」按鈕的連結 ---
        const viewAllLink = document.getElementById('view-all-trips-link');
        if(viewAllLink) {
            // 假設您有一個 all_reports 頁面，可以接收 user_id 進行篩選
            viewAllLink.href = `/all_reports?user_id=${memberId}`;
        }

        // --- 更新趨勢圖表 ---
        const trendsCtx = document.getElementById('trendsChart')?.getContext('2d');
        if (trendsCtx) {
            const labels = trendsData.map(item => item.month);
            const scores = trendsData.map(item => item.average_score);
            new Chart(trendsCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '每月駕駛分數',
                        data: scores,
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }
    }

    async function initializePage() {
        // 從 URL 獲取成員 ID 和群組 ID
        const urlParams = new URLSearchParams(window.location.search);
        memberId = urlParams.get('member_id');
        groupId = urlParams.get('group_id');

        if (!memberId || !groupId) {
            document.body.innerHTML = '<h1>錯誤：網址缺少成員 ID 或群組 ID</h1>';
            return;
        }

        try {
            // 同時發送所有需要的 API 請求
            const [profileRes, tripsRes, trendsRes, groupRes] = await Promise.all([
                fetchWithAuth(`/api/personnel/${memberId}/profile/`),
                fetchWithAuth(`/api/trips/?user_id=${memberId}&ordering=-start_time`), // 加入排序
                fetchWithAuth(`/api/statistics/trends/?user_id=${memberId}`),
                fetchWithAuth(`/api/groups/${groupId}/`) // 新增：獲取群組資訊
            ]);

            if (!profileRes.ok || !tripsRes.ok || !trendsRes.ok || !groupRes.ok) {
                throw new Error('一個或多個 API 請求失敗，您可能沒有權限查看此成員的資料。');
            }

            const memberData = await profileRes.json();
            const tripsData = await tripsRes.json();
            const trendsData = await trendsRes.json();
            const groupData = await groupRes.json();
            
            updateUI(memberData, tripsData, trendsData, groupData);

        } catch (error) {
            console.error("載入成員儀表板失敗:", error);
            document.querySelector('.dashboard-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
        }
    }
    
    document.addEventListener('DOMContentLoaded', initializePage);

})();