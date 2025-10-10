// 檔案路徑: static/js/pages/login.js

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000';

    if (typeof gsap !== 'undefined') {
        gsap.from(".login-form", { y: 50, opacity: 0, duration: .9, ease: "power2.out" });
    }

    const loginForm = document.getElementById('loginForm');
    const errorMessageDiv = document.getElementById('errorMessage');

    if (!loginForm) {
        console.error('錯誤：在頁面中找不到 id="loginForm" 的表單元素。');
        return;
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        if (errorMessageDiv) {
            errorMessageDiv.style.display = 'none';
        }

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const loginButton = loginForm.querySelector('button[type="submit"]');

        // 禁用按鈕
        loginButton.disabled = true;
        loginButton.textContent = '登入中...';

        try {
            const response = await fetch(`${API_BASE_URL}/api/token/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // --- ▼▼▼ 【核心修改】登入成功後，增加身分檢查步驟 ▼▼▼ ---

                // 步驟 1：成功獲取並儲存 token
                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);

                // 步驟 2：立刻使用剛拿到的 access token 去獲取使用者資料
                const profileResponse = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
                    headers: {
                        'Authorization': `Bearer ${data.access}`
                    }
                });

                if (profileResponse.ok) {
                    const profileData = await profileResponse.json();
                    
                    // 步驟 3：根據回傳資料中的 is_staff 欄位，判斷要跳轉到哪裡
                    if (profileData.is_staff) {
                        // 如果是 staff (管理員或 superuser)，跳轉到群組管理頁
                        window.location.href = '/group_leader_view';
                    } else {
                        // 如果是一般使用者，跳轉到個人儀表板
                        window.location.href = '/dashboard';
                    }
                } else {
                    // 如果獲取 Profile 失敗，作為備用方案，還是跳到儀表板
                    window.location.href = '/dashboard';
                }
                
                // --- ▲▲▲ 修改結束 ▲▲▲ ---

            } else {
                if (errorMessageDiv) {
                    errorMessageDiv.textContent = data.detail || '登入失敗，請稍後再試。';
                    errorMessageDiv.style.display = 'block';
                } else {
                    alert(data.detail || '登入失敗，請稍後再試。');
                }
                // 登入失敗時，恢復按鈕狀態
                loginButton.disabled = false;
                loginButton.textContent = '立即登入';
            }

        } catch (error) {
            console.error('登入請求時發生錯誤:', error);
            if (errorMessageDiv) {
                errorMessageDiv.textContent = '無法連線至伺服器，請檢查您的網路或後端是否已啟動。';
                errorMessageDiv.style.display = 'block';
            } else {
                alert('無法連線至伺服器，請檢查您的網路或後端是否已啟動。');
            }
            // 發生錯誤時，恢復按鈕狀態
            loginButton.disabled = false;
            loginButton.textContent = '立即登入';
        }
    });
});