import os
import cv2
import time
from shared import utils
from shared.utils import ensure_dir_exists,  get_current_timestamp

class EventManager:
    def __init__(self, image_dir='./events/images/', video_dir='./events/videos/', record_seconds=10):
        self.image_dir = image_dir
        self.video_dir = video_dir
        self.record_seconds = record_seconds
        ensure_dir_exists(self.image_dir)
        ensure_dir_exists(self.video_dir)
        self.recording = False
        self.video_writer = None
        self.record_start_time = None

    def start_recording(self, frame_shape, timestamp):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_path = os.path.join(self.video_dir, f'alert_{timestamp}.mp4')
        self.video_writer = cv2.VideoWriter(video_path, fourcc, 20.0,
                                            (frame_shape[1], frame_shape[0]))
        self.recording = True
        self.record_start_time = time.time()
        return video_path

    def save_screenshot(self, frame, timestamp):
        image_path = os.path.join(self.image_dir, f'alert_{timestamp}.jpg')
        cv2.imwrite(image_path, frame)
        return image_path

    def record_frame(self, frame):
        if self.recording and self.video_writer is not None:
            self.video_writer.write(frame)

    def stop_recording(self):
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
        self.record_start_time = None

    def check_recording_timeout(self):
        if self.recording and (time.time() - self.record_start_time > self.record_seconds):
            self.stop_recording()
            return True
        return False
