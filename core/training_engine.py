import os
import pickle
import logging
import face_recognition
import numpy as np
from typing import List, Tuple, Optional, Callable

logger = logging.getLogger(__name__)


class TrainingEngine:
    def __init__(self, dataset_dir: str, embeddings_path: str):
        self.dataset_dir = dataset_dir
        self.embeddings_path = embeddings_path

    def train(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Scan dataset directory, generate embeddings, save to pkl.
        dataset_dir/username/image.jpg
        """
        try:
            if not os.path.isdir(self.dataset_dir):
                return False, "Dataset directory not found."

            user_dirs = [
                d for d in os.listdir(self.dataset_dir)
                if os.path.isdir(os.path.join(self.dataset_dir, d))
            ]

            if not user_dirs:
                return False, "No user directories found in dataset."

            all_encodings: List[np.ndarray] = []
            all_labels: List[str] = []
            total_images = 0
            processed = 0

            # Count total images
            for udir in user_dirs:
                upath = os.path.join(self.dataset_dir, udir)
                imgs = self._get_images(upath)
                total_images += len(imgs)

            if total_images == 0:
                return False, "No images found in dataset."

            for udir in user_dirs:
                upath = os.path.join(self.dataset_dir, udir)
                images = self._get_images(upath)
                user_encodings = 0

                for img_file in images:
                    img_path = os.path.join(upath, img_file)
                    try:
                        image = face_recognition.load_image_file(img_path)
                        encodings = face_recognition.face_encodings(
                            image,
                            model="large"
                        )
                        if encodings:
                            all_encodings.append(encodings[0])
                            all_labels.append(udir)
                            user_encodings += 1
                    except Exception as e:
                        logger.warning("Skipping %s: %s", img_path, e)

                    processed += 1
                    pct = processed / total_images
                    if progress_callback:
                        progress_callback(
                            pct,
                            f"Processing {udir}: {user_encodings} encodings so far..."
                        )

                logger.info("User %s: %d encodings", udir, user_encodings)

            if not all_encodings:
                return False, "No valid face encodings could be generated."

            data = {"encodings": all_encodings, "labels": all_labels}
            os.makedirs(os.path.dirname(self.embeddings_path), exist_ok=True)
            with open(self.embeddings_path, "wb") as f:
                pickle.dump(data, f)

            msg = (
                f"Training complete. {len(all_encodings)} encodings "
                f"from {len(user_dirs)} users saved."
            )
            logger.info(msg)
            if progress_callback:
                progress_callback(1.0, msg)
            return True, msg

        except Exception as e:
            logger.error("Training error: %s", e)
            return False, f"Training failed: {e}"

    def _get_images(self, directory: str) -> List[str]:
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        return [
            f for f in os.listdir(directory)
            if os.path.splitext(f.lower())[1] in exts
        ]
