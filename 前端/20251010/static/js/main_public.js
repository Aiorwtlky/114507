/**
 * 檔案名稱：static/js/main_public.js
 * 用途：My Driving God 公開網站的交互功能（導覽選單等）
 */

(function() {
    'use strict';

    // ========== DOM 元素 ==========
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navLinks = document.getElementById('navLinks');
    const navOverlay = document.getElementById('navOverlay');
    const body = document.body;

    // ========== 導覽選單控制功能 ==========
    
    /**
     * 開啟導覽選單
     */
    function openNav() {
        navLinks.classList.add('is-active');
        navOverlay.classList.add('is-active');
        body.classList.add('nav-open');
        
        // 更新 ARIA 屬性
        if (hamburgerBtn) {
            hamburgerBtn.setAttribute('aria-expanded', 'true');
            // 切換圖標（漢堡 → 關閉）
            const icon = hamburgerBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            }
        }
        navOverlay.setAttribute('aria-hidden', 'false');
        
        // 鎖定焦點在選單內
        const firstLink = navLinks.querySelector('a');
        if (firstLink) firstLink.focus();
    }

    /**
     * 關閉導覽選單
     */
    function closeNav() {
        navLinks.classList.remove('is-active');
        navOverlay.classList.remove('is-active');
        body.classList.remove('nav-open');
        
        // 更新 ARIA 屬性
        if (hamburgerBtn) {
            hamburgerBtn.setAttribute('aria-expanded', 'false');
            // 切換圖標（關閉 → 漢堡）
            const icon = hamburgerBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
            hamburgerBtn.focus(); // 焦點返回按鈕
        }
        navOverlay.setAttribute('aria-hidden', 'true');
    }

    /**
     * 切換導覽選單狀態
     */
    function toggleNav() {
        if (navLinks.classList.contains('is-active')) {
            closeNav();
        } else {
            openNav();
        }
    }

    // ========== 事件監聽器 ==========

    // 1. 漢堡按鈕點擊
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleNav);
    }

    // 2. 遮罩層點擊（關閉選單）
    if (navOverlay) {
        navOverlay.addEventListener('click', closeNav);
    }

    // 3. ESC 鍵關閉選單
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && navLinks.classList.contains('is-active')) {
            closeNav();
        }
    });

    // 4. 點擊選單內的連結後，在手機版自動關閉選單
    if (navLinks) {
        const links = navLinks.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', function() {
                // 只在手機版關閉選單
                if (window.innerWidth <= 768) {
                    closeNav();
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
                navLinks.classList.remove('is-active');
                navOverlay.classList.remove('is-active');
                body.classList.remove('nav-open');
                
                if (hamburgerBtn) {
                    hamburgerBtn.setAttribute('aria-expanded', 'false');
                    const icon = hamburgerBtn.querySelector('i');
                    if (icon) {
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                }
            }
        }, 250);
    });

    // ========== 滑動手勢支援（手機版） ==========
    
    let touchStartX = 0;
    let touchEndX = 0;
    
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
        
        // 從右邊向左滑動 -> 關閉選單
        if (touchStartX > window.innerWidth - 280 && swipeDistance < -minSwipeDistance) {
            if (navLinks.classList.contains('is-active')) {
                closeNav();
            }
        }
    }

    // ========== 平滑滾動效果（錨點連結） ==========
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return; // 忽略 href="#" 的連結
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                
                // 在手機版先關閉選單
                if (window.innerWidth <= 768) {
                    closeNav();
                }
                
                // 平滑滾動到目標元素
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ========== 頁首滾動效果（可選） ==========
    
    let lastScrollTop = 0;
    const topbar = document.querySelector('.topbar');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // 向下滾動時添加陰影
        if (scrollTop > 10) {
            topbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            topbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
        }
        
        lastScrollTop = scrollTop;
    }, { passive: true });

    // ========== 無障礙：焦點陷阱（Focus Trap） ==========
    
    function setupFocusTrap() {
        if (!navLinks) return;
        
        navLinks.addEventListener('keydown', function(e) {
            if (!navLinks.classList.contains('is-active')) return;
            
            const focusableElements = navLinks.querySelectorAll(
                'a[href], button:not([disabled])'
            );
            
            if (focusableElements.length === 0) return;
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
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

    // ========== 頁面載入完成後的初始化 ==========
    
    window.addEventListener('DOMContentLoaded', function() {
        // 確保初始狀態正確
        if (window.innerWidth <= 768) {
            navLinks.classList.remove('is-active');
            navOverlay.classList.remove('is-active');
            body.classList.remove('nav-open');
        }
        
        console.log('✅ My Driving God 公開網站 JavaScript 已載入');
    });

    // ========== 公開 API（如需要在其他腳本中使用） ==========
    
    window.MDGPublic = {
        openNav: openNav,
        closeNav: closeNav,
        toggleNav: toggleNav
    };

})();