// static/js/pages/chat.js

document.addEventListener('DOMContentLoaded', () => {
    const messagesArea = document.getElementById('messagesArea');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');

    let chatHistory = [];

    const initialGreeting = "您好！我是吾仙，是MDG的AI客服，請問有什麼可以為您服務的嗎？";
    appendMessage(initialGreeting, 'is-admin');
    chatHistory.push({ role: 'assistant', content: initialGreeting });

    async function sendMessage() {
        const text = messageInput.value.trim();
        if (text === '') return;

        chatHistory.push({ role: 'user', content: text });
        appendMessage(text, 'is-user');
        
        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendBtn.disabled = true;
        const thinkingBubble = appendMessage("吾仙思考中...", 'is-admin', { isTemporary: true });

        try {
            const response = await fetch('/api/proxy/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: chatHistory }),
            });

            thinkingBubble.remove();

            if (!response.ok) throw new Error(`伺服器錯誤: ${response.statusText}`);

            const data = await response.json();
            const aiReply = data.reply;

            chatHistory.push({ role: 'assistant', content: aiReply });
            appendMessage(aiReply, 'is-admin');

        } catch (error) {
            thinkingBubble.remove();
            console.error('Error:', error);
            appendMessage('抱歉，通訊時發生錯誤，請稍後再試。', 'is-admin');
        } finally {
            sendBtn.disabled = false;
            messageInput.focus();
        }
    }

    function appendMessage(text, type, options = {}) {
        const { isTemporary = false } = options;
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

        if (type === 'is-admin' && !isTemporary) {
            const feedbackContainer = document.createElement('div');
            feedbackContainer.className = 'feedback-controls';

            const likeBtn = document.createElement('button');
            likeBtn.className = 'feedback-btn like-btn';
            likeBtn.title = '喜歡這則回應';
            likeBtn.innerHTML = '<i class="fa-regular fa-thumbs-up"></i>';

            const dislikeBtn = document.createElement('button');
            dislikeBtn.className = 'feedback-btn dislike-btn';
            dislikeBtn.title = '不喜歡這則回應';
            dislikeBtn.innerHTML = '<i class="fa-regular fa-thumbs-down"></i>';
            
            feedbackContainer.appendChild(likeBtn);
            feedbackContainer.appendChild(dislikeBtn);
            messageDiv.appendChild(feedbackContainer);

            likeBtn.addEventListener('click', () => handleFeedback(1, text, likeBtn, dislikeBtn));
            dislikeBtn.addEventListener('click', () => handleFeedback(-1, text, likeBtn, dislikeBtn));
        }

        messagesArea.appendChild(messageDiv);
        messagesArea.scrollTop = messagesArea.scrollHeight;
        return messageDiv;
    }

    function handleFeedback(feedbackType, aiResponse, likeBtn, dislikeBtn) {
        likeBtn.disabled = true;
        dislikeBtn.disabled = true;

        if (feedbackType === 1) {
            console.log("使用者「喜歡」了回應:", aiResponse);
            likeBtn.classList.add('selected');
            likeBtn.innerHTML = '<i class="fa-solid fa-thumbs-up"></i>';
        } else {
            console.log("使用者「不喜歡」了回應:", aiResponse);
            dislikeBtn.classList.add('selected');
            dislikeBtn.innerHTML = '<i class="fa-solid fa-thumbs-down"></i>';
            const reason = prompt("感謝您的回饋，請問您不喜歡這則回應的原因是？(選填)");
            if (reason) {
                console.log("使用者留下的原因:", reason);
            }
        }
    }

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