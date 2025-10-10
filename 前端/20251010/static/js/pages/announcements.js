/**
 * 檔案：static/js/pages/announcements.js
 * 用途：公告詳細頁面互動功能
 */

(function() {
    'use strict';

    // ========== 等待 DOM 完全載入 ==========
    document.addEventListener('DOMContentLoaded', function() {
        console.log('✅ 公告詳細頁面已載入');

        initPrintButton();
        initScrollProgress();
    });

    // ========== 1. 列印按鈕功能 ==========
    function initPrintButton() {
        const printButtons = document.querySelectorAll('.btn-primary');
        
        printButtons.forEach(button => {
            if (button.textContent.includes('列印')) {
                button.addEventListener('click', function(e) {
                    console.log('準備列印公告...');
                    // window.print() 已經在 onclick 中處理
                });
            }
        });

        console.log('✅ 列印功能已初始化');
    }

    // ========== 2. 閱讀進度追蹤（可選） ==========
    function initScrollProgress() {
        const announcementBody = document.querySelector('.announcement-body');
        
        if (!announcementBody) return;

        let hasReadToBottom = false;

        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight;

            // 計算閱讀進度
            const scrollProgress = (scrollTop / (documentHeight - windowHeight)) * 100;

            // 如果滾動到底部（90%以上），標記為已讀
            if (scrollProgress >= 90 && !hasReadToBottom) {
                hasReadToBottom = true;
                console.log('✅ 使用者已閱讀完整公告');
                // 未來可以在這裡記錄閱讀狀態到後端
                // markAnnouncementAsRead();
            }
        }, { passive: true });
    }

    // ========== 3. 鍵盤快捷鍵（可選） ==========
    document.addEventListener('keydown', function(e) {
        // Ctrl + P 或 Cmd + P 列印
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            window.print();
        }

        // ESC 返回上一頁
        if (e.key === 'Escape') {
            const backButton = document.querySelector('.btn-outline');
            if (backButton) {
                window.location.href = backButton.getAttribute('href');
            }
        }
    });

    // ========== 4. 工具函數：標記為已讀（未來功能） ==========
    function markAnnouncementAsRead() {
        // 未來可以透過 AJAX 發送到後端
        // const announcementId = getAnnouncementIdFromURL();
        // fetch('/api/announcements/' + announcementId + '/mark-read', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' }
        // });
    }

    // ========== 5. 公開 API ==========
    window.AnnouncementDetail = {
        print: function() {
            window.print();
        }
    };

})();