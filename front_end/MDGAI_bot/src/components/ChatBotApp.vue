<template>
  <div class="chat-container">
    <header><h1>MDG智慧客服系統</h1></header>
    <div class="chat-window" ref="chatWindow">
      <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.sender]">
        <img v-if="msg.type === 'image'" :src="msg.content" class="message-image" />
        <div class="message-bubble" v-else>{{ msg.content }}</div>
      </div>
    </div>
    <div class="input-area">
      <label for="upload-image" id="upload-image-label">📎
        <input type="file" id="upload-image" @change="handleImageUpload" accept=".jpg,.jpeg,.png" hidden />
      </label>
      <input type="text" v-model="message" @keypress.enter="sendMessage" placeholder="輸入訊息..." id="message-input" />
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
  mounted() {
    // 預設歡迎訊息
    this.appendMessage('您好，我是 MDG 智慧客服。\n我們的專題是以 AI 模型與多鏡頭系統偵測大型車輛內輪差危險情境，歡迎提問！', 'bot');
  },
  methods: {
    sendMessage() {
      const text = this.message.trim();
      if (!text) return;
      this.appendMessage(text, 'user');

      let reply = '請問您需要什麼幫助？';
      const lower = text.toLowerCase();

      if (lower.includes('內輪差')) {
        reply = '「內輪差」是指大型車轉彎時，後輪走的路徑會比前輪更內側，容易產生視野死角。';
      } else if (lower.includes('系統') && lower.includes('判斷')) {
        reply = '本系統透過 YOLO AI 模型與多鏡頭偵測，辨識行人、車輛是否進入危險區域。';
      } else if (lower.includes('鏡頭') && (lower.includes('裝') || lower.includes('安裝'))) {
        reply = '建議於車輛左右後方與盲點處共安裝多顆鏡頭，以完整覆蓋內輪差區域。';
      }

      this.appendMessage(reply, 'bot');
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
.chat-container {
  max-width: 600px;
  height: 90vh;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background-color: #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  color: white;
  box-shadow: 0 0 20px rgba(255, 165, 0, 0.3);
  font-family: 'Segoe UI', sans-serif;
}
header {
  background-color: #2b2b2b;
  padding: 12px;
  text-align: center;
  font-size: 1.3rem;
  font-weight: bold;
  color: #ff9933;
}
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background-color: #121212;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.message {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}
.message.user {
  align-self: flex-end;
}
.message.bot {
  align-self: flex-start;
}
.message-bubble {
  background-color: #333;
  padding: 10px 14px;
  border-radius: 14px;
  color: white;
  font-size: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.message.user .message-bubble {
  background-color: #ff9933;
  color: #111;
}
.message-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 10px;
  border: 2px solid #ff9933;
  margin-top: 5px;
}
.input-area {
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: #2b2b2b;
  border-top: 1px solid #444;
}
#upload-image-label {
  background-color: #444;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 1.2rem;
}
#send-button {
  background: none;
  border: none;
  color: #ff9933;
  font-size: 1.6rem;
  cursor: pointer;
}
#message-input {
  flex: 1;
  padding: 10px 15px;
  border-radius: 20px;
  border: none;
  font-size: 1rem;
  outline: none;
  background-color: #fff;
  color: #000;
}
</style>
