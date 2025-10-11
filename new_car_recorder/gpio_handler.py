# gpio_handler.py
"""
GPIO 處理模組
負責與 Raspberry Pi Pico 通訊，接收 NFC 刷卡事件
"""

import serial
import threading
import time
from typing import Optional, Callable
import re


class GPIOHandler:
    def __init__(self, port: str = "/dev/cu.usbmodem1401", baudrate: int = 9600):
        """
        初始化 GPIO 處理器
        
        Args:
            port: 串列埠位置
            baudrate: 鮑率
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        
        # 執行緒控制
        self.is_running = False
        self.read_thread: Optional[threading.Thread] = None
        
        # 回調函式
        self.on_nfc_detected: Optional[Callable[[str], None]] = None
        
        # 嘗試連接
        self._connect()
    
    def _connect(self):
        """連接到串列埠"""
        try:
            print(f"[GPIOHandler] Attempting to connect to {self.port}...") 
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"[GPIOHandler] ✅ Connected to {self.port}")
        except Exception as e:
            print(f"[GPIOHandler] Failed to connect to {self.port}: {e}")
            print("[GPIOHandler] Running in DEMO mode (no hardware)")
            self.serial_conn = None
    
    def start(self):
        """啟動 GPIO 監聽"""
        if self.is_running:
            print("[GPIOHandler] Already running")
            return
        
        self.is_running = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        print("[GPIOHandler] Started")
    
    def stop(self):
        """停止 GPIO 監聽"""
        self.is_running = False
        if self.read_thread:
            self.read_thread.join(timeout=2)
        if self.serial_conn:
            self.serial_conn.close()
        print("[GPIOHandler] Stopped")
    
    def _read_loop(self):
        """讀取迴圈（在背景執行緒中運行）"""
        while self.is_running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    # 讀取一行資料
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if line:
                        self._process_line(line)
                else:
                    # 如果沒有硬體，模擬等待
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"[GPIOHandler] Read error: {e}")
                time.sleep(1)
    
    def _process_line(self, line: str):
        """
        處理從 Pico 接收到的資料
        
        預期格式：
        - NFC:A1:B2:C3:D4  (NFC 卡片被偵測到)
        - BUTTON:1  (按鈕被按下)
        """
        if line.startswith("NFC:"):
            # 提取 NFC UID
            nfc_uid = line.split(":", 1)[1]
            print(f"[GPIOHandler] NFC detected: {nfc_uid}")
            
            # 呼叫回調函式
            if self.on_nfc_detected:
                self.on_nfc_detected(nfc_uid)
        
        elif line.startswith("BUTTON:"):
            button_id = line.split(":", 1)[1]
            print(f"[GPIOHandler] Button pressed: {button_id}")
            # TODO: 處理按鈕事件
        
        else:
            print(f"[GPIOHandler] Unknown message: {line}")
    
    def simulate_nfc_scan(self, nfc_uid: str):
        """
        模擬 NFC 刷卡（用於測試）
        
        Args:
            nfc_uid: 模擬的 NFC UID
        """
        print(f"[GPIOHandler] SIMULATED NFC scan: {nfc_uid}")
        if self.on_nfc_detected:
            self.on_nfc_detected(nfc_uid)
    
    def send_command(self, command: str):
        """
        發送命令到 Pico
        
        Args:
            command: 命令字串
        """
        if self.serial_conn:
            try:
                self.serial_conn.write(f"{command}\n".encode('utf-8'))
                print(f"[GPIOHandler] Sent command: {command}")
            except Exception as e:
                print(f"[GPIOHandler] Send error: {e}")
        else:
            print(f"[GPIOHandler] Cannot send (no connection): {command}")