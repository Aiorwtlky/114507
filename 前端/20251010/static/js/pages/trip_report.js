// 檔案路徑: static/js/pages/trip_report.js (最終完整、未省略版)

(function() {
    'use strict';

    // 您的後端 API 基礎網址
    const API_BASE_URL = 'http://127.0.0.1:8000';
    // 用於儲存當前頁面的行程 ID
    let tripId = null;

    /**
     * 帶有認證 Token 的通用 API 請求函式
     * @param {string} endpoint - API 的端點路徑
     * @param {object} options - fetch 的設定選項
     * @returns {Promise<Response>}
     */
    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            alert('您尚未登入或登入已逾時，將跳轉至登入頁面。');
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
            alert('您的登入已過期，請重新登入。');
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    /**
     * 安全地格式化數值（分數、里程），如果無效則回傳佔位符
     * @param {number|null} value - 原始數值
     * @param {number} decimals - 要保留的小數點位數
     * @returns {string} 格式化後的字串或 '--'
     */
    function formatValue(value, decimals = 2) {
        const numericValue = parseFloat(value);
        if (typeof numericValue === 'number' && !isNaN(numericValue)) {
            return numericValue.toFixed(decimals);
        }
        return '--'; // 如果分數是 null 或無效，回傳佔位符
    }

    /**
     * 根據從 API 獲取的行程資料，更新整個頁面的 UI
     * @param {object} tripData - 包含行程所有詳情的物件
     */
    function updateUI(tripData) {
        // 更新頁面主標題和時間資訊
        document.getElementById('tripTitle').textContent = tripData.name || `行程報告 #${tripData.trip_number}`;
        
        const startTime = new Date(tripData.start_time);
        const endTime = tripData.end_time ? new Date(tripData.end_time) : null;
        let durationDisplay = '進行中';

        if (endTime) {
            const durationMs = endTime - startTime;
            const hours = Math.floor(durationMs / 3600000);
            const minutes = Math.round((durationMs % 3600000) / 60000);
            durationDisplay = `總耗時 ${hours}h ${minutes}m`;
        }

        document.getElementById('tripTimeInfo').innerHTML = 
            `<i class="fa-solid fa-calendar"></i> ${startTime.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })} - ${endTime ? endTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : ''} · ${durationDisplay}`;

        // 使用安全的格式化函式更新分數總覽區塊
        document.getElementById('score-total').textContent = formatValue(tripData.score, 2);
        document.getElementById('score-in-car').textContent = formatValue(tripData.in_car_score, 2);
        document.getElementById('score-out-car').textContent = formatValue(tripData.out_car_score, 2);
        document.getElementById('score-mileage').textContent = `${formatValue(tripData.total_mileage, 1)} km`; // 里程保留一位小數

        // 動態生成違規項目列表
        const inCarList = document.getElementById('in-car-violations-list');
        const outCarList = document.getElementById('out-car-violations-list');
        inCarList.innerHTML = '';
        outCarList.innerHTML = '';

        if (tripData.aivisionlog_set && tripData.aivisionlog_set.length > 0) {
            tripData.aivisionlog_set.forEach(log => {
                const eventCategory = log.event.event_number[0].toUpperCase();
                const item = document.createElement('div');
                item.className = 'violation-item';
                item.innerHTML = `
                    <div class="violation-header">
                        <div class="violation-time">${new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}</div>
                        <div class="violation-score">-${log.event.deduction_points}</div>
                    </div>
                    <div class="violation-desc">${log.event.description} (${log.event_details})</div>
                `;
                if (eventCategory === 'A') {
                    inCarList.appendChild(item);
                } else if (eventCategory === 'B') {
                    outCarList.appendChild(item);
                }
            });
        }
        
        if (inCarList.innerHTML === '') inCarList.innerHTML = '<p class="no-violations">無車內違規項目</p>';
        if (outCarList.innerHTML === '') outCarList.innerHTML = '<p class="no-violations">無車外違規項目</p>';

        // 更新 AI 建議
        document.getElementById('ai-suggestion-detail').innerHTML = `<p>${(tripData.ai_suggestion || '本次行程無 AI 建議。').replace(/\n/g, '<br>')}</p>`;

        // 為列印按鈕設定 data-trip-id 屬性，方便後續的事件監聽
        const printButton = document.querySelector('.btn-print-report');
        if (printButton) {
            printButton.setAttribute('data-trip-id', tripData.id);
        }
    }

    /**
     * 設定編輯行程標題的 Modal 彈窗及其所有事件監聽
     */
    function setupTitleEditor() {
        const modal = document.getElementById('editTitleModal');
        const modalOverlay = document.getElementById('modalOverlay');
        const editTitleBtn = document.getElementById('editTitleBtn');
        const closeModalBtn = document.getElementById('closeModalBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const saveTitleBtn = document.getElementById('saveTitleBtn');
        const titleInput = document.getElementById('titleInput');
        const tripTitle = document.getElementById('tripTitle');

        const openModal = () => {
            titleInput.value = tripTitle.textContent;
            modal.style.display = 'block';
            setTimeout(() => { titleInput.focus(); titleInput.select(); }, 100);
        };
        const closeModal = () => modal.style.display = 'none';

        const saveTitle = async () => {
            const newTitle = titleInput.value.trim();
            if (newTitle && newTitle !== tripTitle.textContent) {
                saveTitleBtn.textContent = '儲存中...';
                saveTitleBtn.disabled = true;
                try {
                    const response = await fetchWithAuth(`/api/trips/${tripId}/`, {
                        method: 'PATCH',
                        body: JSON.stringify({ name: newTitle })
                    });
                    if (response.ok) {
                        tripTitle.textContent = newTitle;
                        showNotification('行程名稱已更新', 'success');
                        closeModal();
                    } else {
                        throw new Error('儲存失敗');
                    }
                } catch (error) {
                    console.error('儲存標題失敗:', error);
                    showNotification('儲存失敗，請稍後再試', 'error');
                } finally {
                    saveTitleBtn.textContent = '儲存';
                    saveTitleBtn.disabled = false;
                }
            } else if (!newTitle) {
                showNotification('請輸入行程名稱', 'error');
            } else {
                closeModal(); // 如果標題沒變，直接關閉
            }
        };

        editTitleBtn.addEventListener('click', openModal);
        closeModalBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        modalOverlay.addEventListener('click', closeModal);
        saveTitleBtn.addEventListener('click', saveTitle);
        titleInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') saveTitle(); });
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && modal.style.display === 'block') closeModal(); });
    }

    /**
     * 頁面初始化主函式：獲取行程 ID 並發起 API 請求
     */
    async function initializePage() {
        const urlParams = new URLSearchParams(window.location.search);
        tripId = urlParams.get('trip_id');

        if (!tripId) {
            document.querySelector('.trip-report-container').innerHTML = '<h1>錯誤：未指定行程 ID</h1><p>請確認網址是否正確。</p>';
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/trips/${tripId}/`);
            if (!response.ok) {
                if (response.status === 404) throw new Error('找不到指定的行程。');
                if (response.status === 403) throw new Error('您沒有權限查看此行程報告。');
                throw new Error('無法載入行程資料，請稍後再試。');
            }
            const tripData = await response.json();
            
            updateUI(tripData);
            setupTitleEditor(); // 在獲取到資料後，才設定編輯器

        } catch (error) {
            console.error('載入行程報告失敗:', error);
            document.querySelector('.trip-report-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
        }
    }

    /**
     * 顯示一個短暫的通知訊息
     * @param {string} message - 要顯示的訊息
     * @param {string} type - 通知類型 ('success' 或 'error')
     */
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i><span>${message}</span>`;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out forwards';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // 將通知動畫的 CSS 動態注入到 <head> 中，避免需要修改 CSS 檔案
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed; top: 20px; right: 20px; padding: 1rem 1.5rem; 
            background: #22c55e; color: white; border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); display: flex; 
            align-items: center; gap: 0.75rem; font-weight: 600; 
            z-index: 10000; animation: slideInRight 0.3s ease-out forwards;
        }
        .notification-error { background: #ef4444; }
        @keyframes slideInRight { from { transform: translateX(110%); } to { transform: translateX(0); } }
        @keyframes slideOutRight { from { transform: translateX(0); } to { transform: translateX(110%); } }
    `;
    document.head.appendChild(style);


    // 當 DOM 載入完成後，啟動頁面初始化
    document.addEventListener('DOMContentLoaded', () => {
        initializePage();

        // 使用事件代理來處理「列印報表」按鈕的點擊事件
        document.body.addEventListener('click', async function(event) {
            const printButton = event.target.closest('.btn-print-report');
            if (printButton) {
                const currentTripId = printButton.getAttribute('data-trip-id');
                if (currentTripId) {
                    printButton.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>處理中...</span>`;
                    printButton.disabled = true;
                    try {
                        const response = await fetchWithAuth(`/api/trips/${currentTripId}/report/`, { responseType: 'blob' });
                        if (!response.ok) { throw new Error('PDF 生成失敗'); }
                        const pdfBlob = await response.blob();
                        const pdfUrl = URL.createObjectURL(pdfBlob);
                        window.open(pdfUrl, '_blank');
                    } catch (error) {
                        console.error('列印報表失敗:', error);
                        showNotification('無法生成報表', 'error');
                    } finally {
                        printButton.innerHTML = `<i class="fa-solid fa-print"></i> <span>列印報表</span>`;
                        printButton.disabled = false;
                    }
                }
            }
        });
    });

})();