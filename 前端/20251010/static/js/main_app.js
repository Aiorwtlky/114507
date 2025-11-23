// 檔案路徑: static/js/main_app.js (已修復登出功能)

(function() {
    'use strict';

    // ========== DOM 元素 ==========
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const appSidebar = document.getElementById('appSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const body = document.body;
    // 【新增】選取登出按鈕
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
            // 如果沒有使用者資料，可能代表未登入，這裡不做強制導向，交給各頁面自己判斷
            return;
        }

        try {
            const userProfile = JSON.parse(userProfileString);

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

        } catch (error) {
            console.error('更新側邊欄 UI 失敗:', error);
        }
    }

    // ========== 【新增】全域登出功能 ==========
    function handleLogout(e) {
        e.preventDefault();
        if (confirm('您確定要登出系統嗎？')) {
            // 1. 清除所有本地暫存 (Token, UserProfile)
            localStorage.clear();
            // 2. 導向後端的登出路由
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
    
    // 【新增】綁定登出按鈕事件
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
                // 如果是手機版，點擊連結後自動收起側邊欄
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
        console.log('✅ MDG Pro App JavaScript 已載入 (含登出功能)');
    });

    // ========== 公開 API ==========
    window.MDGApp = {
        openSidebar: openSidebar,
        closeSidebar: closeSidebar,
        toggleSidebar: toggleSidebar,
        updateSidebarUI: updateSidebarUI
    };

})();