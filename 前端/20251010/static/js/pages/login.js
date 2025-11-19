// 檔案路徑: static/js/pages/login.js (完整修正版)

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
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);

            const profileResponse = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
                headers: { 'Authorization': `Bearer ${data.access}` }
            });

            if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                localStorage.setItem('userProfile', JSON.stringify(profileData));
                
                //無論角色，一律跳轉到儀表板 
                window.location.href = '/dashboard';
                
            } else {
                localStorage.clear();
                throw new Error('登入成功，但無法獲取使用者資料。');
            }

        } else {
            if (errorMessageDiv) {
                errorMessageDiv.textContent = data.detail || '登入失敗，請稍後再試。';
                errorMessageDiv.style.display = 'block';
            }
            loginButton.disabled = false;
            loginButton.textContent = '立即登入';
        }

    } catch (error) {
        console.error('登入請求時發生錯誤:', error);
        if (errorMessageDiv) {
            errorMessageDiv.textContent = '無法連線至伺服器，請檢查您的網路。';
            errorMessageDiv.style.display = 'block';
        }
        loginButton.disabled = false;
        loginButton.textContent = '立即登入';
    }
});
});