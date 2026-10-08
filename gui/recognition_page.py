import customtkinter as ctk
import threading
import time
import logging
from PIL import Image
import cv2
from .base_frame import BaseFrame
from config import settings
from utils import frame_to_pil, pil_to_ctk_image

logger = logging.getLogger(__name__)

CAMERA_W, CAMERA_H = 580, 430


class RecognitionPage(BaseFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._running = False
        self._thread = None
        self._last_confirmed_user = None
        self._song_playing = False
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        ctk.CTkLabel(
            header,
            text="Live Recognition",
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).pack(side="left")

        status_frame = ctk.CTkFrame(header, fg_color=settings.BG_SURFACE, corner_radius=20)
        status_frame.pack(side="right", padx=4)
        self._status_dot = ctk.CTkLabel(
            status_frame, text="●", text_color="#555", font=ctk.CTkFont(size=14)
        )
        self._status_dot.pack(side="left", padx=(10, 4), pady=6)
        self._status_label = ctk.CTkLabel(
            status_frame, text="Camera Off",
            font=ctk.CTkFont(size=12), text_color=settings.TEXT_SECONDARY
        )
        self._status_label.pack(side="left", padx=(0, 12), pady=6)

        # Content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=4)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # Camera feed
        cam_frame = ctk.CTkFrame(
            content, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        cam_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._camera_label = ctk.CTkLabel(cam_frame, text="")
        self._camera_label.place(relx=0.5, rely=0.5, anchor="center")
        self._placeholder_label = ctk.CTkLabel(
            cam_frame,
            text="📷\n\nCamera feed will appear here.\nStart recognition to begin.",
            font=ctk.CTkFont(size=14),
            text_color=settings.TEXT_SECONDARY,
            justify="center"
        )
        self._placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        # Info panel
        info_panel = ctk.CTkFrame(content, fg_color="transparent")
        info_panel.grid(row=0, column=1, sticky="nsew")
        info_panel.grid_rowconfigure(0, weight=1)
        info_panel.grid_rowconfigure(1, weight=1)
        info_panel.grid_rowconfigure(2, weight=1)

        # Identity card
        id_card = ctk.CTkFrame(
            info_panel, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        id_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        ctk.CTkLabel(
            id_card, text="DETECTED USER",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).pack(pady=(16, 4))
        self._user_label = ctk.CTkLabel(
            id_card, text="—",
            font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        )
        self._user_label.pack(pady=(0, 4))
        self._user_icon = ctk.CTkLabel(
            id_card, text="",
            font=ctk.CTkFont(size=40)
        )
        self._user_icon.pack(pady=(0, 16))

        # Confidence card
        conf_card = ctk.CTkFrame(
            info_panel, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        conf_card.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        ctk.CTkLabel(
            conf_card, text="CONFIDENCE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).pack(pady=(16, 6))
        self._confidence_bar = ctk.CTkProgressBar(
            conf_card, width=160, height=12,
            corner_radius=6,
            fg_color=settings.BG_DARK,
            progress_color=settings.ACCENT_COLOR
        )
        self._confidence_bar.pack(pady=(0, 6))
        self._confidence_bar.set(0)
        self._conf_label = ctk.CTkLabel(
            conf_card, text="0%",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=settings.ACCENT_COLOR
        )
        self._conf_label.pack(pady=(0, 16))

        # Stability card
        stab_card = ctk.CTkFrame(
            info_panel, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        stab_card.grid(row=2, column=0, sticky="nsew")
        ctk.CTkLabel(
            stab_card, text="RECOGNITION STABILITY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).pack(pady=(16, 6))
        self._stability_bar = ctk.CTkProgressBar(
            stab_card, width=160, height=12,
            corner_radius=6,
            fg_color=settings.BG_DARK,
            progress_color=settings.SUCCESS_COLOR
        )
        self._stability_bar.pack(pady=(0, 6))
        self._stability_bar.set(0)
        self._song_status = ctk.CTkLabel(
            stab_card, text="No song playing",
            font=ctk.CTkFont(size=11),
            text_color=settings.TEXT_SECONDARY
        )
        self._song_status.pack(pady=(0, 16))

        # Controls
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(10, 20))
        self._start_btn = ctk.CTkButton(
            ctrl_frame,
            text="▶  Start Recognition",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=settings.ACCENT_COLOR,
            hover_color="#6A50E0",
            height=44,
            corner_radius=12,
            command=self._toggle_recognition
        )
        self._start_btn.pack(side="left", padx=(0, 12))

        if not self.app.recognition_engine.is_model_loaded:
            self._model_warn = ctk.CTkLabel(
                ctrl_frame,
                text="⚠  No model trained. Go to Training to train first.",
                text_color=settings.WARNING_COLOR,
                font=ctk.CTkFont(size=12)
            )
            self._model_warn.pack(side="left")

    def on_show(self):
        pass

    def on_hide(self):
        self._stop_recognition()

    def _toggle_recognition(self):
        if self._running:
            self._stop_recognition()
        else:
            self._start_recognition()

    def _start_recognition(self):
        if self._running:
            return
        if not self.app.camera.open():
            self._set_status("Camera Error", "#FF5252")
            return

        self.app.recognition_engine.reload_model()
        self.app.recognition_engine.reset_stability()
        self._running = True
        self._last_confirmed_user = None
        self._song_playing = False
        self._placeholder_label.place_forget()
        self._start_btn.configure(text="⏹  Stop Recognition", fg_color=settings.ERROR_COLOR, hover_color="#CC3333")
        self._set_status("Active", settings.SUCCESS_COLOR)
        self._thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self._thread.start()

    def _stop_recognition(self):
        self._running = False
        self.app.audio.stop()
        self.app.camera.close()
        self._reset_ui()
        self._start_btn.configure(
            text="▶  Start Recognition",
            fg_color=settings.ACCENT_COLOR, hover_color="#6A50E0"
        )
        self._set_status("Camera Off", "#555")

    def _recognition_loop(self):
        while self._running:
            frame = self.app.camera.read()
            if frame is None:
                time.sleep(0.05)
                continue

            if self.app.audio.is_playing:
                self._update_frame_display(frame)
                self._update_song_status("🎵 Playing song...", settings.ACCENT_COLOR)
                time.sleep(0.05)
                continue

            result, annotated = self.app.recognition_engine.process_frame(frame)
            self._update_frame_display(annotated)

            if result is None:
                self._update_identity(None, 0)
                self._update_stability(0)
                continue

            self._update_identity(result.name if result.is_known else "UNKNOWN USER", result.confidence)
            prog = self.app.recognition_engine.stability.get_progress()
            self._update_stability(prog)

            confirmed = self.app.recognition_engine.stability.update(
                result.name if result.is_known else None
            )

            if confirmed and confirmed != self._last_confirmed_user and result.is_known:
                self._last_confirmed_user = confirmed
                self._on_user_confirmed(confirmed)

            if not result.is_known:
                self._last_confirmed_user = None
                self._update_song_status("No song for unknown user", settings.TEXT_SECONDARY)

            time.sleep(0.04)

    def _on_user_confirmed(self, name: str):
        user = self.app.db.get_user(name)
        self.app.db.add_log(name, "RECOGNIZED")
        if user and user.get("song_path"):
            song = user["song_path"]
            self._update_song_status(f"🎵 Playing: {song.split('/')[-1]}", settings.SUCCESS_COLOR)
            self.app.audio.play(song, on_finish=self._on_song_finish)
        else:
            self._update_song_status("No song assigned", settings.TEXT_SECONDARY)

    def _on_song_finish(self):
        self._update_song_status("Song finished", settings.TEXT_SECONDARY)
        self._last_confirmed_user = None

    def _update_frame_display(self, frame):
        try:
            pil = frame_to_pil(frame)
            ctk_img = pil_to_ctk_image(pil, (CAMERA_W, CAMERA_H))
            self.after(0, lambda img=ctk_img: self._camera_label.configure(image=img))
        except Exception:
            pass

    def _update_identity(self, name, confidence):
        def _do():
            if name is None:
                self._user_label.configure(text="—", text_color=settings.TEXT_PRIMARY)
                self._user_icon.configure(text="")
                self._confidence_bar.set(0)
                self._conf_label.configure(text="0%", text_color=settings.ACCENT_COLOR)
            elif name == "UNKNOWN USER":
                self._user_label.configure(text="UNKNOWN USER", text_color=settings.ERROR_COLOR)
                self._user_icon.configure(text="❓")
                self._confidence_bar.set(confidence)
                self._conf_label.configure(text=f"{confidence:.0%}", text_color=settings.ERROR_COLOR)
                self._stability_bar.set(0)
            else:
                self._user_label.configure(text=name, text_color=settings.SUCCESS_COLOR)
                self._user_icon.configure(text="👤")
                self._confidence_bar.set(confidence)
                self._conf_label.configure(text=f"{confidence:.0%}", text_color=settings.SUCCESS_COLOR)
        self.after(0, _do)

    def _update_stability(self, progress):
        self.after(0, lambda: self._stability_bar.set(progress))

    def _update_song_status(self, text, color):
        self.after(0, lambda: self._song_status.configure(text=text, text_color=color))

    def _reset_ui(self):
        self.after(0, lambda: [
            self._user_label.configure(text="—", text_color=settings.TEXT_PRIMARY),
            self._user_icon.configure(text=""),
            self._confidence_bar.set(0),
            self._conf_label.configure(text="0%", text_color=settings.ACCENT_COLOR),
            self._stability_bar.set(0),
            self._song_status.configure(text="No song playing", text_color=settings.TEXT_SECONDARY),
            self._camera_label.configure(image=None),
            self._placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        ])

    def _set_status(self, text, color):
        self.after(0, lambda: [
            self._status_label.configure(text=text),
            self._status_dot.configure(text_color=color)
        ])
