import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from db import ActividadController, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, ExcelService, TEMPLATE_PATH, ASIC_PREDETERMINADOS, MUNICIPIOS_TACHIRA
from themes import THEME
import os
import threading

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False

from ui_helpers import (
    frame, frame_transparent, label, label_title, label_subtitle,
    btn_primary, btn_secondary, btn_danger, btn_success,
    separator, treeview_style, scrollable_frame, entry_with_placeholder,
    spinbox_numeric, combobox, entry_numeric, date_picker
)
from utils import set_favicon


class VistaActividad:
    def __init__(self, parent, controlador):
        self.parent     = parent
        self.controlador = controlador
        self.t          = THEME
        self.puede_escribir = controlador.puede_escribir()

        self._construir_ui()

    def _construir_ui(self):
        t = self.t

        ctk.CTkLabel(
            self.parent, text="Registro de Actividades",
            font=("Arial", 18, "bold"), text_color=t["text_primary"]
        ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(
            self.parent,
            text="Administra, busca y registra actividades de las ASIC.",
            font=("Arial", 10), text_color=t["text_muted"]
        ).pack(anchor="w", padx=30, pady=(0, 15))

        marco_filtros = ctk.CTkFrame(
            self.parent, fg_color=t["bg_surface"], corner_radius=10,
            border_width=1, border_color=t["border"]
        )
        marco_filtros.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(marco_filtros, text="ASIC:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_filtro_asic = ctk.CTkOptionMenu(
            marco_filtros,
            values=["Todos"],
            fg_color=t["bg_base"],
            button_color=t["bg_card"],
            button_hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            dropdown_fg_color=t["bg_base"],
            dropdown_text_color=t["text_primary"],
            font=("Arial", 10),
            width=180
        )
        self.combo_filtro_asic.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Tipo:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_filtro_tipo = ctk.CTkOptionMenu(
            marco_filtros,
            values=["Todos"],
            fg_color=t["bg_base"],
            button_color=t["bg_card"],
            button_hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            dropdown_fg_color=t["bg_base"],
            dropdown_text_color=t["text_primary"],
            font=("Arial", 10),
            width=180
        )
        self.combo_filtro_tipo.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Desde:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.ent_filtro_desde = date_picker(marco_filtros, placeholder="AAAA-MM-DD", width=140, font=("Arial", 10),
                                            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], default_today=False)
        self.ent_filtro_desde.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Hasta:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.ent_filtro_hasta = date_picker(marco_filtros, placeholder="AAAA-MM-DD", width=140, font=("Arial", 10),
                                            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], default_today=False)
        self.ent_filtro_hasta.grid(row=0, column=7, padx=5, pady=5)

        nombres_asic = ["Todos"] + sorted(list(self.controlador.asic_map.keys()))
        nombres_tipo = ["Todos"] + sorted(list(self.controlador.tipo_map.keys()))
        self.combo_filtro_asic.configure(values=nombres_asic)
        self.combo_filtro_asic.set("Todos")
        self.combo_filtro_tipo.configure(values=nombres_tipo)
        self.combo_filtro_tipo.set("Todos")

        ctk.CTkButton(marco_filtros, text="Buscar", font=("Arial", 9, "bold"),
                      fg_color=t["accent"], hover_color=t["accent_dim"],
                      corner_radius=8, command=self.controlador.aplicar_filtros
                      ).grid(row=0, column=8, padx=10, pady=5)

        ctk.CTkButton(marco_filtros, text="Limpiar", font=("Arial", 9),
                      fg_color=t["bg_hover"], hover_color=t["border"],
                      corner_radius=8, command=self.controlador.limpiar_filtros
                      ).grid(row=0, column=9, padx=2, pady=5)

        marco_acciones_top = ctk.CTkFrame(self.parent, fg_color="transparent")
        marco_acciones_top.pack(fill="x", padx=30, pady=(10, 5))

        if self.puede_escribir:
            ctk.CTkButton(marco_acciones_top, text="+ Registrar Nueva Actividad",
                          font=("Arial", 10, "bold"), fg_color=t["accent"],
                          hover_color=t["accent_dim"], corner_radius=8,
                          command=self.controlador.abrir_form_nueva
                          ).pack(side="left")

        ctk.CTkButton(marco_acciones_top, text="Actualizar Tabla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], corner_radius=8,
                      command=self.controlador.cargar_datos_tabla
                      ).pack(side="left", padx=10)

        if self.puede_escribir:
            self.btn_editar = ctk.CTkButton(marco_acciones_top, text="Editar",
                          font=("Arial", 9), fg_color=t["accent_dim"],
                          hover_color=t["accent"], corner_radius=8,
                          command=self.controlador.editar_seleccionada)

            self.btn_eliminar = ctk.CTkButton(marco_acciones_top, text="Eliminar",
                          font=("Arial", 9), fg_color=t["red_bg"],
                          hover_color=t["red"], corner_radius=8,
                          command=self.controlador.eliminar_seleccionada)

            self._ocultar_botones_accion()

        ctk.CTkButton(marco_acciones_top, text="⬇ Descargar Plantilla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], corner_radius=8,
                      command=self.controlador.descargar_plantilla
                      ).pack(side="right", padx=5)

        if self.puede_escribir:
            ctk.CTkButton(marco_acciones_top, text="📥 Importar Actividades",
                          font=("Arial", 9, "bold"), fg_color=t["success"],
                          hover_color=t["success_dim"], corner_radius=8,
                          command=self.controlador.abrir_modal_importar
                          ).pack(side="right")

        marco_tabla = ctk.CTkFrame(self.parent, fg_color="transparent", corner_radius=10)
        marco_tabla.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        # Configurar estilo ANTES de crear el Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Act.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=28,
                        borderwidth=0)
        style.configure("Act.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        font=("Arial", 10, "bold"), relief="flat", borderwidth=0)
        style.map("Act.Treeview.Heading",
                  background=[("active", t["bg_card"])],
                  foreground=[("active", t["text_primary"])])
        style.map("Act.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["text_primary"])])

        columnas = (
            "asic", "tipo", "fecha", "estado",
            "municipio", "parroquia", "establecimiento_salud",
            "nombre_establecimiento", "comites_salud",
            "participantes"
        )
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=12, style="Act.Treeview")

        self.tabla.heading("asic",                     text="ASIC", anchor="w")
        self.tabla.heading("tipo",                     text="Tipo de Actividad", anchor="w")
        self.tabla.heading("fecha",                    text="Fecha", anchor="w")
        self.tabla.heading("estado",                   text="Estado", anchor="w")
        self.tabla.heading("municipio",                text="Municipio", anchor="w")
        self.tabla.heading("parroquia",                text="Parroquia", anchor="w")
        self.tabla.heading("establecimiento_salud",    text="Establecimiento", anchor="w")
        self.tabla.heading("nombre_establecimiento",   text="Nombre Establecimiento", anchor="w")
        self.tabla.heading("comites_salud",            text="Comités", anchor="w")
        self.tabla.heading("participantes",            text="Participantes", anchor="w")

        self.tabla.column("asic",                  width=150,  anchor="w")
        self.tabla.column("tipo",                  width=160,  anchor="w")
        self.tabla.column("fecha",                 width=90,   anchor="center")
        self.tabla.column("estado",                width=100,  anchor="w")
        self.tabla.column("municipio",             width=110,  anchor="w")
        self.tabla.column("parroquia",             width=110,  anchor="w")
        self.tabla.column("establecimiento_salud", width=120,  anchor="w")
        self.tabla.column("nombre_establecimiento", width=170, anchor="w")
        self.tabla.column("comites_salud",         width=120,  anchor="w")
        self.tabla.column("participantes",         width=90,   anchor="center")

        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tabla.bind("<<TreeviewSelect>>", self.controlador.on_seleccion_cambio)
        self.tabla.bind("<Button-1>", self._on_tabla_click, add="+")

    def _on_tabla_click(self, event):
        """Deselecciona fila si se hace clic en área vacía de la tabla."""
        tree = event.widget
        item = tree.identify_row(event.y)
        if not item:
            tree.selection_remove(tree.selection())

    def _mostrar_botones_accion(self):
        """Muestra los botones Editar y Eliminar."""
        if self.puede_escribir:
            self.btn_editar.pack(side="left", padx=5)
            self.btn_eliminar.pack(side="left", padx=5)

    def _ocultar_botones_accion(self):
        """Oculta los botones Editar y Eliminar."""
        if self.puede_escribir:
            self.btn_editar.pack_forget()
            self.btn_eliminar.pack_forget()

    # ── Helpers de placeholder y total (lógica puramente de UI) ──

    def _poner_placeholder_fecha(self, entry_widget):
        """Compatibilidad para limpiar filtros con placeholder de fecha."""
        placeholder = "AAAA-MM-DD"
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)
            entry_widget.configure(text_color=self.t["text_dim"])
        entry_widget._placeholder_text = placeholder

    def _poner_placeholder_entry(self, entry_widget, placeholder):
        """Muestra un placeholder en un CTkEntry vacío."""
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)
            entry_widget.configure(text_color=self.t["text_dim"])
        entry_widget._placeholder_text = placeholder

    def _limpiar_placeholder_entry(self, entry_widget, placeholder):
        """Retira el placeholder cuando el campo recibe el foco."""
        if entry_widget.get() == placeholder:
            entry_widget.delete(0, tk.END)
        entry_widget.configure(text_color=self.t["text_primary"])

    def _valor_entry(self, entry_widget):
        """Retorna vacío si el CTkEntry aún muestra su placeholder."""
        valor = entry_widget.get().strip()
        if valor == getattr(entry_widget, "_placeholder_text", None):
            return ""
        return valor

    def _actualizar_total_participantes(self):
        """Suma los campos numéricos de participantes y actualiza el label del total."""
        total = 0
        for name in getattr(self, '_participantes_field_names', []):
            ent = getattr(self, name, None)
            if not ent:
                continue
            try:
                val = int(ent.get() or 0)
            except Exception:
                try:
                    val = int(str(ent.get()).strip() or 0)
                except Exception:
                    val = 0
            total += val
        try:
            self.lbl_total_participantes.configure(text=str(total))
        except Exception:
            pass
        return total

    def abrir_formulario(self, datos_edicion=None):
        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        set_favicon(ventana)
        ventana.title("Registrar Actividad" if datos_edicion is None else "Editar Actividad")
        ventana.resizable(True, True)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.grab_set()

        ventana.update_idletasks()
        screen_w = ventana.winfo_screenwidth()
        screen_h = ventana.winfo_screenheight()

        # Altura al 100% de la pantalla (restando un margen para evitar que se oculte bajo la barra de tareas)
        ancho = 900
        alto = screen_h - 80

        x = (screen_w // 2) - (ancho // 2)
        y = 10
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        ctk.CTkLabel(ventana,
             text="Registrar Actividad" if datos_edicion is None else "Editar Actividad",
             font=("Arial", 16, "bold"), text_color=t["text_primary"]
             ).pack(pady=(15, 5))

        marco_pie_formulario = ctk.CTkFrame(ventana, fg_color="transparent")
        marco_pie_formulario.pack(side="bottom", fill="x", padx=25, pady=(5, 15))

        lbl_error = ctk.CTkLabel(
            marco_pie_formulario,
            text="",
            font=("Arial", 12, "bold"),
            text_color=t["text_primary"],
            fg_color=t["red"],
            corner_radius=6,
            wraplength=820,
            justify="left",
            anchor="w",
        )

        # Scrollable frame for form
        scroll_frame = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=25, pady=5)

        marco_form = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        marco_form.pack(fill="both", expand=True)

        # --- ASIC y Tipo ---
        ctk.CTkLabel(marco_form, text="ASIC *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(2, 2))
        nombres_asics = sorted(list(self.controlador.asic_map.keys()))
        combo_asic = ctk.CTkOptionMenu(
            marco_form,
            values=nombres_asics,
            fg_color=t["bg_base"],
            button_color=t["bg_card"],
            button_hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            dropdown_fg_color=t["bg_base"],
            dropdown_text_color=t["text_primary"]
        )
        if nombres_asics:
            try:
                combo_asic.set(nombres_asics[0])
            except Exception:
                pass
        combo_asic.pack(fill="x")

        ctk.CTkLabel(marco_form, text="Tipo de Actividad *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))
        nombres_tipos = sorted(self.controlador.tipo_map.keys())
        combo_tipo = ctk.CTkOptionMenu(
            marco_form,
            values=nombres_tipos,
            fg_color=t["bg_base"],
            button_color=t["bg_card"],
            button_hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            dropdown_fg_color=t["bg_base"],
            dropdown_text_color=t["text_primary"]
        )
        if nombres_tipos:
            try:
                combo_tipo.set(nombres_tipos[0])
            except Exception:
                pass
        combo_tipo.pack(fill="x")

        # --- Fecha ---
        marco_fechas = ctk.CTkFrame(marco_form, fg_color="transparent")
        marco_fechas.pack(fill="x", pady=8)

        ctk.CTkLabel(marco_fechas, text="Fecha *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_fecha_inicio = date_picker(marco_fechas, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                       border_color=t["border"], corner_radius=6)
        ent_fecha_inicio.pack(fill="x", pady=(2, 0))
        if ent_fecha_inicio.cal:
            ent_fecha_inicio.cal.configure(maxdate=date.today())
        ent_fecha_fin = ent_fecha_inicio

        # Contenedor para campos opcionales/avanzados (siempre visible)
        frame_avanzado = ctk.CTkFrame(marco_form, fg_color="transparent")
        frame_avanzado.pack(fill="x", pady=(6, 6))

        # --- Ubicación (campos de la plantilla) ---
        ctk.CTkLabel(frame_avanzado, text="Ubicación", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))

        marco_ubicacion = ctk.CTkFrame(frame_avanzado, fg_color=t["bg_card"], corner_radius=8)
        marco_ubicacion.pack(fill="x", pady=(0, 4))
        inner_ubic = ctk.CTkFrame(marco_ubicacion, fg_color="transparent")
        inner_ubic.pack(fill="x", padx=10, pady=8)
        for column in range(3):
            inner_ubic.grid_columnconfigure(column, weight=1, uniform="ubicacion")

        # Fila 1: Estado, Municipio, Parroquia
        col_estado = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        col_estado.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(col_estado, text="Estado *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_estado = ctk.CTkOptionMenu(col_estado, values=["Táchira"], fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        ent_estado.set("Táchira")
        ent_estado.pack(fill="x", pady=(2, 0))

        col_municipio = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        col_municipio.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(col_municipio, text="Municipio *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        municipios = MUNICIPIOS_TACHIRA
        ent_municipio = ctk.CTkOptionMenu(col_municipio, values=municipios, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        if municipios:
            try:
                ent_municipio.set(municipios[0])
            except Exception:
                pass
        ent_municipio.pack(fill="x", pady=(2, 0))

        col_parroquia = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        col_parroquia.grid(row=0, column=2, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(col_parroquia, text="Parroquia *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_parroquia = ctk.CTkEntry(col_parroquia, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                     border_color=t["border"], corner_radius=6)
        ent_parroquia.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_parroquia, "Parroquia")
        ent_parroquia.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_parroquia, "Parroquia"))
        ent_parroquia.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_parroquia, "Parroquia"))

        # Fila 2: Establecimiento, Nombre Establecimiento, Comités de Salud
        col_estab = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        col_estab.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(col_estab, text="Establecimiento de Salud *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        establecimientos = [
            "Consultorio Popular TIPO I",
            "Consultorio Popular TIPO II",
            "Consultorio Popular TIPO III",
            "Clinica Popular TIPO I",
            "Clinica Popular TIPO II",
            "CDI",
            "SRI",
            "CAT",
            "Hospitales TIPO I",
            "Hospitales TIPO II",
            "Hospitales TIPO III",
            "Hospitales TIPO IV",
        ]
        ent_establecimiento = ctk.CTkOptionMenu(col_estab, values=establecimientos, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        if establecimientos:
            try:
                ent_establecimiento.set(establecimientos[0])
            except Exception:
                pass
        ent_establecimiento.pack(fill="x", pady=(2, 0))

        col_nom_estab = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        col_nom_estab.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(col_nom_estab, text="Nombre del Establecimiento *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_nombre_establecimiento = ctk.CTkEntry(col_nom_estab, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                                  border_color=t["border"], corner_radius=6)
        ent_nombre_establecimiento.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_nombre_establecimiento, "Nombre del establecimiento")
        ent_nombre_establecimiento.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_nombre_establecimiento, "Nombre del establecimiento"))
        ent_nombre_establecimiento.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_nombre_establecimiento, "Nombre del establecimiento"))

        col_comites = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        col_comites.grid(row=1, column=2, sticky="ew", padx=5, pady=2)
        ent_comites = entry_numeric(col_comites, "Comités de Salud *", max_digits=2,
                        fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])
        ent_comites.insert(0, "0")

        # --- Descripción ---
        ctk.CTkLabel(marco_form, text="Tema Tratado * (máximo 150 caracteres)", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))
        marco_txt = ctk.CTkFrame(marco_form, fg_color=t["bg_base"], corner_radius=6)
        marco_txt.pack(fill="x")
        txt_desc = tk.Text(marco_txt, font=("Arial", 11), bg=t["bg_base"], fg=t["text_primary"], relief="flat", height=3, insertbackground=t["text_primary"], wrap="word")
        txt_desc.pack(fill="both", expand=True, padx=5, pady=5)
        # Placeholder para descripción
        placeholder_desc = "Breve descripción del tema tratado..."
        txt_desc.insert("1.0", placeholder_desc)
        try:
            txt_desc.configure(fg=t["text_dim"])
        except Exception:
            pass
        def _txt_focus_in(e):
            if txt_desc.get("1.0", "end-1c") == placeholder_desc:
                txt_desc.delete("1.0", "end")
                try:
                    txt_desc.configure(fg=t["text_primary"])
                except Exception:
                    pass
        def _txt_focus_out(e):
            if txt_desc.get("1.0", "end-1c").strip() == "":
                txt_desc.insert("1.0", placeholder_desc)
                try:
                    txt_desc.configure(fg=t["text_dim"])
                except Exception:
                    pass
        txt_desc.bind("<FocusIn>", _txt_focus_in)
        txt_desc.bind("<FocusOut>", _txt_focus_out)

        def _limitar_tema(event=None):
            if not txt_desc.edit_modified():
                return
            contenido = txt_desc.get("1.0", "end-1c")
            if len(contenido) > 150:
                txt_desc.delete("1.0+150c", "end-1c")
                txt_desc.mark_set("insert", "1.0+150c")
            txt_desc.edit_modified(False)

        txt_desc.bind("<<Modified>>", _limitar_tema)
        txt_desc.edit_modified(False)

        # --- Participantes por categoría ---
        ctk.CTkLabel(frame_avanzado, text="Participantes", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(10, 2))

        marco_part = ctk.CTkFrame(frame_avanzado, fg_color=t["bg_card"], corner_radius=8)
        marco_part.pack(fill="x", pady=(0, 4))
        inner_part = ctk.CTkFrame(marco_part, fg_color="transparent")
        inner_part.pack(fill="x", padx=10, pady=8)
        for column in range(3):
            inner_part.grid_columnconfigure(column, weight=1, uniform="participantes")

        # Fila 1: Médicos, Promotores, Voceros Comité
        col_p1_1 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p1_1.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.ent_medicos = entry_numeric(col_p1_1, "Médicos *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        col_p1_2 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p1_2.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.ent_promotores = entry_numeric(col_p1_2, "Promotores en Salud *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        col_p1_3 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p1_3.grid(row=0, column=2, sticky="ew", padx=5, pady=2)
        self.ent_voceros_comite = entry_numeric(col_p1_3, "Voceros Comité Salud *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        # Fila 2: Vocero Consejo, Coordinador Docencia, Autoridades
        col_p2_1 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p2_1.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        self.ent_vocero_consejo = entry_numeric(col_p2_1, "Vocero Consejo Dir. ASIC *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        col_p2_2 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p2_2.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.ent_coordinador = entry_numeric(col_p2_2, "Coordinador Docencia ASIC *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        col_p2_3 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p2_3.grid(row=1, column=2, sticky="ew", padx=5, pady=2)
        self.ent_autoridades = entry_numeric(col_p2_3, "Autoridades Presentes *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        # Fila 3: Otros Actores, Personas Comunidad, Estudiantes Aspirantes
        col_p3_1 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p3_1.grid(row=2, column=0, sticky="new", padx=5, pady=2)
        self.ent_otros_actores = entry_numeric(col_p3_1, "Otros Actores *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        col_p3_2 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p3_2.grid(row=2, column=1, sticky="new", padx=5, pady=2)
        self.ent_personas_comunidad = entry_numeric(col_p3_2, "Personas Comunidad *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])
        ctk.CTkLabel(col_p3_2, text="Total de Asistencia *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(6, 0))
        self.lbl_total_participantes = ctk.CTkLabel(col_p3_2, text="0", font=("Arial", 12, "bold"), text_color=t["text_primary"], fg_color=t["bg_base"], corner_radius=6)
        self.lbl_total_participantes.pack(fill="x", pady=(2, 0))

        col_p3_3 = ctk.CTkFrame(inner_part, fg_color="transparent")
        col_p3_3.grid(row=2, column=2, sticky="new", padx=5, pady=2)
        self.ent_estudiantes = entry_numeric(col_p3_3, "Estudiantes Aspirantes *", max_digits=5, on_change=self._actualizar_total_participantes, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])

        # Total Participantes (mostrar contador calculado)
        self._participantes_field_names = [
            "ent_medicos", "ent_promotores", "ent_voceros_comite",
            "ent_vocero_consejo", "ent_coordinador", "ent_autoridades",
            "ent_otros_actores", "ent_personas_comunidad", "ent_estudiantes",
        ]

        try:
            self._actualizar_total_participantes()
        except Exception:
            pass

        id_actividad_edicion = datos_edicion["id_actividad"] if datos_edicion else None

        if datos_edicion:
            if datos_edicion.get("asic_nombre") in nombres_asics:
                combo_asic.set(datos_edicion["asic_nombre"])
            if datos_edicion.get("tipo_nombre") in nombres_tipos:
                try:
                    combo_tipo.set(datos_edicion["tipo_nombre"])
                except Exception:
                    pass

            f_ini_val = datos_edicion.get("fecha")
            if f_ini_val:
                if isinstance(f_ini_val, (date, datetime)):
                    f_ini_val = f_ini_val.strftime("%Y-%m-%d")
                if hasattr(ent_fecha_inicio, "set_date"):
                    try:
                        ent_fecha_inicio.set_date(f_ini_val)
                    except Exception:
                        ent_fecha_inicio.delete(0, tk.END)
                        ent_fecha_inicio.insert(0, str(f_ini_val))
                else:
                    ent_fecha_inicio.delete(0, tk.END)
                    ent_fecha_inicio.insert(0, str(f_ini_val or ""))

            # Cargar campos de ubicación
            estado_valor = datos_edicion.get("estado", "") or "Táchira"
            try:
                ent_estado.set(estado_valor)
            except Exception:
                pass

            municipio_valor = datos_edicion.get("municipio", "") or ""
            if municipio_valor in municipios:
                ent_municipio.set(municipio_valor)
            elif municipio_valor:
                try:
                    ent_municipio.set(municipio_valor)
                except Exception:
                    pass

            ent_parroquia.delete(0, tk.END)
            if datos_edicion.get("parroquia"):
                ent_parroquia.insert(0, str(datos_edicion["parroquia"]))
                ent_parroquia.configure(text_color=t["text_primary"])
            else:
                self._poner_placeholder_entry(ent_parroquia, "Parroquia")

            estab_valor = datos_edicion.get("establecimiento_salud", "") or ""
            if estab_valor in establecimientos:
                ent_establecimiento.set(estab_valor)
            elif estab_valor:
                try:
                    ent_establecimiento.set(estab_valor)
                except Exception:
                    pass

            ent_nombre_establecimiento.delete(0, tk.END)
            if datos_edicion.get("nombre_establecimiento"):
                ent_nombre_establecimiento.insert(0, str(datos_edicion["nombre_establecimiento"]))
                ent_nombre_establecimiento.configure(text_color=t["text_primary"])
            else:
                self._poner_placeholder_entry(ent_nombre_establecimiento, "Nombre del establecimiento")

            ent_comites.delete(0, tk.END)
            if datos_edicion.get("comites_salud"):
                ent_comites.insert(0, str(datos_edicion["comites_salud"]))
            else:
                ent_comites.insert(0, "0")

            # Cargar participantes por categoría según los nombres reales de la BD
            self.ent_medicos.delete(0, tk.END)
            self.ent_medicos.insert(0, str(datos_edicion.get("cant_medicos", 0) or 0))
            self.ent_promotores.delete(0, tk.END)
            self.ent_promotores.insert(0, str(datos_edicion.get("cant_promotores_salud", 0) or 0))
            self.ent_voceros_comite.delete(0, tk.END)
            self.ent_voceros_comite.insert(0, str(datos_edicion.get("cant_voceros_comite_salud", 0) or 0))
            self.ent_vocero_consejo.delete(0, tk.END)
            self.ent_vocero_consejo.insert(0, str(datos_edicion.get("cant_vocero_consejo_direccion", 0) or 0))
            self.ent_coordinador.delete(0, tk.END)
            self.ent_coordinador.insert(0, str(datos_edicion.get("cant_coordinador_docencia", 0) or 0))
            self.ent_autoridades.delete(0, tk.END)
            self.ent_autoridades.insert(0, str(datos_edicion.get("cant_autoridades", 0) or 0))
            self.ent_otros_actores.delete(0, tk.END)
            self.ent_otros_actores.insert(0, str(datos_edicion.get("cant_otros_actores", 0) or 0))
            self.ent_personas_comunidad.delete(0, tk.END)
            self.ent_personas_comunidad.insert(0, str(datos_edicion.get("cant_personas_comunidad", 0) or 0))
            self.ent_estudiantes.delete(0, tk.END)
            self.ent_estudiantes.insert(0, str(datos_edicion.get("cant_estudiantes_aspirantes", 0) or 0))

            try:
                self._actualizar_total_participantes()
            except Exception:
                pass

            try:
                txt_desc.delete("1.0", "end")
            except Exception:
                pass
            desc_val = str(datos_edicion.get("tema") or "").strip()
            if desc_val:
                txt_desc.insert("1.0", desc_val)
                try:
                    txt_desc.configure(fg=t["text_primary"])
                except Exception:
                    pass
            else:
                txt_desc.insert("1.0", placeholder_desc)
                try:
                    txt_desc.configure(fg=t["text_dim"])
                except Exception:
                    pass

        def guardar():
            id_asic = self.controlador.asic_map.get(combo_asic.get())
            id_tipo = self.controlador.tipo_map.get(combo_tipo.get())
            fecha_val = ent_fecha_inicio.get().strip()

            ok, msg = self.controlador.modelo.guardar_actividad(
                id_asic=id_asic,
                id_tipo=id_tipo,
                fecha=fecha_val,
                estado=self._valor_entry(ent_estado),
                municipio=ent_municipio.get().strip(),
                parroquia=self._valor_entry(ent_parroquia),
                establecimiento_salud=self._valor_entry(ent_establecimiento),
                nombre_establecimiento=self._valor_entry(ent_nombre_establecimiento),
                comites_salud=self._valor_entry(ent_comites),
                tema=txt_desc.get("1.0", "end-1c"),
                medicos=self.ent_medicos.get(),
                promotores_salud=self.ent_promotores.get(),
                voceros_comite_salud=self.ent_voceros_comite.get(),
                vocero_consejo_direccion=self.ent_vocero_consejo.get(),
                coordinador_docencia=self.ent_coordinador.get(),
                autoridades_presentes=self.ent_autoridades.get(),
                otros_actores=self.ent_otros_actores.get(),
                personas_comunidad=self.ent_personas_comunidad.get(),
                estudiantes_aspirantes=self.ent_estudiantes.get(),
                participantes=str(self._actualizar_total_participantes()),
                id_actividad=id_actividad_edicion,
                evidencias_temporales=None
            )
            if ok:
                messagebox.showinfo("Exito", msg, parent=ventana)
                ventana.destroy()
                self.controlador.cargar_datos_tabla()
            else:
                lbl_error.configure(text=msg)
                lbl_error.pack(anchor="w", pady=(0, 8), padx=2, ipadx=12, ipady=6, before=btn_guardar)

        btn_guardar = ctk.CTkButton(marco_pie_formulario,
                  text="Crear Actividad" if datos_edicion is None else "Guardar Cambios",
                      font=("Arial", 11, "bold"), fg_color=t["accent"],
                      hover_color=t["accent_dim"], corner_radius=8, command=guardar
                  )
        btn_guardar.pack(fill="x", ipady=8)


__all__ = ['VistaActividad']
