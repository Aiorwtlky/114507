// 檔案路徑: static/js/pages/change_password.js

(function() {
    'use strict';

    const API_BASE_URL = 'http://127.0.0.1:8000';

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            alert('您尚未登入或登入已逾時，將跳轉至登入頁面。');
            window.location.href = '/login';
            throw new Error('Not Authenticated');
        }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) {
            headers.append('Content-Type', 'application/json');
        }
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            alert('您的登入已過期，請重新登入。');
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    // --- 頁面初始化 ---
    document.addEventListener('DOMContentLoaded', () => {

        // --- 你原本的前端互動邏輯 (完全保留) ---
        // 將函式掛載到 window，HTML 中的 onclick 才能找到它
        window.togglePassword = function(inputId) {
            const input = document.getElementById(inputId);
            const icon = input.nextElementSibling.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        }

        const newPasswordInput = document.getElementById('newPassword');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        const passwordMatchText = document.getElementById('passwordMatch');
        const strengthProgress = document.getElementById('strengthProgress');
        const strengthText = document.getElementById('strengthText');

        if(newPasswordInput) {
            newPasswordInput.addEventListener('input', function() {
                const password = this.value;
                let strength = 0;
                if (password.length >= 8) strength++;
                if (password.length >= 12) strength++;
                if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
                if (/\d/.test(password)) strength++;
                if (/[^a-zA-Z0-9]/.test(password)) strength++;
                const percentage = (strength / 5) * 100;
                strengthProgress.style.width = percentage + '%';
                if (strength <= 1) {
                    strengthProgress.style.background = '#ef4444'; strengthText.textContent = '密碼強度：弱'; strengthText.style.color = '#ef4444';
                } else if (strength <= 3) {
                    strengthProgress.style.background = '#f59e0b'; strengthText.textContent = '密碼強度：中等'; strengthText.style.color = '#f59e0b';
                } else {
                    strengthProgress.style.background = '#10b981'; strengthText.textContent = '密碼強度：強'; strengthText.style.color = '#10b981';
                }
            });
        }

        if(confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', function() {
                if (this.value === '') { passwordMatchText.textContent = ''; return; }
                if (this.value === newPasswordInput.value) {
                    passwordMatchText.textContent = '✓ 密碼相符'; passwordMatchText.style.color = '#10b981';
                } else {
                    passwordMatchText.textContent = '✗ 密碼不相符'; passwordMatchText.style.color = '#ef4444';
                }
            });
        }

        // --- 【核心修改】表單提交處理 ---
        const form = document.getElementById('changePasswordForm');
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const currentPassword = document.getElementById('currentPassword').value;
                const newPassword = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                
                // 前端驗證
                if (newPassword !== confirmPassword) { alert('新密碼與確認密碼不相符！'); return; }
                if (newPassword.length < 8) { alert('密碼長度至少需要 8 個字元！'); return; }
                // 備註：一個更安全的作法是建立專門的 API 端點來驗證 currentPassword
                
                try {
                    const response = await fetchWithAuth('/api/auth/profile/', {
                        method: 'PATCH',
                        body: JSON.stringify({
                            password: newPassword
                        })
                    });

                    if (response.ok) {
                        const modal = document.getElementById('successModal');
                        modal.style.display = 'flex';
                        
                        // 為了安全，更改密碼後應強制使用者重新登入，所以清除 token
                        localStorage.clear(); 
                        
                        // 2 秒後跳轉到登入頁
                        setTimeout(() => {
                            window.location.href = "/login";
                        }, 2000);

                    } else {
                        const errorData = await response.json();
                        alert(`密碼更新失敗: ${JSON.stringify(errorData)}`);
                    }
                } catch (error) {
                    console.error('密碼更新時發生錯誤:', error);
                    alert('操作失敗，請檢查網路連線。');
                }
            });
        }
    });
})();