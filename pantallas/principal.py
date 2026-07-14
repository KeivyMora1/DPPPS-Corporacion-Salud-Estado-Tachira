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
        self.root.geometry("1100x680")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=self.t["bg_base"])

        centrar_ventana(self.root, 1100, 680)
        self._construir_ui()
        self._navegar("dashboard")

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
            self.logo_area, width=36, height=36,
            bg=t["accent"], highlightthickness=0,
        )
        self.logo_canvas.pack(side="left")

        self.logo_text_frame = ctk.CTkFrame(
            self.logo_area, fg_color=t["bg_sidebar"], corner_radius=0,
        )
        self.logo_text_frame.pack(side="left", padx=(10, 0))

        self.lbl_logo_title = ctk.CTkLabel(
            self.logo_text_frame, text="DPPPS",
            font=("Segoe UI", 15, "bold"),
            text_color=t["text_primary"],
        )
        self.lbl_logo_title.pack(anchor="w")

        self.lbl_logo_sub = ctk.CTkLabel(
            self.logo_text_frame, text="SISTEMA DE INFORMES",
            font=("Segoe UI", 7),
            text_color=t["text_dim"],
        )
        self.lbl_logo_sub.pack(anchor="w")

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
            item = ctk.CTkFrame(
                self.nav_frame, fg_color=t["bg_sidebar"], corner_radius=0,
            )
            item.pack(fill="x", pady=2)

            lbl = ctk.CTkLabel(
                item, text=f"    {label}",
                font=("Segoe UI", 10),
                text_color=t["text_muted"],
                anchor="w", padx=12, pady=10,
            )
            lbl.pack(fill="x")

            for widget in (item, lbl):
                widget.bind("<Enter>", lambda e, i=item, l=lbl, k=clave:
                            self._hover_enter(i, l, k))
                widget.bind("<Leave>", lambda e, i=item, l=lbl, k=clave:
                            self._hover_leave(i, l, k))
                widget.bind("<Button-1>", lambda e, c=clave: self._navegar(c))

            self.frames_menu[clave] = {"frame": item, "label": lbl}

        # ── Theme toggle (bottom) ──────────────────────────
        self.sep_bottom = ctk.CTkFrame(
            self.sidebar_inner, fg_color=t["border"], height=1, corner_radius=0,
        )
        self.sep_bottom.pack(side="bottom", fill="x", padx=20, pady=(12, 0))

        self.theme_frame = ctk.CTkFrame(
            self.sidebar_inner, fg_color=t["bg_sidebar"], corner_radius=0,
        )
        self.theme_frame.pack(side="bottom", fill="x", padx=10, pady=(8, 16))

        self.btn_tema_icon = ctk.CTkLabel(
            self.theme_frame, text="\u2600",
            font=("Segoe UI", 12), fg_color="transparent",
            text_color=t["text_muted"],
        )
        self.btn_tema_icon.pack(side="left", padx=(12, 8))

        self.btn_tema = ctk.CTkButton(
            self.theme_frame, text="Modo claro",
            font=("Segoe UI", 10),
            fg_color="transparent",
            hover_color=t["bg_hover"],
            text_color=t["text_muted"],
            anchor="w",
            command=self._alternar_tema,
        )
        self.btn_tema.pack(side="left")

        self._bind_theme_toggle()

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
            self.status_frame, text="Servidor Activo",
            font=("Segoe UI", 9), text_color=t["text_muted"],
        )
        self.lbl_status.pack(side="left")

        self.header_right = ctk.CTkFrame(
            self.barra_top, fg_color=t["bg_header"], corner_radius=0,
        )
        self.header_right.pack(side="right", padx=24)

        self.btn_logout = ctk.CTkButton(
            self.header_right, text="  Salir  ",
            font=("Segoe UI", 9),
            fg_color=t["red_bg"], hover_color=t["red"],
            text_color=t["red_fg"],
            corner_radius=6,
            command=self._cerrar_sesion,
        )
        self.btn_logout.pack(side="right", padx=(12, 0))

        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"

        self.avatar_canvas = tk.Canvas(
            self.header_right, width=34, height=34,
            bg=t["border"], highlightthickness=1,
            highlightbackground=t["accent"],
        )
        self.avatar_canvas.pack(side="right", padx=(12, 0))

        self.user_text_frame = ctk.CTkFrame(
            self.barra_top, fg_color=t["bg_header"], corner_radius=0,
        )
        self.user_text_frame.pack(side="right")

        self.lbl_user_name = ctk.CTkLabel(
            self.user_text_frame, text=nombre,
            font=("Segoe UI", 10, "bold"),
            text_color=t["text_primary"],
        )
        self.lbl_user_name.pack(anchor="e")

        self.lbl_user_email = ctk.CTkLabel(
            self.user_text_frame, text="admin@dppps.gob",
            font=("Segoe UI", 8),
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

    def _bind_theme_toggle(self):
        for w in (self.theme_frame, self.btn_tema_icon):
            w.bind("<Button-1>", lambda e: self._alternar_tema())
            w.bind("<Enter>", lambda e: (
                self.theme_frame.configure(fg_color=self.t["bg_hover"]),
                self.btn_tema_icon.configure(fg_color=self.t["bg_hover"]),
                self.btn_tema.configure(fg_color=self.t["bg_hover"], text_color=self.t["text_primary"]),
            ))
            w.bind("<Leave>", lambda e: (
                self.theme_frame.configure(fg_color=self.t["bg_sidebar"]),
                self.btn_tema_icon.configure(fg_color=self.t["bg_sidebar"]),
                self.btn_tema.configure(fg_color="transparent", text_color=self.t["text_muted"]),
            ))

    def _draw_logo_letter(self):
        self.logo_canvas.delete("all")
        self.logo_canvas.create_text(18, 18, text="D",
                                     font=("Segoe UI", 14, "bold"), fill="#ffffff")

    def _draw_status_dot(self):
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 7, 7, fill=self.t["success"], outline="")

    def _draw_avatar(self, nombre):
        self.avatar_canvas.delete("all")
        inicial = nombre[0].upper() if nombre else "U"
        self.avatar_canvas.create_text(17, 17, text=inicial,
                                       font=("Segoe UI", 13, "bold"),
                                       fill=self.t["accent"])

    def _hover_enter(self, frame, label, clave):
        if clave != self.seccion_actual:
            frame.configure(fg_color=self.t["bg_hover"])
            label.configure(fg_color=self.t["bg_hover"], text_color=self.t["text_primary"])

    def _hover_leave(self, frame, label, clave):
        if clave != self.seccion_actual:
            frame.configure(fg_color=self.t["bg_sidebar"])
            label.configure(fg_color=self.t["bg_sidebar"], text_color=self.t["text_muted"])

    def _navegar(self, seccion):
        self.seccion_actual = seccion
        t = self.t

        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        for clave, data in self.frames_menu.items():
            frame = data["frame"]
            label = data["label"]
            if clave == seccion:
                frame.configure(fg_color=t["bg_active"])
                label.configure(fg_color=t["bg_active"], text_color=t["accent"])
            else:
                frame.configure(fg_color=t["bg_sidebar"])
                label.configure(fg_color=t["bg_sidebar"], text_color=t["text_muted"])

        from pantallas.dashboard   import DashboardView
        from pantallas.catalogos   import CatalogoView
        from pantallas.actividades import ActividadView
        from pantallas.importacion import ImportacionView
        from pantallas.reportes    import ReporteView

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

    def _alternar_tema(self):
        self.tema_actual = "light" if self.tema_actual == "dark" else "dark"
        self.t = THEMES[self.tema_actual]
        t = self.t
        self.btn_tema.configure(
            text="Modo oscuro" if self.tema_actual == "light" else "Modo claro"
        )
        self.btn_tema_icon.configure(
            text="☾" if self.tema_actual == "light" else "☀"
        )

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
        self.theme_frame.configure(fg_color=t["bg_sidebar"])
        self.btn_tema_icon.configure(fg_color=t["bg_sidebar"], text_color=t["text_muted"])
        self.btn_tema.configure(fg_color="transparent", text_color=t["text_muted"])
        for clave, data in self.frames_menu.items():
            data["frame"].configure(fg_color=t["bg_sidebar"])
            data["label"].configure(fg_color=t["bg_sidebar"], text_color=t["text_muted"])
        self.main_area.configure(fg_color=t["bg_base"])
        self.barra_top.configure(fg_color=t["bg_header"])
        self.status_frame.configure(fg_color=t["bg_header"])
        self.status_dot.config(bg=t["bg_header"])
        self._draw_status_dot()
        self.lbl_status.configure(text_color=t["text_muted"])
        self.header_right.configure(fg_color=t["bg_header"])
        self.user_text_frame.configure(fg_color=t["bg_header"])
        self.avatar_canvas.config(bg=t["border"], highlightbackground=t["accent"])
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
            if clave == seccion:
                data["frame"].configure(fg_color=t["bg_active"])
                data["label"].configure(fg_color=t["bg_active"], text_color=t["accent"])
            else:
                data["frame"].configure(fg_color=t["bg_sidebar"])
                data["label"].configure(fg_color=t["bg_sidebar"], text_color=t["text_muted"])

        self.area_contenido.configure(fg_color=t["bg_base"])

        from pantallas.dashboard   import DashboardView
        from pantallas.catalogos   import CatalogoView
        from pantallas.actividades import ActividadView
        from pantallas.importacion import ImportacionView
        from pantallas.reportes    import ReporteView

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

        self.area_contenido.update_idletasks()

    def _cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres salir?")
        if confirmar:
            self.auth.logout()
            self.root.destroy()
            import main
            main.iniciar_app()
