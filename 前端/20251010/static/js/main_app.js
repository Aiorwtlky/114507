// 檔案路徑: static/js/main_app.js (已新增參數調整頁面權限控管)

(function() {
    'use strict';

    // ========== DOM 元素 ==========
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const appSidebar = document.getElementById('appSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const body = document.body;
    const logoutBtn = document.getElementById('logoutButton');

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

    // ========== 【核心】共用 UI 更新功能 ==========
    function updateSidebarUI() {
        const userProfileString = localStorage.getItem('userProfile');
        
        if (!userProfileString) {
            return;
        }

        try {
            const userProfile = JSON.parse(userProfileString);

            // 1. 更新基本個人資料
            const sidebarAvatar = document.getElementById('sidebar-avatar');
            const sidebarUsername = document.getElementById('sidebar-username');
            const sidebarUserRole = document.getElementById('sidebar-user-role');
            const myVideosLink = document.getElementById('sidebar-my-videos-link');

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
            if (myVideosLink && userProfile.id) {
                myVideosLink.href = `/member_videos/${userProfile.id}`;
            }

            // 2. 【新增】檢查權限並顯示「參數調整」連結
            // 只要是「系統管理員 (is_staff)」或「群組管理員 (is_group_admin)」就顯示
            const isManager = userProfile.is_staff || userProfile.is_group_admin;
            const systemWeightsLink = document.getElementById('nav-system-weights');
            
            if (systemWeightsLink && isManager) {
                systemWeightsLink.style.display = 'flex'; // 解除隱藏
            }

        } catch (error) {
            console.error('更新側邊欄 UI 失敗:', error);
        }
    }

    // ========== 全域登出功能 ==========
    function handleLogout(e) {
        e.preventDefault();
        if (confirm('您確定要登出系統嗎？')) {
            localStorage.clear();
            window.location.href = '/logout';
        }
    }

    // ========== 事件監聽器 ==========
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
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

    // ========== 初始化 ==========
    document.addEventListener('DOMContentLoaded', function() {
        updateSidebarUI();
        console.log('✅ MDG Pro App JavaScript 已載入 (含權限控管)');
    });

    // ========== 公開 API ==========
    window.MDGApp = {
        openSidebar: openSidebar,
        closeSidebar: closeSidebar,
        toggleSidebar: toggleSidebar,
        updateSidebarUI: updateSidebarUI
    };

})();