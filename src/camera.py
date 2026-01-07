import cv2, os
from datetime import datetime

class Camera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError("❌ Kamera tidak dapat dibuka")

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def take_photo(self, path):
        os.makedirs(path, exist_ok=True)
        frame = self.get_frame()
        if frame is None:
            raise RuntimeError("❌ Gagal mengambil foto")

        filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.png")
        full = os.path.join(path, filename)
        cv2.imwrite(full, frame)
        return full

    def record_video(self, path, duration=5, fps=20):
        os.makedirs(path, exist_ok=True)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        filename = datetime.now().strftime("video_%Y%m%d_%H%M%S.avi")
        full = os.path.join(path, filename)

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(full, fourcc, fps, (width, height))

        start = cv2.getTickCount()
        while (cv2.getTickCount() - start) / cv2.getTickFrequency() < duration:
            frame = self.get_frame()
            if frame is not None:
                out.write(frame)

        out.release()
        return full

    def release(self):
        if self.cap:
            self.cap.release()
