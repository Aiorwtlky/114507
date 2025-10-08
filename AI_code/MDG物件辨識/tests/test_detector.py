import unittest
from edge_device.yolo_detector import detect_objects  # 假設你的偵測函式名稱

class TestYoloDetector(unittest.TestCase):
    def test_detect_objects_returns_list(self):
        # 測試傳入模擬影像能回傳物件列表
        dummy_image = None  # 可用cv2.imread讀取測試圖片
        results = detect_objects(dummy_image)
        self.assertIsInstance(results, list)
        if results:
            self.assertIn('class', results[0])
            self.assertIn('confidence', results[0])
            self.assertIn('bbox', results[0])

if __name__ == '__main__':
    unittest.main()
