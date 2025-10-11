// 檔案路徑: static/js/pages/member_dashboard.js (這是一個新檔案)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let memberId = null;

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

    function updateUI(memberData, tripsData, trendsData) {
        const profile = memberData.personnelprofile || {};
        
        // --- 更新成員資訊卡片 ---
        document.getElementById('member-avatar').src = profile.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('member-name').textContent = memberData.first_name || memberData.username;
        
        // 需要額外獲取群組資訊才能顯示
        // 這裡我們先暫時留空或顯示 ID
        document.getElementById('member-group').textContent = '載入中...'; 
        document.getElementById('member-role').textContent = '成員';

        // --- 更新過往行程列表 ---
        const tripsList = document.getElementById('past-trips-list');
        tripsList.innerHTML = '';
        if (tripsData.results && tripsData.results.length > 0) {
            tripsData.results.slice(0, 5).forEach(trip => { // 只顯示最新的 5 筆
                tripsList.innerHTML += `
                    <li>
                        <a href="/trip_report?trip_id=${trip.id}" class="trip-link">
                            <div class="trip-info">
                                <span class="trip-date-group">${new Date(trip.start_time).toLocaleDateString()} ‧ ${trip.group}</span>
                                <span class="trip-time-route">${new Date(trip.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${new Date(trip.end_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} ‧ ${trip.name || '未命名行程'}</span>
                            </div>
                            <div class="trip-score">${Math.round(trip.score)}</div>
                        </a>
                    </li>
                `;
            });
        } else {
            tripsList.innerHTML = '<li><p>此成員尚無行程記錄。</p></li>';
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
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    }

    async function initializePage() {
        const pathParts = window.location.pathname.split('/');
        memberId = pathParts[pathParts.length - 1];

        if (!memberId) {
            document.body.innerHTML = '<h1>錯誤：未指定成員 ID</h1>';
            return;
        }

        try {
            // 同時發送所有需要的 API 請求
            const [profileRes, tripsRes, trendsRes] = await Promise.all([
                fetchWithAuth(`/api/personnel/${memberId}/profile/`), // 獲取成員資料
                fetchWithAuth(`/api/trips/?user_id=${memberId}`),    // 獲取成員的行程
                fetchWithAuth(`/api/statistics/trends/?user_id=${memberId}`) // 獲取成員的趨勢
            ]);

            if (!profileRes.ok || !tripsRes.ok || !trendsRes.ok) {
                throw new Error('一個或多個 API 請求失敗，您可能沒有權限查看此成員的資料。');
            }

            const memberData = await profileRes.json();
            const tripsData = await tripsRes.json();
            const trendsData = await trendsRes.json();
            
            updateUI(memberData, tripsData, trendsData);

        } catch (error) {
            console.error("載入成員儀表板失敗:", error);
            document.querySelector('.dashboard-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
        }
    }
    
    document.addEventListener('DOMContentLoaded', initializePage);

})();