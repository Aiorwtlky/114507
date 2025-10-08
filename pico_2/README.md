# Raspberry Pi Pico 2 - GPIO 狀態回傳模組

本模組使用 Raspberry Pi Pico 2（RP2350），透過 USB 串列方式回傳 3 個 GPIO 腳位的狀態，供 Raspberry Pi 5 查詢。

## 腳位定義

| 名稱   | GPIO |
|--------|------|
| left   | 17   |
| right  | 27   |
| rear   | 22   |

## 功能說明

- 接收主機傳入指令 `STATUS`
- 回傳 GPIO 狀態（格式為 `1,0,1`）
- 可與主機端 Flask API 搭配查詢實體按鈕狀態

## 使用說明

1. 將 MicroPython 韌體燒錄至 Pico 2
2. 上傳已設定好 GPIO 腳位的 `main.py` 程式
3. 主機透過 `/dev/ttyACM0` 發送 `STATUS` 指令，即可取得 GPIO 狀態

## 相容性

- 適用板子：Raspberry Pi Pico 2（RP2350）
- 連接方式：USB 串列通訊（CDC）
- 主機需具備 `pyserial` 套件