<template>
  <div class="chat-container">
    <header>
      <h1>內輪差智慧客服</h1>
    </header>

    <div class="chat-window" ref="chatWindow">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.sender]"
      >
        <img v-if="msg.type === 'image'" :src="msg.content" class="message-image" />
        <span v-else>{{ msg.content }}</span>
      </div>
    </div>

    <div class="input-area">
      <label for="upload-image" id="upload-image-label">
        📎
        <input
          type="file"
          id="upload-image"
          @change="handleImageUpload"
          accept=".jpg,.jpeg,.png"
          hidden
        />
      </label>

      <input
        type="text"
        v-model="message"
        @keypress.enter="sendMessage"
        placeholder="輸入訊息..."
        id="message-input"
      />
      <button @click="sendMessage" id="send-button">⬆</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: '',
      messages: [],
    };
  },
  methods: {
    sendMessage() {
      const text = this.message.trim();
      if (!text) return;
      this.appendMessage(text, 'user');
      this.appendMessage('已收到訊息！', 'bot');
      this.message = '';
    },
    appendMessage(content, sender, type = 'text') {
      this.messages.push({ content, sender, type });
      this.$nextTick(() => {
        const chatWindow = this.$refs.chatWindow;
        chatWindow.scrollTop = chatWindow.scrollHeight;
      });
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file && this.isValidImage(file)) {
        const reader = new FileReader();
        reader.onload = () => {
          this.appendMessage(reader.result, 'user', 'image');
          this.appendMessage('已收到圖片！', 'bot');
        };
        reader.readAsDataURL(file);
      } else {
        alert('請上傳小於 5MB 且格式為 jpg/jpeg/png 的圖片');
      }
    },
    isValidImage(file) {
      const validTypes = ['image/jpeg', 'image/png'];
      return validTypes.includes(file.type) && file.size <= 5 * 1024 * 1024;
    },
  },
};
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
  background-color: #333;
  color: #fff;
  margin: 0;
  padding: 0;
}

.chat-container {
  max-width: 600px;
  min-width: 300px;
  height: 90vh;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background-color: #444;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

header {
  background-color: #555;
  padding: 10px;
  text-align: center;
}

header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #DDB76B;
}

.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background-color: #222;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scrollbar-color: #DDB76B #333;
  scrollbar-width: thin;
}

.message.user {
  background-color: #DDB76B;
  padding: 8px 12px;
  border-radius: 8px;
  max-width: 80%;
  align-self: flex-end;
  color: #333;
}

.message.bot {
  background-color: #555;
  padding: 8px 12px;
  border-radius: 8px;
  max-width: 80%;
  align-self: flex-start;
  color: white;
}

.message-image {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 8px;
  border: 2px solid #DDB76B;
  display: block;
  margin: 5px auto;
}

.input-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: #444;
  border-top: 2px solid #333;
}

#upload-image-label {
  background-color: #555;
  color: #fff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s, box-shadow 0.3s;
}

#upload-image-label:hover {
  background-color: #C49E5A;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

#send-button {
  background: none;
  border: none;
  color: #DDB76B;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  margin-top: -4px;
}

#send-button:hover {
  color: #C49E5A;
}

#message-input {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 20px;
  font-size: 1rem;
  outline: none;
  color: #333;
  background-color: #fff;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

#message-input::placeholder {
  color: #999;
  font-style: italic;
}
</style>
