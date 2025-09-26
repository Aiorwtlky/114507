document.addEventListener('DOMContentLoaded', () => {
    const messagesArea = document.getElementById('messagesArea');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');

    // 傳送訊息的函式
    function sendMessage() {
        const text = messageInput.value.trim();

        if (text === '') {
            return; // 不傳送空訊息
        }

        // 1. 建立並顯示使用者自己的訊息泡泡
        appendMessage(text, 'is-user');

        // 2. 清空輸入框
        messageInput.value = '';
        messageInput.style.height = 'auto'; // 將高度重設

        // 3. 模擬 AI 客服在短暫延遲後回覆
        setTimeout(() => {
            const replyText = `您好，關於「${text}」，我們的專員正在處理中，請稍候。`;
            appendMessage(replyText, 'is-admin');
        }, 1000); // 延遲 1 秒
    }

    // 將訊息泡泡加到畫面的函式
    function appendMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('msg-bubble', type);

        // 如果是管理員訊息，就加上名字的 div
        if (type === 'is-admin') {
            const authorDiv = document.createElement('div');
            authorDiv.classList.add('author-name');
            authorDiv.textContent = '吾仙';
            messageDiv.appendChild(authorDiv);
        }

        const textDiv = document.createElement('div');
        textDiv.classList.add('text');
        textDiv.textContent = text;

        messageDiv.appendChild(textDiv);
        messagesArea.appendChild(messageDiv);

        // 讓捲軸自動滾動到最下方
        messagesArea.scrollTop = messagesArea.scrollHeight;
    } // <-- 就是在這裡補上缺少的右大括號

    // --- 事件監聽 ---

    // 點擊傳送按鈕
    sendBtn.addEventListener('click', sendMessage);

    // 在輸入框按 Enter 鍵 (Shift+Enter 可換行)
    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // 防止預設的換行行為
            sendMessage();
        }
    });

    // 讓 textarea 高度可以自動增長
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = `${messageInput.scrollHeight}px`;
    });
});