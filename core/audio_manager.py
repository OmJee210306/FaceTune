import pygame
import threading
import logging
import os
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class AudioManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._initialized = False
        self._playing = False
        self._current_song: Optional[str] = None
        self._on_finish_callback: Optional[Callable] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._init_pygame()

    def _init_pygame(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._initialized = True
            logger.info("Pygame mixer initialized")
        except Exception as e:
            logger.error("Failed to initialize pygame mixer: %s", e)
            self._initialized = False

    def play(self, song_path: str, on_finish: Optional[Callable] = None) -> bool:
        if not self._initialized:
            logger.error("Audio not initialized")
            return False
        if not song_path or not os.path.isfile(song_path):
            logger.error("Song file not found: %s", song_path)
            return False

        with self._lock:
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play(loops=0)
                self._playing = True
                self._current_song = song_path
                self._on_finish_callback = on_finish
                logger.info("Playing: %s", song_path)
            except Exception as e:
                logger.error("Error playing %s: %s", song_path, e)
                self._playing = False
                return False

        self._start_monitor()
        return True

    def _start_monitor(self):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._monitor_thread = threading.Thread(
            target=self._monitor_playback, daemon=True
        )
        self._monitor_thread.start()

    def _monitor_playback(self):
        import time
        while True:
            time.sleep(0.2)
            with self._lock:
                if not self._playing:
                    break
                if not pygame.mixer.music.get_busy():
                    self._playing = False
                    cb = self._on_finish_callback
                    self._on_finish_callback = None
                    logger.info("Playback finished")
                    if cb:
                        try:
                            cb()
                        except Exception as e:
                            logger.error("on_finish callback error: %s", e)
                    break

    def stop(self):
        with self._lock:
            if self._initialized and self._playing:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                self._playing = False
                self._on_finish_callback = None
                logger.info("Playback stopped")

    @property
    def is_playing(self) -> bool:
        with self._lock:
            return self._playing and pygame.mixer.music.get_busy()

    def cleanup(self):
        self.stop()
        if self._initialized:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
