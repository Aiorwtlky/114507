// 檔案路徑: static/js/utils.js

/**
 * 統一的 API 請求工具
 * 自動帶入 Token、自動處理網址、自動處理 401 登出
 */
async function fetchWithAuth(endpoint, options = {}) {
    // 1. 從大腦 (config.js) 拿目前的 API 網址
    const baseUrl = AppConfig.API_BASE_URL;
    
    // 2. 檢查是否登入
    const token = localStorage.getItem('accessToken');
    
    // 如果沒有 Token，且不是去公開頁面，就踢回登入頁
    // (這裡可以根據需求放寬，例如有些 API 不用登入)
    if (!token) {
        // console.warn('未登入，重導向...');
        // window.location.href = '/login';
        // throw new Error('Not Authenticated');
    }

    // 3. 設定 Header
    const headers = options.headers || new Headers();
    if (token) {
        headers.append('Authorization', `Bearer ${token}`);
    }
    
    // 如果不是上傳檔案 (FormData)，預設都用 JSON
    if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
        headers.append('Content-Type', 'application/json');
    }

    // 4. 發送請求
    const url = `${baseUrl}${endpoint}`;
    
    try {
        const response = await fetch(url, { ...options, headers });

        // 5. 統一處理 Token 過期 (401 Unauthorized)
        if (response.status === 401) {
            alert('您的登入時效已過，請重新登入。');
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        
        return response;
    } catch (error) {
        console.error(`API 請求失敗 (${url}):`, error);
        throw error;
    }
}