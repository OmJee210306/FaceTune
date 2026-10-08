import cv2
import logging
import threading
import numpy as np
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class CameraManager:
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self._cap: Optional[cv2.VideoCapture] = None
        self._lock = threading.Lock()
        self._running = False
        self._latest_frame: Optional[np.ndarray] = None
        self._thread: Optional[threading.Thread] = None

    def open(self) -> bool:
        with self._lock:
            if self._cap and self._cap.isOpened():
                return True
            self._cap = cv2.VideoCapture(self.camera_index)
            if not self._cap.isOpened():
                logger.error("Cannot open camera index %d", self.camera_index)
                return False
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            logger.info("Camera %d opened", self.camera_index)
            return True

    def _capture_loop(self):
        while self._running:
            if self._cap and self._cap.isOpened():
                ret, frame = self._cap.read()
                if ret:
                    with self._lock:
                        self._latest_frame = frame
            import time
            time.sleep(0.02)

    def read(self) -> Optional[np.ndarray]:
        with self._lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()
        return None

    def close(self):
        self._running = False
        with self._lock:
            if self._cap:
                self._cap.release()
                self._cap = None
                self._latest_frame = None
        logger.info("Camera closed")

    def change_camera(self, index: int):
        self.close()
        self.camera_index = index
        self.open()

    @staticmethod
    def list_cameras(max_test: int = 5) -> list:
        available = []
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available

    def capture_single(self) -> Optional[np.ndarray]:
        """Capture one frame synchronously (for registration)."""
        with self._lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()
        return None
