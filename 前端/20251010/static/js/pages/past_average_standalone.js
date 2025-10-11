// 檔案路徑: static/js/pages/past_average_standalone.js (最終修正版)

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let trendsChart = null;

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) { window.location.href = '/login'; throw new Error('Not Authenticated'); }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        headers.append('Content-Type', 'application/json');
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.clear(); window.location.href = '/login'; throw new Error('Token Expired'); }
        return response;
    }

    async function fetchTrendsData(startDate, endDate) {
        const chartArea = document.querySelector('.chart-area');
        const gaugeArea = document.querySelector('.gauge-area');
        chartArea.innerHTML = '<p>載入數據中...</p>';
        if (gaugeArea) gaugeArea.style.opacity = 0.5;

        try {
            const response = await fetchWithAuth(`/api/statistics/trends/?start_date=${startDate}&end_date=${endDate}`);
            if (!response.ok) {
                throw new Error('無法獲取趨勢資料');
            }
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('獲取趨勢數據失敗:', error);
            chartArea.innerHTML = '<p style="color: red;">載入數據失敗。</p>';
        } finally {
            if (gaugeArea) gaugeArea.style.opacity = 1;
        }
    }
    
    function updateUI(trendsData) {
        renderTrendsChart(trendsData);
        updateGauge(trendsData);
    }

    // ▼▼▼【這是唯一且正確的 updateGauge 函式，帶有動畫邏輯】▼▼▼
    function updateGauge(trendsData) {
        const scoreElement = document.getElementById('gauge-score');
        const needleElement = document.getElementById('gauge-needle');
        const titleElement = document.getElementById('gauge-title');
        if (!scoreElement || !needleElement || !titleElement) return;

        let averageScore = 0;
        if (trendsData && trendsData.length > 0) {
            const totalScore = trendsData.reduce((sum, item) => sum + item.average_score, 0);
            averageScore = totalScore / trendsData.length;
        }
        
        const clampedScore = Math.round(Math.max(0, Math.min(100, averageScore)));
        
        scoreElement.textContent = clampedScore;
        titleElement.textContent = '選定區間平均';

        const rotation = (clampedScore / 100) * 180 - 90;

        // 使用 setTimeout 來確保動畫被觸發
        setTimeout(() => {
            needleElement.style.transform = `rotate(${rotation}deg)`;
        }, 100);
    }

    function renderTrendsChart(trendsData) {
        const chartArea = document.querySelector('.chart-area');
        chartArea.innerHTML = '<canvas id="trendsChart"></canvas>'; 
        const ctx = document.getElementById('trendsChart').getContext('2d');
        
        if (!trendsData || trendsData.length === 0) {
            chartArea.innerHTML = '<p>選定範圍內無資料可供顯示。</p>';
            return;
        }

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
    
    function initializePage() {
        const formatDate = (date) => date.toISOString().split('T')[0];
        const endDate = new Date();
        const startDate = new Date();
        startDate.setFullYear(endDate.getFullYear() - 1);
        const defaultStartDateStr = formatDate(startDate);
        const defaultEndDateStr = formatDate(endDate);

        flatpickr("#date-range-picker", {
            mode: "range",
            dateFormat: "Y-m-d",
            defaultDate: [defaultStartDateStr, defaultEndDateStr],
            onClose: function(selectedDates) {
                if (selectedDates.length === 2) {
                    const newStartDate = formatDate(selectedDates[0]);
                    const newEndDate = formatDate(selectedDates[1]);
                    fetchTrendsData(newStartDate, newEndDate);
                }
            }
        });

        fetchTrendsData(defaultStartDateStr, defaultEndDateStr);
    }

    initializePage();
});