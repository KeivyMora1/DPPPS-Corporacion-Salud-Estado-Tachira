from datetime import datetime
import customtkinter as ctk
from tkinter import ttk

from constants import THEME
from utils import centrar_ventana, set_favicon

class VistaTipoActividad:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.t = THEME
        self._tipos_por_id = {}
        self._editor = None
        self._construir_ui()

    def _construir_ui(self):
        t = self.t
        ctk.CTkLabel(
            self.parent,
            text="Tipos de actividad",
            font=("Arial", 18, "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(
            self.parent,
            text="Administra los tipos disponibles al registrar e importar actividades.",
            font=("Arial", 10),
            text_color=t["text_muted"],
        ).pack(anchor="w", padx=30, pady=(0, 15))

        acciones = ctk.CTkFrame(self.parent, fg_color="transparent")
        acciones.pack(fill="x", padx=30, pady=(0, 10))

        self.btn_agregar = ctk.CTkButton(
            acciones,
            text="+ Agregar tipo de actividad",
            fg_color=t["accent"],
            hover_color=t["accent_dim"],
            command=self.agregar_tipo,
            state="normal" if self.controlador.puede_escribir() else "disabled",
        )
        self.btn_agregar.pack(side="left")

        self.btn_editar = ctk.CTkButton(
            acciones,
            text="Editar",
            fg_color=t["bg_card"],
            hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            command=self.editar_seleccionado,
            state="normal" if self.controlador.puede_escribir() else "disabled",
        )
        self.btn_editar.pack(side="left", padx=(8, 0))
        self.btn_editar.pack_forget()

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
            "TiposActividad.Treeview",
            background=t["bg_base"],
            foreground=t["text_primary"],
            fieldbackground=t["bg_base"],
            rowheight=28,
            borderwidth=0,
        )
        estilo.configure(
            "TiposActividad.Treeview.Heading",
            background=t["bg_card"],
            foreground=t["text_primary"],
            font=("Arial", 10, "bold"),
            relief="flat",
            borderwidth=0,
        )
        estilo.map(
            "TiposActividad.Treeview.Heading",
            background=[("active", t["bg_card"])],
            foreground=[("active", t["text_primary"])],
        )
        estilo.map(
            "TiposActividad.Treeview",
            background=[("selected", t["accent"])],
            foreground=[("selected", t["text_primary"])],
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=("nombre", "creado"),
            show="headings",
            height=12,
            style="TiposActividad.Treeview",
            selectmode="browse",
        )
        self.tabla.heading("nombre", text="Nombre", anchor="w")
        self.tabla.heading("creado", text="Fecha de creación", anchor="w")
        self.tabla.column("nombre", anchor="w", width=500)
        self.tabla.column("creado", anchor="center", width=180)

        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._actualizar_boton_editar)
        self.tabla.bind("<Double-1>", lambda _event: self.editar_seleccionado())

    def _actualizar_boton_editar(self, _event=None):
        if self.controlador.puede_escribir() and self.tabla.selection():
            if not self.btn_editar.winfo_manager():
                self.btn_editar.pack(side="left", padx=(8, 0))
        else:
            self.btn_editar.pack_forget()

    def mostrar_tipos(self, tipos):
        self._tipos_por_id = {str(tipo["id_tipo"]): tipo for tipo in tipos}
        self.tabla.delete(*self.tabla.get_children())
        self._actualizar_boton_editar()
        for tipo in tipos:
            creado = tipo.get("created_at")
            if isinstance(creado, datetime):
                creado = creado.strftime("%d/%m/%Y")
            self.tabla.insert(
                "",
                "end",
                iid=str(tipo["id_tipo"]),
                values=(tipo["nombre"], creado or ""),
            )

    def agregar_tipo(self):
        if not self.controlador.puede_escribir():
            return
        self._abrir_editor()

    def editar_seleccionado(self):
        if not self.controlador.puede_escribir():
            return
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        tipo = self._tipos_por_id.get(seleccion[0])
        if tipo:
            self._abrir_editor(tipo)

    def _abrir_editor(self, tipo=None):
        if self._editor and self._editor.winfo_exists():
            self._editor.focus_set()
            return

        t = self.t
        id_tipo = tipo["id_tipo"] if tipo else None
        ventana = ctk.CTkToplevel(self.parent)
        self._editor = ventana
        ventana.title("Editar tipo de actividad" if tipo else "Agregar tipo de actividad")
        ventana.resizable(False, False)
        ventana.configure(fg_color=t["bg_surface"])
        set_favicon(ventana)
        centrar_ventana(ventana, 460, 210)
        ventana.transient(self.parent.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="Nombre del tipo de actividad",
            font=("Arial", 12, "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=24, pady=(24, 6))

        entrada = ctk.CTkEntry(
            ventana,
            height=38,
            fg_color=t["bg_base"],
            text_color=t["text_primary"],
            border_color=t["border"],
        )
        entrada.pack(fill="x", padx=24)
        if tipo:
            entrada.insert(0, tipo["nombre"])
        entrada.focus_set()
        entrada.bind(
            "<Return>",
            lambda _event: self.controlador.guardar_tipo(entrada.get(), id_tipo),
        )

        botones = ctk.CTkFrame(ventana, fg_color="transparent")
        botones.pack(fill="x", padx=24, pady=20)
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
            text="Guardar",
            fg_color=t["accent"],
            hover_color=t["accent_dim"],
            command=lambda: self.controlador.guardar_tipo(entrada.get(), id_tipo),
        ).pack(side="right", padx=(0, 8))

    def cerrar_editor(self):
        if self._editor and self._editor.winfo_exists():
            self._editor.destroy()
        self._editor = None


__all__ = ["VistaTipoActividad"]
