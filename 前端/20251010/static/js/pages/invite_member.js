// 邀請管理頁面功能

// 初始化日期選擇器
document.addEventListener('DOMContentLoaded', function() {
    // 初始化 Flatpickr 日期時間選擇器
    flatpickr("#inviteExpiry", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        time_24hr: true,
        minDate: "today",
        locale: "zh_tw",
        defaultDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 預設30天後
    });

    // 綁定表單提交事件
    const form = document.getElementById('createInviteForm');
    if (form) {
        form.addEventListener('submit', handleCreateInvite);
    }

    // 綁定複製按鈕
    bindCopyButtons();
});

// 處理建立邀請
function handleCreateInvite(e) {
    e.preventDefault();

    const inviteName = document.getElementById('inviteName').value;
    const inviteExpiry = document.getElementById('inviteExpiry').value;
    const requireApproval = document.getElementById('requireApproval').checked;

    if (!inviteName || !inviteExpiry) {
        showNotification('請填寫完整資訊', 'error');
        return;
    }

    // 產生邀請碼
    const inviteCode = generateInviteCode();
    const inviteUrl = `${window.location.origin}/join?code=${inviteCode}`;

    // 顯示結果
    document.getElementById('generatedCode').value = inviteCode;
    document.getElementById('generatedUrl').value = inviteUrl;
    document.getElementById('inviteResult').style.display = 'block';

    // 模擬 API 請求
    // 實際使用時應該發送到後端
    console.log('建立邀請:', {
        name: inviteName,
        code: inviteCode,
        expiry: inviteExpiry,
        requireApproval: requireApproval
    });

    // 顯示成功通知
    showNotification('邀請碼建立成功！', 'success');

    // 可選：重置表單
    // form.reset();
}

// 產生隨機邀請碼
function generateInviteCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    
    for (let i = 0; i < 4; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    code += '-';
    
    for (let i = 0; i < 4; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    return code;
}

// 綁定所有複製按鈕
function bindCopyButtons() {
    // 綁定產生結果的複製按鈕
    const copyCodeBtn = document.getElementById('copyCodeBtn');
    if (copyCodeBtn) {
        copyCodeBtn.addEventListener('click', function() {
            const codeInput = document.getElementById('generatedCode');
            copyToClipboard(codeInput.value, '邀請碼已複製');
        });
    }

    const copyUrlBtn = document.getElementById('copyUrlBtn');
    if (copyUrlBtn) {
        copyUrlBtn.addEventListener('click', function() {
            const urlInput = document.getElementById('generatedUrl');
            copyToClipboard(urlInput.value, '邀請連結已複製');
        });
    }

    // 綁定表格內的複製按鈕
    document.querySelectorAll('.btn-copy-inline').forEach(btn => {
        btn.addEventListener('click', function() {
            const code = this.getAttribute('data-code');
            copyToClipboard(code, '邀請碼已複製');
        });
    });
}

// 複製到剪貼簿
function copyToClipboard(text, successMessage) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification(successMessage || '已複製到剪貼簿', 'success');
        }).catch(err => {
            console.error('複製失敗:', err);
            fallbackCopy(text, successMessage);
        });
    } else {
        fallbackCopy(text, successMessage);
    }
}

// 備用複製方法（舊版瀏覽器）
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
        console.error('複製失敗:', err);
        showNotification('複製失敗，請手動複製', 'error');
    }
    
    document.body.removeChild(textarea);
}

// 顯示通知
function showNotification(message, type = 'success') {
    // 移除舊的通知
    const oldNotification = document.querySelector('.notification');
    if (oldNotification) {
        oldNotification.remove();
    }

    // 建立新通知
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
        <span>${message}</span>
    `;
    
    // 加入樣式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#22c55e' : '#ef4444'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 600;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // 3秒後自動移除
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 撤銷邀請
function revokeInvite(code) {
    if (confirm(`確定要撤銷邀請碼 ${code} 嗎？`)) {
        // 這裡應該發送 API 請求到後端
        console.log('撤銷邀請碼:', code);
        
        // 模擬成功
        showNotification('邀請碼已撤銷', 'success');
        
        // 實際應用中，成功後應重新載入列表或更新 UI
        // location.reload();
    }
}

// 批准申請
function approveApplication(appId) {
    if (confirm('確定要批准此申請嗎？')) {
        // 這裡應該發送 API 請求到後端
        console.log('批准申請:', appId);
        
        // 模擬成功
        showNotification('申請已批准', 'success');
        
        // 實際應用中，成功後應重新載入列表或更新 UI
        // location.reload();
    }
}

// 拒絕申請
function rejectApplication(appId) {
    const reason = prompt('請輸入拒絕原因（選填）：');
    
    if (reason !== null) { // 用戶沒有按取消
        // 這裡應該發送 API 請求到後端
        console.log('拒絕申請:', appId, '原因:', reason);
        
        // 模擬成功
        showNotification('申請已拒絕', 'success');
        
        // 實際應用中，成功後應重新載入列表或更新 UI
        // location.reload();
    }
}

// 加入動畫樣式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);