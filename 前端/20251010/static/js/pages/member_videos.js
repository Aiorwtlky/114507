// 檔案路徑: static/js/pages/member_videos.js

(function() {
    'use strict';
    
    // 請根據您的 Django 伺服器位址修改
    const API_BASE_URL = 'http://127.0.0.1:8000'; 
    let memberId = null;
    let currentMemberName = '成員';

    // --- DOM 元素宣告 ---
    const listContainer = document.getElementById('videos-list-container');
    const modalOverlay = document.getElementById('videoModalOverlay');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalTitle = document.getElementById('modalTitle');
    const modalDownloadFull = document.getElementById('modalDownloadFull');
    // 這個容器必須存在於您的 HTML 樣板中
    const videoPlayerContainer = document.getElementById('video-player-container'); 

    /**
     * 帶有 JWT 認證的 fetch 封裝函式
     * @param {string} endpoint - API 的路徑 (例如: /api/videos/)
     * @param {object} options - Fetch 的設定選項
     * @returns {Promise<Response>}
     */
    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            window.location.href = '/login'; // 未登入則導向登入頁
            throw new Error('Not Authenticated');
        }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        headers.append('Content-Type', 'application/json');

        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

        if (response.status === 401) { // Token 過期或無效
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    /**
     * 將位元組轉換為易讀的檔案大小格式
     * @param {number} bytes - 檔案大小 (位元組)
     * @param {number} decimals - 小數位數
     * @returns {string}
     */
    function formatBytes(bytes, decimals = 2) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
    
    /**
     * 將影片資料渲染到頁面上
     * @param {Array<object>} videos - 從 API 獲取的影片物件陣列
     */
    function renderVideos(videos) {
        if (!listContainer) return;
        listContainer.innerHTML = '';

        if (!videos || videos.length === 0) {
            listContainer.innerHTML = '<p class="no-videos-message">此成員尚無行車影片記錄。</p>';
            return;
        }

        // 按日期將影片分組
        const videosByDate = videos.reduce((acc, video) => {
            const date = new Date(video.start_time).toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' });
            if (!acc[date]) acc[date] = [];
            acc[date].push(video);
            return acc;
        }, {});

        // 遍歷日期並建立對應的區塊
        for (const date in videosByDate) {
            const section = document.createElement('section');
            section.className = 'daily-videos';
            section.innerHTML = `<h2 class="date-header">${date.replace(/\//g, ' / ')}</h2>`;

            const gallery = document.createElement('div');
            gallery.className = 'video-gallery';

            videosByDate[date].forEach(video => {
                const startTime = new Date(video.start_time);
                const endTime = new Date(video.end_time);
                const durationMs = endTime - startTime;
                const hours = Math.floor(durationMs / 3600000);
                const minutes = Math.round((durationMs % 3600000) / 60000);
                const durationText = `${hours > 0 ? hours + ' 小時 ' : ''}${minutes} 分鐘`;

                const card = document.createElement('div');
                card.className = 'video-card';
                // 將重要資訊存放在 data-* 屬性中
                card.dataset.starttime = startTime.toLocaleTimeString([], { hour: '2-digit', minute:'2-digit' });
                card.dataset.endtime = endTime.toLocaleTimeString([], { hour: '2-digit', minute:'2-digit' });
                card.dataset.size = formatBytes(video.file_size || 0);
                // 儲存後端生成的 GCS 簽署後 URL
                card.dataset.signedUrl = video.video_url || '#'; 

                card.innerHTML = `
                    <div class="video-thumbnail">
                        <img src="https://via.placeholder.com/400x225.png/1a2a5f/ffffff?text=點擊播放" alt="影片預覽">
                        <div class="play-icon"><i class="fa-solid fa-play"></i></div>
                    </div>
                    <div class="video-card-content">
                        <h3 class="video-time">${card.dataset.starttime} - ${card.dataset.endtime}</h3>
                        <div class="video-meta">
                            <span><i class="fa-solid fa-database"></i> ${card.dataset.size}</span>
                            <span><i class="fa-solid fa-clock"></i> ${durationText}</span>
                        </div>
                    </div>
                `;
                gallery.appendChild(card);
            });
            section.appendChild(gallery);
            listContainer.appendChild(section);
        }
    }

    /**
     * 開啟影片播放彈出視窗
     * @param {HTMLElement} card - 被點擊的影片卡片元素
     */
    function openModal(card) {
        if (!modalOverlay || !videoPlayerContainer) return;

        // 更新 Modal 標題和下載按鈕
        modalTitle.textContent = `行程影片：${card.dataset.starttime} - ${card.dataset.endtime}`;
        modalDownloadFull.innerHTML = `<i class="fa-solid fa-download"></i> 下載完整影片 (${card.dataset.size})`;
        modalDownloadFull.href = card.dataset.signedUrl;

        // 動態建立並插入 <video> 播放器
        if (card.dataset.signedUrl && card.dataset.signedUrl !== '#') {
            videoPlayerContainer.innerHTML = `
                <video controls autoplay style="width: 100%; height: auto; border-radius: 8px; background-color: #000;">
                    <source src="${card.dataset.signedUrl}" type="video/mp4">
                    您的瀏覽器不支援 Video 標籤。
                </video>
            `;
        } else {
            videoPlayerContainer.innerHTML = `<p style="text-align: center; color: #ccc;">影片連結無效或已過期。</p>`;
        }

        modalOverlay.style.display = 'flex';
    };

    /**
     * 關閉影片播放彈出視窗
     */
    function closeModal() {
        if (modalOverlay) modalOverlay.style.display = 'none';
        
        // 關閉時清空播放器容器，可以立即停止影片播放並釋放資源
        if (videoPlayerContainer) {
            videoPlayerContainer.innerHTML = '';
        }
    };
    
    /**
     * 頁面初始化函式
     */
    async function initializePage() {
        // 從 URL 解析成員 ID
        const pathParts = window.location.pathname.split('/');
        memberId = pathParts[pathParts.length - 1];

        if (!memberId) {
            document.body.innerHTML = '<h1>錯誤：未指定成員 ID</h1>';
            return;
        }

        try {
            // 平行發送 API 請求以提高效率
            const [videosRes, memberRes] = await Promise.all([
                fetchWithAuth(`/api/videos/?user_id=${memberId}`),
                fetchWithAuth(`/api/personnel/${memberId}/profile/`)
            ]);

            if (!videosRes.ok) throw new Error('無法獲取影片列表');
            const videoData = await videosRes.json();
            
            // 獲取成員名稱並更新頁面標題
            if (memberRes.ok) {
                const memberData = await memberRes.json();
                currentMemberName = memberData.first_name || memberData.username;
            } else {
                currentMemberName = `成員 #${memberId}`;
            }
            const pageTitleEl = document.getElementById('page-title-username');
            if(pageTitleEl) pageTitleEl.textContent = currentMemberName;
            
            // 渲染影片列表
            renderVideos(videoData.results || videoData);

        } catch(error) {
            console.error("載入影片頁面失敗:", error);
            if (listContainer) {
                listContainer.innerHTML = '<p class="error-message">載入資料失敗，您可能沒有權限查看此成員的影片。</p>';
            }
        }
    }
    
    // --- 事件監聽器 ---

    // 使用事件委派來監聽所有影片卡片的點擊
    listContainer?.addEventListener('click', (event) => {
        const card = event.target.closest('.video-card');
        if (card) {
            openModal(card);
        }
    });

    // 監聽 Modal 的關閉事件
    modalCloseBtn?.addEventListener('click', closeModal);
    modalOverlay?.addEventListener('click', (e) => {
        // 只有在點擊背景時才關閉
        if (e.target === modalOverlay) {
            closeModal();
        }
    });
    
    // 監聽鍵盤 Esc 鍵
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modalOverlay && modalOverlay.style.display === 'flex') {
            closeModal();
        }
    });

    // 執行初始化
    initializePage();

})();