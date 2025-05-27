import unittest
from edge_device.event_manager import EventManager  # 假設你有事件管理類別
import os

class TestEventManager(unittest.TestCase):
    def setUp(self):
        self.em = EventManager()
        self.test_image_path = 'tests/test_image.jpg'
        self.test_video_path = 'tests/test_video.mp4'

    def test_save_screenshot(self):
        result = self.em.save_screenshot(self.test_image_path)
        self.assertTrue(os.path.exists(self.test_image_path))

    def test_record_event(self):
        event_data = {
            'detected_objects': [{'class': 'person', 'confidence': 0.95, 'bbox': [10,10,100,200]}],
            'image_path': self.test_image_path,
            'video_path': self.test_video_path,
        }
        saved = self.em.record_event(event_data)
        self.assertTrue(saved)

if __name__ == '__main__':
    unittest.main()
