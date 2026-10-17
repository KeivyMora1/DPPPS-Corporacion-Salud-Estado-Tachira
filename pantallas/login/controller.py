from tkinter import messagebox
import customtkinter as ctk

from db import validar_correo
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
        if len(nombre) > 60:
            return "El nombre no puede superar 60 caracteres."
        if any(caracter.isdigit() for caracter in nombre):
            return "El nombre no puede contener números."
        if len(apellido) < 2:
            return "El apellido debe tener al menos 2 caracteres."
        if len(apellido) > 60:
            return "El apellido no puede superar 60 caracteres."
        if any(caracter.isdigit() for caracter in apellido):
            return "El apellido no puede contener números."
        if len(f"{nombre} {apellido}") > 120:
            return "El nombre completo no puede superar 120 caracteres."
        if len(username) < 3:
            return "El nombre de usuario debe tener al menos 3 caracteres."
        if len(username) > 50:
            return "El nombre de usuario no puede superar 50 caracteres."
        if any(caracter.isspace() for caracter in username):
            return "El nombre de usuario no puede contener espacios."
        if not validar_correo(email):
            return "Ingresa un correo válido."
        if len(email) > 60:
            return "El correo no puede superar 60 caracteres."
        if len(password) < 8:
            return "La contraseña debe tener al menos 8 caracteres."
        if len(password) > 60:
            return "La contraseña no puede superar 60 caracteres."
        if len(password.encode("utf-8")) > 72:
            return "La contraseña no puede superar 72 bytes."
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
            usuario = self.modelo.autenticar_pendiente_verificacion(email, password)
            if usuario:
                respuesta = self.modelo.reenviar_codigo_verificacion(usuario["email"])
                self.vista.btn_login.configure(state="normal", text="→ Iniciar sesión")
                self.vista.entrada_password.delete(0, "end")
                color = "#F1B94B" if respuesta["success"] else "#c45050"
                self.vista.lbl_error.configure(text=respuesta["message"], text_color=color)
                if respuesta["success"]:
                    self.abrir_verificacion(usuario["email"])
                return

            self.vista.mostrar_error("⚠  Correo o contraseña incorrectos.")
            self.vista.btn_login.configure(state="normal", text="→ Iniciar sesión")
            self.vista.entrada_password.delete(0, "end")
            self.vista.entrada_password.focus()
            self.vista.animar_sacudida()

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

        def validar_codigo_recuperacion(texto):
            return texto == "" or (texto.isdigit() and len(texto) <= 6)

        vcmd_codigo = (ventana.register(validar_codigo_recuperacion), "%P")
        codigo = ctk.CTkEntry(
            frame,
            placeholder_text="Código recibido",
            validate="key",
            validatecommand=vcmd_codigo,
        )
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
