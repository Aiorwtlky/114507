/* --- 全新、整理過的 dashboard.js --- */

// --- 主邏輯：等待整個網頁文件 (DOM) 載入完成後，再執行裡面的所有程式碼 ---
document.addEventListener('DOMContentLoaded', function () {

    console.log("dashboard.js 執行了！所有功能準備中...");

    // --- 功能一：設定「查看更多」按鈕 ---
    // (這段是您原本的程式碼，我幫您保留並整理好)
    function setupShowMoreToggle(toggleSelector, listSelector, initialVisibleCount) {
        const toggleButton = document.querySelector(toggleSelector);
        if (!toggleButton) return;

        const listItems = document.querySelectorAll(`${listSelector} li`);
        const hiddenItems = Array.from(listItems).slice(initialVisibleCount);

        hiddenItems.forEach(item => item.style.display = 'none');

        if (hiddenItems.length === 0) {
            toggleButton.style.display = 'none';
            return;
        }

        let isExpanded = false;
        toggleButton.addEventListener('click', function () {
            isExpanded = !isExpanded;
            hiddenItems.forEach(item => {
                item.style.display = isExpanded ? 'flex' : 'none';
            });
            // 注意：這裡假設您的按鈕本身就是一個 <button> 或 <a>
            // 如果按鈕結構複雜，可能需要調整 this.querySelector
            this.textContent = isExpanded ? '查看較少' : '查看更多';
        });
    }

    // 呼叫「查看更多」功能
    // 注意：您 HTML 中的 class name 要與這裡對應，例如 .score-violation-more-toggle
    // 我看了一下您的 HTML，裡面並沒有這些 class，所以這段功能可能暫時不會生效。
    // 但我先幫您保留，未來您可以加上對應的 class 來啟用它。
    setupShowMoreToggle('.score-violation-more-toggle', '.score-list-items', 3);
    setupShowMoreToggle('.group-more-toggle', '.group-list-items', 4);
    setupShowMoreToggle('.report-more-toggle', '.report-list-items', 3);


    // --- 功能二：繪製「趨勢追蹤」折線圖 ---

    // 1. 找到我們的 canvas 畫布
    const ctx = document.getElementById('trendsChart');

    // 檢查畫布是否存在
    if (ctx) {
        // 2. 準備圖表數據
        const labels = ['2025 第1季', '2025 第2季', '2025 第3季', '2025 第4季'];
        const dataPoints = [95, 98.1, 49.8, 96];

        // 3. 建立並設定我們的折線圖
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '安全分數',
                    data: dataPoints,
                    fill: false,
                    borderColor: '#28a745',
                    backgroundColor: '#28a745',
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    tension: 0.1
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
    } // if (ctx) 結束

}); // DOMContentLoaded 結束

