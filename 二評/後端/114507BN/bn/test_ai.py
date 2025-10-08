# test_ai.py
from transformers import pipeline, set_seed
import time

print("正在載入 AI 模型，第一次可能會需要幾分鐘下載...")
start_time = time.time()
# 確保使用和您 service.py 中完全相同的模型
try:
    generator = pipeline('text-generation', model='uer/gpt2-chinese-cluecorpussmall')
    load_time = time.time() - start_time
    print(f"模型載入完成！耗時: {load_time:.2f} 秒")
    print("-" * 50)
except Exception as e:
    print(f"模型載入失敗，錯誤訊息: {e}")
    exit()


# 這是我們在 service.py 中使用的 prompt
event_summary = "1 次「車道偏離 (未打方向燈)」"
prompt = f"針對一次駕駛行為分析，該駕駛的危險事件摘要如下：{event_summary}。請根據這些事件，以一位專業駕駛教練的口吻，提供一段大約50字的簡短、溫和且具體的改善建議："

print("使用的 Prompt (提示詞):")
print(prompt)
print("-" * 50)

print("正在生成建議...")
set_seed(42) # 固定隨機種子以確保結果可重現
start_time = time.time()

# 執行生成，我們也可以加入一些額外參數來調整行為
outputs = generator(
    prompt, 
    max_length=150, 
    num_return_sequences=1,
    # no_repeat_ngram_size=2, # 防止重複詞語
    # temperature=0.7, # 讓回答不那麼死板
)

generation_time = time.time() - start_time
print(f"生成完成！耗時: {generation_time:.2f} 秒")
print("-" * 50)

# 清理並印出結果
generated_text = outputs[0]['generated_text']
suggestion = generated_text.replace(prompt, "").strip()

print("AI 模型生成的原始建議:")
print(suggestion)