document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.querySelector('.all-reports-toggle');
    const reportCards = document.querySelectorAll('.report-card');
  
    if (!toggleButton || reportCards.length <= 3) {
      // 沒有按鈕或報表數太少，不需要功能
      if (toggleButton) toggleButton.style.display = 'none';
      return;
    }
  
    const initialVisible = 3;
    const hiddenCards = Array.from(reportCards).slice(initialVisible);
  
    // 預設先隱藏後面的報表
    hiddenCards.forEach(card => card.style.display = 'none');
  
    let expanded = false;
  
    toggleButton.addEventListener('click', () => {
      expanded = !expanded;
  
      hiddenCards.forEach(card => {
        card.style.display = expanded ? 'block' : 'none';
      });
  
      toggleButton.textContent = expanded ? '查看較少報表' : '查看更多報表';
    });
  });
  