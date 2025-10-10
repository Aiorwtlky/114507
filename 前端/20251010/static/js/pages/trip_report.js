// 行程報告頁面功能

document.addEventListener('DOMContentLoaded', function() {
    // Modal 元素
    const modal = document.getElementById('editTitleModal');
    const modalOverlay = document.getElementById('modalOverlay');
    const editTitleBtn = document.getElementById('editTitleBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const saveTitleBtn = document.getElementById('saveTitleBtn');
    const titleInput = document.getElementById('titleInput');
    const tripTitle = document.getElementById('tripTitle');

    // 開啟 Modal
    editTitleBtn.addEventListener('click', function() {
        titleInput.value = tripTitle.textContent;
        modal.style.display = 'block';
        setTimeout(() => {
            titleInput.focus();
            titleInput.select();
        }, 100);
    });

    // 關閉 Modal
    function closeModal() {
        modal.style.display = 'none';
    }

    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);

    // ESC 鍵關閉
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });

    // Enter 鍵儲存
    titleInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            saveTitle();
        }
    });

    // 儲存標題
    saveTitleBtn.addEventListener('click', saveTitle);

    function saveTitle() {
        const newTitle = titleInput.value.trim();
        if (newTitle) {
            tripTitle.textContent = newTitle;
            
            // 這裡應該發送 API 請求到後端儲存
            // fetch('/api/trips/update_title', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify({
            //         trip_id: TRIP_ID,
            //         title: newTitle
            //     })
            // });

            showNotification('行程名稱已更新', 'success');
            closeModal();
        } else {
            showNotification('請輸入行程名稱', 'error');
        }
    }

    // 顯示通知
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
            <span>${message}</span>
        `;
        
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
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});

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