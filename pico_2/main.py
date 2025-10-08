from machine import Pin
import sys

left = Pin(17, Pin.IN, Pin.PULL_UP)
right = Pin(27, Pin.IN, Pin.PULL_UP)
rear = Pin(22, Pin.IN, Pin.PULL_UP)

while True:
    try:
        cmd = sys.stdin.readline().strip()
        if cmd == "STATUS":
            result = {
                "left": 0 if left.value() else 1,
                "right": 0 if right.value() else 1,
                "rear": 0 if rear.value() else 1
            }
            print(f"{result['left']},{result['right']},{result['rear']}")
    except Exception as e:
        print("ERROR:", e)
