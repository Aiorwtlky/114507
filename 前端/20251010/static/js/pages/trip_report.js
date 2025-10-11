// 檔案路徑: static/js/pages/trip_report.js (最終整合版)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let tripId = null;

    // --- 核心 API 呼叫函式 ---
    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) { window.location.href = '/login'; throw new Error('Not Authenticated'); }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) { headers.append('Content-Type', 'application/json'); }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.clear(); window.location.href = '/login'; throw new Error('Token Expired'); }
        return response;
    }

    // --- 動態更新頁面 UI 的函式 ---
    function updateUI(tripData) {
        document.getElementById('tripTitle').textContent = tripData.name || `行程報告 #${tripData.trip_number}`;
        
        const startTime = new Date(tripData.start_time);
        const endTime = new Date(tripData.end_time);
        const durationMs = endTime - startTime;
        const hours = Math.floor(durationMs / 3600000);
        const minutes = Math.round((durationMs % 3600000) / 60000);
        document.getElementById('tripTimeInfo').textContent = 
            `${startTime.toLocaleString()} - ${endTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} · 總耗時 ${hours}h ${minutes}m`;

        document.getElementById('score-total').textContent = Math.round(tripData.score || 0);
        document.getElementById('score-in-car').textContent = Math.round(tripData.in_car_score || 0);
        document.getElementById('score-out-car').textContent = Math.round(tripData.out_car_score || 0);
        document.getElementById('score-mileage').textContent = `${tripData.total_mileage || 0} km`;

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
                        <div class="violation-time">${new Date(log.timestamp).toLocaleTimeString()}</div>
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

        document.getElementById('ai-suggestion-detail').innerHTML = `<p>${(tripData.ai_suggestion || '本次行程無 AI 建議。').replace(/\n/g, '<br>')}</p>`;

        const printButton = document.querySelector('.btn-print-report');
        if (printButton) {
            printButton.href = `/api/trips/${tripData.id}/report/`;
            printButton.target = '_blank';
            printButton.onclick = null;
        }
    }

    // --- 編輯標題 Modal 的邏輯 (整合您的版本) ---
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
                    // ▼▼▼【核心整合】執行真實的 API 請求來儲存標題 ▼▼▼
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

    // --- 頁面初始化 ---
    async function initializePage() {
        const urlParams = new URLSearchParams(window.location.search);
        tripId = urlParams.get('trip_id');

        if (!tripId) {
            document.querySelector('.trip-report-container').innerHTML = '<h1>錯誤：未指定行程 ID</h1>';
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/trips/${tripId}/`);
            if (!response.ok) {
                if (response.status === 404) throw new Error('找不到指定的行程。');
                if (response.status === 403) throw new Error('您沒有權限查看此行程報告。');
                throw new Error('無法載入行程資料。');
            }
            const tripData = await response.json();
            
            updateUI(tripData);
            setupTitleEditor(); // 在獲取到資料後，才設定編輯器

        } catch (error) {
            console.error('載入行程報告失敗:', error);
            document.querySelector('.trip-report-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
        }
    }

    // --- 通知功能的輔助函式 (來自您的版本) ---
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i><span>${message}</span>`;
        notification.style.cssText = `position: fixed; top: 20px; right: 20px; padding: 1rem 1.5rem; background: ${type === 'success' ? '#22c55e' : '#ef4444'}; color: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); display: flex; align-items: center; gap: 0.75rem; font-weight: 600; z-index: 10000; animation: slideInRight 0.3s ease-out;`;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    const style = document.createElement('style');
    style.textContent = `@keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } } @keyframes slideOutRight { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }`;
    document.head.appendChild(style);


    // 啟動頁面
    document.addEventListener('DOMContentLoaded', initializePage);

})();