window.addEventListener("DOMContentLoaded", () => {
  const spinner = document.querySelector(".spinner");
  const target = spinner.dataset.target; // 建議放在 HTML 上自訂 data-target="{{ target }}"

  setTimeout(() => {
    // 停止旋轉（直接清掉 animation）
    spinner.style.animation = "none";

    // 跳轉
    window.location.href = target;
  }, 2500);
});
