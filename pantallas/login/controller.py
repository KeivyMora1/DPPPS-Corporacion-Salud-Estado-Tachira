from tkinter import messagebox
import customtkinter as ctk

from db import AuthController
from .model import ModeloLogin
from .view import VistaLogin
from utils import centrar_ventana, set_favicon


class ControladorLogin:
    def __init__(self, root, al_iniciar_sesion):
        self.al_iniciar_sesion = al_iniciar_sesion
        self.modelo = ModeloLogin()
        self.vista = VistaLogin(root, self)
        self._after_ids = []

    @staticmethod
    def _validar_datos_registro(nombre, apellido, username, email, password):
        nombre = (nombre or "").strip()
        apellido = (apellido or "").strip()
        username = (username or "").strip()
        email = (email or "").strip()

        if not nombre or not apellido or not username or not email or not password:
            return "Completa todos los campos."
        if len(nombre) < 2:
            return "El nombre debe tener al menos 2 caracteres."
        if any(caracter.isdigit() for caracter in nombre):
            return "El nombre no puede contener números."
        if len(apellido) < 2:
            return "El apellido debe tener al menos 2 caracteres."
        if any(caracter.isdigit() for caracter in apellido):
            return "El apellido no puede contener números."
        if len(username) < 3:
            return "El nombre de usuario debe tener al menos 3 caracteres."
        if any(caracter.isspace() for caracter in username):
            return "El nombre de usuario no puede contener espacios."
        if "@" not in email or "." not in email.split("@")[-1] or len(email.split("@")[-1]) < 2:
            return "Ingresa un correo válido."
        if len(password) < 6:
            return "La contraseña debe tener al menos 6 caracteres."
        return None

    def intentar_login(self):
        email = self.vista.entrada_email.get().strip()
        password = self.vista.entrada_password.get()

        if not email or not password:
            self.vista.mostrar_error("⚠  Por favor completa todos los campos.")
            return

        self.vista.btn_login.configure(state="disabled", text="⏳ Verificando...")
        self.vista.lbl_error.configure(text="")
        self.vista.root.update_idletasks()

        exito = self.modelo.login(email, password)

        if exito:
            self.vista.lbl_error.configure(text="✔  Acceso concedido", text_color="#317E87")
            aid = self.vista.root.after(400, self.al_iniciar_sesion)
            self._after_ids.append(aid)
        else:
            usuario = None
            if "@" in email:
                usuario = self.modelo.obtener_usuario_por_email(email)
            else:
                usuario = self.modelo.auth.usuario_dao.obtener_por_username(email)

            if usuario and usuario.get("email_verificado") in (False, 0, None):
                self.modelo.reenviar_codigo_verificacion(usuario["email"])
                self.vista.lbl_error.configure(text="⚠  Tu cuenta aún no está verificada. Te hemos enviado un nuevo código.", text_color="#F1B94B")
                self.vista.btn_login.configure(state="normal", text="→ Iniciar sesión")
                self.vista.entrada_password.delete(0, "end")
                self.abrir_verificacion(usuario["email"])
                return

            self.vista.mostrar_error("⚠  Correo o contraseña incorrectos.")
            self.vista.btn_login.configure(state="normal", text="→ Iniciar sesión")
            self.vista.entrada_password.delete(0, "end")
            self.vista.entrada_password.focus()
            self.vista.animar_sacudida()

    def abrir_registro(self):
        ventana = ctk.CTkToplevel(self.vista.root)
        set_favicon(ventana)
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

        username = ctk.CTkEntry(frame, placeholder_text="Nombre de usuario")
        username.pack(fill="x", pady=(0, 8))

        email = ctk.CTkEntry(frame, placeholder_text="Correo electrónico")
        email.pack(fill="x", pady=(0, 8))

        password = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="●")
        password.pack(fill="x", pady=(0, 12))

        def registrar():
            nombre_texto = nombre.get().strip()
            apellido_texto = apellido.get().strip()
            username_texto = username.get().strip()
            email_texto = email.get().strip()
            password_texto = password.get()

            error = self._validar_datos_registro(
                nombre_texto,
                apellido_texto,
                username_texto,
                email_texto,
                password_texto,
            )
            if error:
                messagebox.showerror("Registro", error)
                if not nombre_texto:
                    nombre.focus()
                elif not apellido_texto:
                    apellido.focus()
                elif not username_texto:
                    username.focus()
                elif not email_texto:
                    email.focus()
                else:
                    password.focus()
                return

            btn.configure(state="disabled", text="⏳ Cargando...")
            ventana.update_idletasks()

            respuesta = self.modelo.registrar_usuario(
                nombre_texto,
                apellido_texto,
                email_texto,
                password_texto,
                username=username_texto,
            )
            if not respuesta["success"]:
                btn.configure(state="normal", text="Registrarme")
                messagebox.showerror("Registro", respuesta["message"])
                return
            ventana.destroy()
            self.abrir_verificacion(email_texto)

        btn = ctk.CTkButton(frame, text="Registrarme", command=registrar)
        btn.pack(fill="x", pady=(8, 0))

    def abrir_verificacion(self, email):
        ventana = ctk.CTkToplevel(self.vista.root)
        set_favicon(ventana)
        ventana.title("Verificar correo")
        ventana.geometry("400x260")
        ventana.resizable(False, False)
        centrar_ventana(ventana, 400, 260)
        ventana.grab_set()

        frame = ctk.CTkFrame(ventana, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(frame, text="Se envio un codigo a tu correo", font=("Segoe UI", 18, "bold")).pack(pady=(0, 12))
        ctk.CTkLabel(frame, text=f"Correo: {email}", wraplength=300).pack(pady=(0, 12))

        def validar_codigo(texto):
            return texto == "" or (texto.isdigit() and len(texto) <= 6)

        vcmd = (ventana.register(validar_codigo), "%P")
        codigo_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Código de verificación",
            validate="key",
            validatecommand=vcmd,
            )
        codigo_entry.pack(fill="x", pady=(0, 10))

        def confirmar():
            codigo = codigo_entry.get().strip()
            if not codigo:
                messagebox.showerror("Verificación", "Ingresa el código de verificación.")
                codigo_entry.focus()
                return
            if len(codigo) != 6 or not codigo.isdigit():
                messagebox.showerror("Verificación", "El código debe tener exactamente 6 dígitos numéricos.")
                codigo_entry.focus()
                return

            ok = self.modelo.verificar_email(email, codigo)
            if ok:
                messagebox.showinfo("Verificación", "Correo verificado correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Verificación", "Código incorrecto o expirado.")

        ctk.CTkButton(frame, text="Verificar", command=confirmar).pack(fill="x")

    def abrir_recuperacion(self):
        ventana = ctk.CTkToplevel(self.vista.root)
        set_favicon(ventana)
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

            respuesta = self.modelo.solicitar_recuperacion(email)
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
            email = self.modelo.obtener_usuario_por_email(correo.get().strip())
            if email is None:
                messagebox.showerror("Recuperación", "No se encontró ese correo registrado.")
                return

            codigo_ingresado = codigo.get().strip()
            if not codigo_ingresado:
                messagebox.showerror("Recuperación", "Ingresa el código recibido por correo.")
                return

            usuario = self.modelo.obtener_usuario_por_email(correo.get().strip())
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

            resultado = self.modelo.cambiar_password_con_codigo(email, codigo_ingresado, nueva_password)
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


__all__ = ["ControladorLogin"]
