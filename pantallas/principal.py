import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

from db import AuthController
from utils import centrar_ventana, set_favicon
from ui_helpers import (
    frame, frame_transparent, label, label_title, label_subtitle,
    btn_nav, btn_danger, separator, canvas_circle, scrollable_frame
)

from pantallas.actividades.controller import ControladorActividad
from pantallas.vocerias.controller import ControladorVoceria
from pantallas.reportes.controller import ControladorReporte
from pantallas.tipos_actividad.controller import ControladorTipoActividad

SECCION_INICIAL = "actividades"
CONTROLADORES = {
    "actividades": ControladorActividad,
    "vocerias": ControladorVoceria,
    "reportes": ControladorReporte,
    "tipos_actividad": ControladorTipoActividad,
}


class ModeloPrincipal:
    def __init__(self):
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

    def logout(self):
        self.auth.logout()

    def get_nombre_usuario(self):
        if self.usuario:
            return self.usuario["nombre_completo"]
        return "Usuario"

    def get_username(self):
        if self.usuario:
            username = self.usuario.get("username") or "Usuario"
            return username[:1].upper() + username[1:]
        return "Usuario"

    def get_email(self):
        if self.usuario:
            return self.usuario.get("email", "")
        return ""

    def get_rol(self):
        if self.usuario:
            roles = {
                "propietario": "Propietario",
                "administrador": "Administrador",
                "lector": "Lector",
            }
            return roles.get(self.usuario.get("rol"), "Lector")
        return "Lector"

    def es_propietario(self):
        return bool(self.usuario and self.usuario.get("rol") == "propietario")


