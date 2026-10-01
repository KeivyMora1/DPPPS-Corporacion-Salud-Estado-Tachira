import os
import customtkinter as ctk
from utils import centrar_ventana


class VistaLogin:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self._after_ids = []

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

        logo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "assets", "images", "logo2.png")
        )
        if os.path.exists(logo_path):
            try:
                from PIL import Image
                img = Image.open(logo_path)
                logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
                ctk.CTkLabel(inner, image=logo_img, text="").pack(pady=(0, 12))
            except Exception:
                pass

        ctk.CTkLabel(inner, text="DPPPS", font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        ctk.CTkLabel(
            inner,
            text="División para la Promoción de la Participación Popular en Salud",
            font=("Segoe UI", 11),
            wraplength=340,
            justify="center",
        ).pack(pady=(0, 24))

        validar_credencial = (inner.register(lambda texto: len(texto) <= 60), "%P")
        self.entrada_email = ctk.CTkEntry(
            inner,
            font=("Segoe UI", 12),
            corner_radius=6,
            placeholder_text="Nombre de usuario o correo",
            height=38,
            validate="key",
            validatecommand=validar_credencial,
        )
        self.entrada_email.pack(fill="x", pady=(0, 14))

        pw_frame = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=0)
        pw_frame.pack(fill="x", pady=(0, 18))

        validar_password = (
            pw_frame.register(
                lambda texto: len(texto) <= 60 and len(texto.encode("utf-8")) <= 72
            ),
            "%P",
        )
        self.entrada_password = ctk.CTkEntry(
            pw_frame,
            font=("Segoe UI", 12),
            corner_radius=6,
            show="●",
            placeholder_text="Contraseña",
            height=38,
            validate="key",
            validatecommand=validar_password,
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
            command=self.controlador.intentar_login,
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
            command=self.controlador.abrir_registro,
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
            command=self.controlador.abrir_recuperacion,
        )
        self.btn_recuperar.pack(fill="x")

        self.lbl_error = ctk.CTkLabel(inner, text="", font=("Segoe UI", 9), wraplength=320)
        self.lbl_error.pack(pady=(14, 0))

        self.root.bind("<Return>", lambda e: self.controlador.intentar_login())
        self.entrada_email.focus()

    def _toggle_ojo(self):
        self._ojo_visible = not self._ojo_visible
        if self._ojo_visible:
            self.entrada_password.configure(show="")
            self.btn_ojo.configure(text_color="#613BE3")
        else:
            self.entrada_password.configure(show="●")
            self.btn_ojo.configure(text_color="gray70")

    def mostrar_error(self, msg):
        self.lbl_error.configure(text=msg, text_color="#c45050")

    def animar_sacudida(self):
        x0, y0 = self.root.winfo_x(), self.root.winfo_y()
        movs = [6, -6, 5, -5, 3, -3, 0]

        def paso(i=0):
            if i < len(movs):
                self.root.geometry(f"+{x0 + movs[i]}+{y0}")
                aid = self.root.after(35, lambda: paso(i + 1))
                self._after_ids.append(aid)
            else:
                self.root.geometry(f"+{x0}+{y0}")

        paso()


__all__ = ["VistaLogin"]
