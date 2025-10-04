document.addEventListener('DOMContentLoaded', function() {
  const tripList = document.getElementById('tripList');
  
  // Modal 相關元素
  const modalOverlay = document.getElementById('feedback-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const cancelFeedbackBtn = document.getElementById('cancel-feedback-btn');
  const submitFeedbackBtn = document.getElementById('submit-feedback-btn');
  const feedbackTextarea = document.getElementById('feedback-textarea');
  const feedbackViolationIdInput = document.getElementById('feedback-violation-id');
  const feedbackEmailInput = document.getElementById('feedback-email');

  // 打開 modal 的函式
  function openModal(violationId) {
    if (!modalOverlay) return;
    feedbackViolationIdInput.value = violationId;
    modalOverlay.classList.remove('hidden');
  }

  // 關閉 modal 的函式
  function closeModal() {
    if (!modalOverlay) return;
    feedbackTextarea.value = '';
    feedbackViolationIdInput.value = '';
    feedbackEmailInput.value = '';
    modalOverlay.classList.add('hidden');
  }

  // 處理讚/倒讚的點擊
  if (tripList) {
    tripList.addEventListener('click', function(e) {
      const targetIcon = e.target;
      if (!targetIcon.matches('.fa-thumbs-up') && !targetIcon.matches('.fa-thumbs-down')) {
        return;
      }

      const parent = targetIcon.parentElement;
      const coachTag = targetIcon.closest('.coach-tag');
      const violationId = coachTag.dataset.violationId;
      
      const thumbsUp = parent.querySelector('.fa-thumbs-up');
      const thumbsDown = parent.querySelector('.fa-thumbs-down');
      
      const isAlreadyActive = targetIcon.classList.contains('active');
      let feedbackType = 'none';

      // 重設狀態
      thumbsUp.classList.remove('active', 'like', 'fa-solid');
      thumbsUp.classList.add('fa-regular');
      thumbsDown.classList.remove('active', 'dislike', 'fa-solid');
      thumbsDown.classList.add('fa-regular');
      
      if (!isAlreadyActive) {
        targetIcon.classList.add('active');
        targetIcon.classList.remove('fa-regular');
        targetIcon.classList.add('fa-solid');
        
        if (targetIcon.classList.contains('fa-thumbs-up')) {
          targetIcon.classList.add('like');
          feedbackType = 'like';
        } else {
          targetIcon.classList.add('dislike');
          feedbackType = 'dislike';
          openModal(violationId); // 點擊倒讚時打開 modal
        }
      }
      
      // 呼叫後台 API (傳送 like/dislike/none)
      fetch('/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          violation_id: violationId,
          feedback: feedbackType,
        }),
      })
      .then(response => response.ok ? response.json() : Promise.reject('Network response was not ok.'))
      .then(data => console.log('Like/Dislike feedback success:', data))
      .catch(error => console.error('Like/Dislike feedback error:', error));
    });
  }

  // 為 modal 上的按鈕加上事件監聽
  if (modalOverlay) {
    closeModalBtn.addEventListener('click', closeModal);
    cancelFeedbackBtn.addEventListener('click', closeModal);
    
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === modalOverlay) { closeModal(); }
    });

    submitFeedbackBtn.addEventListener('click', function() {
      const violationId = feedbackViolationIdInput.value;
      const feedbackText = feedbackTextarea.value;
      const feedbackEmail = feedbackEmailInput.value;

      console.log(`準備提交文字回饋: ID=${violationId}, 內容=${feedbackText}, Email=${feedbackEmail}`);
      
      // 呼叫 API 提交文字
      fetch('/submit_feedback_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          violation_id: violationId,
          text: feedbackText,
          email: feedbackEmail,
        }),
      })
      .then(response => response.ok ? response.json() : Promise.reject('Network response was not ok.'))
      .then(data => {
        console.log('Text feedback success:', data);
        closeModal();
      })
      .catch(error => {
        console.error('Text feedback error:', error);
        alert('提交失敗，請稍後再試。');
      });
    });
  }

  // 分頁按鈕邏輯
  const tabAll = document.getElementById('tab-all');
  const tabAttn = document.getElementById('tab-attn');
  const allTrips = document.querySelectorAll('.coach-trip');

  function filterTrips() {
      const showAttnOnly = tabAttn.classList.contains('is-active');
      allTrips.forEach(trip => {
          const needsAttention = trip.dataset.attn === '1';
          if (showAttnOnly) {
              trip.style.display = needsAttention ? 'flex' : 'none';
          } else {
              trip.style.display = 'flex';
          }
      });
  }

  if (tabAll && tabAttn) {
      tabAll.addEventListener('click', () => {
          tabAll.classList.add('is-active');
          tabAttn.classList.remove('is-active');
          filterTrips();
      });

      tabAttn.addEventListener('click', () => {
          tabAttn.classList.add('is-active');
          tabAll.classList.remove('is-active');
          filterTrips();
      });
  }
});
