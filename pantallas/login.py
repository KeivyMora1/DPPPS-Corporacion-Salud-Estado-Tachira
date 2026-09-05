# ============================================================
# pantallas/login.py
# Pantalla de inicio de sesión del sistema DPPPS.
# Rediseñada con customtkinter y estética premium.
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
from db import AuthController
from utils import centrar_ventana


class LoginView:
    """
    Ventana de login rediseñada con estética premium.
    """

    def __init__(self, root, al_iniciar_sesion):
        self.root = root
        self.al_iniciar_sesion = al_iniciar_sesion
        self.auth = AuthController()

        self.root.title("DPPPS — Iniciar Sesión")
        self.root.geometry("460x560")
        self.root.resizable(False, False)

        centrar_ventana(self.root, 460, 560)
        self._construir_ui()

    def _construir_ui(self):
        content = ctk.CTkFrame(self.root, corner_radius=0)
        content.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(content, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=48, pady=72)

        ctk.CTkLabel(
            inner, text="DPPPS",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            inner,
            text="Dirección de Programas y Proyectos de Promoción de Salud",
            font=("Segoe UI", 11),
            wraplength=340,
            justify="center",
        ).pack(pady=(0, 28))

        self.entrada_usuario = ctk.CTkEntry(
            inner,
            font=("Segoe UI", 12),
            corner_radius=6,
            placeholder_text="Usuario",
            height=38,
        )
        self.entrada_usuario.pack(fill="x", pady=(0, 14), ipady=0)

        pw_frame = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=0)
        pw_frame.pack(fill="x", pady=(0, 28))

        self.entrada_password = ctk.CTkEntry(
            pw_frame,
            font=("Segoe UI", 12),
            corner_radius=6,
            show="●",
            placeholder_text="Contraseña",
            height=38,
        )
        self.entrada_password.pack(fill="x")

        self._ojo_visible = False
        self.btn_ojo = ctk.CTkButton(
            pw_frame, text="👁", width=32, height=30,
            font=("Segoe UI", 14),
            fg_color="transparent",
            corner_radius=4,
            command=self._toggle_ojo,
        )
        self.btn_ojo.place(relx=1.0, rely=0.5, anchor="e", x=-6)

        self.btn_login = ctk.CTkButton(
            inner,
            text="  →  Iniciar Sesión",
            font=("Segoe UI", 12, "bold"),
            fg_color="#613BE3",
            hover_color="#4e2fb8",
            corner_radius=8,
            height=44,
            cursor="hand2",
            command=self._intentar_login,
        )
        self.btn_login.pack(fill="x")

        self.lbl_error = ctk.CTkLabel(
            inner, text="",
            font=("Segoe UI", 9),
            wraplength=320,
        )
        self.lbl_error.pack(pady=(14, 0))

        self.root.bind("<Return>", lambda e: self._intentar_login())
        self.entrada_usuario.focus()

    def _toggle_ojo(self):
        self._ojo_visible = not self._ojo_visible
        if self._ojo_visible:
            self.entrada_password.configure(show="")
            self.btn_ojo.configure(text_color="#613BE3")
        else:
            self.entrada_password.configure(show="●")
            self.btn_ojo.configure(text_color="gray70")

    def _intentar_login(self):
        username = self.entrada_usuario.get().strip()
        password = self.entrada_password.get()

        if not username or not password:
            self._mostrar_error("⚠  Por favor completa todos los campos.")
            return

        self.btn_login.configure(state="disabled", text="  ⏳  Verificando...")
        self.lbl_error.configure(text="")
        self.root.update_idletasks()

        exito = self.auth.login(username, password)

        if exito:
            self.lbl_error.configure(text="✔  Acceso concedido", text_color="#317E87")
            self.root.after(400, self.al_iniciar_sesion)
        else:
            self._mostrar_error("⚠  Usuario o contraseña incorrectos.")
            self.btn_login.configure(state="normal", text="  →  Iniciar Sesión")
            self.entrada_password.delete(0, "end")
            self.entrada_password.focus()
            self._animar_sacudida()

    def _mostrar_error(self, msg):
        self.lbl_error.configure(text=msg, text_color="#c45050")

    def _animar_sacudida(self):
        x0, y0 = self.root.winfo_x(), self.root.winfo_y()
        movs = [6, -6, 5, -5, 3, -3, 0]

        def paso(i=0):
            if i < len(movs):
                self.root.geometry(f"+{x0 + movs[i]}+{y0}")
                self.root.after(35, lambda: paso(i + 1))
            else:
                self.root.geometry(f"+{x0}+{y0}")

        paso()