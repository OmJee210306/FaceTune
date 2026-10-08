import customtkinter as ctk
import logging
from .base_frame import BaseFrame
from config import settings

logger = logging.getLogger(__name__)


class LogsPage(BaseFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        ctk.CTkLabel(
            header, text="Recognition Logs",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkButton(
            header, text="🔄 Refresh",
            fg_color=settings.BG_SURFACE, hover_color=settings.BG_CARD,
            text_color=settings.TEXT_PRIMARY, height=34, corner_radius=8, width=100,
            command=self._refresh_logs
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            header, text="🗑 Clear",
            fg_color="#CC2222", hover_color="#AA1111",
            height=34, corner_radius=8, width=80,
            command=self._clear_logs
        ).pack(side="right")

        # Table frame
        table_outer = ctk.CTkFrame(
            self, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        table_outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        table_outer.grid_columnconfigure(0, weight=1)
        table_outer.grid_rowconfigure(1, weight=1)

        # Column headers
        cols = ctk.CTkFrame(table_outer, fg_color=settings.BG_DARK, corner_radius=0)
        cols.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        for i, (text, w) in enumerate([("ID", 60), ("User", 200), ("Status", 140), ("Timestamp", 260)]):
            ctk.CTkLabel(
                cols, text=text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=settings.TEXT_SECONDARY,
                width=w, anchor="w"
            ).grid(row=0, column=i, padx=16 if i == 0 else 8, pady=10, sticky="w")

        self._scroll = ctk.CTkScrollableFrame(
            table_outer, fg_color="transparent", corner_radius=0
        )
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self._scroll.grid_columnconfigure(0, weight=1)

        self._refresh_logs()

    def on_show(self):
        self._refresh_logs()

    def _refresh_logs(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        logs = self.app.db.get_logs(200)
        if not logs:
            ctk.CTkLabel(
                self._scroll,
                text="No recognition events logged yet.",
                font=ctk.CTkFont(size=13),
                text_color=settings.TEXT_SECONDARY
            ).pack(pady=30)
            return

        for i, log in enumerate(logs):
            bg = settings.BG_CARD if i % 2 == 0 else settings.BG_SURFACE
            row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=6, height=36)
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure(1, weight=1)

            status_color = settings.SUCCESS_COLOR if log["status"] == "RECOGNIZED" else settings.ERROR_COLOR

            for j, (val, w) in enumerate([
                (str(log["id"]), 60),
                (log["user_name"], 200),
                (log["status"], 140),
                (log["timestamp"][:19].replace("T", " "), 260)
            ]):
                color = status_color if j == 2 else settings.TEXT_PRIMARY
                ctk.CTkLabel(
                    row, text=val,
                    font=ctk.CTkFont(size=12),
                    text_color=color,
                    width=w, anchor="w"
                ).grid(row=0, column=j, padx=16 if j == 0 else 8, pady=6, sticky="w")

    def _clear_logs(self):
        self.app.db.clear_logs()
        self._refresh_logs()
