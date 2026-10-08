#!/usr/bin/env python3
"""
FaceTune - Facial Recognition Personalized Music System
Entry point
"""
import os
import sys
import logging

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from config import settings
from database import DatabaseManager
from core import RecognitionEngine, CameraManager, AudioManager
from gui import (
    Sidebar,
    RecognitionPage,
    UserManagementPage,
    TrainingPage,
    LogsPage,
    SettingsPage,
)

# Logging setup
os.makedirs(settings.LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(settings.LOGS_DIR, "facetune.log")),
    ]
)
logger = logging.getLogger("facetune")


class FaceTuneApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode(settings.THEME)
        ctk.set_default_color_theme(settings.COLOR_THEME)

        self.title(settings.APP_TITLE)
        self.geometry(settings.APP_GEOMETRY)
        self.minsize(1000, 650)
        self.configure(fg_color=settings.BG_DARK)

        logger.info("Initializing FaceTune")

        # Core services
        self.db = DatabaseManager(settings.DB_PATH)
        self.camera = CameraManager(
            settings.DEFAULT_CAMERA_INDEX,
            settings.FRAME_WIDTH,
            settings.FRAME_HEIGHT
        )
        self.audio = AudioManager()
        self.recognition_engine = RecognitionEngine(
            settings.EMBEDDINGS_PATH,
            settings.DEFAULT_THRESHOLD,
            settings.RECOGNITION_STABLE_SECONDS
        )

        self._pages: dict = {}
        self._current_page = None
        self._build_layout()
        self._show_page("recognition")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        logger.info("FaceTune ready")

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._sidebar = Sidebar(self, on_navigate=self._show_page)
        self._sidebar.grid(row=0, column=0, sticky="nsew")

        self._page_container = ctk.CTkFrame(self, fg_color=settings.BG_DARK)
        self._page_container.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        self._page_container.grid_columnconfigure(0, weight=1)
        self._page_container.grid_rowconfigure(0, weight=1)

        page_map = {
            "recognition": RecognitionPage,
            "users": UserManagementPage,
            "training": TrainingPage,
            "logs": LogsPage,
            "settings": SettingsPage,
        }

        for key, PageClass in page_map.items():
            page = PageClass(self._page_container, self)
            page.grid(row=0, column=0, sticky="nsew")
            self._pages[key] = page

    def _show_page(self, key: str):
        if self._current_page and self._current_page != key:
            old = self._pages.get(self._current_page)
            if old:
                old.on_hide()
                old.grid_remove()

        page = self._pages.get(key)
        if page:
            page.grid()
            page.on_show()
            page.tkraise()
            self._current_page = key
            logger.info("Navigated to: %s", key)

    def _on_close(self):
        logger.info("Shutting down FaceTune")
        try:
            for page in self._pages.values():
                try:
                    page.on_hide()
                except Exception:
                    pass
            self.audio.cleanup()
            self.camera.close()
        except Exception as e:
            logger.error("Error during shutdown: %s", e)
        self.destroy()


def main():
    app = FaceTuneApp()
    app.mainloop()


if __name__ == "__main__":
    main()
