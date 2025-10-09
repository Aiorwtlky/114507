# dummy_gpio.py
from pynput import keyboard

class GPIOSimulator:
    def __init__(self):
        self.left_signal_on = False
        self.right_signal_on = False
        self._nfc_scan_event = False
        self._mode_switch_event = False
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()
        print("GPIO Simulator started:")
        print("  - 'n': NFC Scan | 'l'/'r': Turn Signals | 'Tab': Switch Mode | 'q': Quit")

    def _on_press(self, key):
        if key == keyboard.Key.tab:
            print("[GPIO SIM] Mode Switch key (Tab) detected!")
            self._mode_switch_event = True
            return

        try:
            char = key.char.lower()
            if char == 'n':
                print("[GPIO SIM] NFC scan detected!")
                self._nfc_scan_event = True
            elif char == 'l':
                if not self.left_signal_on:
                    self.left_signal_on = True
                    print("[GPIO SIM] Left turn signal is now ON")
            elif char == 'r':
                if not self.right_signal_on:
                    self.right_signal_on = True
                    print("[GPIO SIM] Right turn signal is now ON")
        except AttributeError:
            pass
            
    def _on_release(self, key):
        # 為了模擬真實方向燈（按著才亮，放開就滅），我們在放開時關閉
        try:
            char = key.char.lower()
            if char == 'l':
                self.left_signal_on = False
                print("[GPIO SIM] Left turn signal is now OFF")
            elif char == 'r':
                self.right_signal_on = False
                print("[GPIO SIM] Right turn signal is now OFF")
        except AttributeError:
            pass

    def check_mode_switch(self):
        if self._mode_switch_event:
            self._mode_switch_event = False
            return True
        return False

    def check_nfc_scan(self):
        if self._nfc_scan_event:
            self._nfc_scan_event = False
            return True
        return False

    def is_left_on(self):
        return self.left_signal_on

    def is_right_on(self):
        return self.right_signal_on

    def stop(self):
        self.listener.stop()