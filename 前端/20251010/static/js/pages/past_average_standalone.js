// 檔案路徑: static/js/pages/past_average_standalone.js

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let trendsChart = null;

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
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

    function updateGauge(score) {
        const scoreElement = document.getElementById('gauge-score');
        const needleElement = document.getElementById('gauge-needle');
        if(!scoreElement || !needleElement) return;

        const clampedScore = Math.max(0, Math.min(100, score));
        const rotation = (clampedScore / 100) * 180 - 90;

        scoreElement.textContent = Math.round(clampedScore);
        needleElement.style.transform = `rotate(${rotation}deg)`;
    }

    function renderTrendsChart(trendsData) {
        const ctx = document.getElementById('trendsChart')?.getContext('2d');
        if (!ctx) return;

        const labels = trendsData.map(item => item.month);
        const scores = trendsData.map(item => item.average_score);
        
        if (trendsChart) {
            trendsChart.destroy();
        }

        trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '每月駕駛分數平均',
                    data: scores,
                    borderColor: 'var(--primary-color)',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
    
    async function initializePage() {
        try {
            const response = await fetchWithAuth('/api/statistics/trends/');
            if (!response.ok) throw new Error('無法獲取趨勢資料');

            const trendsData = await response.json();
            
            renderTrendsChart(trendsData);

            const latestScore = trendsData.length > 0 ? trendsData[trendsData.length - 1].average_score : 0;
            updateGauge(latestScore);

        } catch (error) {
            console.error('載入數據分析頁面失敗:', error);
        }
    }

    flatpickr("#date-range-picker", {
        mode: "range",
        dateFormat: "Y-m-d",
    });

    initializePage();
});