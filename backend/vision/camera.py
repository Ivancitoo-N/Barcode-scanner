import cv2
import threading
import time

class VideoProcessor:
    def __init__(self, src=0):
        self.src = src
        # Force DirectShow on Windows to avoid MSMF errors
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def start(self):
        if self.started:
            print("Video stream already started.")
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame
            time.sleep(0.01) # Small sleep to preventing CPU hogging

    def read(self):
        with self.read_lock:
            if not self.grabbed:
                return None
            return self.frame.copy()

    def stop(self):
        self.started = False
        if hasattr(self, 'thread'):
            self.thread.join()
        self.cap.release()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
