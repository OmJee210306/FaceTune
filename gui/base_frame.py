import customtkinter as ctk
from config import settings


class BaseFrame(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("fg_color", settings.BG_CARD)
        kwargs.setdefault("corner_radius", 16)
        super().__init__(parent, **kwargs)
        self.app = app

    def on_show(self):
        """Called when this page becomes visible."""
        pass

    def on_hide(self):
        """Called when this page is hidden."""
        pass
