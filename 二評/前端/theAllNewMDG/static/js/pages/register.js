document.addEventListener("DOMContentLoaded", () => {
  const termsBox = document.getElementById("termsBox");
  const agreeCheckbox = document.getElementById("agreeCheckbox");
  const submitBtn = document.getElementById("submitBtn");

  // --- 【以下為主要修改部分】 ---

  // 【新增】建立一個可重複呼叫的檢查函式
  function checkScroll() {
    const { scrollTop, scrollHeight, clientHeight } = termsBox;

    // 【修改】新的判斷條件：
    // 1. scrollHeight <= clientHeight  => 內容高度小於等於容器高度，代表不需要捲動
    // 2. scrollTop + clientHeight >= scrollHeight - 5 => 已經捲動到底部
    // 只要滿足其中一個條件，就啟用勾選框
    if (scrollHeight <= clientHeight || scrollTop + clientHeight >= scrollHeight - 5) {
      agreeCheckbox.disabled = false;
    }
  }

  // 條款滑動時，持續檢查
  termsBox.addEventListener("scroll", checkScroll);

  // 【新增】頁面載入完成後，立刻執行一次檢查，處理內容太短不需捲動的情況
  checkScroll();

  // --- 【修改結束，以下不變】 ---

  // 勾選後啟用送出按鈕
  agreeCheckbox.addEventListener("change", () => {
    submitBtn.disabled = !agreeCheckbox.checked;
  });

  // 聚焦動畫
  const fields = document.querySelectorAll("input, select");
  fields.forEach(field => {
    field.addEventListener("focus", () => {
      // 移除原有的 box-shadow 直接控制，讓 CSS :focus 偽類接管，效果更佳
    });
    field.addEventListener("blur", () => {
      // 移除原有的 box-shadow 直接控制
    });
  });

  // 照片預覽功能
  const photoInput = document.getElementById("photo");
  const photoPreview = document.getElementById("photoPreview");
  const photoBox = document.querySelector(".photo-upload");

  photoInput.addEventListener("change", () => {
    const file = photoInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => {
        photoPreview.src = e.target.result;
        photoPreview.style.display = "block"; // 確保圖片可見
        photoBox.classList.add("has-image");
      };
      reader.readAsDataURL(file);
    }
  });
});