import tkinter as tk
import customtkinter as ctk
from themes import THEMES


class VoceriaView:

    def __init__(self, parent: tk.Frame, theme: str = "dark"):
        self.parent = parent
        self.theme = theme
        self.t = THEMES[theme]

        self._scroll = ctk.CTkScrollableFrame(
            parent, fg_color=self.t["bg_base"],
            scrollbar_fg_color=self.t["bg_base"],
            scrollbar_button_color=self.t["bg_sidebar"],
            scrollbar_button_hover_color=self.t["border"],
        )
        self._scroll.pack(fill="both", expand=True)

        self._construir()

    def _construir(self):
        t = self.t

        ctk.CTkLabel(
            self._scroll,
            text="Plantilla de voceria de comite de salud",
            font=("Segoe UI", 20, "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=32, pady=(24, 0))
