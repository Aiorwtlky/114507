/**
 * 檔案名稱：static/js/main_app.js
 * 用途：MDG Pro 應用的交互功能（側邊欄、漢堡選單等）
 */

(function() {
    'use strict';

    // ========== DOM 元素 ==========
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const appSidebar = document.getElementById('appSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const body = document.body;

    // ========== 側邊欄控制功能 ==========
    
    /**
     * 開啟側邊欄
     */
    function openSidebar() {
        appSidebar.classList.add('is-active');
        sidebarOverlay.classList.add('is-active');
        body.classList.add('sidebar-open');
        
        // 更新 ARIA 屬性
        if (hamburgerBtn) {
            hamburgerBtn.setAttribute('aria-expanded', 'true');
        }
        sidebarOverlay.setAttribute('aria-hidden', 'false');
        
        // 鎖定焦點在側邊欄內
        appSidebar.focus();
    }

    /**
     * 關閉側邊欄
     */
    function closeSidebar() {
        appSidebar.classList.remove('is-active');
        sidebarOverlay.classList.remove('is-active');
        body.classList.remove('sidebar-open');
        
        // 更新 ARIA 屬性
        if (hamburgerBtn) {
            hamburgerBtn.setAttribute('aria-expanded', 'false');
            hamburgerBtn.focus(); // 焦點返回按鈕
        }
        sidebarOverlay.setAttribute('aria-hidden', 'true');
    }

    /**
     * 切換側邊欄狀態
     */
    function toggleSidebar() {
        if (appSidebar.classList.contains('is-active')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    // ========== 事件監聽器 ==========

    // 1. 漢堡按鈕點擊
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleSidebar);
    }

    // 2. 遮罩層點擊（關閉側邊欄）
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // 3. ESC 鍵關閉側邊欄
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && appSidebar.classList.contains('is-active')) {
            closeSidebar();
        }
    });

    // 4. 點擊側邊欄內的連結後，在手機版自動關閉側邊欄
    if (appSidebar) {
        const navLinks = appSidebar.querySelectorAll('.nav-item');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                // 只在手機版（側邊欄為 fixed 定位時）關閉
                if (window.innerWidth <= 768) {
                    closeSidebar();
                }
            });
        });
    }

    // 5. 視窗大小改變時的處理
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // 如果從手機版切換到桌面版，確保移除手機版的狀態
            if (window.innerWidth > 768) {
                appSidebar.classList.remove('is-active');
                sidebarOverlay.classList.remove('is-active');
                body.classList.remove('sidebar-open');
                
                if (hamburgerBtn) {
                    hamburgerBtn.setAttribute('aria-expanded', 'false');
                }
            }
        }, 250);
    });

    // ========== 滑動手勢支援（手機版） ==========
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    // 偵測從左邊緣滑動開啟側邊欄
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
        const swipeDistance = touchEndX - touchStartX;
        const minSwipeDistance = 50;
        
        // 從左邊緣向右滑動 -> 開啟側邊欄
        if (touchStartX < 30 && swipeDistance > minSwipeDistance) {
            if (!appSidebar.classList.contains('is-active')) {
                openSidebar();
            }
        }
        
        // 在側邊欄上向左滑動 -> 關閉側邊欄
        if (touchStartX < 280 && swipeDistance < -minSwipeDistance) {
            if (appSidebar.classList.contains('is-active')) {
                closeSidebar();
            }
        }
    }

    // ========== 頁面載入完成後的初始化 ==========
    
    window.addEventListener('DOMContentLoaded', function() {
        // 確保初始狀態正確
        if (window.innerWidth <= 768) {
            appSidebar.classList.remove('is-active');
            sidebarOverlay.classList.remove('is-active');
            body.classList.remove('sidebar-open');
        }
        
        console.log('✅ MDG Pro App JavaScript 已載入');
    });

    // ========== 效能優化：防抖函數 ==========
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ========== 無障礙：焦點陷阱（Focus Trap） ==========
    
    /**
     * 當側邊欄打開時，將焦點限制在側邊欄內
     */
    function setupFocusTrap() {
        if (!appSidebar) return;
        
        const focusableElements = appSidebar.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        appSidebar.addEventListener('keydown', function(e) {
            if (!appSidebar.classList.contains('is-active')) return;
            
            if (e.key === 'Tab') {
                if (e.shiftKey) { // Shift + Tab
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else { // Tab
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
    }
    
    setupFocusTrap();

    // ========== 公開 API（如需要在其他腳本中使用） ==========
    
    window.MDGApp = {
        openSidebar: openSidebar,
        closeSidebar: closeSidebar,
        toggleSidebar: toggleSidebar
    };

})();