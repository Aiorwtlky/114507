// 檔案路徑: static/js/pages/register.js

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. 元素選取 ---
    const registerForm = document.getElementById('registerForm');
    const steps = document.querySelectorAll('.form-step');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const progressSteps = document.querySelectorAll('.progress-step');
    let currentStep = 1;

    // --- 2. 多步驟表單切換邏輯 ---
    const updateFormUI = () => {
        // 更新進度條樣式
        progressSteps.forEach(step => {
            const stepNumber = parseInt(step.dataset.step);
            step.classList.toggle('active', stepNumber <= currentStep);
        });

        // 顯示當前步驟的表單，隱藏其他
        steps.forEach(step => {
            step.classList.toggle('active', parseInt(step.dataset.step) === currentStep);
        });

        // 更新按鈕的顯示狀態
        prevBtn.style.display = currentStep === 1 ? 'none' : 'inline-block';
        nextBtn.style.display = currentStep === steps.length ? 'none' : 'inline-block';
        submitBtn.style.display = currentStep === steps.length ? 'inline-block' : 'none';
    };

    nextBtn.addEventListener('click', () => {
        // TODO: 你可以在這裡為每個步驟加入欄位驗證，如果驗證失敗就 return;
        if (currentStep < steps.length) {
            currentStep++;
            updateFormUI();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            updateFormUI();
        }
    });

    // --- 3. 互動功能邏輯 ---
    // 3.1 照片預覽
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');
    photoInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => { photoPreview.src = e.target.result; }
            reader.readAsDataURL(this.files[0]);
        }
    });

    // 3.2 條款滾動解鎖
    const termsBox = document.getElementById('termsBox');
    const agreeCheckbox = document.getElementById('agreeCheckbox');
    termsBox.addEventListener('scroll', () => {
        // 滾動到底部時，啟用 checkbox
        if (termsBox.scrollTop + termsBox.clientHeight >= termsBox.scrollHeight - 10) { // 10px 容錯
            agreeCheckbox.disabled = false;
        }
    });
    agreeCheckbox.addEventListener('change', () => {
        submitBtn.disabled = !agreeCheckbox.checked;
    });
    
    // --- 4. 【核心】API 提交邏輯 ---
    registerForm.addEventListener('submit', async (event) => {
        // 阻止表單的預設提交行為
        event.preventDefault();

        submitBtn.disabled = true;
        submitBtn.textContent = '註冊中...';

        // 使用 FormData 自動收集表單中的所有欄位資料，包含檔案
        const formData = new FormData(registerForm);
        
        // 後端 API 的 URL
        const API_BASE_URL = 'http://127.0.0.1:8000';
        const API_ENDPOINT = `${API_BASE_URL}/api/auth/register/`;

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                body: formData,
                // 注意：當 body 是 FormData 時，絕對不要手動設定 'Content-Type' header。
                // 瀏覽器會自動處理 multipart/form-data 格式。
            });

            if (response.ok) { // 狀態碼 201 Created
                alert('註冊成功！您現在可以前往登入頁面。');
                window.location.href = '/login'; // 跳轉到登入頁
            } else {
                // 處理後端回傳的錯誤訊息
                const errorData = await response.json();
                let errorMessage = '註冊失敗，請檢查以下問題：\n';
                for (const field in errorData) {
                    errorMessage += `- ${errorData[field].join(', ')}\n`;
                }
                alert(errorMessage);
            }
        } catch (error) {
            console.error('註冊請求失敗:', error);
            alert('註冊失敗，無法連線至伺服器，請稍後再試。');
        } finally {
            // 無論成功或失敗，都恢復按鈕狀態
            submitBtn.disabled = !agreeCheckbox.checked; // 恢復根據 checkbox 的狀態
            submitBtn.textContent = '完成註冊';
        }
    });
    
    // --- 初始化頁面 ---
    updateFormUI();
});