// 檔案路徑: static/js/pages/past_average_standalone.js (完整重構版)

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let trendsChart = null; // 用來存放 Chart.js 實例，以便更新

    // --- 核心 API 呼叫函式 ---
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

    /**
     * 【新增】專門用來獲取趨勢數據的函式
     * @param {string} startDate - YYYY-MM-DD 格式的開始日期
     * @param {string} endDate - YYYY-MM-DD 格式的結束日期
     */
    async function fetchTrendsData(startDate, endDate) {
        const chartArea = document.querySelector('.chart-area');
        const gaugeArea = document.querySelector('.gauge-area');
        chartArea.innerHTML = '<p>載入數據中...</p>'; // 顯示載入提示
        gaugeArea.style.opacity = 0.5;

        try {
            const response = await fetchWithAuth(`/api/statistics/trends/?start_date=${startDate}&end_date=${endDate}`);
            if (!response.ok) {
                throw new Error('無法獲取趨勢資料');
            }
            const data = await response.json();
            updateUI(data); // 成功後更新畫面
        } catch (error) {
            console.error('獲取趨勢數據失敗:', error);
            chartArea.innerHTML = '<p style="color: red;">載入數據失敗。</p>';
        } finally {
            gaugeArea.style.opacity = 1;
        }
    }
    
    /**
     * 【重構】專門用來更新所有 UI 元件的函式
     * @param {Array} trendsData - 從 API 獲取的趨勢資料陣列
     */
    function updateUI(trendsData) {
        renderTrendsChart(trendsData);
        updateGauge(trendsData);
    }

    function updateGauge(trendsData) {
        const scoreElement = document.getElementById('gauge-score');
        const needleElement = document.getElementById('gauge-needle');
        const titleElement = document.getElementById('gauge-title');
        if (!scoreElement || !needleElement || !titleElement) return;

        // 計算選定區間的總平均分
        const totalScore = trendsData.reduce((sum, item) => sum + item.average_score, 0);
        const averageScore = trendsData.length > 0 ? totalScore / trendsData.length : 0;
        
        const clampedScore = Math.max(0, Math.min(100, averageScore));
        const rotation = (clampedScore / 100) * 180 - 90;

        scoreElement.textContent = Math.round(clampedScore);
        needleElement.style.transform = `rotate(${rotation}deg)`;
        titleElement.textContent = '選定區間平均'; // 更新標題
    }

    function renderTrendsChart(trendsData) {
        const chartArea = document.querySelector('.chart-area');
        // 先清空，再重新建立 canvas，確保圖表乾淨
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
    
    // --- 頁面初始化與事件綁定 ---
    function initializePage() {
        // 格式化日期為 YYYY-MM-DD
        const formatDate = (date) => date.toISOString().split('T')[0];

        // 1. 設定預設日期範圍：今天往前推一年
        const endDate = new Date();
        const startDate = new Date();
        startDate.setFullYear(endDate.getFullYear() - 1);
        
        const defaultStartDateStr = formatDate(startDate);
        const defaultEndDateStr = formatDate(endDate);

        // 2. 初始化 Flatpickr 日期選擇器
        flatpickr("#date-range-picker", {
            mode: "range",
            dateFormat: "Y-m-d",
            defaultDate: [defaultStartDateStr, defaultEndDateStr],
            // 當使用者選完日期並關閉選擇器時觸發
            onClose: function(selectedDates) {
                if (selectedDates.length === 2) {
                    const newStartDate = formatDate(selectedDates[0]);
                    const newEndDate = formatDate(selectedDates[1]);
                    // 使用新的日期範圍，重新獲取並渲染數據
                    fetchTrendsData(newStartDate, newEndDate);
                }
            }
        });

        // 3. 頁面初次載入時，使用預設日期範圍獲取數據
        fetchTrendsData(defaultStartDateStr, defaultEndDateStr);
    }

    initializePage();
});