document.addEventListener('DOMContentLoaded', () => {
    // --- 元素選取 ---
    const videoCards = document.querySelectorAll('.video-card');
    const modalOverlay = document.getElementById('videoModalOverlay');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    
    // 檢查核心元素是否存在，如果不存在就直接返回，避免後續報錯
    if (!modalOverlay || !modalCloseBtn || videoCards.length === 0) {
        console.error('Modal elements or video cards not found. Interaction will not work.');
        return;
    }

    const modalTitle = document.getElementById('modalTitle');
    const modalDownloadFull = document.getElementById('modalDownloadFull');
    const modalSegmentList = document.getElementById('modalSegmentList');

    // --- 函數定義 ---
    const openModal = (card) => {
        const startTimeStr = card.dataset.starttime;
        const endTimeStr = card.dataset.endtime;
        const size = card.dataset.size;
        
        if (!startTimeStr || !endTimeStr || !size) {
            console.error('Card is missing data attributes.');
            return;
        }

        modalTitle.textContent = `行程影片：${startTimeStr} - ${endTimeStr}`;
        modalDownloadFull.innerHTML = `<i class="fa-solid fa-download"></i> 下載完整行程影片 (${size})`;
        modalSegmentList.innerHTML = '';

        const segments = generateTimeSegments(startTimeStr, endTimeStr);
        if (segments.length > 0) {
            segments.forEach(segment => {
                const segmentEl = document.createElement('div');
                segmentEl.className = 'segment-item';
                // 暫時將按鈕的連結設為 #
                segmentEl.innerHTML = `
                    <span class="segment-time">${segment.start} - ${segment.end}</span>
                    <div class="segment-actions">
                        <button type="button" class="btn btn-secondary btn-sm">播放</button>
                        <a href="#" class="btn btn-primary btn-sm">下載</a>
                    </div>
                `;
                modalSegmentList.appendChild(segmentEl);
            });
        } else {
            modalSegmentList.innerHTML = '<p class="no-videos-message">無法生成影片區段。</p>';
        }

        modalOverlay.style.display = 'flex';
    };

    const closeModal = () => {
        modalOverlay.style.display = 'none';
    };

    // 輔助函數：生成時間區段
    function generateTimeSegments(startTime, endTime) {
        const segments = [];
        // 加上 try-catch 以免時間格式錯誤導致整個腳本崩潰
        try {
            let current = new Date(`1970-01-01T${startTime}:00`);
            const end = new Date(`1970-01-01T${endTime}:00`);

            if (isNaN(current.getTime()) || isNaN(end.getTime())) {
                throw new Error('Invalid time format');
            }

            while (current < end) {
                const segmentStart = current;
                const segmentEnd = new Date(current.getTime() + 15 * 60000);

                const startStr = segmentStart.toTimeString().substring(0, 5);
                const endStr = segmentEnd > end ? endTime : segmentEnd.toTimeString().substring(0, 5);
                
                segments.push({ start: startStr, end: endStr });
                
                current = segmentEnd;
            }
        } catch (error) {
            console.error("Error generating time segments:", error);
            return []; // 返回空陣列
        }
        return segments;
    }

    // --- 事件監聽 ---
    videoCards.forEach(card => {
        card.addEventListener('click', () => openModal(card));
    });

    modalCloseBtn.addEventListener('click', closeModal);

    modalOverlay.addEventListener('click', (e) => {
        // 確保點擊的是灰色背景本身，而不是裡面的白色 content
        if (e.target === modalOverlay) {
            closeModal();
        }
    });
});