import pickle
import logging
import time
import face_recognition
import numpy as np
import cv2
from typing import Optional, Tuple, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RecognitionResult:
    name: str
    confidence: float        # 0.0–1.0, higher = more confident
    face_location: Tuple     # (top, right, bottom, left)
    is_known: bool


class StabilityTracker:
    """Requires consistent recognition for N seconds before confirming."""
    def __init__(self, required_seconds: float = 1.0):
        self.required_seconds = required_seconds
        self._candidate: Optional[str] = None
        self._start_time: float = 0.0
        self._confirmed: Optional[str] = None

    def update(self, name: Optional[str]) -> Optional[str]:
        now = time.time()
        if name is None:
            self._reset()
            return None

        if name != self._candidate:
            self._candidate = name
            self._start_time = now
            return None

        elapsed = now - self._start_time
        if elapsed >= self.required_seconds:
            if name != self._confirmed:
                self._confirmed = name
                return name
            return name
        return None

    def _reset(self):
        self._candidate = None
        self._start_time = 0.0
        self._confirmed = None

    def get_progress(self) -> float:
        if self._candidate is None:
            return 0.0
        elapsed = time.time() - self._start_time
        return min(elapsed / self.required_seconds, 1.0)

    @property
    def current_candidate(self) -> Optional[str]:
        return self._candidate


class RecognitionEngine:
    def __init__(
        self,
        embeddings_path: str,
        threshold: float = 0.50,
        stable_seconds: float = 1.0
    ):
        self.embeddings_path = embeddings_path
        self.threshold = threshold
        self._known_encodings: List[np.ndarray] = []
        self._known_labels: List[str] = []
        self._model_loaded = False
        self.stability = StabilityTracker(stable_seconds)
        self._load_model()

    def _load_model(self) -> bool:
        try:
            with open(self.embeddings_path, "rb") as f:
                data = pickle.load(f)
            self._known_encodings = data["encodings"]
            self._known_labels = data["labels"]
            self._model_loaded = True
            logger.info(
                "Loaded %d embeddings for %d unique users",
                len(self._known_encodings),
                len(set(self._known_labels))
            )
            return True
        except FileNotFoundError:
            logger.warning("Embeddings not found at %s", self.embeddings_path)
            self._model_loaded = False
            return False
        except Exception as e:
            logger.error("Error loading embeddings: %s", e)
            self._model_loaded = False
            return False

    def reload_model(self) -> bool:
        return self._load_model()

    @property
    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def process_frame(
        self, frame: np.ndarray
    ) -> Tuple[Optional[RecognitionResult], np.ndarray]:
        """
        Process a BGR frame from OpenCV.
        Returns (RecognitionResult or None, annotated_frame).
        """
        if not self._model_loaded:
            return None, frame

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)

        locations = face_recognition.face_locations(small, model="hog")
        if not locations:
            self.stability.update(None)
            return None, frame

        # Scale locations back
        locations = [
            (t * 2, r * 2, b * 2, l * 2)
            for t, r, b, l in locations
        ]

        # Select largest face
        best_loc = max(
            locations,
            key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3])
        )

        encodings = face_recognition.face_encodings(
            rgb, [best_loc], model="large"
        )
        if not encodings:
            self.stability.update(None)
            return None, frame

        query_enc = encodings[0]
        name, confidence = self._identify(query_enc)
        is_known = name != "UNKNOWN"

        self.stability.update(name if is_known else None)

        result = RecognitionResult(
            name=name,
            confidence=confidence,
            face_location=best_loc,
            is_known=is_known
        )

        annotated = self._annotate(frame.copy(), result)
        return result, annotated

    def _identify(self, encoding: np.ndarray) -> Tuple[str, float]:
        if not self._known_encodings:
            return "UNKNOWN", 0.0

        distances = face_recognition.face_distance(self._known_encodings, encoding)
        best_idx = int(np.argmin(distances))
        best_dist = float(distances[best_idx])
        confidence = 1.0 - best_dist

        if best_dist > self.threshold:
            return "UNKNOWN", confidence

        return self._known_labels[best_idx], confidence

    def _annotate(self, frame: np.ndarray, result: RecognitionResult) -> np.ndarray:
        top, right, bottom, left = result.face_location
        color = (0, 230, 118) if result.is_known else (255, 82, 82)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        label = f"{result.name} ({result.confidence:.0%})"
        label_y = top - 10 if top > 30 else bottom + 25
        cv2.rectangle(
            frame,
            (left, label_y - 20),
            (left + len(label) * 10, label_y + 4),
            color, cv2.FILLED
        )
        cv2.putText(
            frame, label,
            (left, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
        )
        return frame

    def reset_stability(self):
        self.stability._reset()
