// 檔案路徑: static/js/pages/all_reports.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
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
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    function getScoreClass(score) {
        if (score >= 90) return 'score-high';
        if (score >= 70) return 'score-medium';
        return 'score-low';
    }

    function renderReports(trips) {
        const grid = document.getElementById('reports-grid-container');
        if(!grid) return;
        grid.innerHTML = '';

        if (!trips || trips.length === 0) {
            grid.innerHTML = '<p>找不到任何過往行程記錄。</p>';
            return;
        }

        trips.forEach(trip => {
            const score = Math.round(trip.score || 0);
            const card = document.createElement('div');
            card.className = 'report-card';
            card.innerHTML = `
                <div class="report-header">
                    <div class="report-meta">
                        <p class="report-id">行程編號: <span>${trip.trip_number}</span></p>
                        <p class="report-date">${new Date(trip.start_time).toLocaleDateString()}</p>
                    </div>
                    <div class="report-score ${getScoreClass(score)}">${score}</div>
                </div>
                <div class="report-body">
                    <div class="report-name-wrapper">
                        <h3 class="report-name ${trip.name ? '' : 'placeholder'}">${trip.name || `未命名的行程 (${new Date(trip.start_time).toLocaleDateString()})`}</h3>
                        <i class="fa-solid fa-pencil edit-icon" title="編輯名稱"></i>
                    </div>
                </div>
                <a href="/trip_report?trip_id=${trip.id}" class="btn btn-details">查看詳細</a>
            `;
            grid.appendChild(card);
        });
    }

    async function initializePage() {
        try {
            const response = await fetchWithAuth(`/api/trips/`);
            if (!response.ok) {
                throw new Error('無法獲取行程列表');
            }
            const data = await response.json();
            renderReports(data.results || data);
        } catch (error) {
            console.error('載入過往行程失敗:', error);
            const grid = document.getElementById('reports-grid-container');
            if(grid) grid.innerHTML = '<p style="color: red;">載入資料失敗，請稍後再試。</p>';
        }
    }
    
    document.addEventListener('DOMContentLoaded', initializePage);
})();