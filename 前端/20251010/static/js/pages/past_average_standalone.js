// 檔案路徑: static/js/pages/past_average_standalone.js

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // 1. 移除 API_BASE_URL 和 fetchWithAuth
    let trendsChart = null;

    async function fetchTrendsData(startDate, endDate) {
        const chartArea = document.querySelector('.chart-area');
        const gaugeArea = document.querySelector('.gauge-area');
        if (chartArea) chartArea.innerHTML = '<p>載入數據中...</p>';
        if (gaugeArea) gaugeArea.style.opacity = 0.5;

        try {
            // 直接呼叫全域 fetchWithAuth
            const response = await fetchWithAuth(`/api/statistics/trends/?start_date=${startDate}&end_date=${endDate}`);
            if (!response.ok) { throw new Error('無法獲取趨勢資料'); }
            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error('獲取趨勢數據失敗:', error);
            if (chartArea) chartArea.innerHTML = '<p style="color: red;">載入數據失敗。</p>';
        } finally {
            if (gaugeArea) gaugeArea.style.opacity = 1;
        }
    }
    
    function updateUI(trendsData) {
        renderTrendsChart(trendsData);
        updateGauge(trendsData);
    }

    function updateGauge(trendsData) {
        const scoreElement = document.getElementById('gauge-score');
        const needleElement = document.getElementById('gauge-needle');
        const centerCircleElement = document.getElementById('gauge-center-circle');
        const titleElement = document.getElementById('gauge-title');
        const statusTextElement = document.getElementById('gauge-status-text');
        const commentTextElement = document.getElementById('gauge-comment');
        
        if (!scoreElement || !needleElement) return;

        let averageScore = 0;
        if (trendsData && trendsData.length > 0) {
            const totalScore = trendsData.reduce((sum, item) => sum + item.average_score, 0);
            averageScore = totalScore / trendsData.length;
        }
        
        const clampedScore = Math.round(Math.max(0, Math.min(100, averageScore)));
        
        let scoreClass = '';
        let statusText = '';
        let commentText = '';

        if (clampedScore <= 80) {
            scoreClass = 'danger';
            statusText = '危險駕駛';
            commentText = '您的駕駛習慣存在較大風險，請立即改善。';
        } else if (clampedScore <= 90) {
            scoreClass = 'warning';
            statusText = '普通危險駕駛';
            commentText = '表現尚有改善空間，請多注意駕駛細節。';
        } else {
            scoreClass = 'excellent';
            statusText = '普通駕駛';
            commentText = '表現良好，請繼續保持安全的駕駛習慣。';
        }
        
        scoreElement.textContent = clampedScore;
        if(titleElement) titleElement.textContent = '選定區間平均';
        if(statusTextElement) statusTextElement.textContent = statusText;
        if(commentTextElement) commentTextElement.textContent = commentText;

        [needleElement, centerCircleElement, statusTextElement].forEach(el => {
            if(el) {
                el.classList.remove('danger', 'warning', 'excellent');
                el.classList.add(scoreClass);
            }
        });
        
        const rotation = (clampedScore / 100) * 180 - 90;
        setTimeout(() => {
            needleElement.style.transform = `rotate(${rotation}deg)`;
        }, 100);
    }

    function renderTrendsChart(trendsData) {
        const chartArea = document.querySelector('.chart-area');
        if (!chartArea) return;
        
        chartArea.innerHTML = '<canvas id="trendsChart"></canvas>'; 
        const ctx = document.getElementById('trendsChart').getContext('2d');
        
        if (!trendsData || trendsData.length === 0) {
            chartArea.innerHTML = '<p>選定範圍內無資料可供顯示。</p>';
            return;
        }

        const labels = trendsData.map(item => item.month);
        const scores = trendsData.map(item => item.average_score);
        
        if (trendsChart) trendsChart.destroy();

        trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '每月駕駛分數平均',
                    data: scores,
                    borderColor: '#4f46e5', // 使用具體顏色而非 var，避免 CSS 變數未定義
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
    
    function initializePage() {
        // 如果沒有 flatpickr，簡單的防呆
        if (typeof flatpickr === 'undefined') {
            console.warn('Flatpickr library not found');
            const now = new Date();
            const lastYear = new Date();
            lastYear.setFullYear(now.getFullYear() - 1);
            fetchTrendsData(lastYear.toISOString().split('T')[0], now.toISOString().split('T')[0]);
            return;
        }

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
                    fetchTrendsData(formatDate(selectedDates[0]), formatDate(selectedDates[1]));
                }
            }
        });

        fetchTrendsData(defaultStartDateStr, defaultEndDateStr);
    }

    initializePage();
});