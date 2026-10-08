import customtkinter as ctk
from config import settings


class Sidebar(ctk.CTkFrame):
    NAV_ITEMS = [
        ("recognition", "👁", "Recognition"),
        ("users", "👤", "Users"),
        ("training", "🧠", "Training"),
        ("logs", "📋", "Logs"),
        ("settings", "⚙", "Settings"),
    ]

    def __init__(self, parent, on_navigate, **kwargs):
        kwargs.setdefault("fg_color", settings.BG_DARK)
        kwargs.setdefault("width", 200)
        kwargs.setdefault("corner_radius", 0)
        super().__init__(parent, **kwargs)
        self._on_navigate = on_navigate
        self._active = "recognition"
        self._buttons = {}
        self._build()

    def _build(self):
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.grid(row=0, column=0, pady=(24, 8), padx=16, sticky="ew")
        ctk.CTkLabel(
            logo_frame, text="🎵",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            logo_frame, text="FaceTune",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).pack(side="left")

        sep = ctk.CTkFrame(self, fg_color="#2A2A3E", height=1)
        sep.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 16))

        ctk.CTkLabel(
            self, text="NAVIGATION",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#555"
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 6))

        for i, (key, icon, label) in enumerate(self.NAV_ITEMS):
            btn = ctk.CTkButton(
                self,
                text=f"  {icon}  {label}",
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color="#1E1E3A",
                text_color=settings.TEXT_SECONDARY,
                anchor="w",
                height=44,
                corner_radius=10,
                command=lambda k=key: self._navigate(k)
            )
            btn.grid(row=i + 3, column=0, sticky="ew", padx=12, pady=2)
            self._buttons[key] = btn

        self._set_active("recognition")

    def _navigate(self, key: str):
        self._set_active(key)
        self._on_navigate(key)

    def _set_active(self, key: str):
        if self._active in self._buttons:
            self._buttons[self._active].configure(
                fg_color="transparent",
                text_color=settings.TEXT_SECONDARY
            )
        self._active = key
        if key in self._buttons:
            self._buttons[key].configure(
                fg_color="#1E1E3A",
                text_color=settings.ACCENT_COLOR
            )
