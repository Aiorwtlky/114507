// 獲取 DOM 元素
const chatWindow = document.getElementById('chat-window');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const uploadImage = document.getElementById('upload-image');

// 傳送訊息功能
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        appendMessage(message, 'user'); // 使用者訊息
        appendMessage('已收到訊息！', 'bot'); // 機器人回覆
        messageInput.value = ''; // 清空輸入框
    }
}

// 添加訊息到對話框
function appendMessage(content, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender); // 根據 sender 類型設置樣式
    messageElement.textContent = content;
    chatWindow.appendChild(messageElement);
    scrollToBottom();
}

// 上傳圖片功能
uploadImage.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && isValidImage(file)) {
        const reader = new FileReader();
        reader.onload = function () {
            appendImage(reader.result, 'user');
            appendMessage('已收到圖片！', 'bot'); // 機器人回覆
        };
        reader.readAsDataURL(file);
    } else {
        alert('請上傳小於 5MB 且格式為 jpg/jpeg/png 的圖片');
    }
});

// 驗證圖片格式和大小
function isValidImage(file) {
    const validTypes = ['image/jpeg', 'image/png'];
    return validTypes.includes(file.type) && file.size <= 5 * 1024 * 1024;
}

// 添加圖片到對話框並滾動到底部
function appendImage(imageSrc, sender) {
    const imageElement = document.createElement('img');
    imageElement.src = imageSrc;
    imageElement.classList.add('message-image');
    
    const wrapper = document.createElement('div');
    wrapper.classList.add('message', sender);
    wrapper.appendChild(imageElement);
    
    chatWindow.appendChild(wrapper);

    // 等圖片加載完成後滾動到底部
    imageElement.onload = () => {
        scrollToBottom();
    };
}

// 自動滾動到底部
function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}



// 綁定按鈕點擊事件
sendButton.addEventListener('click', sendMessage);

// 綁定 Enter 鍵事件
messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
