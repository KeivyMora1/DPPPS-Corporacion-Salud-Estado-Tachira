import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from db import AuthController
from utils import centrar_ventana
from ui_helpers import (
    frame, frame_transparent, label, label_title, label_subtitle,
    btn_nav, btn_danger, separator, canvas_circle, scrollable_frame
)


class MainView:

    MENU_ITEMS = [
        ("actividades", "Actividades"),
        ("asic",        "ASIC"),
        ("reportes",    "Reportes"),
        ("vocerias",    "Vocerias CS"),
    ]

    def __init__(self, root):
        self.root = root
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        self.frames_menu = {}
        self.seccion_actual = "actividades"

        self.root.title("DPPPS")

        self._construir_ui()
        self._navegar("actividades")

        self.root.after(50, lambda: self.root.state("zoomed"))

    def _construir_ui(self):
        # ── Sidebar (left, full height) ───────────────────
        self.panel_menu = frame(self.root, fg_color="gray20", width=240, corner_radius=0)
        self.panel_menu.pack(fill="y", side="left")
        self.panel_menu.pack_propagate(False)

        self.sidebar_inner = frame(self.panel_menu, fg_color="gray20", corner_radius=0)
        self.sidebar_inner.pack(fill="both", expand=True)

        # ── Logo ───────────────────────────────────────────
        self.logo_area = frame(self.sidebar_inner, fg_color="gray20", corner_radius=0)
        self.logo_area.pack(fill="x", padx=20, pady=(20, 28))

        self.logo_canvas = canvas_circle(self.logo_area, 52, bg="#613BE3")
        self.logo_canvas.pack(side="left")

        self.logo_text_frame = frame(self.logo_area, fg_color="gray20", corner_radius=0)
        self.logo_text_frame.pack(side="left", padx=(12, 0))

        self.lbl_logo_title = label_title(self.logo_text_frame, "DPPPS")
        self.lbl_logo_title.pack(anchor="w", pady=0)

        self.lbl_logo_sub = label_subtitle(self.logo_text_frame, "SISTEMA DE INFORMES")
        self.lbl_logo_sub.pack(anchor="w", pady=0)

        # ── Separator ──────────────────────────────────────
        separator(self.sidebar_inner, horizontal=True, fg_color="gray40").pack(fill="x", padx=20, pady=(0, 12))

        # ── Navigation ─────────────────────────────────────
        self.nav_frame = frame(self.sidebar_inner, fg_color="gray20", corner_radius=0)
        self.nav_frame.pack(fill="x", padx=10)

        for clave, label_text in self.MENU_ITEMS:
            btn = btn_nav(self.nav_frame, label_text, lambda c=clave: self._navegar(c))
            btn.pack(fill="x", pady=3, padx=4)
            self.frames_menu[clave] = {"button": btn}

        # ── Main area ──────────────────────────────────────
        self.main_area = frame(self.root, corner_radius=0)
        self.main_area.pack(fill="both", expand=True)

        # ── Header ─────────────────────────────────────────
        self.barra_top = frame(self.main_area, fg_color="gray15", height=64, corner_radius=0)
        self.barra_top.pack(fill="x", side="top")
        self.barra_top.pack_propagate(False)

        self.status_frame = frame(self.barra_top, fg_color="gray15", corner_radius=0)
        self.status_frame.pack(side="left", padx=24)

        self.status_dot = canvas_circle(self.status_frame, 8, bg="gray15")
        self.status_dot.pack(side="left", padx=(0, 8))

        self.lbl_status = label(
            self.status_frame, "DPPPS Corporación Salud Estado Táchira",
            font_size=14, bold=True
        )
        self.lbl_status.pack(side="left")

        self.header_right = frame(self.barra_top, fg_color="gray15", corner_radius=0)
        self.header_right.pack(side="right", padx=24)

        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"

        self.user_info_frame = frame_transparent(self.header_right)
        self.user_info_frame.pack(side="right")

        self.avatar_canvas = canvas_circle(self.user_info_frame, 44, bg="gray15", cursor="hand2")
        self.avatar_canvas.pack(side="right", padx=(10, 0), pady=10)
        self.avatar_canvas.bind("<Button-1>", lambda e: self._toggle_avatar_menu(e))

        self.user_text_frame = frame_transparent(self.user_info_frame)
        self.user_text_frame.pack(side="right", padx=(0, 10))

        self.lbl_user_name = label(self.user_text_frame, nombre, font_size=12, bold=True)
        self.lbl_user_name.pack(anchor="e")

        self.lbl_user_email = label(self.user_text_frame, "admin@dppps.gob", font_size=10)
        self.lbl_user_email.pack(anchor="e")

        # ── Separator below header ─────────────────────────
        separator(self.main_area, horizontal=True, fg_color="gray40").pack(fill="x", side="top")

        # ── Content area ───────────────────────────────────
        self.area_contenido = frame(self.main_area, corner_radius=0)
        self.area_contenido.pack(fill="both", expand=True)

        self._draw_status_dot()
        self._draw_avatar(nombre)

    def _draw_logo_letter(self):
        self.logo_canvas.delete("all")
        self.logo_canvas.create_text(26, 26, text="D",
                                     font=("Segoe UI", 18, "bold"), fill="#ffffff")

    def _draw_status_dot(self):
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 7, 7, fill="#317E87", outline="")

    def _draw_avatar(self, nombre):
        self.avatar_canvas.delete("all")
        inicial = nombre[0].upper() if nombre else "U"
        self.avatar_canvas.create_oval(0, 0, 44, 44, fill="#613BE3", outline="")
        self.avatar_canvas.create_text(22, 22, text=inicial,
                                       font=("Segoe UI", 15, "bold"),
                                       fill="#FFFFFF")

    def _toggle_avatar_menu(self, event):
        if hasattr(self, "_avatar_menu") and self._avatar_menu.winfo_exists():
            self._avatar_menu.destroy()
            self.root.unbind("<Button-1>")
            return

        x = self.avatar_canvas.winfo_rootx()
        y = self.avatar_canvas.winfo_rooty() + 48

        self._avatar_menu = ctk.CTkToplevel(self.root)
        self._avatar_menu.overrideredirect(True)
        self._avatar_menu.geometry(f"180x42+{x - 136}+{y}")
        self._avatar_menu.configure(fg_color="gray25", corner_radius=10)

        btn_logout = btn_danger(self._avatar_menu, "Cerrar sesión", self._cerrar_sesion)
        btn_logout.pack(fill="x", padx=8, pady=8)

        self._avatar_menu.focus_set()

        self.root.after(10, lambda: self.root.bind(
            "<Button-1>", self._cerrar_avatar_menu, add="+"
        ))

    def _cerrar_avatar_menu(self, event):
        if not hasattr(self, "_avatar_menu") or not self._avatar_menu.winfo_exists():
            self.root.unbind("<Button-1>")
            return
        widget = event.widget
        try:
            wstr = str(widget)
            menu_wstr = str(self._avatar_menu)
            if wstr.startswith(menu_wstr) or wstr.startswith(str(self.avatar_canvas)):
                return
            self._avatar_menu.destroy()
            self.root.unbind("<Button-1>")
        except Exception:
            pass

    def _navegar(self, seccion):
        self.seccion_actual = seccion

        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        for clave, data in self.frames_menu.items():
            btn = data["button"]
            if clave == seccion:
                btn.configure(fg_color="#613BE3", hover_color="#4e2fb8", text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", hover_color="gray30", text_color="gray70")

        from pantallas.catalogos   import CatalogoView
        from pantallas.actividades import ActividadView
        from pantallas.reportes    import ReporteView
        from pantallas.vocerias    import VoceriaView

        if seccion == "asic":
            CatalogoView(self.area_contenido, modo="asic")
        elif seccion == "tipos":
            CatalogoView(self.area_contenido, modo="tipos")
        elif seccion == "actividades":
            ActividadView(self.area_contenido)
        elif seccion == "reportes":
            ReporteView(self.area_contenido)
        elif seccion == "vocerias":
            VoceriaView(self.area_contenido)

        self.area_contenido.update_idletasks()

    def _cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres salir?")
        if confirmar:
            self.auth.logout()
            self.root.destroy()
            import main
            main.iniciar_app()