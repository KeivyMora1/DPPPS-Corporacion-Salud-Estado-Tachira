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
    """Ventana de login con registro, verificación y recuperación por correo."""

    def __init__(self, root, al_iniciar_sesion):
        self.root = root
        self.al_iniciar_sesion = al_iniciar_sesion
        self.auth = AuthController()

        self.root.title("DPPPS — Iniciar Sesión")
        self.root.geometry("460x620")
        self.root.resizable(False, False)

        centrar_ventana(self.root, 460, 620)
        self._construir_ui()

    def _construir_ui(self):
        content = ctk.CTkFrame(self.root, corner_radius=0)
        content.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(content, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=48, pady=50)

        ctk.CTkLabel(inner, text="DPPPS", font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        ctk.CTkLabel(
            inner,
            text="División para la Promoción de la Participación Popular en Salud",
            font=("Segoe UI", 11),
            wraplength=340,
            justify="center",
        ).pack(pady=(0, 24))

        self.entrada_email = ctk.CTkEntry(
            inner,
            font=("Segoe UI", 12),
            corner_radius=6,
            placeholder_text="Correo electrónico",
            height=38,
        )
        self.entrada_email.pack(fill="x", pady=(0, 14))

        pw_frame = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=0)
        pw_frame.pack(fill="x", pady=(0, 18))

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
            pw_frame,
            text="👁",
            width=32,
            height=30,
            font=("Segoe UI", 14),
            fg_color="transparent",
            corner_radius=4,
            command=self._toggle_ojo,
        )
        self.btn_ojo.place(relx=1.0, rely=0.5, anchor="e", x=-6)

        self.btn_login = ctk.CTkButton(
            inner,
            text="→ Iniciar sesión",
            font=("Segoe UI", 12, "bold"),
            fg_color="#613BE3",
            hover_color="#4e2fb8",
            corner_radius=8,
            height=44,
            cursor="hand2",
            command=self._intentar_login,
        )
        self.btn_login.pack(fill="x")

        self.btn_registro = ctk.CTkButton(
            inner,
            text="Crear cuenta",
            font=("Segoe UI", 11, "bold"),
            fg_color="#1C8C5C",
            hover_color="#166C49",
            corner_radius=8,
            height=38,
            cursor="hand2",
            command=self._abrir_registro,
        )
        self.btn_registro.pack(fill="x", pady=(12, 6))

        self.btn_recuperar = ctk.CTkButton(
            inner,
            text="Olvidé mi contraseña",
            font=("Segoe UI", 10),
            fg_color="transparent",
            border_color="#613BE3",
            border_width=1,
            height=34,
            cursor="hand2",
            command=self._abrir_recuperacion,
        )
        self.btn_recuperar.pack(fill="x")

        self.lbl_error = ctk.CTkLabel(inner, text="", font=("Segoe UI", 9), wraplength=320)
        self.lbl_error.pack(pady=(14, 0))

        self.root.bind("<Return>", lambda e: self._intentar_login())
        self.entrada_email.focus()

    def _toggle_ojo(self):
        self._ojo_visible = not self._ojo_visible
        if self._ojo_visible:
            self.entrada_password.configure(show="")
            self.btn_ojo.configure(text_color="#613BE3")
        else:
            self.entrada_password.configure(show="●")
            self.btn_ojo.configure(text_color="gray70")

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

    def _intentar_login(self):
        email = self.entrada_email.get().strip()
        password = self.entrada_password.get()

        if not email or not password:
            self._mostrar_error("⚠  Por favor completa todos los campos.")
            return

        self.btn_login.configure(state="disabled", text="⏳ Verificando...")
        self.lbl_error.configure(text="")
        self.root.update_idletasks()

        exito = self.auth.login(email, password)

        if exito:
            self.lbl_error.configure(text="✔  Acceso concedido", text_color="#317E87")
            self.root.after(400, self.al_iniciar_sesion)
        else:
            self._mostrar_error("⚠  Correo o contraseña incorrectos, o tu cuenta aún no está verificada.")
            self.btn_login.configure(state="normal", text="→ Iniciar sesión")
            self.entrada_password.delete(0, "end")
            self.entrada_password.focus()
            self._animar_sacudida()

    def _abrir_registro(self):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Crear cuenta")
        ventana.geometry("420x420")
        ventana.resizable(False, False)
        centrar_ventana(ventana, 420, 420)
        ventana.grab_set()

        frame = ctk.CTkFrame(ventana, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(frame, text="Registro", font=("Segoe UI", 18, "bold")).pack(pady=(0, 16))

        nombre = ctk.CTkEntry(frame, placeholder_text="Nombre")
        nombre.pack(fill="x", pady=(0, 8))

        apellido = ctk.CTkEntry(frame, placeholder_text="Apellido")
        apellido.pack(fill="x", pady=(0, 8))

        email = ctk.CTkEntry(frame, placeholder_text="Correo electrónico")
        email.pack(fill="x", pady=(0, 8))

        password = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="●")
        password.pack(fill="x", pady=(0, 12))

        def registrar():
            nombre_texto = nombre.get().strip()
            apellido_texto = apellido.get().strip()
            email_texto = email.get().strip()
            password_texto = password.get()

            respuesta = self.auth.registrar_usuario(nombre_texto, apellido_texto, email_texto, password_texto)
            if not respuesta["success"]:
                messagebox.showerror("Registro", respuesta["message"])
                return
            messagebox.showinfo("Registro", respuesta["message"])
            ventana.destroy()
            self._abrir_verificacion(email_texto)

        btn = ctk.CTkButton(frame, text="Registrarme", command=registrar)
        btn.pack(fill="x", pady=(8, 0))

    def _abrir_verificacion(self, email):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Verificar correo")
        ventana.geometry("400x260")
        ventana.resizable(False, False)
        centrar_ventana(ventana, 400, 260)
        ventana.grab_set()

        frame = ctk.CTkFrame(ventana, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(frame, text="Verifica tu correo", font=("Segoe UI", 18, "bold")).pack(pady=(0, 12))
        ctk.CTkLabel(frame, text=f"Correo: {email}", wraplength=300).pack(pady=(0, 12))

        codigo_entry = ctk.CTkEntry(frame, placeholder_text="Código de verificación")
        codigo_entry.pack(fill="x", pady=(0, 10))

        def confirmar():
            ok = self.auth.verificar_email(email, codigo_entry.get())
            if ok:
                messagebox.showinfo("Verificación", "Correo verificado correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Verificación", "Código incorrecto o expirado.")

        ctk.CTkButton(frame, text="Confirmar código", command=confirmar).pack(fill="x")

    def _abrir_recuperacion(self):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Recuperar contraseña")
        ventana.geometry("400x340")
        ventana.resizable(False, False)
        centrar_ventana(ventana, 400, 340)
        ventana.grab_set()

        frame = ctk.CTkFrame(ventana, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Recuperar contraseña", font=("Segoe UI", 18, "bold")).pack(pady=(0, 14))

        correo = ctk.CTkEntry(frame, placeholder_text="Correo electrónico")
        correo.pack(fill="x", pady=(0, 8))

        codigo = ctk.CTkEntry(frame, placeholder_text="Código recibido")
        codigo.pack(fill="x", pady=(0, 8))
        codigo.pack_forget()

        nueva = ctk.CTkEntry(frame, placeholder_text="Nueva contraseña", show="●")
        nueva.pack(fill="x", pady=(0, 12))
        nueva.pack_forget()

        def enviar_codigo():
            email = correo.get().strip()
            if not email:
                messagebox.showerror("Recuperación", "Ingresa tu correo electrónico.")
                return

            respuesta = self.auth.solicitar_recuperacion(email)
            if not respuesta["success"]:
                messagebox.showerror("Recuperación", respuesta["message"])
                return

            messagebox.showinfo("Recuperación", respuesta["message"])

            correo.pack_forget()
            codigo.pack(fill="x", pady=(0, 8))
            btn_verificar.pack(fill="x")
            btn_enviar.pack_forget()
            btn_restablecer.pack_forget()

        def verificar_codigo():
            email = self.auth.usuario_dao.obtener_por_email(correo.get().strip())
            if email is None:
                messagebox.showerror("Recuperación", "No se encontró ese correo registrado.")
                return

            codigo_ingresado = codigo.get().strip()
            if not codigo_ingresado:
                messagebox.showerror("Recuperación", "Ingresa el código recibido por correo.")
                return

            usuario = self.auth.usuario_dao.obtener_por_email(correo.get().strip())
            if usuario and usuario.get("codigo_recuperacion") != codigo_ingresado:
                messagebox.showerror("Recuperación", "Código incorrecto o expirado.")
                return

            codigo.pack_forget()
            nueva.pack(fill="x", pady=(0, 12))
            btn_verificar.pack_forget()
            btn_restablecer.pack(fill="x")

        def recuperar():
            email = correo.get().strip()
            codigo_ingresado = codigo.get().strip()
            nueva_password = nueva.get()

            if not email or not codigo_ingresado or not nueva_password:
                messagebox.showerror("Recuperación", "Debes ingresar el correo, el código y la nueva contraseña.")
                return

            resultado = self.auth.cambiar_password_con_codigo(email, codigo_ingresado, nueva_password)
            if not resultado["success"]:
                messagebox.showerror("Recuperación", resultado["message"])
                return
            messagebox.showinfo("Recuperación", resultado["message"])
            ventana.destroy()

        btn_enviar = ctk.CTkButton(frame, text="Enviar código de recuperación", command=enviar_codigo)
        btn_enviar.pack(fill="x")

        btn_verificar = ctk.CTkButton(frame, text="Verificar código", command=verificar_codigo)
        btn_verificar.pack(fill="x")
        btn_verificar.pack_forget()

        btn_restablecer = ctk.CTkButton(frame, text="Restablecer contraseña", command=recuperar)
        btn_restablecer.pack(fill="x")
        btn_restablecer.pack_forget()
