// 檔案路徑: static/js/pages/dashboard.js (最終完整修正版)

(function() {
    'use strict';

    // 1. 設定與工具函式 (注意：若已使用 config.js/utils.js 架構，這些可刪除)
    const API_BASE_URL = 'http://127.0.0.1:8000';

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            alert('您尚未登入或登入已逾時，將跳轉至登入頁面。');
            window.location.href = '/login';
            throw new Error('Not Authenticated');
        }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData) && options.responseType !== 'blob') {
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

    // 2. 報表預覽功能
    async function handlePdfPreview(tripId) {
        if (!tripId) return;
        const printButton = document.querySelector(`button[data-trip-id="${tripId}"]`);
        if (printButton) {
            printButton.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 報表生成中...`;
            printButton.disabled = true;
        }
        try {
            const response = await fetchWithAuth(`/api/trips/${tripId}/report/`, { responseType: 'blob' });
            if (!response.ok) { throw new Error(`無法生成報表 (狀態碼: ${response.status})`); }
            const pdfBlob = await response.blob();
            const pdfUrl = URL.createObjectURL(pdfBlob);
            window.open(pdfUrl, '_blank');
        } catch (error) {
            console.error('預覽 PDF 失敗:', error);
            alert('無法載入 PDF 報表，請確認後端伺服器運作正常。');
        } finally {
            if (printButton) {
                printButton.innerHTML = `<i class="fa-solid fa-print"></i> 列印報表`;
                printButton.disabled = false;
            }
        }
    }

    // 3. 數值格式化輔助函式
    function formatScore(score) {
        const numericScore = parseFloat(score);
        if (typeof numericScore === 'number' && !isNaN(numericScore)) {
            return numericScore.toFixed(2);
        }
        return '--';
    }

    // 4. UI 更新核心邏輯
    function updateUI(userData, groupData, tripsData, trendsData) {
        const profile = userData.personnelprofile || {};

        // --- A. 更新儀表板主要區域 ---
        // 注意路徑是否正確 (img vs images)
        document.getElementById('dashboard-avatar').src = profile.avatar || '/static/images/user-placeholder.svg';
        document.getElementById('dashboard-username').textContent = userData.first_name || userData.username;
        document.getElementById('dashboard-email').textContent = userData.email;
        if (userData.last_login) {
            document.getElementById('dashboard-last-login').textContent = `上次登入: ${new Date(userData.last_login).toLocaleString()}`;
        }

        // --- B. 【核心修正】同步更新左側 Sidebar (解決側邊欄不同步問題) ---
        const sidebarAvatar = document.getElementById('sidebar-avatar');
        const sidebarName = document.getElementById('sidebar-username');
        const sidebarRole = document.getElementById('sidebar-user-role');

        if (sidebarAvatar) {
            sidebarAvatar.src = profile.avatar || '/static/images/user-placeholder.svg';
        }
        if (sidebarName) {
            sidebarName.textContent = userData.first_name || userData.username;
        }
        if (sidebarRole) {
            // 根據權限顯示對應的中文角色
            if (userData.is_staff) {
                sidebarRole.textContent = '網站管理員';
            } else if (userData.is_group_admin) {
                sidebarRole.textContent = '群組管理員';
            } else {
                sidebarRole.textContent = '一般成員';
            }
        }
        // -------------------------------------------------------------

        // --- C. 更新群組列表 ---
        const groupsList = document.getElementById('dashboard-groups-list');
        groupsList.innerHTML = '';
        if (groupData.results && groupData.results.length > 0) {
            const targetUrl = '/group_leader_view';
            groupData.results.slice(0, 5).forEach(group => {
                groupsList.innerHTML += `<li class="list-item"><a href="${targetUrl}?group_id=${group.id}" class="list-link"><i class="fa-solid fa-user-group"></i><span>${group.name}</span></a></li>`;
            });
        } else {
            groupsList.innerHTML = '<li class="list-item"><span>您尚未加入任何群組</span></li>';
        }

        // --- D. 權限控制：顯示管理入口 ---
        const managementEntryPoint = document.getElementById('management-entry-point');
        if (managementEntryPoint && (userData.is_staff || userData.is_group_admin)) {
            managementEntryPoint.style.display = 'block';
        }

        // --- E. 更新行程列表 ---
        const tripsList = document.getElementById('dashboard-trips-list');
        tripsList.innerHTML = '';
        if (tripsData.results && tripsData.results.length > 0) {
            tripsData.results.slice(0, 5).forEach(trip => {
                const score = parseFloat(trip.score);
                const scoreDisplay = formatScore(trip.score);
                const scoreClass = score <= 80 ? 'danger' : (score <= 90 ? 'warning' : 'excellent');
                
                tripsList.innerHTML += `
                    <li class="trip-item">
                        <div class="trip-info">
                            <span class="trip-date">${new Date(trip.start_time).toLocaleDateString()}</span>
                            <span class="trip-group">${trip.group}</span>
                        </div>
                        <a href="/trip_report?trip_id=${trip.id}" class="trip-score ${scoreClass}">
                            ${scoreDisplay}分
                        </a>
                    </li>`;
            });
        } else {
            tripsList.innerHTML = '<li class="trip-item"><span>尚無行程記錄</span></li>';
        }

        // --- F. 更新「前次行程報告」卡片 ---
        const latestTrip = tripsData.results && tripsData.results[0];
        const latestTripReport = document.getElementById('latest-trip-report');
        if (latestTripReport && latestTrip) {
            const startTime = new Date(latestTrip.start_time);
            const endTime = latestTrip.end_time ? new Date(latestTrip.end_time) : null;
            let durationDisplay = '--';
            if(endTime) {
                const durationMs = endTime - startTime;
                const hours = Math.floor(durationMs / 3600000);
                const minutes = Math.round((durationMs % 3600000) / 60000);
                durationDisplay = `${hours}h ${minutes}m`;
            }

            latestTripReport.innerHTML = `
                <div class="card-header with-meta">
                    <div><h3 class="card-title"><i class="fa-solid fa-flag-checkered"></i> 前次行程報告</h3><p class="card-meta">${startTime.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })} - ${endTime ? endTime.toLocaleTimeString([], { timeStyle: 'short' }) : '進行中'}</p></div>
                </div>
                <div class="scores-grid">
                    <div class="score-box primary"><div class="score-value">${formatScore(latestTrip.score)}</div><div class="score-label">安全總分</div></div>
                    <div class="score-box"><div class="score-value">${formatScore(latestTrip.in_car_score)}</div><div class="score-label">車內分數</div></div>
                    <div class="score-box"><div class="score-value">${formatScore(latestTrip.out_car_score)}</div><div class="score-label">車外分數</div></div>
                    <div class="score-box"><div class="score-value">${durationDisplay}</div><div class="score-label">總耗時</div></div>
                </div>
                <div class="card-actions">
                    <button data-trip-id="${latestTrip.id}" class="btn btn-outline btn-print-dynamic"><i class="fa-solid fa-print"></i> 列印報表</button>
                    <a href="/trip_report?trip_id=${latestTrip.id}" class="btn btn-primary"><i class="fa-solid fa-magnifying-glass-chart"></i> 查看詳細報告</a>
                </div>
            `;
        } else if(latestTripReport) {
            latestTripReport.innerHTML = '<div class="card-header"><div><h3 class="card-title"><i class="fa-solid fa-flag-checkered"></i> 前次行程報告</h3></div></div><p style="text-align: center; padding: 2rem;">尚無任何行程記錄可供顯示。</p>';
        }

        // --- G. 初始化圖表 ---
        initTrendsChart(trendsData);
        initGauge(trendsData);
    }
    
    // 5. 初始化儀表圖 (包含評語邏輯)
    function initGauge(trendsData) {
        const gaugeNeedle = document.getElementById('trends-gauge-needle');
        const gaugeCenter = document.querySelector('.gauge-center');
        const gaugeText = document.getElementById('trends-gauge-text')?.querySelector('strong');
        const gaugeStatusText = document.getElementById('gauge-status-text');
        const gaugeComment = document.getElementById('gauge-comment'); // 選取評語元素
        
        if (!gaugeNeedle || !gaugeText || !gaugeCenter || !gaugeStatusText || !gaugeComment) return;

        let score = 0;
        if (trendsData && trendsData.length > 0) {
            score = Math.round(trendsData[trendsData.length - 1].average_score);
        }

        gaugeText.textContent = score;

        let scoreClass = '';
        let statusText = '';
        let commentText = ''; // 用於儲存評語

        if (score <= 80) {
            scoreClass = 'danger';
            statusText = '危險駕駛';
            commentText = '您的駕駛習慣存在較大風險，請立即改善。';
        } else if (score <= 90) {
            scoreClass = 'warning';
            statusText = '普通危險駕駛';
            commentText = '表現尚有改善空間，請多注意駕駛細節。';
        } else {
            scoreClass = 'excellent';
            statusText = '普通駕駛';
            commentText = '表現良好，請繼續保持安全的駕駛習慣。';
        }
        
        // 更新指針和中心圓點的顏色
        gaugeNeedle.classList.remove('danger', 'warning', 'excellent');
        gaugeCenter.classList.remove('danger', 'warning', 'excellent');
        gaugeNeedle.classList.add(scoreClass);
        gaugeCenter.classList.add(scoreClass);

        // 更新下方的狀態文字和顏色
        gaugeStatusText.textContent = statusText;
        gaugeStatusText.className = 'gauge-status ' + scoreClass;

        // 更新評語文字
        gaugeComment.textContent = commentText;

        const rotation = (score / 100) * 180;

        setTimeout(() => {
            gaugeNeedle.style.setProperty('--gauge-rotation', `${rotation}deg`);
        }, 100);
    }

    // 6. 初始化趨勢圖
    function initTrendsChart(trendsData) {
        const canvas = document.getElementById('trendsChart');
        if (!canvas) return;
        
        const labels = trendsData ? trendsData.map(item => item.month) : [];
        const scores = trendsData ? trendsData.map(item => item.average_score) : [];

        new Chart(canvas, { 
            type: 'line', 
            data: {
                labels: labels,
                datasets: [{
                    label: '安全分數',
                    data: scores,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            }, 
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } } 
        });
    }

    // 7. 頁面初始化主程序
    async function initializeDashboard() {
        try {
            const [profileRes, groupsRes, tripsRes, trendsRes] = await Promise.all([
                fetchWithAuth('/api/auth/profile/'),
                fetchWithAuth('/api/me/groups/'),
                fetchWithAuth('/api/trips/?ordering=-start_time&limit=5'),
                fetchWithAuth('/api/statistics/trends/')
            ]);
            if (!profileRes.ok || !groupsRes.ok || !tripsRes.ok || !trendsRes.ok) {
                throw new Error('一個或多個 API 請求失敗');
            }
            const [userData, groupData, tripData, trendsData] = await Promise.all([
                profileRes.json(),
                groupsRes.json(),
                tripsRes.json(),
                trendsRes.json()
            ]);
            updateUI(userData, groupData, tripData, trendsData);
        } catch (error) {
            console.error("載入儀表板資料失敗:", error.message);
        }
    }

    // 8. 綁定事件
    document.addEventListener('DOMContentLoaded', () => {
        initializeDashboard();

        document.body.addEventListener('click', function(event) {
            const printButton = event.target.closest('.btn-print-dynamic');
            if (printButton) {
                const tripId = printButton.dataset.tripId;
                handlePdfPreview(tripId);
            }
        });
    });

})();