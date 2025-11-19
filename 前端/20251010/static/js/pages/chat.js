// static/js/pages/chat.js

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000';
    const API_URL = `${API_BASE_URL}/api/chatbot/`;
    const messagesArea = document.getElementById('messagesArea');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // 儲存對話歷史
    let chatHistory = [
        { role: 'model', content: '您好！我是吾仙 AI 客服，請問有什麼可以為您服務的嗎？' }
    ];

    /**
     * 執行一個帶有認證標頭的 fetch 請求
     * @param {string} endpoint - API 的端點
     * @param {object} options - fetch 的設定選項
     * @returns {Promise<Response>}
     */
    async function fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');
        
        if (!token) {
            // 如果沒有 token，直接提示並導向登入頁
            alert('您尚未登入或登入已逾時，無法使用此功能。');
            window.location.href = '/login';
            throw new Error('Not Authenticated');
        }

        const headers = options.headers || new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        if (!(options.body instanceof FormData)) {
            headers.append('Content-Type', 'application/json');
        }

        const response = await fetch(endpoint, { ...options, headers });
        
        if (response.status === 401) {
            alert('您的登入已過期，請重新登入。');
            localStorage.clear();
            window.location.href = '/login';
            throw new Error('Token Expired');
        }
        return response;
    }

    // 將訊息泡泡加到畫面的函式
    function appendMessage(text, type, author = '吾仙') {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('msg-bubble', type);

        if (type === 'is-admin') {
            const authorDiv = document.createElement('div');
            authorDiv.classList.add('author-name');
            authorDiv.textContent = author;
            messageDiv.appendChild(authorDiv);
        }

        const textDiv = document.createElement('div');
        textDiv.classList.add('text');
        textDiv.textContent = text;

        messageDiv.appendChild(textDiv);
        messagesArea.appendChild(messageDiv);
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    // 核心函式：傳送訊息給後端 API
    async function sendMessage() {
        const userText = messageInput.value.trim();
        if (userText === '') return;

        appendMessage(userText, 'is-user');
        messageInput.value = '';
        messageInput.style.height = 'auto';
        chatHistory.push({ role: 'user', content: userText });

        try {
            sendBtn.disabled = true; 
            
            const response = await fetchWithAuth(API_URL, {
                method: 'POST',
                body: JSON.stringify({
                    messages: chatHistory 
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ reply: '伺服器發生未知錯誤。' }));
                throw new Error(errorData.reply || `API 錯誤: ${response.status}`);
            }

            const data = await response.json();
            const aiReply = data.reply;

            appendMessage(aiReply, 'is-admin');
            chatHistory.push({ role: 'model', content: aiReply });

        } catch (error) {
            console.error("Chat API Error:", error);
            appendMessage(`連線失敗：${error.message || '無法取得 AI 回覆。'}`, 'is-admin');
            chatHistory.pop(); 
        } finally {
            sendBtn.disabled = false;
        }
    }

    // --- 事件監聽 ---
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = `${messageInput.scrollHeight}px`;
    });
});