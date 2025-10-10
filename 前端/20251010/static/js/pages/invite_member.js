// 檔案路徑: static/js/pages/invite_member.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let groupId = null; // 在全域儲存從 URL 讀取到的群組ID

    /**
     * 執行一個帶有認證標頭的 fetch 請求
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
     * 處理建立新邀請的表單提交
     */
    async function handleCreateInvite(e) {
        e.preventDefault();
        if (!groupId) {
            showNotification('錯誤：未指定群組', 'error');
            return;
        }

        const submitButton = e.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 產生中...`;

        const inviteName = document.getElementById('inviteName').value;
        const inviteExpiry = document.getElementById('inviteExpiry').value;

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/invitations/create/`, {
                method: 'POST',
                body: JSON.stringify({
                    name: inviteName,
                    expires_at: inviteExpiry // 將日期時間字串直接傳給後端
                })
            });

            if (response.ok) {
                const newInvite = await response.json();
                document.getElementById('generatedCode').value = newInvite.code;
                document.getElementById('inviteResult').style.display = 'block';
                showNotification('邀請碼建立成功！', 'success');
                loadAndRenderInvites(); // 成功後重新載入邀請碼列表
                e.target.reset();
                // 手動重設日期選擇器的預設值
                flatpickr("#inviteExpiry").setDate(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000));
            } else {
                const errorData = await response.json();
                const errorMsg = errorData.name || errorData.expires_at || '請檢查欄位';
                showNotification(`建立失敗: ${errorMsg}`, 'error');
            }
        } catch (error) {
            console.error('建立邀請時發生錯誤:', error);
            showNotification('建立失敗，請檢查網路連線', 'error');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> 產生邀請碼`;
        }
    }

    /**
     * 處理撤銷 (刪除) 邀請碼
     */
    async function handleRevokeInvite(inviteId, code) {
        if (confirm(`確定要撤銷邀請碼 ${code} 嗎？此邀請碼將立即失效。`)) {
            try {
                const response = await fetchWithAuth(`/api/invitations/${inviteId}/`, {
                    method: 'DELETE'
                });
                if (response.ok) { // HTTP 204 No Content
                    showNotification('邀請碼已撤銷', 'success');
                    loadAndRenderInvites(); // 成功後重新載入列表
                } else {
                    showNotification('撤銷失敗，您可能沒有權限', 'error');
                }
            } catch (error) {
                console.error('撤銷邀請時發生錯誤:', error);
                showNotification('操作失敗，請檢查網路連線', 'error');
            }
        }
    }

    /**
     * 將從 API 獲取的邀請碼列表渲染到表格中
     */
    function renderInviteList(invites) {
        const tableBody = document.getElementById('inviteListBody');
        const countBadge = document.getElementById('inviteCount');
        tableBody.innerHTML = '';
        
        const validInvites = invites.filter(inv => !inv.is_used && new Date(inv.expires_at) > new Date());
        countBadge.textContent = validInvites.length;

        if (invites.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">尚無任何邀請碼記錄。</td></tr>';
            return;
        }

        invites.forEach(inv => {
            const isExpired = new Date(inv.expires_at) < new Date();
            const statusClass = inv.is_used ? 'danger' : (isExpired ? 'warning' : 'excellent');
            const statusText = inv.is_used ? '已使用' : (isExpired ? '已過期' : '有效');

            tableBody.innerHTML += `
                <tr>
                    <td><div class="name-cell"><i class="fa-solid fa-tag"></i><span>${inv.name}</span></div></td>
                    <td><div class="code-cell"><code>${inv.code}</code><button class="btn-action btn-copy-inline" data-code="${inv.code}" title="複製"><i class="fa-solid fa-copy"></i></button></div></td>
                    <td><span class="score-badge ${statusClass}">${statusText}</span></td>
                    <td><i class="fa-solid fa-times-circle icon-no"></i></td>
                    <td>${new Date(inv.created_at).toLocaleString()}</td>
                    <td>${new Date(inv.expires_at).toLocaleString()}</td>
                    <td class="actions-col">
                        <button class="btn-action danger" onclick="App.revokeInvite(${inv.id}, '${inv.code}')" ${inv.is_used || isExpired ? 'disabled' : ''} title="撤銷"><i class="fa-solid fa-ban"></i></button>
                    </td>
                </tr>
            `;
        });

        bindCopyButtons();
    }

    /**
     * 從 API 載入邀請碼列表並渲染
     */
    async function loadAndRenderInvites() {
        if (!groupId) return;
        try {
            const res = await fetchWithAuth(`/api/groups/${groupId}/invitations/`);
            if (res.ok) {
                const invites = await res.json();
                renderInviteList(invites.results || invites);
            }
        } catch (error) {
            console.error('載入邀請碼列表失敗:', error);
            document.getElementById('inviteListBody').innerHTML = '<tr><td colspan="7" style="text-align: center; color: red; padding: 2rem;">邀請碼列表載入失敗</td></tr>';
        }
    }

    /**
     * 頁面載入後執行的主要函式
     */
    async function initializePage() {
        const urlParams = new URLSearchParams(window.location.search);
        groupId = urlParams.get('group_id');
        if (!groupId) {
            document.getElementById('group-name').textContent = '錯誤：未指定群組';
            document.querySelector('button[type="submit"]').disabled = true;
            return;
        }

        try {
            const groupRes = await fetchWithAuth(`/api/groups/${groupId}/`);
            if (groupRes.ok) {
                const group = await groupRes.json();
                document.getElementById('group-name').textContent = group.name;
            }
            // 頁面載入時，也一併載入邀請碼列表
            await loadAndRenderInvites();
        } catch (error) {
            console.error('頁面初始化失敗', error);
        }
    }

    // --- 以下是你原本的輔助函式，我們把它們整合進來 ---

    function bindCopyButtons() {
        const copyCodeBtn = document.getElementById('copyCodeBtn');
        if (copyCodeBtn) {
            copyCodeBtn.addEventListener('click', function() {
                const codeInput = document.getElementById('generatedCode');
                copyToClipboard(codeInput.value, '邀請碼已複製');
            });
        }
        document.querySelectorAll('.btn-copy-inline').forEach(btn => {
            btn.addEventListener('click', function() {
                const code = this.getAttribute('data-code');
                copyToClipboard(code, '邀請碼已複製');
            });
        });
    }

    function copyToClipboard(text, successMessage) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification(successMessage || '已複製到剪貼簿', 'success');
            }).catch(err => fallbackCopy(text, successMessage));
        } else {
            fallbackCopy(text, successMessage);
        }
    }
    
    function fallbackCopy(text, successMessage) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showNotification(successMessage || '已複製到剪貼簿', 'success');
        } catch (err) {
            showNotification('複製失敗，請手動複製', 'error');
        }
        document.body.removeChild(textarea);
    }

    function showNotification(message, type = 'success') {
        const oldNotification = document.querySelector('.notification');
        if (oldNotification) oldNotification.remove();
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


    // --- 頁面初始化 ---
    document.addEventListener('DOMContentLoaded', function() {
        initializePage();
        
        flatpickr("#inviteExpiry", {
            enableTime: true, dateFormat: "Y-m-d H:i",
            time_24hr: true, minDate: "today",
            locale: "zh_tw",
            defaultDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 預設30天後
        });
        
        const form = document.getElementById('createInviteForm');
        if (form) form.addEventListener('submit', handleCreateInvite);
        
        // 將需要被 HTML onclick 呼叫的函式，掛載到一個全域物件上
        window.App = { 
            revokeInvite: handleRevokeInvite 
        };

        bindCopyButtons(); // 初始綁定
    });

})();