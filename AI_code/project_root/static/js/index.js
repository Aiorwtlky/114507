// index.js - 首頁功能按鈕效果與初始化腳本

console.log('Index page loaded.');

document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.btn-card');

    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'scale(1.05)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'scale(1.0)';
        });
    });
});
