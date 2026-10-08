import os
import logging
import face_recognition
import numpy as np
import cv2
from PIL import Image
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def detect_and_crop_face(
    image_path_or_array,
    padding: float = 0.3
) -> Optional[np.ndarray]:
    """
    Detect face in image, return cropped BGR face array or None.
    padding: fraction of face size to add around the crop.
    """
    try:
        if isinstance(image_path_or_array, str):
            img = face_recognition.load_image_file(image_path_or_array)
        else:
            img = image_path_or_array
            if img.shape[2] == 4:
                img = img[:, :, :3]

        locations = face_recognition.face_locations(img, model="hog")
        if not locations:
            return None

        # Pick largest
        best = max(locations, key=lambda l: (l[2] - l[0]) * (l[1] - l[3]))
        top, right, bottom, left = best

        h, w = img.shape[:2]
        fh = bottom - top
        fw = right - left
        pad_v = int(fh * padding)
        pad_h = int(fw * padding)

        top = max(0, top - pad_v)
        bottom = min(h, bottom + pad_v)
        left = max(0, left - pad_h)
        right = min(w, right + pad_h)

        face = img[top:bottom, left:right]
        return cv2.cvtColor(face, cv2.COLOR_RGB2BGR)

    except Exception as e:
        logger.error("detect_and_crop_face error: %s", e)
        return None


def save_face_image(
    face_bgr: np.ndarray,
    user_dir: str,
    index: int
) -> Optional[str]:
    os.makedirs(user_dir, exist_ok=True)
    path = os.path.join(user_dir, f"face_{index:04d}.jpg")
    cv2.imwrite(path, face_bgr)
    return path


def frame_to_pil(frame: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def pil_to_ctk_image(pil_img: Image.Image, size: Tuple[int, int]):
    """Convert PIL image to CTkImage."""
    import customtkinter as ctk
    pil_img = pil_img.resize(size, Image.LANCZOS)
    return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)


def count_user_images(user_dir: str) -> int:
    if not os.path.isdir(user_dir):
        return 0
    return sum(
        1 for f in os.listdir(user_dir)
        if os.path.splitext(f.lower())[1] in VALID_EXTENSIONS
    )
