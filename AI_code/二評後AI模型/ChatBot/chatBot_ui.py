import streamlit as st
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# 載入環境變數
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# 初始化 Hugging Face 客戶端
client = InferenceClient(
    provider="featherless-ai",
    api_key=HF_TOKEN,
)

# 🧠 吾仙角色定義（System Prompt）
system_prompt = """
你是「吾仙」，是吾駕仙智慧交通系統中的智慧助理。
你的任務是協助駕駛者理解他們的駕駛行為評分、違規紀錄、AI 分析建議，並提供改善方向與安全提醒。

【你可以回答的主題如下】：
1. 行車評分總結
2. 違規紀錄與扣分原因
3. AI 行車建議與改善方式
4. 疲勞、盲區、內輪差等駕駛風險分析
5. 常見疑問，例如「吾仙怎麼判斷我疲勞？」

【你應避免的內容】：
- 不回答與交通無關的問題（如寫程式、問笑話等）
- 不提及自身是 AI、模型或技術原理

請依據上傳的報表內容（如有）進行輔助說明，並保持條列式、親切、中文敬語風格。
"""

# ✅ 頁面設定
st.set_page_config(page_title="吾仙智慧助理", page_icon="🧠")
st.title("🧠 吾仙 - 智慧交通對話助理")

# ✅ 聊天初始化（含歡迎訊息）
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "您好，我是吾仙智慧交通助理。\n\n我可以協助您：\n- 查看行車評分與違規紀錄\n- 解釋 AI 報表內容\n- 提供行車安全建議與改善方向\n\n請問您有什麼需要我協助的呢？"}
    ]

# ✅ 顯示聊天紀錄（含歡迎詞）
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ✅ 檔案上傳（.txt 格式）
uploaded_knowledge = ""
uploaded_file = st.file_uploader("📤 上傳 AI 報表（txt 格式）", type=["txt"])
if uploaded_file:
    uploaded_knowledge = uploaded_file.read().decode("utf-8")
    st.success("✅ 報表已上傳，吾仙會根據內容協助您回答。")

# ✅ 使用者輸入
user_input = st.chat_input("請輸入您的問題...")
if user_input:
    # 顯示使用者輸入
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 組合 prompt（包含報表內容）
    all_messages = st.session_state.messages.copy()
    if uploaded_knowledge:
        all_messages.insert(1, {
            "role": "user",
            "content": f"以下是 AI 報表內容，請依據此資料進行分析輔助：\n\n{uploaded_knowledge}"
        })

    # 呼叫模型
    with st.spinner("吾仙正在思考中..."):
        try:
            response = client.chat.completions.create(
                model="Qwen/Qwen2.5-14B-Instruct",
                messages=all_messages,
            )
            reply = response.choices[0].message["content"]
        except Exception as e:
            reply = f"❌ 系統錯誤：{str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
