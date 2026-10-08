import customtkinter as ctk
import threading
import logging
from .base_frame import BaseFrame
from config import settings
from core import TrainingEngine

logger = logging.getLogger(__name__)


class TrainingPage(BaseFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._training = False
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        ctk.CTkLabel(
            header, text="Model Training",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).pack(side="left")

        content = ctk.CTkFrame(
            self, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=1)

        # Training card
        card = ctk.CTkFrame(content, fg_color=settings.BG_DARK, corner_radius=14)
        card.grid(row=0, column=0, padx=40, pady=40, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="🧠",
            font=ctk.CTkFont(size=48)
        ).grid(row=0, column=0, pady=(28, 8))
        ctk.CTkLabel(
            card, text="Train Face Recognition Model",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).grid(row=1, column=0, pady=(0, 8))
        ctk.CTkLabel(
            card,
            text="Scans the dataset directory, generates face embeddings for all users,\n"
                 "and saves them to embeddings.pkl for recognition.",
            font=ctk.CTkFont(size=12),
            text_color=settings.TEXT_SECONDARY,
            justify="center"
        ).grid(row=2, column=0, pady=(0, 20))

        self._train_btn = ctk.CTkButton(
            card, text="▶  Train Model",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=settings.ACCENT_COLOR, hover_color="#6A50E0",
            height=46, corner_radius=12, width=200,
            command=self._start_training
        )
        self._train_btn.grid(row=3, column=0, pady=(0, 20))

        # Progress section
        prog_frame = ctk.CTkFrame(content, fg_color="transparent")
        prog_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        prog_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            prog_frame, text="PROGRESS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self._progress_bar = ctk.CTkProgressBar(
            prog_frame, height=14, corner_radius=7,
            fg_color=settings.BG_DARK,
            progress_color=settings.ACCENT_COLOR
        )
        self._progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self._progress_bar.set(0)

        self._progress_label = ctk.CTkLabel(
            prog_frame, text="Ready to train.",
            font=ctk.CTkFont(size=12),
            text_color=settings.TEXT_SECONDARY
        )
        self._progress_label.grid(row=2, column=0, sticky="w")

        # Log output
        log_frame = ctk.CTkFrame(content, fg_color="transparent")
        log_frame.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 40))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            log_frame, text="TRAINING LOG",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self._log_box = ctk.CTkTextbox(
            log_frame,
            fg_color=settings.BG_DARK,
            text_color=settings.TEXT_SECONDARY,
            font=ctk.CTkFont(family="Courier", size=11),
            corner_radius=10,
            state="disabled"
        )
        self._log_box.grid(row=1, column=0, sticky="nsew")

    def _start_training(self):
        if self._training:
            return
        self._training = True
        self._train_btn.configure(state="disabled", text="Training...")
        self._progress_bar.set(0)
        self._clear_log()
        self._log("Starting training process...")
        threading.Thread(target=self._run_training, daemon=True).start()

    def _run_training(self):
        engine = TrainingEngine(settings.DATASET_DIR, settings.EMBEDDINGS_PATH)

        def progress_cb(pct: float, msg: str):
            self.after(0, lambda p=pct, m=msg: self._update_progress(p, m))

        success, message = engine.train(progress_callback=progress_cb)

        def finish():
            self._training = False
            self._train_btn.configure(state="normal", text="▶  Train Model")
            if success:
                self._progress_bar.configure(progress_color=settings.SUCCESS_COLOR)
                self._log(f"✅ {message}")
                self.app.recognition_engine.reload_model()
            else:
                self._progress_bar.configure(progress_color=settings.ERROR_COLOR)
                self._log(f"❌ {message}")

        self.after(0, finish)

    def _update_progress(self, pct: float, msg: str):
        self._progress_bar.set(pct)
        self._progress_label.configure(text=msg)
        self._log(msg)

    def _log(self, text: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", text + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")
