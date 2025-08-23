document.addEventListener('DOMContentLoaded', () => {
  const toggleButton = document.querySelector('.all-reports-toggle');
  const reportCards = document.querySelectorAll('.report-card');

  // 如果按鈕不存在，或報表數量不足，就隱藏按鈕並結束
  if (!toggleButton || reportCards.length <= 3) {
    if (toggleButton) toggleButton.parentElement.style.display = 'none';
    return;
  }

  const initialVisible = 3;
  const hiddenCards = Array.from(reportCards).slice(initialVisible);

  // 預設先為要隱藏的卡片加上 is-hidden class
  hiddenCards.forEach(card => card.classList.add('is-hidden'));

  let expanded = false;

  toggleButton.addEventListener('click', () => {
    expanded = !expanded;

    // 只需要切換 is-hidden class 即可，CSS 會自動處理動畫
    hiddenCards.forEach(card => {
      card.classList.toggle('is-hidden', !expanded);
    });

    // 更新按鈕文字和圖示
    const buttonText = toggleButton.querySelector('span');
    const buttonIcon = toggleButton.querySelector('i');
    
    buttonText.textContent = expanded ? '查看較少報表' : '查看更多報表';
    buttonIcon.style.transform = expanded ? 'rotate(180deg)' : 'rotate(0deg)';
  });
});