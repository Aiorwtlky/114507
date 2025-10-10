// static/js/pages/chat.js

document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:8000/api/chatbot/'; 
    const messagesArea = document.getElementById('messagesArea');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // ⚠️ 核心：儲存對話歷史。
    // 初始訊息 (來自 chat.html) 已經是 AI 助理的開場白，但為了多輪對話，我們將它加入歷史紀錄。
    let chatHistory = [
        // 初始 AI 訊息已經包含在 chat.html 中，我們將其視為 AI 的第一句回覆
        // 雖然後端會自動插入 system prompt，但為了對話連貫性，我們將 AI 的初始話術也加入歷史。
        { role: 'model', content: '您好！我是吾駕仙 AI 客服，請問有什麼可以為您服務的嗎？' }
    ];

    // 輔助函式：獲取 JWT Token 和 Header
    const getAuthHeaders = () => {
        // 【✅ 修改點 1】從實際的儲存位置獲取 Token
        // 假設 Token 儲存在 localStorage 中
        const token = localStorage.getItem('access_token') || 'DUMMY_TOKEN'; 
        return {
            'Content-Type': 'application/json',
            // 【✅ 修改點 2】加入 Authorization Header
            'Authorization': `Bearer ${token}` 
        };
    };

    // 輔助函式：將訊息泡泡加到畫面的函式 (沿用您的邏輯)
    function appendMessage(text, type) {
        // ... (這部分沿用您原本的邏輯)
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('msg-bubble', type);

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

        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    // 核心函式：傳送訊息給後端 API
    async function sendMessage() {
        const userText = messageInput.value.trim();

        if (userText === '') {
            return;
        }

        // 1. 建立並顯示使用者自己的訊息泡泡
        appendMessage(userText, 'is-user');

        // 2. 清空輸入框並重設高度
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // 3. 將使用者訊息加入歷史紀錄
        chatHistory.push({ role: 'user', content: userText });

        try {
            // 禁用按鈕防止重複送出
            sendBtn.disabled = true; 
            
            // 【✅ 修改點 3】呼叫真實的 API
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    // 【✅ 修改點 4】傳送完整的對話歷史給後端
                    messages: chatHistory 
                })
            });

            if (!response.ok) {
                // 處理 4xx/5xx 錯誤
                const errorData = await response.json().catch(() => ({error: '伺服器發生未知錯誤。'}));
                throw new Error(errorData.error || `API 錯誤: ${response.status}`);
            }

            const data = await response.json();
            const aiReply = data.reply; // 期望後端回傳 { "reply": "..." }

            // 4. 顯示 AI 客服的回覆
            appendMessage(aiReply, 'is-admin');
            
            // 5. 將 AI 回覆加入歷史紀錄
            chatHistory.push({ role: 'model', content: aiReply });

        } catch (error) {
            console.error("Chat API Error:", error);
            // 顯示錯誤訊息
            appendMessage(`連線失敗：${error.message || '無法取得 AI 回覆。請確認網路或登入狀態。'}`, 'is-admin');
            // 如果出錯，將剛剛加入的使用者訊息從歷史紀錄移除 (可選，但有助於重試)
            chatHistory.pop(); 
        } finally {
            sendBtn.disabled = false; // 重新啟用按鈕
        }
    }

    // --- 事件監聽 ---
    // (沿用您原本的邏輯，無需修改)
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