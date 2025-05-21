import cv2

class MultiObjectTracker:
    def __init__(self):
        self.multiTracker = cv2.legacy.MultiTracker_create()
        self.tracking = False
        self.colors = [(0,0,255), (0,255,255), (0,255,0), (255,0,0), (255,255,0)]

    def init_trackers(self, frame, boxes):
        self.multiTracker = cv2.legacy.MultiTracker_create()
        for box in boxes:
            tracker = cv2.legacy.TrackerCSRT_create()
            self.multiTracker.add(tracker, frame, box)
        self.tracking = True

    def update(self, frame):
        success, boxes = self.multiTracker.update(frame)
        return success, boxes

    def draw_boxes(self, frame, boxes):
        for i, box in enumerate(boxes):
            p1 = (int(box[0]), int(box[1]))
            p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
            color = self.colors[i % len(self.colors)]
            cv2.rectangle(frame, p1, p2, color, 3)
