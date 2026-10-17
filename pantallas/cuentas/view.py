from datetime import datetime
from tkinter import ttk

import customtkinter as ctk

from constants import THEME
from utils import centrar_ventana, set_favicon


class VistaCuentas:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.t = THEME
        self._cuentas_por_id = {}
        self._editor = None
        self._construir_ui()

    def _construir_ui(self):
        t = self.t
        ctk.CTkLabel(
            self.parent,
            text="Cuentas",
            font=("Arial", 18, "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(
            self.parent,
            text="Administra las cuentas de acceso a la aplicación.",
            font=("Arial", 10),
            text_color=t["text_muted"],
        ).pack(anchor="w", padx=30, pady=(0, 15))

        acciones = ctk.CTkFrame(self.parent, fg_color="transparent")
        acciones.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkButton(
            acciones,
            text="+ Crear Cuenta",
            fg_color=t["accent"],
            hover_color=t["accent_dim"],
            command=self.controlador.abrir_formulario,
        ).pack(side="left")
        ctk.CTkButton(
            acciones,
            text="Actualizar Tabla",
            fg_color=t["bg_card"],
            hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            command=self.controlador.cargar_cuentas,
        ).pack(side="left", padx=(8, 0))

        contenedor = ctk.CTkFrame(
            self.parent,
            fg_color=t["bg_surface"],
            corner_radius=10,
            border_width=1,
            border_color=t["border"],
        )
        contenedor.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Cuentas.Treeview",
            background=t["bg_base"],
            foreground=t["text_primary"],
            fieldbackground=t["bg_base"],
            rowheight=28,
            borderwidth=0,
        )
        estilo.configure(
            "Cuentas.Treeview.Heading",
            background=t["bg_card"],
            foreground=t["text_primary"],
            font=("Arial", 10, "bold"),
            relief="flat",
            borderwidth=0,
        )
        estilo.map(
            "Cuentas.Treeview",
            background=[("selected", t["accent"])],
            foreground=[("selected", t["text_primary"])],
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=("usuario", "nombre", "correo", "rol", "estado", "creado"),
            show="headings",
            style="Cuentas.Treeview",
            selectmode="browse",
        )
        columnas = (
            ("usuario", "Usuario", 140, "w"),
            ("nombre", "Nombre completo", 190, "w"),
            ("correo", "Correo electrónico", 210, "w"),
            ("rol", "Rol", 110, "center"),
            ("estado", "Verificación", 120, "center"),
            ("creado", "Fecha de creación", 130, "center"),
        )
        for columna, titulo, ancho, anclaje in columnas:
            self.tabla.heading(columna, text=titulo, anchor=anclaje)
            self.tabla.column(columna, anchor=anclaje, width=ancho)

        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def mostrar_cuentas(self, cuentas):
        self._cuentas_por_id = {
            str(cuenta["id_usuario"]): cuenta for cuenta in cuentas
        }
        self.tabla.delete(*self.tabla.get_children())
        for cuenta in cuentas:
            creado = cuenta.get("created_at")
            if isinstance(creado, (datetime,)):
                creado = creado.strftime("%d/%m/%Y")
            self.tabla.insert(
                "",
                "end",
                iid=str(cuenta["id_usuario"]),
                values=(
                    cuenta.get("username") or "",
                    cuenta.get("nombre_completo") or "",
                    cuenta.get("email") or "",
                    (cuenta.get("rol") or "lector").capitalize(),
                    "Verificado" if cuenta.get("email_verificado") else "Pendiente",
                    creado or "",
                ),
            )

    def abrir_formulario(self):
        if self._editor and self._editor.winfo_exists():
            self._editor.focus_set()
            return

        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        self._editor = ventana
        ventana.title("Crear cuenta")
        ventana.geometry("440x510")
        ventana.resizable(False, False)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.transient(self.parent.winfo_toplevel())
        set_favicon(ventana)
        centrar_ventana(ventana, 440, 510)
        ventana.grab_set()

        formulario = ctk.CTkFrame(ventana, fg_color="transparent")
        formulario.pack(fill="both", expand=True, padx=24, pady=22)
        ctk.CTkLabel(
            formulario,
            text="Crear cuenta",
            font=("Arial", 18, "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", pady=(0, 16))

        val_nombre = (formulario.register(lambda texto: len(texto) <= 60), "%P")
        val_usuario = (formulario.register(lambda texto: len(texto) <= 50), "%P")
        val_correo = (formulario.register(lambda texto: len(texto) <= 60), "%P")
        val_password = (
            formulario.register(
                lambda texto: len(texto) <= 60 and len(texto.encode("utf-8")) <= 72
            ),
            "%P",
        )

        entradas = {}
        for clave, placeholder, validacion in (
            ("nombre", "Nombre", val_nombre),
            ("apellido", "Apellido", val_nombre),
            ("username", "Nombre de usuario", val_usuario),
            ("email", "Correo electrónico", val_correo),
            ("password", "Contraseña inicial", val_password),
        ):
            entrada = ctk.CTkEntry(
                formulario,
                height=36,
                placeholder_text=placeholder,
                fg_color=t["bg_base"],
                text_color=t["text_primary"],
                border_color=t["border"],
                validate="key",
                validatecommand=validacion,
                show="●" if clave == "password" else "",
            )
            entrada.pack(fill="x", pady=(0, 9))
            entradas[clave] = entrada

        administrador = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            formulario,
            text="Cuenta administrador",
            variable=administrador,
            text_color=t["text_primary"],
        ).pack(anchor="w", pady=(2, 8))

        ctk.CTkLabel(
            formulario,
            text="El usuario verificará su correo al iniciar sesión por primera vez.",
            font=("Arial", 10),
            text_color=t["text_muted"],
            wraplength=380,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        botones = ctk.CTkFrame(formulario, fg_color="transparent")
        botones.pack(fill="x", side="bottom")
        ctk.CTkButton(
            botones,
            text="Cancelar",
            fg_color=t["bg_card"],
            hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            command=self.cerrar_editor,
        ).pack(side="right")
        ctk.CTkButton(
            botones,
            text="Crear Cuenta",
            fg_color=t["accent"],
            hover_color=t["accent_dim"],
            command=lambda: self.controlador.crear_cuenta(
                entradas["nombre"].get(),
                entradas["apellido"].get(),
                entradas["email"].get(),
                entradas["password"].get(),
                entradas["username"].get(),
                administrador.get(),
            ),
        ).pack(side="right", padx=(0, 8))

    def cerrar_editor(self):
        if self._editor and self._editor.winfo_exists():
            self._editor.destroy()
        self._editor = None


__all__ = ["VistaCuentas"]
