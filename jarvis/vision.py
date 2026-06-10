import cv2
import os
from datetime import datetime

class Camera:
    def __init__(self, camera_index=0):
        self.index = camera_index
        self.screenshot_dir = os.path.expanduser("~/Pictures/Jarvis")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def capture(self):
        cap = cv2.VideoCapture(self.index)
        if not cap.isOpened():
            return None
        ret, frame = cap.read()
        cap.release()
        if ret:
            path = os.path.join(
                self.screenshot_dir,
                f"cam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            )
            cv2.imwrite(path, frame)
            return path
        return None
