// static/js/pages/dashboard.js

document.addEventListener('DOMContentLoaded', function () {

    // --- 功能：繪製「趨勢追蹤」折線圖 ---
    const ctx = document.getElementById('trendsChart');

    // 檢查圖表畫布是否存在，以及 Flask 是否傳來了有效的數據
    // (trendsDataFromServer 這個變數是在 dashboard.html 中被定義的)
    if (ctx && typeof trendsDataFromServer !== 'undefined' && trendsDataFromServer.length > 0) {
        
        // 【動態部分】從 trendsDataFromServer 動態生成圖表標籤和數據點
        const labels = trendsDataFromServer.map(item => item.month);
        const dataPoints = trendsDataFromServer.map(item => item.average_score);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '安全分數',
                    data: dataPoints,
                    fill: false,
                    borderColor: '#1a2a5f', // 使用主題藍色
                    backgroundColor: '#1a2a5f',
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    tension: 0.2 // 讓線條更平滑
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        suggestedMin: 40,
                        suggestedMax: 100,
                        grid: { color: '#e9ecef' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    } else if (ctx) {
        // 如果沒有數據，在圖表中央顯示一個提示文字
        const context = ctx.getContext('2d');
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillStyle = '#999';
        context.font = '16px "Noto Sans TC", sans-serif';
        context.fillText('暫無趨勢數據可供顯示', ctx.width / 2, ctx.height / 2);
    }
    
});