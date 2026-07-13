# ============================================================
# pantallas/login.py
# Pantalla de inicio de sesión del sistema DPPPS.
# Es la primera ventana que ve el usuario al abrir la app.
# ============================================================

import tkinter as tk
from tkinter import messagebox
from db import AuthController
from utils import centrar_ventana


class LoginView:
    """
    Ventana de login. Muestra un formulario con usuario y contraseña.
    Si las credenciales son correctas, llama a la función 'al_iniciar_sesion'
    que abre la ventana principal.
    """

    def __init__(self, root, al_iniciar_sesion):
        """
        root              → La ventana raíz de Tkinter
        al_iniciar_sesion → Función que se llama cuando el login es exitoso
        """
        self.root = root
        self.al_iniciar_sesion = al_iniciar_sesion
        self.auth = AuthController()

        self.root.title("DPPPS — Iniciar Sesión")
        self.root.geometry("420x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        centrar_ventana(self.root, 420, 500)
        self._construir_ui()

    def _construir_ui(self):
        """Crea todos los elementos visuales de la pantalla de login."""

        # Marco principal centrado
        marco = tk.Frame(self.root, bg="#16213e", padx=40, pady=40)
        marco.place(relx=0.5, rely=0.5, anchor="center", width=340, height=420)

        # Logo / Título
        tk.Label(
            marco, text="🏥", font=("Arial", 40),
            bg="#16213e", fg="#e94560"
        ).pack(pady=(0, 5))

        tk.Label(
            marco, text="DPPPS", font=("Arial", 20, "bold"),
            bg="#16213e", fg="#ffffff"
        ).pack()

        tk.Label(
            marco, text="Sistema de Informes", font=("Arial", 10),
            bg="#16213e", fg="#8892b0"
        ).pack(pady=(0, 30))

        # Campo: Usuario
        tk.Label(
            marco, text="Usuario", font=("Arial", 10, "bold"),
            bg="#16213e", fg="#ccd6f6", anchor="w"
        ).pack(fill="x")

        self.entrada_usuario = tk.Entry(
            marco, font=("Arial", 12),
            bg="#0f3460", fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat", bd=8
        )
        self.entrada_usuario.pack(fill="x", pady=(4, 16))

        # Campo: Contraseña
        tk.Label(
            marco, text="Contraseña", font=("Arial", 10, "bold"),
            bg="#16213e", fg="#ccd6f6", anchor="w"
        ).pack(fill="x")

        self.entrada_password = tk.Entry(
            marco, font=("Arial", 12),
            bg="#0f3460", fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat", bd=8,
            show="●"
        )
        self.entrada_password.pack(fill="x", pady=(4, 24))

        # Botón de login
        self.btn_login = tk.Button(
            marco, text="Iniciar Sesión",
            font=("Arial", 12, "bold"),
            bg="#e94560", fg="#ffffff",
            relief="flat", cursor="hand2",
            command=self._intentar_login
        )
        self.btn_login.pack(fill="x", ipady=10)

        # Efecto hover en el botón
        self.btn_login.bind("<Enter>", lambda e: self.btn_login.config(bg="#c73652"))
        self.btn_login.bind("<Leave>", lambda e: self.btn_login.config(bg="#e94560"))

        # Mensaje de error (oculto por defecto)
        self.lbl_error = tk.Label(
            marco, text="", font=("Arial", 9),
            bg="#16213e", fg="#e94560"
        )
        self.lbl_error.pack(pady=(12, 0))

        # Atajo de teclado: Enter también hace login
        self.root.bind("<Return>", lambda e: self._intentar_login())
        self.entrada_usuario.focus()

    def _intentar_login(self):
        """
        Se ejecuta cuando el usuario hace clic en 'Iniciar Sesión' o presiona Enter.
        Valida los campos y llama al controlador de autenticación.
        """
        username = self.entrada_usuario.get().strip()
        password = self.entrada_password.get()

        if not username or not password:
            self.lbl_error.config(text="⚠ Por favor completa todos los campos.")
            return

        self.btn_login.config(state="disabled", text="Verificando...")

        exito = self.auth.login(username, password)

        if exito:
            self.lbl_error.config(text="")
            self.al_iniciar_sesion()
        else:
            self.lbl_error.config(text="⚠ Usuario o contraseña incorrectos.")
            self.btn_login.config(state="normal", text="Iniciar Sesión")
            self.entrada_password.delete(0, "end")
            self.entrada_password.focus()
