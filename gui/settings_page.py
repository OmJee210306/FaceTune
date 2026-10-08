import customtkinter as ctk
import logging
from .base_frame import BaseFrame
from config import settings
from core import CameraManager

logger = logging.getLogger(__name__)


class SettingsPage(BaseFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        ctk.CTkLabel(
            header, text="Settings",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).pack(side="left")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        scroll.grid_columnconfigure(0, weight=1)

        # Recognition section
        self._make_section(scroll, "🎯 Recognition", 0, [
            self._build_threshold_setting,
            self._build_stable_seconds_setting,
        ])

        # Camera section
        self._make_section(scroll, "📷 Camera", 1, [
            self._build_camera_setting,
        ])

        # About section
        self._make_section(scroll, "ℹ️ About", 2, [
            self._build_about,
        ])

    def _make_section(self, parent, title: str, row: int, builders: list):
        section = ctk.CTkFrame(
            parent, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        section.grid(row=row, column=0, sticky="ew", pady=(0, 16))
        section.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            section, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 12))

        sep = ctk.CTkFrame(section, fg_color="#2A2A3E", height=1)
        sep.grid(row=1, column=0, sticky="ew", padx=20)

        for i, builder in enumerate(builders):
            builder(section, i + 2)

    def _build_threshold_setting(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=20, pady=12)
        f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            f, text="Recognition Threshold",
            font=ctk.CTkFont(size=13),
            text_color=settings.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            f, text="Lower = stricter matching (fewer false positives)",
            font=ctk.CTkFont(size=11),
            text_color=settings.TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w")

        self._threshold_val = ctk.CTkLabel(
            f,
            text=f"{self.app.recognition_engine.threshold:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=settings.ACCENT_COLOR,
            width=50
        )
        self._threshold_val.grid(row=0, column=2, padx=(16, 0))

        self._threshold_slider = ctk.CTkSlider(
            f, from_=0.3, to=0.7, number_of_steps=40,
            fg_color=settings.BG_DARK,
            progress_color=settings.ACCENT_COLOR,
            button_color=settings.ACCENT_COLOR,
            width=200,
            command=self._on_threshold_change
        )
        self._threshold_slider.set(self.app.recognition_engine.threshold)
        self._threshold_slider.grid(row=0, column=1, padx=(20, 0), sticky="e")

    def _on_threshold_change(self, val: float):
        self.app.recognition_engine.threshold = val
        self._threshold_val.configure(text=f"{val:.2f}")

    def _build_stable_seconds_setting(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=20, pady=12)
        f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            f, text="Recognition Stability (seconds)",
            font=ctk.CTkFont(size=13),
            text_color=settings.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            f, text="How long a face must be recognized before triggering",
            font=ctk.CTkFont(size=11),
            text_color=settings.TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w")

        cur = self.app.recognition_engine.stability.required_seconds
        self._stable_val = ctk.CTkLabel(
            f, text=f"{cur:.1f}s",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=settings.ACCENT_COLOR, width=50
        )
        self._stable_val.grid(row=0, column=2, padx=(16, 0))

        self._stable_slider = ctk.CTkSlider(
            f, from_=0.5, to=3.0, number_of_steps=25,
            fg_color=settings.BG_DARK,
            progress_color=settings.ACCENT_COLOR,
            button_color=settings.ACCENT_COLOR,
            width=200,
            command=self._on_stable_change
        )
        self._stable_slider.set(cur)
        self._stable_slider.grid(row=0, column=1, padx=(20, 0), sticky="e")

    def _on_stable_change(self, val: float):
        self.app.recognition_engine.stability.required_seconds = val
        self._stable_val.configure(text=f"{val:.1f}s")

    def _build_camera_setting(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=20, pady=12)
        f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            f, text="Camera Index",
            font=ctk.CTkFont(size=13),
            text_color=settings.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            f, text="Select which camera to use",
            font=ctk.CTkFont(size=11),
            text_color=settings.TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w")

        cameras = CameraManager.list_cameras()
        cam_labels = [f"Camera {i}" for i in cameras] if cameras else ["Camera 0"]

        self._cam_option = ctk.CTkOptionMenu(
            f,
            values=cam_labels,
            fg_color=settings.BG_DARK,
            button_color=settings.ACCENT_COLOR,
            button_hover_color="#6A50E0",
            dropdown_fg_color=settings.BG_DARK,
            text_color=settings.TEXT_PRIMARY,
            command=self._on_camera_change
        )
        self._cam_option.grid(row=0, column=1, padx=(20, 0), sticky="e")

    def _on_camera_change(self, val: str):
        idx = int(val.split()[-1])
        self.app.camera.change_camera(idx)

    def _build_about(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=20, pady=16)

        info = [
            ("Application", "FaceTune"),
            ("Version", "1.0.0"),
            ("Recognition", "dlib face_recognition (large model)"),
            ("Embeddings", settings.EMBEDDINGS_PATH.split("/")[-1]),
            ("Database", settings.DB_PATH.split("/")[-1]),
        ]

        for i, (k, v) in enumerate(info):
            row_f = ctk.CTkFrame(f, fg_color="transparent")
            row_f.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row_f, text=k + ":",
                font=ctk.CTkFont(size=12),
                text_color=settings.TEXT_SECONDARY,
                width=160, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row_f, text=v,
                font=ctk.CTkFont(size=12),
                text_color=settings.TEXT_PRIMARY,
                anchor="w"
            ).pack(side="left")
