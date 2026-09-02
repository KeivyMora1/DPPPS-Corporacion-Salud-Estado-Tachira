import tkinter as tk
import customtkinter as ctk


class VoceriaView:

    def __init__(self, parent: tk.Frame):
        self.parent = parent

        self._scroll = ctk.CTkScrollableFrame(parent)
        self._scroll.pack(fill="both", expand=True)

        self._construir()

    def _construir(self):
        ctk.CTkLabel(
            self._scroll,
            text="Plantilla de vocería de comité de salud",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w", padx=32, pady=(24, 0))