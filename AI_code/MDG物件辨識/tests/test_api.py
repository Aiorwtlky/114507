import unittest
from server.app import app

class TestApi(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_event_upload(self):
        payload = {
            'device_serial': 'TEST123',
            'event_time': '2025-05-28T12:00:00',
            'camera_position': 'left',
            'detected_objects': [{'class': 'person', 'confidence': 0.9, 'bbox': [10, 20, 100, 200]}],
            'image_path': '/path/to/image.jpg',
            'video_path': '/path/to/video.mp4'
        }
        response = self.app.post('/api/events/upload', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json['status'])

if __name__ == '__main__':
    unittest.main()
