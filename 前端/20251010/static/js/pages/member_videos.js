// 檔案路徑: static/js/pages/member_videos.js

(function() {
    'use strict';
    
    const API_BASE_URL = 'http://127.0.0.1:8000';
    let memberId = null;
    let currentMemberName = '成員';

    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        if (!token) { window.location.href = '/login'; throw new Error('Not Authenticated'); }
        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        headers.append('Content-Type', 'application/json');
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.clear(); window.location.href = '/login'; throw new Error('Token Expired'); }
        return response;
    }

    function formatBytes(bytes, decimals = 2) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
    
    function renderVideos(videos) {
        const listContainer = document.getElementById('videos-list-container');
        if(!listContainer) return;
        listContainer.innerHTML = '';

        if (!videos || videos.length === 0) {
            listContainer.innerHTML = '<p class="no-videos-message">此成員尚無行車影片記錄。</p>';
            return;
        }

        const videosByDate = videos.reduce((acc, video) => {
            const date = new Date(video.start_time).toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' });
            if (!acc[date]) acc[date] = [];
            acc[date].push(video);
            return acc;
        }, {});

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
                card.dataset.starttime = startTime.toLocaleTimeString([], { hour: '2-digit', minute:'2-digit' });
                card.dataset.endtime = endTime.toLocaleTimeString([], { hour: '2-digit', minute:'2-digit' });
                card.dataset.size = formatBytes(video.file_size || 0);
                card.dataset.fullUrl = video.video_url || '#';

                card.innerHTML = `
                    <div class="video-thumbnail">
                        <img src="https://via.placeholder.com/400x225.png/1a2a5f/ffffff?text=Video" alt="影片預覽">
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

    const modalOverlay = document.getElementById('videoModalOverlay');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalTitle = document.getElementById('modalTitle');
    const modalDownloadFull = document.getElementById('modalDownloadFull');

    function openModal(card) {
        if(!modalOverlay) return;
        modalTitle.textContent = `行程影片：${card.dataset.starttime} - ${card.dataset.endtime}`;
        modalDownloadFull.innerHTML = `<i class="fa-solid fa-download"></i> 下載完整影片 (${card.dataset.size})`;
        modalDownloadFull.href = card.dataset.fullUrl;
        modalOverlay.style.display = 'flex';
    };

    function closeModal() {
        if(modalOverlay) modalOverlay.style.display = 'none';
    };
    
    async function initializePage() {
        const pathParts = window.location.pathname.split('/');
        memberId = pathParts[pathParts.length - 1];

        if (!memberId) {
            document.body.innerHTML = '<h1>錯誤：未指定成員 ID</h1>';
            return;
        }

        try {
            const [videosRes, memberRes] = await Promise.all([
                fetchWithAuth(`/api/videos/?user_id=${memberId}`),
                fetchWithAuth(`/api/personnel/${memberId}/profile/`)
            ]);

            if (!videosRes.ok) throw new Error('無法獲取影片列表');
            const videoData = await videosRes.json();
            
            if (memberRes.ok) {
                const memberData = await memberRes.json();
                currentMemberName = memberData.first_name || memberData.username;
            } else {
                currentMemberName = `成員 #${memberId}`;
            }

            document.getElementById('page-title-username').textContent = currentMemberName;
            
            renderVideos(videoData.results || videoData);

        } catch(error) {
            console.error("載入影片頁面失敗:", error);
            document.getElementById('videos-list-container').innerHTML = '<p style="color: red;">載入資料失敗，您可能沒有權限查看此成員的影片。</p>';
        }
    }
    
    document.getElementById('videos-list-container')?.addEventListener('click', (event) => {
        const card = event.target.closest('.video-card');
        if (card) openModal(card);
    });

    modalCloseBtn?.addEventListener('click', closeModal);
    modalOverlay?.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    initializePage();
})();