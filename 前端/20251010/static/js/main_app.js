/**
 * 檔案名稱：static/js/main_app.js
 * 用途：MDG Pro 應用的核心交互功能（側邊欄、共用 UI 更新等）
 */

(function() {
    'use strict';

    // ========== DOM 元素 ==========
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const appSidebar = document.getElementById('appSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const body = document.body;

    // ========== 側邊欄控制功能 ==========
    function openSidebar() {
        if (!appSidebar || !sidebarOverlay) return;
        appSidebar.classList.add('is-active');
        sidebarOverlay.classList.add('is-active');
        body.classList.add('sidebar-open');
        if (hamburgerBtn) {
            hamburgerBtn.setAttribute('aria-expanded', 'true');
        }
        sidebarOverlay.setAttribute('aria-hidden', 'false');
        appSidebar.focus();
    }

    function closeSidebar() {
        if (!appSidebar || !sidebarOverlay) return;
        appSidebar.classList.remove('is-active');
        sidebarOverlay.classList.remove('is-active');
        body.classList.remove('sidebar-open');
        if (hamburgerBtn) {
            hamburgerBtn.setAttribute('aria-expanded', 'false');
            hamburgerBtn.focus();
        }
        sidebarOverlay.setAttribute('aria-hidden', 'true');
    }

    function toggleSidebar() {
        if (appSidebar && appSidebar.classList.contains('is-active')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    // ========== 【核心新增】共用 UI 更新功能 ==========
    /**
     * 讀取 localStorage 中的使用者資料，並更新側邊欄 UI。
     * 這是所有登入後頁面的共用函式。
     */
    function updateSidebarUI() {
        const userProfileString = localStorage.getItem('userProfile');
        
        if (!userProfileString) {
            console.warn('userProfile not found in localStorage. Sidebar will not be updated.');
            // 如果找不到使用者資料，可以考慮導向到登入頁
            // window.location.href = '/login';
            return;
        }

        try {
            const userProfile = JSON.parse(userProfileString);

            const sidebarAvatar = document.getElementById('sidebar-avatar');
            const sidebarUsername = document.getElementById('sidebar-username');
            const sidebarUserRole = document.getElementById('sidebar-user-role');

            if (sidebarAvatar) {
                sidebarAvatar.src = userProfile.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
            }
            if (sidebarUsername) {
                sidebarUsername.textContent = userProfile.first_name || userProfile.username;
            }
            if (sidebarUserRole) {
                let roleText = '一般成員';
                if (userProfile.is_staff) {
                    roleText = '系統管理員';
                } else if (userProfile.is_group_admin) {
                    roleText = '群組管理員';
                }
                sidebarUserRole.textContent = roleText;
            }
        } catch (error) {
            console.error('Failed to parse userProfile from localStorage or update sidebar:', error);
        }
    }


    // ========== 事件監聽器 ==========
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && appSidebar && appSidebar.classList.contains('is-active')) {
            closeSidebar();
        }
    });
    if (appSidebar) {
        const navLinks = appSidebar.querySelectorAll('.nav-item');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    closeSidebar();
                }
            });
        });
    }
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 768 && appSidebar) {
                appSidebar.classList.remove('is-active');
                sidebarOverlay.classList.remove('is-active');
                body.classList.remove('sidebar-open');
                if (hamburgerBtn) {
                    hamburgerBtn.setAttribute('aria-expanded', 'false');
                }
            }
        }, 250);
    });

    // ========== 頁面載入完成後的初始化 ==========
    document.addEventListener('DOMContentLoaded', function() {
        // 在每個頁面載入完成時，自動呼叫更新側邊欄的函式
        updateSidebarUI();
        
        console.log('✅ MDG Pro App JavaScript 已載入');
    });

    // ========== 公開 API ==========
    window.MDGApp = {
        openSidebar: openSidebar,
        closeSidebar: closeSidebar,
        toggleSidebar: toggleSidebar,
        updateSidebarUI: updateSidebarUI
    };

})();