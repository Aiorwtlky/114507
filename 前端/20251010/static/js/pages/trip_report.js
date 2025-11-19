// 檔案路徑: static/js/pages/trip_report.js (最終時間修正版)

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let tripId = null;

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) { window.location.href = '/login'; throw new Error('Not Authenticated'); }
        const headers = new Headers(options.headers || {});
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) { headers.append('Content-Type', 'application/json'); }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.clear(); window.location.href = '/login'; throw new Error('Token Expired'); }
        return response;
    }

    function formatValue(value, decimals = 2) {
        const numericValue = parseFloat(value);
        if (typeof numericValue === 'number' && !isNaN(numericValue)) {
            return numericValue.toFixed(decimals);
        }
        return '--';
    }

    function updateUI(tripData) {
        document.getElementById('tripTitle').textContent = tripData.name || `行程報告 #${tripData.trip_number}`;
        
        const startTime = new Date(tripData.start_time);
        const endTime = tripData.end_time ? new Date(tripData.end_time) : null;
        let durationDisplay = '進行中';

        // 計算總行駛時間
        if (endTime) {
            const durationMs = endTime - startTime;
            const totalMinutes = Math.floor(durationMs / 60000);
            const hours = Math.floor(totalMinutes / 60);
            const minutes = totalMinutes % 60;
            durationDisplay = `${hours}h ${minutes}m`;
        }

        // 更新頂部標題列的時間資訊
        document.getElementById('tripTimeInfo').innerHTML = 
            `<i class="fa-solid fa-calendar"></i> ${startTime.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })} - ${endTime ? endTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : ''} · 總耗時 ${durationDisplay}`;

        // 更新分數總覽區塊
        document.getElementById('score-total').textContent = formatValue(tripData.score, 2);
        document.getElementById('score-in-car').textContent = formatValue(tripData.in_car_score, 2);
        document.getElementById('score-out-car').textContent = formatValue(tripData.out_car_score, 2);
        
        // ▼▼▼【核心修改】將計算出的行駛時間填入對應的元素中 ▼▼▼
        document.getElementById('trip-duration').textContent = durationDisplay;

        // 更新違規項目列表
        const inCarList = document.getElementById('in-car-violations-list');
        const outCarList = document.getElementById('out-car-violations-list');
        inCarList.innerHTML = '';
        outCarList.innerHTML = '';
        const inCarEvents = (tripData.aivisionlog_set || []).filter(log => log.event.event_number.startsWith('A'));
        const outCarEvents = (tripData.aivisionlog_set || []).filter(log => log.event.event_number.startsWith('B'));

        if (inCarEvents.length > 0) {
            inCarEvents.forEach(log => {
                inCarList.innerHTML += `<div class="violation-item"><div class="violation-header"><div class="violation-time">${new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}</div><div class="violation-score">-${log.event.deduction_points}</div></div><div class="violation-desc">${log.event.description} (${log.event_details})</div></div>`;
            });
        } else { inCarList.innerHTML = '<p class="no-violations">無車內違規項目</p>'; }

        if (outCarEvents.length > 0) {
            outCarEvents.forEach(log => {
                outCarList.innerHTML += `<div class="violation-item"><div class="violation-header"><div class="violation-time">${new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}</div><div class="violation-score">-${log.event.deduction_points}</div></div><div class="violation-desc">${log.event.description} (${log.event_details})</div></div>`;
            });
        } else { outCarList.innerHTML = '<p class="no-violations">無車外違規項目</p>'; }
        
        // 更新 AI 建議
        document.getElementById('ai-suggestion-detail').innerHTML = `<p>${(tripData.ai_suggestion || '本次行程無 AI 建議。').replace(/\n/g, '<br>')}</p>`;

        // 設定列印按鈕
        const printButton = document.querySelector('.btn-print-report');
        if (printButton) { printButton.setAttribute('data-trip-id', tripData.id); }
    }

    function setupTitleEditor() {
        const modal = document.getElementById('editTitleModal');
        const modalOverlay = document.getElementById('modalOverlay');
        const editTitleBtn = document.getElementById('editTitleBtn');
        const closeModalBtn = document.getElementById('closeModalBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const saveTitleBtn = document.getElementById('saveTitleBtn');
        const titleInput = document.getElementById('titleInput');
        const tripTitle = document.getElementById('tripTitle');
        const openModal = () => { titleInput.value = tripTitle.textContent; modal.style.display = 'block'; setTimeout(() => { titleInput.focus(); titleInput.select(); }, 100); };
        const closeModal = () => modal.style.display = 'none';
        const saveTitle = async () => {
            const newTitle = titleInput.value.trim();
            if (newTitle && newTitle !== tripTitle.textContent) {
                saveTitleBtn.textContent = '儲存中...'; saveTitleBtn.disabled = true;
                try {
                    const response = await fetchWithAuth(`/api/trips/${tripId}/`, { method: 'PATCH', body: JSON.stringify({ name: newTitle }) });
                    if (response.ok) { tripTitle.textContent = newTitle; showNotification('行程名稱已更新', 'success'); closeModal(); } 
                    else { throw new Error('儲存失敗'); }
                } catch (error) { console.error('儲存標題失敗:', error); showNotification('儲存失敗，請稍後再試', 'error');
                } finally { saveTitleBtn.textContent = '儲存'; saveTitleBtn.disabled = false; }
            } else if (!newTitle) { showNotification('請輸入行程名稱', 'error'); } 
            else { closeModal(); }
        };
        editTitleBtn.addEventListener('click', openModal);
        closeModalBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        modalOverlay.addEventListener('click', closeModal);
        saveTitleBtn.addEventListener('click', saveTitle);
        titleInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') saveTitle(); });
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && modal.style.display === 'block') closeModal(); });
    }

    async function initializePage() {
        const urlParams = new URLSearchParams(window.location.search);
        tripId = urlParams.get('trip_id');
        if (!tripId) { document.querySelector('.trip-report-container').innerHTML = '<h1>錯誤：未指定行程 ID</h1>'; return; }
        try {
            const response = await fetchWithAuth(`/api/trips/${tripId}/`);
            if (!response.ok) {
                if (response.status === 404) throw new Error('找不到指定的行程。');
                if (response.status === 403) throw new Error('您沒有權限查看此行程報告。');
                throw new Error('無法載入行程資料。');
            }
            const tripData = await response.json();
            updateUI(tripData);
            setupTitleEditor();
        } catch (error) {
            console.error('載入行程報告失敗:', error);
            document.querySelector('.trip-report-container').innerHTML = `<h1>載入失敗</h1><p>${error.message}</p>`;
        }
    }

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
    const style = document.createElement('style');
    style.textContent = `.notification { position: fixed; top: 20px; right: 20px; padding: 1rem 1.5rem; background: #22c55e; color: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); display: flex; align-items: center; gap: 0.75rem; font-weight: 600; z-index: 10000; animation: slideInRight 0.3s ease-out forwards; } .notification-error { background: #ef4444; } @keyframes slideInRight { from { transform: translateX(110%); } to { transform: translateX(0); } } @keyframes slideOutRight { from { transform: translateX(0); } to { transform: translateX(110%); } }`;
    document.head.appendChild(style);

    document.addEventListener('DOMContentLoaded', () => {
        initializePage();
        document.body.addEventListener('click', async function(event) {
            const printButton = event.target.closest('.btn-print-dynamic');
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
                    } catch (error) { console.error('列印報表失敗:', error); showNotification('無法生成報表', 'error');
                    } finally { printButton.innerHTML = `<i class="fa-solid fa-print"></i> <span>列印報表</span>`; printButton.disabled = false; }
                }
            }
        });
    });
})();