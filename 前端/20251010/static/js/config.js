// 檔案路徑: static/js/config.js

const AppConfig = (function() {
    'use strict';

    const hostname = window.location.hostname;
    let apiBase = '';

    // 判斷邏輯：
    // 1. 如果網址是 localhost 或 127.0.0.1 -> 設定為本機後端 (8000 port)
    // 2. 如果是其他 (代表在學校伺服器) -> 設定為學校後端
    
    if (hostname === '127.0.0.1' || hostname === 'localhost') {
        // 本地端 Django 開發伺服器
        apiBase = 'http://127.0.0.1:8000'; 
        console.log('🔧 目前環境：本地端開發 (Localhost)');
    } else {
        // 學校伺服器 (請確認 Django 是跑在 8000 還是其他 port)
        // 如果學校伺服器有設網域，建議直接用網域
        apiBase = 'http://mdgitrc.ntub.edu.tw:8000'; 
        // 備用 IP 設定 (如果有需要可以直接改這裡)：
        // apiBase = 'http://140.131.114.182:8000';
        console.log('🌍 目前環境：學校伺服器 (Server)');
    }

    return {
        API_BASE_URL: apiBase
    };
})();