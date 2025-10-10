/**
 * 檔案：static/js/pages/group_detail.js
 * 用途：群組詳情頁面互動功能
 */

(function() {
    'use strict';

    // ========== 等待 DOM 完全載入 ==========
    document.addEventListener('DOMContentLoaded', function() {
        console.log('✅ 群組詳情頁面已載入');

        initAnnouncementLinks();
    });

    // ========== 1. 公告連結點擊追蹤 ==========
    function initAnnouncementLinks() {
        const announcementButtons = document.querySelectorAll('.btn-view-announcement');
        
        announcementButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const title = this.closest('.announcement-item')
                    ?.querySelector('.announcement-title')?.textContent;
                console.log('查看公告:', title);
                // 這裡可以加上統計或追蹤
            });
        });

        console.log(`✅ 已初始化 ${announcementButtons.length} 個公告連結`);
    }

    // ========== 2. 工具函數：平滑滾動 ==========
    function smoothScrollTo(element) {
        if (!element) return;
        
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    // ========== 3. 公開 API ==========
    window.GroupDetail = {
        scrollToElement: smoothScrollTo
    };

})();