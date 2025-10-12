# test_gcp.py - 獨立的 GCP 連線測試腳本

import os
import vertexai
from vertexai.generative_models import GenerativeModel

# ▼▼▼【 唯一需要您手動修改的地方 】▼▼▼
# 請將這裡的路徑，換成您電腦上「新金鑰檔案」的「絕對路徑」。
# Mac範例: '/Users/joych53/114507/後端/114507BN/secrets/YOUR_NEW_KEY.json'
# Windows範例: 'C:\\Users\\supernova\\Desktop\\114507\\後端\\114507BN\\secrets\\YOUR_NEW_KEY.json'
#
# (請務必確認這是從「MDG Backend Test」這個新專案下載的金鑰)
#
KEY_FILE_PATH = "/Users/joych53/114507/後端/114507BN/bn/secrets/mdg_gemini.json"
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

# --- 以下程式碼無需修改 ---

PROJECT_ID = "mdg-backend-test"
LOCATION = "us-central1"
MODEL_NAME = "gemini-1.0-pro"

def run_test():
    """執行最直接的 Vertex AI API 呼叫測試"""
    print("=========================================================")
    print("🚀 開始執行獨立的 GCP 連線診斷測試...")
    
    if KEY_FILE_PATH == "請在這裡貼上您的金鑰檔案的絕對路徑":
        print("❌ 錯誤：請先修改 test_gcp.py 檔案，填寫 KEY_FILE_PATH 的絕對路徑。")
        return

    try:
        # 1. 強制設定環境變數，確保使用的是正確的金鑰
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_FILE_PATH
        print(f"✅ 步驟 1/4: 已強制設定認證檔案路徑為 -> {KEY_FILE_PATH}")

        # 2. 初始化 Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print(f"✅ 步驟 2/4: Vertex AI 初始化成功 (專案: {PROJECT_ID})")

        # 3. 載入模型
        model = GenerativeModel(MODEL_NAME)
        print(f"✅ 步驟 3/4: 成功載入模型 '{MODEL_NAME}'")

        # 4. 發送請求
        print("⏳ 步驟 4/4: 正在向 Gemini 發送請求...")
        response = model.generate_content("Hello")
        
        print("\n🎉🎉🎉 診斷成功！🎉🎉🎉")
        print("已成功收到來自 Google Gemini 的回覆！")
        print(f"收到的回覆內容: {response.text}")
        print("\n這證明您的本地環境、Python 套件和金鑰檔案都是正常的。")

    except Exception as e:
        print("\n🔥🔥🔥 診斷失敗 🔥🔥🔥")
        print("在直接呼叫 API 時發生錯誤，這幾乎可以肯定是您的 Google Cloud 帳戶或專案本身的問題。")
        print("\n--- 詳細錯誤訊息 ---")
        print(e)
        print("--------------------")
        print("\n建議的下一步：請帶著這個錯誤訊息聯繫 Google Cloud 技術支援。")

if __name__ == "__main__":
    run_test()