class VistaPrincipal:

    MENU_ITEMS = [
        ("actividades", "Actividades"),
        ("vocerias",    "Vocerias CS"),
        ("reportes",    "Reportes"),
        ("tipos_actividad", "Tipos de actividad"),
    ]

    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self._after_ids = []

        self.frames_menu = {}
        self.seccion_actual = SECCION_INICIAL

        self.root.title("DPPPS")

        self._construir_ui()

        aid = self.root.after(50, lambda: self.root.state("zoomed"))
        self._after_ids.append(aid)

    def _construir_ui(self):
        self.panel_menu = frame(
            self.root,
            fg_color="#2d2d2d",
            width=240,
            corner_radius=0,
            border_width=2,
            border_color="#111827"
        )
        self.panel_menu.pack(fill="y", side="left")
        self.panel_menu.pack_propagate(False)

        self.sidebar_inner = frame(self.panel_menu, fg_color="#2d2d2d", corner_radius=0)
        self.sidebar_inner.pack(side="left", fill="both", expand=True)

        self.logo_area = frame(self.sidebar_inner, fg_color="#2d2d2d", corner_radius=0)
        self.logo_area.pack(fill="x", padx=20, pady=(20, 28))

        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "logo2.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(140, 140))
                self.logo_label = ctk.CTkLabel(self.logo_area, image=logo_img, text="")
                self.logo_label.pack(anchor="center", pady=(0, 16))
            except Exception:
                self._draw_logo_letter_fallback()
        else:
            self._draw_logo_letter_fallback()

        self.logo_text_frame = frame(self.logo_area, fg_color="#2d2d2d", corner_radius=0)
        self.logo_text_frame.pack(anchor="center")

        self.lbl_logo_title = label_title(self.logo_text_frame, "DPPPS")
        self.lbl_logo_title.pack(anchor="center", pady=0)

        self.lbl_logo_sub = label_subtitle(self.logo_text_frame, "SISTEMA DE INFORMES")
        self.lbl_logo_sub.pack(anchor="center", pady=0)

        separator(self.sidebar_inner, horizontal=True, fg_color="gray40").pack(fill="x", padx=20, pady=(0, 12))

        self.nav_frame = frame(self.sidebar_inner, fg_color="#2d2d2d", corner_radius=0)
        self.nav_frame.pack(fill="x", padx=10)

        items_menu = self.MENU_ITEMS
        if not self.controlador.modelo.es_propietario():
            items_menu = [
                (clave, texto)
                for clave, texto in items_menu
                if clave != "tipos_actividad"
            ]

        for clave, label_text in items_menu:
            btn = btn_nav(self.nav_frame, label_text, lambda c=clave: self.controlador.navegar(c))
            btn.pack(fill="x", pady=3, padx=4)
            self.frames_menu[clave] = {"button": btn}

        self.main_area = frame(self.root, corner_radius=0)
        self.main_area.pack(fill="both", expand=True)

        self.barra_top = frame(self.main_area, fg_color="gray15", height=64, corner_radius=0)
        self.barra_top.pack(fill="x", side="top")
        self.barra_top.pack_propagate(False)

        self.status_frame = frame(self.barra_top, fg_color="gray15", corner_radius=0)
        self.status_frame.pack(side="left", padx=24)

        self.status_dot = canvas_circle(self.status_frame, 8, bg="gray15")
        self.status_dot.pack(side="left", padx=(0, 8))

        self.lbl_status = label(
            self.status_frame, "DPPPS | División para la Promoción de la Participación Popular en Salud",
            font_size=14, bold=True
        )
        self.lbl_status.pack(side="left")

        self.header_right = frame(self.barra_top, fg_color="gray15", corner_radius=0)
        self.header_right.pack(side="right", padx=24)

        nombre = self.controlador.modelo.get_nombre_usuario()
        username = self.controlador.modelo.get_username()
        email = self.controlador.modelo.get_email()
        rol = self.controlador.modelo.get_rol()

        self.user_info_frame = frame_transparent(self.header_right)
        self.user_info_frame.pack(side="right")

        self.avatar_canvas = canvas_circle(self.user_info_frame, 44, bg="gray15", cursor="hand2")
        self.avatar_canvas.pack(side="right", padx=(10, 0), pady=10)
        self.avatar_canvas.bind("<Button-1>", lambda e: self._toggle_avatar_menu(e))

        self.user_text_frame = frame_transparent(self.user_info_frame)
        self.user_text_frame.pack(side="right", padx=(0, 10))

        self.lbl_user_name = label(
            self.user_text_frame, username, font_size=12, bold=True, height=17
        )
        self.lbl_user_name.pack(anchor="e")

        self.lbl_user_email = label(self.user_text_frame, email, font_size=10, height=15)
        self.lbl_user_email.pack(anchor="e")

        self.lbl_user_role = ctk.CTkLabel(
            self.user_text_frame,
            text=rol,
            font=("Segoe UI", 9),
            text_color="#9CA3AF",
            height=14,
        )
        self.lbl_user_role.pack(anchor="e")

        separator(self.main_area, horizontal=True, fg_color="gray40").pack(fill="x", side="top")

        self.area_contenido = frame(self.main_area, corner_radius=0)
        self.area_contenido.pack(fill="both", expand=True)

        self._draw_status_dot()
        self._draw_avatar(username)

    def _draw_logo_letter_fallback(self):
        """Dibuja un círculo con la letra D si no se puede cargar la imagen."""
        canvas = canvas_circle(self.logo_area, 140, bg="#613BE3")
        canvas.pack(anchor="center", pady=(0, 16))
        canvas.create_text(70, 70, text="D", font=("Segoe UI", 48, "bold"), fill="#ffffff")

        self.logo_text_frame = frame(self.logo_area, fg_color="#2d2d2d", corner_radius=0)
        self.logo_text_frame.pack(anchor="center")

        self.lbl_logo_title = label_title(self.logo_text_frame, "DPPPS")
        self.lbl_logo_title.pack(anchor="center", pady=0)

        self.lbl_logo_sub = label_subtitle(self.logo_text_frame, "SISTEMA DE INFORMES")
        self.lbl_logo_sub.pack(anchor="center", pady=0)

    def _draw_status_dot(self):
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 7, 7, fill="#317E87", outline="")

    def _draw_avatar(self, username):
        self.avatar_canvas.delete("all")
        inicial = username[0].upper() if username else "U"
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
        set_favicon(self._avatar_menu)
        self._avatar_menu.overrideredirect(True)
        self._avatar_menu.geometry(f"180x42+{x - 136}+{y}")
        self._avatar_menu.configure(fg_color="gray25", corner_radius=10)

        btn_logout = btn_danger(self._avatar_menu, "Cerrar sesión", self.controlador.cerrar_sesion)
        btn_logout.pack(fill="x", padx=8, pady=8)

        self._avatar_menu.focus_set()

        aid = self.root.after(10, lambda: self.root.bind(
            "<Button-1>", self._cerrar_avatar_menu, add="+"
        ))
        self._after_ids.append(aid)

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

    def actualizar_nav(self, seccion):
        """Resalta el botón activo en el menú."""
        for clave, data in self.frames_menu.items():
            btn = data["button"]
            if clave == seccion:
                btn.configure(fg_color="#613BE3", hover_color="#4e2fb8", text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", hover_color="gray30", text_color="gray70")


# ─────────────────────────────────────────────────────────────
# CONTROLADOR
class ControladorPrincipal:
    def __init__(self, root):
        self.root = root
        self.modelo = ModeloPrincipal()
        self.vista = None
        self.vista = VistaPrincipal(root, self)
        self.navegar(SECCION_INICIAL)

    def navegar(self, seccion):
        if self.vista is None:
            return

        if seccion == "tipos_actividad" and not self.modelo.es_propietario():
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el usuario propietario puede acceder a Tipos de actividad.",
            )
            return

        self.vista.seccion_actual = seccion

        for widget in self.vista.area_contenido.winfo_children():
            widget.destroy()

        self.vista.actualizar_nav(seccion)

        controlador_clase = CONTROLADORES.get(seccion)
        if controlador_clase is None:
            self.vista.area_contenido.update_idletasks()
            return

        controlador_clase(self.vista.area_contenido)

        self.vista.area_contenido.update_idletasks()

    def cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres salir?")
        if confirmar:
            if self.vista and hasattr(self.vista, '_after_ids'):
                for aid in self.vista._after_ids:
                    try:
                        self.root.after_cancel(aid)
                    except Exception:
                        pass
            self.modelo.logout()
            self.root.destroy()
            import main
            main.iniciar_app()


class MainView:
    def __init__(self, root):
        self._controlador = ControladorPrincipal(root)


__all__ = [
    "ModeloPrincipal",
    "VistaPrincipal",
    "ControladorPrincipal",
    "MainView",
    "SECCION_INICIAL",
]