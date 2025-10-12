// 檔案路徑: static/js/pages/create_announcement.js (更穩健的版本)

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

    async function handleFormSubmit(event) {
        event.preventDefault();
        const submitButton = document.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 發布中...`;

        const urlParams = new URLSearchParams(window.location.search);
        const groupId = urlParams.get('group_id');
        if (!groupId) {
            alert('錯誤：缺少群組資訊，無法發布。');
            return;
        }

        const subject = document.getElementById('subject').value;
        const content = tinymce.get('content').getContent();

        if (!subject || !content) {
            alert('主旨和內容為必填欄位！');
            submitButton.disabled = false;
            submitButton.innerHTML = `<i class="fa-solid fa-paper-plane"></i> 發佈公告`;
            return;
        }
        
        const fullContent = `<h3>${subject}</h3>${content}`;

        try {
            const response = await fetchWithAuth(`/api/groups/${groupId}/announcements/`, {
                method: 'POST',
                body: JSON.stringify({
                    content: fullContent,
                    is_active: true
                })
            });

            if (response.ok) {
                alert('公告已成功發布！');
                window.location.href = '/group_leader_view';
            } else {
                const errorData = await response.json();
                let errorMessage = '發布失敗：\n';
                for (const field in errorData) {
                    errorMessage += `${field}: ${errorData[field].join(', ')}\n`;
                }
                alert(errorMessage);
            }
        } catch (error) {
            console.error('發布公告時發生錯誤:', error.message);
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = `<i class="fa-solid fa-paper-plane"></i> 發佈公告`;
        }
    }

    async function initializePage() {
        tinymce.init({
            selector: '#content', plugins: 'lists link image table code help wordcount',
            toolbar: 'undo redo | blocks | bold italic | bullist numlist | link image | table | code | help',
            language: 'zh_TW', height: 400, menubar: false, placeholder: '請在此輸入公告內容...',
            content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 16px; }'
        });
        flatpickr("#scheduled_time_picker", { enableTime: true, dateFormat: "Y-m-d H:i", minDate: "today" });
        
        const form = document.getElementById('announcementForm');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
        }
        
        // ---  檢查 group_id 是否存在  ---
        const urlParams = new URLSearchParams(window.location.search);
        const groupId = urlParams.get('group_id');

        if (!groupId) {
            console.error("錯誤：URL 中缺少 group_id，無法載入頁面資料。");
            alert("錯誤：缺少群組資訊，無法載入此頁面。\n\n請從「群組管理」頁面點擊「新增公告」按鈕進入。");
            // 讓使用者無法操作表單
            const submitButton = document.querySelector('button[type="submit"]');
            if(submitButton) submitButton.disabled = true;
            // 更新標題提示錯誤
            document.getElementById('group-context-name').textContent = '錯誤：未指定群組';
            document.getElementById('publisher-name').textContent = '錯誤';
            return; 
        }
        // --- ▲▲▲ 修正結束 ▲▲▲ ---

        try {
            const [currentUserRes, groupRes] = await Promise.all([
                fetchWithAuth('/api/auth/profile/'),
                fetchWithAuth(`/api/groups/${groupId}/`)
            ]);

            if (currentUserRes.ok && groupRes.ok) {
                const currentUser = await currentUserRes.json();
                const group = await groupRes.json();

                // 更新頁首 UI
                document.getElementById('publisher-unit').textContent = group.description || '總公司';
                document.getElementById('group-context-name').textContent = group.name;
                document.getElementById('publisher-avatar').src = currentUser.personnelprofile?.avatar || '/static/images/user-placeholder.svg';
                document.getElementById('publisher-name').textContent = currentUser.first_name || currentUser.username;
            } else {
                throw new Error('API 請求失敗');
            }
        } catch (error) {
            console.error("載入頁首資訊失敗:", error.message);
        }
    }

    document.addEventListener('DOMContentLoaded', initializePage);

})();