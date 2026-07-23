import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from db import AuthController
from utils import centrar_ventana
from themes import THEMES


class MainView:

    MENU_ITEMS = [
        ("dashboard",   "Dashboard"),
        ("actividades", "Actividades"),
        ("asic",        "ASIC"),
        ("tipos",       "Tipos"),
        ("importar",    "Importar"),
        ("reportes",    "Reportes"),
        ("vocerias",    "Vocerias CS"),
    ]

    def __init__(self, root):
        self.root = root
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        self.frames_menu = {}
        self.tema_actual = "dark"
        self.seccion_actual = "dashboard"
        self.t = THEMES["dark"]

        self.root.title("DPPPS")
        self.root.configure(fg_color=self.t["bg_base"])

        self._construir_ui()
        self._navegar("dashboard")

        self.root.after(50, lambda: self.root.state("zoomed"))

    def _construir_ui(self):
        t = self.t

        # ── Sidebar (left, full height) ───────────────────
        self.panel_menu = ctk.CTkFrame(
            self.root, fg_color=t["bg_sidebar"], width=240, corner_radius=0,
        )
        self.panel_menu.pack(fill="y", side="left")
        self.panel_menu.pack_propagate(False)

        self.sidebar_inner = ctk.CTkFrame(
            self.panel_menu, fg_color=t["bg_sidebar"], corner_radius=0,
        )
        self.sidebar_inner.pack(fill="both", expand=True)

        # ── Logo ───────────────────────────────────────────
        self.logo_area = ctk.CTkFrame(
            self.sidebar_inner, fg_color=t["bg_sidebar"], corner_radius=0,
        )
        self.logo_area.pack(fill="x", padx=20, pady=(20, 28))

        self.logo_canvas = tk.Canvas(
            self.logo_area, width=52, height=52,
            bg=t["accent"], highlightthickness=0,
        )
        self.logo_canvas.pack(side="left")

        self.logo_text_frame = ctk.CTkFrame(
            self.logo_area, fg_color=t["bg_sidebar"], corner_radius=0,
        )
        self.logo_text_frame.pack(side="left", padx=(12, 0))

        self.lbl_logo_title = ctk.CTkLabel(
            self.logo_text_frame, text="DPPPS",
            font=("Segoe UI", 18, "bold"),
            text_color=t["text_primary"],
        )
        self.lbl_logo_title.pack(anchor="w", pady=0)

        self.lbl_logo_sub = ctk.CTkLabel(
            self.logo_text_frame, text="SISTEMA DE INFORMES",
            font=("Segoe UI", 9),
            text_color=t["text_dim"],
        )
        self.lbl_logo_sub.pack(anchor="w", pady=0)

        # ── Separator ──────────────────────────────────────
        self.sep_nav = ctk.CTkFrame(
            self.sidebar_inner, fg_color=t["border"], height=1, corner_radius=0,
        )
        self.sep_nav.pack(fill="x", padx=20, pady=(0, 12))

        # ── Navigation ─────────────────────────────────────
        self.nav_frame = ctk.CTkFrame(
            self.sidebar_inner, fg_color=t["bg_sidebar"], corner_radius=0,
        )
        self.nav_frame.pack(fill="x", padx=10)

        for clave, label in self.MENU_ITEMS:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"  {label}",
                font=("Segoe UI", 13),
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                hover_color=t["bg_hover"],
                text_color=t["text_muted"],
                command=lambda c=clave: self._navegar(c),
            )
            btn.pack(fill="x", pady=3, padx=4)
            self.frames_menu[clave] = {"button": btn}

        # ── Theme toggle (bottom) ──────────────────────────
        self.sep_bottom = ctk.CTkFrame(
            self.sidebar_inner, fg_color=t["border"], height=1, corner_radius=0,
        )
        self.sep_bottom.pack(side="bottom", fill="x", padx=20, pady=(12, 0))

        self.btn_tema = ctk.CTkButton(
            self.sidebar_inner,
            text="☀  Modo claro",
            font=("Segoe UI", 12),
            anchor="w",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            hover_color=t["bg_hover"],
            text_color=t["text_muted"],
            command=self._alternar_tema,
        )
        self.btn_tema.pack(side="bottom", fill="x", padx=14, pady=(8, 16))

        # ── Main area ──────────────────────────────────────
        self.main_area = ctk.CTkFrame(
            self.root, fg_color=t["bg_base"], corner_radius=0,
        )
        self.main_area.pack(fill="both", expand=True)

        # ── Header ─────────────────────────────────────────
        self.barra_top = ctk.CTkFrame(
            self.main_area, fg_color=t["bg_header"], height=64, corner_radius=0,
        )
        self.barra_top.pack(fill="x", side="top")
        self.barra_top.pack_propagate(False)

        self.status_frame = ctk.CTkFrame(
            self.barra_top, fg_color=t["bg_header"], corner_radius=0,
        )
        self.status_frame.pack(side="left", padx=24)

        self.status_dot = tk.Canvas(
            self.status_frame, width=8, height=8,
            bg=t["bg_header"], highlightthickness=0,
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        self.lbl_status = ctk.CTkLabel(
            self.status_frame,             text="DPPPS Corporación Salud Estado Táchira",
            font=("Segoe UI", 14, "bold"), text_color=t["text_primary"],
        )
        self.lbl_status.pack(side="left")

        self.header_right = ctk.CTkFrame(
            self.barra_top, fg_color=t["bg_header"], corner_radius=0,
        )
        self.header_right.pack(side="right", padx=24)

        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"

        self.user_info_frame = ctk.CTkFrame(
            self.header_right, fg_color="transparent",
        )
        self.user_info_frame.pack(side="right")

        self.avatar_canvas = tk.Canvas(
            self.user_info_frame, width=44, height=44,
            bg=t["bg_header"], highlightthickness=0,
            cursor="hand2",
        )
        self.avatar_canvas.pack(side="right", padx=(10, 0), pady=10)
        self.avatar_canvas.bind("<Button-1>", lambda e: self._toggle_avatar_menu(e))

        self.user_text_frame = ctk.CTkFrame(
            self.user_info_frame, fg_color="transparent",
        )
        self.user_text_frame.pack(side="right", padx=(0, 10))

        self.lbl_user_name = ctk.CTkLabel(
            self.user_text_frame, text=nombre,
            font=("Segoe UI", 12, "bold"),
            text_color=t["text_primary"],
        )
        self.lbl_user_name.pack(anchor="e")

        self.lbl_user_email = ctk.CTkLabel(
            self.user_text_frame, text="admin@dppps.gob",
            font=("Segoe UI", 10),
            text_color=t["text_muted"],
        )
        self.lbl_user_email.pack(anchor="e")

        # ── Separator below header ─────────────────────────
        self.sep_header = ctk.CTkFrame(
            self.main_area, fg_color=t["border"], height=1, corner_radius=0,
        )
        self.sep_header.pack(fill="x", side="top")

        # ── Content area ───────────────────────────────────
        self.area_contenido = ctk.CTkFrame(
            self.main_area, fg_color=t["bg_base"], corner_radius=0,
        )
        self.area_contenido.pack(fill="both", expand=True)

        self._draw_status_dot()
        self._draw_avatar(nombre)

    def _draw_logo_letter(self):
        self.logo_canvas.delete("all")
        self.logo_canvas.create_text(26, 26, text="D",
                                     font=("Segoe UI", 18, "bold"), fill="#ffffff")

    def _draw_status_dot(self):
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 7, 7, fill=self.t["success"], outline="")

    def _draw_avatar(self, nombre):
        self.avatar_canvas.delete("all")
        inicial = nombre[0].upper() if nombre else "U"
        self.avatar_canvas.create_oval(0, 0, 44, 44, fill=self.t["accent"], outline="")
        self.avatar_canvas.create_text(22, 22, text=inicial,
                                       font=("Segoe UI", 15, "bold"),
                                       fill="#FFFFFF")

    def _toggle_avatar_menu(self, event):
        if hasattr(self, "_avatar_menu") and self._avatar_menu.winfo_exists():
            self._avatar_menu.destroy()
            self.root.unbind("<Button-1>")
            return

        t = self.t
        x = self.avatar_canvas.winfo_rootx()
        y = self.avatar_canvas.winfo_rooty() + 48

        self._avatar_menu = ctk.CTkToplevel(self.root)
        self._avatar_menu.overrideredirect(True)
        self._avatar_menu.geometry(f"180x42+{x - 136}+{y}")
        self._avatar_menu.configure(fg_color=t["bg_card"], corner_radius=10)

        btn_logout = ctk.CTkButton(
            self._avatar_menu, text="Cerrar sesión",
            font=("Segoe UI", 11), anchor="w",
            fg_color="transparent", hover_color=t["red_bg"],
            text_color=t["red_fg"], corner_radius=6, height=32,
            command=self._cerrar_sesion,
        )
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
        t = self.t

        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        for clave, data in self.frames_menu.items():
            btn = data["button"]
            if clave == seccion:
                btn.configure(
                    fg_color=t["accent"],
                    hover_color=t["accent_dim"],
                    text_color="#FFFFFF",
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=t["bg_hover"],
                    text_color=t["text_muted"],
                )

        from pantallas.dashboard   import DashboardView
        from pantallas.catalogos   import CatalogoView
        from pantallas.actividades import ActividadView
        from pantallas.importacion import ImportacionView
        from pantallas.reportes    import ReporteView
        from pantallas.vocerias    import VoceriaView

        if seccion == "dashboard":
            DashboardView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "asic":
            CatalogoView(self.area_contenido, modo="asic", theme=self.tema_actual)
        elif seccion == "tipos":
            CatalogoView(self.area_contenido, modo="tipos", theme=self.tema_actual)
        elif seccion == "actividades":
            ActividadView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "importar":
            ImportacionView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "reportes":
            ReporteView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "vocerias":
            VoceriaView(self.area_contenido, theme=self.tema_actual)

    def _alternar_tema(self):
        self.tema_actual = "light" if self.tema_actual == "dark" else "dark"
        self.t = THEMES[self.tema_actual]
        t = self.t

        icono = "☾" if self.tema_actual == "light" else "☀"
        texto = "Modo oscuro" if self.tema_actual == "light" else "Modo claro"
        self.btn_tema.configure(text=f"{icono}  {texto}")

        self.root.configure(fg_color=t["bg_base"])
        self.panel_menu.configure(fg_color=t["bg_sidebar"])
        self.sidebar_inner.configure(fg_color=t["bg_sidebar"])
        self.logo_area.configure(fg_color=t["bg_sidebar"])
        self.logo_text_frame.configure(fg_color=t["bg_sidebar"])
        self.sep_nav.configure(fg_color=t["border"])
        self.nav_frame.configure(fg_color=t["bg_sidebar"])
        self.sep_bottom.configure(fg_color=t["border"])
        self.logo_canvas.config(bg=t["accent"])
        self._draw_logo_letter()
        self.lbl_logo_title.configure(text_color=t["text_primary"])
        self.lbl_logo_sub.configure(text_color=t["text_dim"])
        self.btn_tema.configure(fg_color="transparent", text_color=t["text_muted"])
        for clave, data in self.frames_menu.items():
            btn = data["button"]
            if clave == self.seccion_actual:
                btn.configure(
                    fg_color=t["accent"],
                    hover_color=t["accent_dim"],
                    text_color="#FFFFFF",
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=t["bg_hover"],
                    text_color=t["text_muted"],
                )
        self.main_area.configure(fg_color=t["bg_base"])
        self.barra_top.configure(fg_color=t["bg_header"])
        self.status_frame.configure(fg_color=t["bg_header"])
        self.status_dot.config(bg=t["bg_header"])
        self._draw_status_dot()
        self.lbl_status.configure(text_color=t["text_muted"])
        self.header_right.configure(fg_color=t["bg_header"])
        self.user_info_frame.configure(fg_color="transparent")
        self.user_text_frame.configure(fg_color="transparent")
        self.avatar_canvas.config(bg=t["bg_header"])
        self.lbl_user_name.configure(text_color=t["text_primary"])
        self.lbl_user_email.configure(text_color=t["text_muted"])
        self.btn_logout.configure(fg_color=t["red_bg"], text_color=t["red_fg"])
        self.sep_header.configure(fg_color=t["border"])
        self.area_contenido.configure(fg_color=t["bg_base"])

        self._recargar_seccion()
    def _recargar_seccion(self):
        t = self.t
        seccion = self.seccion_actual

        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        for clave, data in self.frames_menu.items():
            btn = data["button"]
            if clave == seccion:
                btn.configure(
                    fg_color=t["accent"],
                    hover_color=t["accent_dim"],
                    text_color="#FFFFFF",
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=t["bg_hover"],
                    text_color=t["text_muted"],
                )

        self.area_contenido.configure(fg_color=t["bg_base"])

        from pantallas.dashboard   import DashboardView
        from pantallas.catalogos   import CatalogoView
        from pantallas.actividades import ActividadView
        from pantallas.importacion import ImportacionView
        from pantallas.reportes    import ReporteView
        from pantallas.vocerias    import VoceriaView

        if seccion == "dashboard":
            DashboardView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "asic":
            CatalogoView(self.area_contenido, modo="asic", theme=self.tema_actual)
        elif seccion == "tipos":
            CatalogoView(self.area_contenido, modo="tipos", theme=self.tema_actual)
        elif seccion == "actividades":
            ActividadView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "importar":
            ImportacionView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "reportes":
            ReporteView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "vocerias":
            VoceriaView(self.area_contenido, theme=self.tema_actual)

        self.area_contenido.update_idletasks()

    def _cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres salir?")
        if confirmar:
            self.auth.logout()
            self.root.destroy()
            import main
            main.iniciar_app()
