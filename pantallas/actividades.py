# ============================================================
# pantallas/actividades.py
# Vista para gestionar las Actividades de Salud del sistema.
# Contiene la barra de filtros, la tabla de visualización,
# y la ventana emergente para crear/editar actividades.
# ============================================================

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from db import ActividadController, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, ExcelService, TEMPLATE_PATH
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
    spinbox_numeric, combobox
)


class ActividadView:
    """
    Vista principal de Actividades.
    Se carga en el panel de contenido de la ventana principal.
    """

    def __init__(self, parent):
        self.parent     = parent
        self.controller = ActividadController()
        self.t          = THEME

        self.asic_map = {}
        self.tipo_map = {}

        self._cargar_catalogos()
        self._construir_ui()

    def _cargar_catalogos(self):
        try:
            asics = self.controller.listar_asics()
            self.asic_map = {a["nombre"]: a["id_asic"] for a in asics}

            tipos = self.controller.listar_tipos_actividad()
            self.tipo_map = {t["nombre"]: t["id_tipo"] for t in tipos}
        except Exception as e:
            messagebox.showerror("Error de base de datos", f"No se pudieron cargar los catalogos: {str(e)}")

    def _construir_ui(self):
        t = self.t

        ctk.CTkLabel(
            self.parent, text="Registro de Actividades",
            font=("Arial", 18, "bold"), text_color=t["text_primary"]
        ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(
            self.parent,
            text="Administra, busca y registra las jornadas y actividades medicas de las ASIC.",
            font=("Arial", 10), text_color=t["text_muted"]
        ).pack(anchor="w", padx=30, pady=(0, 15))

        marco_filtros = ctk.CTkFrame(
            self.parent, fg_color=t["bg_surface"], corner_radius=10,
            border_width=1, border_color=t["border"]
        )
        marco_filtros.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(marco_filtros, text="ASIC:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_filtro_asic = ttk.Combobox(marco_filtros, state="readonly", width=22, font=("Arial", 10))
        self.combo_filtro_asic.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Tipo:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_filtro_tipo = ttk.Combobox(marco_filtros, state="readonly", width=22, font=("Arial", 10))
        self.combo_filtro_tipo.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Desde:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.ent_filtro_desde = entry_with_placeholder(marco_filtros, placeholder="AAAA-MM-DD", width=130, font=("Arial", 10))
        self.ent_filtro_desde.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Hasta:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.ent_filtro_hasta = entry_with_placeholder(marco_filtros, placeholder="AAAA-MM-DD", width=130, font=("Arial", 10))
        self.ent_filtro_hasta.grid(row=0, column=7, padx=5, pady=5)

        nombres_asic = ["Todos"] + sorted(list(self.asic_map.keys()))
        nombres_tipo = ["Todos"] + sorted(list(self.tipo_map.keys()))
        self.combo_filtro_asic["values"] = nombres_asic
        self.combo_filtro_asic.current(0)
        self.combo_filtro_tipo["values"] = nombres_tipo
        self.combo_filtro_tipo.current(0)

        ctk.CTkButton(marco_filtros, text="Buscar", font=("Arial", 9, "bold"),
                      fg_color=t["accent"], hover_color=t["accent_dim"],
                      corner_radius=8, command=self._aplicar_filtros
                      ).grid(row=0, column=8, padx=10, pady=5)

        ctk.CTkButton(marco_filtros, text="Limpiar", font=("Arial", 9),
                      fg_color=t["bg_hover"], hover_color=t["border"],
                      corner_radius=8, command=self._limpiar_filtros
                      ).grid(row=0, column=9, padx=2, pady=5)

        marco_acciones_top = ctk.CTkFrame(self.parent, fg_color="transparent")
        marco_acciones_top.pack(fill="x", padx=30, pady=(10, 5))

        ctk.CTkButton(marco_acciones_top, text="+ Registrar Nueva Actividad",
                      font=("Arial", 10, "bold"), fg_color=t["accent"],
                      hover_color=t["accent_dim"], corner_radius=8,
                      command=self._abrir_form_nueva
                      ).pack(side="left")

        ctk.CTkButton(marco_acciones_top, text="Actualizar Tabla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], corner_radius=8,
                      command=self._cargar_datos_tabla
                      ).pack(side="left", padx=10)

        ctk.CTkButton(marco_acciones_top, text="⬇ Descargar Plantilla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], corner_radius=8,
                      command=self._descargar_plantilla
                      ).pack(side="right", padx=5)

        ctk.CTkButton(marco_acciones_top, text="📥 Importar Actividades",
                      font=("Arial", 9, "bold"), fg_color=t["success"],
                      hover_color=t["success_dim"], corner_radius=8,
                      command=self._abrir_modal_importar
                      ).pack(side="right")

        marco_tabla = ctk.CTkFrame(self.parent, fg_color="transparent", corner_radius=10)
        marco_tabla.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        columnas = ("id", "asic", "tipo", "fecha_inicio", "fecha_fin", "estado", "municipio", "lugar", "participantes", "registrador")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=12)

        self.tabla.heading("id",            text="ID")
        self.tabla.heading("asic",          text="ASIC")
        self.tabla.heading("tipo",          text="Tipo de Actividad")
        self.tabla.heading("fecha_inicio",  text="F. Inicio")
        self.tabla.heading("fecha_fin",     text="F. Fin")
        self.tabla.heading("estado",        text="Estado")
        self.tabla.heading("municipio",     text="Municipio")
        self.tabla.heading("lugar",         text="Lugar")
        self.tabla.heading("participantes", text="Part.")
        self.tabla.heading("registrador",   text="Registrado Por")

        self.tabla.column("id",            width=45,  anchor="center")
        self.tabla.column("asic",          width=150, anchor="w")
        self.tabla.column("tipo",          width=160, anchor="w")
        self.tabla.column("fecha_inicio",  width=85,  anchor="center")
        self.tabla.column("fecha_fin",     width=85,  anchor="center")
        self.tabla.column("estado",        width=100, anchor="w")
        self.tabla.column("municipio",     width=100, anchor="w")
        self.tabla.column("lugar",         width=140, anchor="w")
        self.tabla.column("participantes", width=60,  anchor="center")
        self.tabla.column("registrador",   width=120, anchor="w")

        style = ttk.Style()
        style.configure("Act.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=28)
        style.configure("Act.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        font=("Arial", 10, "bold"), relief="flat")
        style.map("Act.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["text_primary"])])

        self.tabla.configure(style="Act.Treeview")

        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        marco_acciones_bottom = ctk.CTkFrame(self.parent, fg_color="transparent")
        marco_acciones_bottom.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(marco_acciones_bottom, text="Editar Seleccionada",
                      font=("Arial", 10), fg_color=t["accent_dim"],
                      hover_color=t["accent"], corner_radius=8,
                      command=self._editar_seleccionada
                      ).pack(side="left")

        ctk.CTkButton(marco_acciones_bottom, text="Eliminar Seleccionada",
                      font=("Arial", 10), fg_color=t["red_bg"],
                      hover_color=t["red"], corner_radius=8,
                      command=self._eliminar_seleccionada
                      ).pack(side="left", padx=10)

        self._cargar_datos_tabla()

    def _aplicar_filtros(self):
        asic_sel = self.combo_filtro_asic.get()
        tipo_sel = self.combo_filtro_tipo.get()
        f_desde  = self.ent_filtro_desde.get().strip()
        f_hasta  = self.ent_filtro_hasta.get().strip()

        filtros = {}

        if asic_sel != "Todos":
            filtros["id_asic"] = self.asic_map.get(asic_sel)
        if tipo_sel != "Todos":
            filtros["id_tipo"] = self.tipo_map.get(tipo_sel)

        if f_desde and f_desde != "AAAA-MM-DD":
            try:
                datetime.strptime(f_desde, "%Y-%m-%d")
                filtros["fecha_desde"] = f_desde
            except ValueError:
                messagebox.showerror("Error en Filtros", "La fecha 'Desde' debe tener el formato AAAA-MM-DD (ej: 2026-05-17).")
                return

        if f_hasta and f_hasta != "AAAA-MM-DD":
            try:
                datetime.strptime(f_hasta, "%Y-%m-%d")
                filtros["fecha_hasta"] = f_hasta
            except ValueError:
                messagebox.showerror("Error en Filtros", "La fecha 'Hasta' debe tener el formato AAAA-MM-DD (ej: 2026-05-17).")
                return

        self._cargar_datos_tabla(filtros)

    def _limpiar_filtros(self):
        self.combo_filtro_asic.current(0)
        self.combo_filtro_tipo.current(0)
        self.ent_filtro_desde.delete(0, tk.END)
        self._poner_placeholder_fecha(self.ent_filtro_desde)
        self.ent_filtro_hasta.delete(0, tk.END)
        self._poner_placeholder_fecha(self.ent_filtro_hasta)
        self._cargar_datos_tabla()

    def _cargar_datos_tabla(self, filtros=None):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            lista = self.controller.listar_actividades(filtros)
            for act in lista:
                f_ini = act["fecha_inicio"]
                f_fin = act["fecha_fin"]
                if isinstance(f_ini, (date, datetime)):
                    f_ini = f_ini.strftime("%d/%m/%Y")
                if isinstance(f_fin, (date, datetime)):
                    f_fin = f_fin.strftime("%d/%m/%Y")

                self.tabla.insert("", "end", values=(
                    act["id_actividad"],
                    act["asic_nombre"],
                    act["tipo_nombre"],
                    f_ini,
                    f_fin,
                    act.get("estado") or "",
                    act.get("municipio") or "",
                    act["lugar"] or "",
                    act["participantes"],
                    act["usuario_nombre"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrio un error al cargar las actividades: {str(e)}")

    def _abrir_formulario(self, datos_edicion=None):
        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Registrar Actividad" if datos_edicion is None else "Editar Actividad")
        ventana.resizable(False, False)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.grab_set()

        ventana.update_idletasks()
        screen_w = ventana.winfo_screenwidth()
        screen_h = ventana.winfo_screenheight()
        
        # Altura al 100% de la pantalla (restando un margen para evitar que se oculte bajo la barra de tareas)
        ancho = 600
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

        lbl_error = ctk.CTkLabel(marco_pie_formulario, text="", font=("Arial", 9), text_color=t["red"])
        lbl_error.pack(pady=(0, 3))

        # Scrollable frame for form
        scroll_frame = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=25, pady=5)

        marco_form = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        marco_form.pack(fill="both", expand=True)

        # Contenedor para campos opcionales/avanzados (siempre visible)
        frame_avanzado = ctk.CTkFrame(marco_form, fg_color="transparent")
        frame_avanzado.pack(fill="x", pady=(6, 6))

        # --- ASIC y Tipo ---
        ctk.CTkLabel(marco_form, text="ASIC *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(2, 2))
        nombres_asics = sorted(list(self.asic_map.keys()))
        combo_asic = ctk.CTkOptionMenu(marco_form, values=nombres_asics)
        if nombres_asics:
            try:
                combo_asic.set(nombres_asics[0])
            except Exception:
                pass
        combo_asic.pack(fill="x")

        ctk.CTkLabel(marco_form, text="Tipo de Actividad *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))
        nombres_tipos = sorted(self.tipo_map.keys())
        combo_tipo = ctk.CTkOptionMenu(marco_form, values=nombres_tipos)
        if nombres_tipos:
            try:
                combo_tipo.set(nombres_tipos[0])
            except Exception:
                pass
        combo_tipo.pack(fill="x")

        # --- Fechas ---
        marco_fechas = ctk.CTkFrame(marco_form, fg_color="transparent")
        marco_fechas.pack(fill="x", pady=8)

        # La actividad puede cubrir uno o varios días.
        col_fecha_inicio = ctk.CTkFrame(marco_fechas, fg_color="transparent")
        col_fecha_inicio.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_fecha_inicio, text="Fecha de inicio *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_fecha_inicio = ctk.CTkEntry(col_fecha_inicio, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                        border_color=t["border"], corner_radius=6)
        ent_fecha_inicio.pack(fill="x", pady=(2, 0))
        ent_fecha_inicio.insert(0, date.today().strftime("%Y-%m-%d"))

        col_fecha_fin = ctk.CTkFrame(marco_fechas, fg_color="transparent")
        col_fecha_fin.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_fecha_fin, text="Fecha de fin *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_fecha_fin = ctk.CTkEntry(col_fecha_fin, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                         border_color=t["border"], corner_radius=6)
        ent_fecha_fin.pack(fill="x", pady=(2, 0))
        ent_fecha_fin.insert(0, date.today().strftime("%Y-%m-%d"))

        # --- Ubicación (campos de la plantilla) ---
        ctk.CTkLabel(frame_avanzado, text="Ubicación", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))

        marco_ubicacion = ctk.CTkFrame(frame_avanzado, fg_color=t["bg_card"], corner_radius=8)
        marco_ubicacion.pack(fill="x", pady=(0, 4))
        inner_ubic = ctk.CTkFrame(marco_ubicacion, fg_color="transparent")
        inner_ubic.pack(fill="x", padx=10, pady=8)

        # Fila 1: Estado, Municipio, Parroquia
        fila_ubi1 = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        fila_ubi1.pack(fill="x", pady=2)

        col_estado = ctk.CTkFrame(fila_ubi1, fg_color="transparent")
        col_estado.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_estado, text="Estado", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_estado = ctk.CTkEntry(col_estado, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                  border_color=t["border"], corner_radius=6)
        ent_estado.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_estado, "Estado")
        ent_estado.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_estado, "Estado"))
        ent_estado.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_estado, "Estado"))

        col_municipio = ctk.CTkFrame(fila_ubi1, fg_color="transparent")
        col_municipio.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_municipio, text="Municipio", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_municipio = ctk.CTkEntry(col_municipio, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                     border_color=t["border"], corner_radius=6)
        ent_municipio.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_municipio, "Municipio")
        ent_municipio.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_municipio, "Municipio"))
        ent_municipio.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_municipio, "Municipio"))

        col_parroquia = ctk.CTkFrame(fila_ubi1, fg_color="transparent")
        col_parroquia.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_parroquia, text="Parroquia", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_parroquia = ctk.CTkEntry(col_parroquia, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                     border_color=t["border"], corner_radius=6)
        ent_parroquia.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_parroquia, "Parroquia")
        ent_parroquia.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_parroquia, "Parroquia"))
        ent_parroquia.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_parroquia, "Parroquia"))

        # Fila 2: Establecimiento, Nombre Establecimiento, Comités de Salud
        fila_ubi2 = ctk.CTkFrame(inner_ubic, fg_color="transparent")
        fila_ubi2.pack(fill="x", pady=2)

        col_estab = ctk.CTkFrame(fila_ubi2, fg_color="transparent")
        col_estab.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_estab, text="Establecimiento de Salud", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_establecimiento = ctk.CTkEntry(col_estab, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                           border_color=t["border"], corner_radius=6)
        ent_establecimiento.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_establecimiento, "Establecimiento")
        ent_establecimiento.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_establecimiento, "Establecimiento"))
        ent_establecimiento.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_establecimiento, "Establecimiento"))

        col_nom_estab = ctk.CTkFrame(fila_ubi2, fg_color="transparent")
        col_nom_estab.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_nom_estab, text="Nombre del Establecimiento", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_nombre_establecimiento = ctk.CTkEntry(col_nom_estab, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                                  border_color=t["border"], corner_radius=6)
        ent_nombre_establecimiento.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_nombre_establecimiento, "Nombre del establecimiento")
        ent_nombre_establecimiento.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_nombre_establecimiento, "Nombre del establecimiento"))
        ent_nombre_establecimiento.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_nombre_establecimiento, "Nombre del establecimiento"))

        col_comites = ctk.CTkFrame(fila_ubi2, fg_color="transparent")
        col_comites.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_comites, text="Comités de Salud", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_comites = ctk.CTkEntry(col_comites, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                   border_color=t["border"], corner_radius=6)
        ent_comites.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_comites, "Comités (ej: Comité A, Comité B)")
        ent_comites.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_comites, "Comités (ej: Comité A, Comité B)"))
        ent_comites.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_comites, "Comités (ej: Comité A, Comité B)"))

        # Lugar combinado (legacy/opcional)
        ctk.CTkLabel(marco_form, text="Lugar / Centro de Salud (resumen)", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))
        ent_lugar = ctk.CTkEntry(marco_form, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"],
                                 border_color=t["border"], corner_radius=6)
        ent_lugar.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(ent_lugar, "Lugar o centro de salud")
        ent_lugar.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(ent_lugar, "Lugar o centro de salud"))
        ent_lugar.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(ent_lugar, "Lugar o centro de salud"))

        # --- Descripción ---
        ctk.CTkLabel(marco_form, text="Tema Tratado / Descripción *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))
        marco_txt = ctk.CTkFrame(marco_form, fg_color=t["bg_base"], corner_radius=6)
        marco_txt.pack(fill="x")
        txt_desc = tk.Text(marco_txt, font=("Arial", 11), bg=t["bg_base"], fg=t["text_primary"], relief="flat", height=3, insertbackground=t["text_primary"], wrap="word")
        txt_desc.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scroll_txt = ttk.Scrollbar(marco_txt, orient="vertical", command=txt_desc.yview)
        txt_desc.configure(yscrollcommand=scroll_txt.set)
        scroll_txt.pack(side="right", fill="y")
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

        # --- Participantes por categoría ---
        ctk.CTkLabel(frame_avanzado, text="Participantes por Categoría", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(10, 2))

        marco_part = ctk.CTkFrame(frame_avanzado, fg_color=t["bg_card"], corner_radius=8)
        marco_part.pack(fill="x", pady=(0, 4))
        inner_part = ctk.CTkFrame(marco_part, fg_color="transparent")
        inner_part.pack(fill="x", padx=10, pady=8)

        # Fila 1: Médicos, Promotores, Voceros Comité
        fila_p1 = ctk.CTkFrame(inner_part, fg_color="transparent")
        fila_p1.pack(fill="x", pady=2)

        self.ent_medicos = spinbox_numeric(fila_p1, "Médicos", 0, self._actualizar_total_participantes)
        self.ent_promotores = spinbox_numeric(fila_p1, "Promotores en Salud", 0, self._actualizar_total_participantes)
        self.ent_voceros_comite = spinbox_numeric(fila_p1, "Voceros Comité Salud", 0, self._actualizar_total_participantes)

        # Fila 2: Vocero Consejo, Coordinador Docencia, Autoridades
        fila_p2 = ctk.CTkFrame(inner_part, fg_color="transparent")
        fila_p2.pack(fill="x", pady=2)

        self.ent_vocero_consejo = spinbox_numeric(fila_p2, "Vocero Consejo Dir. ASIC", 0, self._actualizar_total_participantes)
        self.ent_coordinador = spinbox_numeric(fila_p2, "Coordinador Docencia ASIC", 0, self._actualizar_total_participantes)
        self.ent_autoridades = spinbox_numeric(fila_p2, "Autoridades Presentes", 0, self._actualizar_total_participantes)

        # Fila 3: Otros Actores, Personas Comunidad, Estudiantes Aspirantes
        fila_p3 = ctk.CTkFrame(inner_part, fg_color="transparent")
        fila_p3.pack(fill="x", pady=2)

        self.ent_otros_actores = spinbox_numeric(fila_p3, "Otros Actores", 0, self._actualizar_total_participantes)
        self.ent_personas_comunidad = spinbox_numeric(fila_p3, "Personas Comunidad", 0, self._actualizar_total_participantes)
        self.ent_estudiantes = spinbox_numeric(fila_p3, "Estudiantes Aspirantes", 0, self._actualizar_total_participantes)

        # Total Participantes (mostrar contador calculado)
        # Registrar nombres de campos de participantes para sumar automáticamente
        self._participantes_field_names = [
            "ent_medicos", "ent_promotores", "ent_voceros_comite",
            "ent_vocero_consejo", "ent_coordinador", "ent_autoridades",
            "ent_otros_actores", "ent_personas_comunidad", "ent_estudiantes",
        ]

        marco_total = ctk.CTkFrame(marco_form, fg_color="transparent")
        marco_total.pack(fill="x", pady=4)
        ctk.CTkLabel(marco_total, text="Total de Asistencia *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.lbl_total_participantes = ctk.CTkLabel(marco_total, text="0", font=("Arial", 12, "bold"), text_color=t["text_primary"], fg_color=t["bg_base"], corner_radius=6)
        self.lbl_total_participantes.pack(fill="x", pady=(6, 0))
        # Inicializar total con los valores actuales de los spinboxes
        try:
            self._actualizar_total_participantes()
        except Exception:
            pass

        # --- Evidencias ---
        marco_evidencias = ctk.CTkFrame(
            frame_avanzado, fg_color=t["bg_surface"], corner_radius=10,
            border_width=1, border_color=t["border"]
        )
        marco_evidencias.pack(fill="x", pady=(10, 2))

        ctk.CTkLabel(marco_evidencias, text=" Evidencias / Adjuntos ",
                     font=("Arial", 9, "bold"), text_color=t["text_muted"]
                     ).pack(anchor="w", padx=10, pady=(5, 0))

        marco_ev_content = ctk.CTkFrame(marco_evidencias, fg_color="transparent")
        marco_ev_content.pack(fill="x", padx=10, pady=5)

        marco_lista_ev = ctk.CTkFrame(marco_ev_content, fg_color=t["bg_card"], corner_radius=6)
        marco_lista_ev.pack(side="left", fill="both", expand=True)
        listbox_evidencias = tk.Listbox(marco_lista_ev, font=("Arial", 9), bg=t["bg_card"], fg=t["text_primary"],
                                        selectbackground=t["accent"], relief="flat", height=3)
        listbox_evidencias.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scroll_ev = ttk.Scrollbar(marco_lista_ev, orient="vertical", command=listbox_evidencias.yview)
        listbox_evidencias.configure(yscrollcommand=scroll_ev.set)
        scroll_ev.pack(side="right", fill="y")

        marco_btns_ev = ctk.CTkFrame(marco_ev_content, fg_color="transparent")
        marco_btns_ev.pack(side="right", padx=(10, 0), fill="y")

        evidencias_locales_nuevas = []
        evidencias_existentes     = []
        id_actividad_edicion      = datos_edicion["id_actividad"] if datos_edicion else None

        def refrescar_lista_evidencias():
            listbox_evidencias.delete(0, tk.END)
            if id_actividad_edicion:
                evidencias_existentes.clear()
                try:
                    for ev in self.controller.listar_evidencias_de_actividad(id_actividad_edicion):
                        evidencias_existentes.append(ev)
                        listbox_evidencias.insert(tk.END, ev["nombre_archivo"])
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudieron cargar los adjuntos: {str(e)}", parent=ventana)
            else:
                for ruta in evidencias_locales_nuevas:
                    listbox_evidencias.insert(tk.END, os.path.basename(ruta))

        def adjuntar_archivo():
            ruta = filedialog.askopenfilename(
                title="Seleccionar evidencia",
                filetypes=[("Archivos permitidos", "*.jpg;*.jpeg;*.png;*.pdf;*.docx"),
                           ("Imagenes", "*.jpg;*.jpeg;*.png"),
                           ("Documentos", "*.pdf;*.docx"),
                           ("Todos los archivos", "*.*")],
                parent=ventana
            )
            if not ruta:
                return
            ext = os.path.splitext(ruta)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                messagebox.showerror("Error", f"Extension no permitida ({ext}). Permitidas: {', '.join(ALLOWED_EXTENSIONS)}", parent=ventana)
                return
            if os.path.getsize(ruta) > MAX_FILE_SIZE_MB * 1024 * 1024:
                messagebox.showerror("Error", f"El archivo supera el tamano maximo de {MAX_FILE_SIZE_MB} MB.", parent=ventana)
                return

            if id_actividad_edicion:
                ok_ev, msg_ev = self.controller.procesar_y_guardar_evidencia(id_actividad_edicion, ruta)
                if ok_ev:
                    messagebox.showinfo("Exito", msg_ev, parent=ventana)
                    refrescar_lista_evidencias()
                else:
                    messagebox.showerror("Error", msg_ev, parent=ventana)
            else:
                if ruta in evidencias_locales_nuevas:
                    messagebox.showwarning("Atencion", "Este archivo ya ha sido seleccionado.", parent=ventana)
                    return
                evidencias_locales_nuevas.append(ruta)
                refrescar_lista_evidencias()

        def quitar_archivo():
            seleccion = listbox_evidencias.curselection()
            if not seleccion:
                messagebox.showwarning("Atencion", "Selecciona un archivo de la lista para quitar.", parent=ventana)
                return
            idx = seleccion[0]
            if id_actividad_edicion:
                ev = evidencias_existentes[idx]
                if messagebox.askyesno("Confirmar eliminacion",
                                       f"¿Deseas eliminar permanentemente el archivo '{ev['nombre_archivo']}' del servidor?",
                                       parent=ventana):
                    ok_del, msg_del = self.controller.eliminar_evidencia(ev["id_evidencia"])
                    if ok_del:
                        messagebox.showinfo("Exito", msg_del, parent=ventana)
                        refrescar_lista_evidencias()
                    else:
                        messagebox.showerror("Error", msg_del, parent=ventana)
            else:
                evidencias_locales_nuevas.pop(idx)
                refrescar_lista_evidencias()

        ctk.CTkButton(marco_btns_ev, text="+ Adjuntar", font=("Arial", 9, "bold"),
                      fg_color=t["bg_card"], hover_color=t["bg_hover"],
                      corner_radius=8, command=adjuntar_archivo).pack(fill="x", pady=2)
        ctk.CTkButton(marco_btns_ev, text="- Quitar", font=("Arial", 9),
                      fg_color=t["red_bg"], hover_color=t["red"],
                      corner_radius=8, command=quitar_archivo).pack(fill="x", pady=2)

        refrescar_lista_evidencias()

        if datos_edicion:
            if datos_edicion["asic_nombre"] in nombres_asics:
                combo_asic.set(datos_edicion["asic_nombre"])
            if datos_edicion["tipo_nombre"] in nombres_tipos:
                try:
                    combo_tipo.set(datos_edicion["tipo_nombre"])
                except Exception:
                    pass
            ent_fecha_inicio.delete(0, tk.END)
            ent_fecha_inicio.insert(0, datos_edicion["fecha_inicio"])
            ent_fecha_fin.delete(0, tk.END)
            ent_fecha_fin.insert(0, datos_edicion["fecha_fin"])

            # Cargar campos de ubicación (limpiando placeholders previos)
            ent_estado.delete(0, tk.END)
            ent_estado.insert(0, datos_edicion.get("estado", "") or "")
            ent_municipio.delete(0, tk.END)
            ent_municipio.insert(0, datos_edicion.get("municipio", "") or "")
            ent_parroquia.delete(0, tk.END)
            ent_parroquia.insert(0, datos_edicion.get("parroquia", "") or "")
            ent_establecimiento.delete(0, tk.END)
            ent_establecimiento.insert(0, datos_edicion.get("establecimiento_salud", "") or "")
            ent_nombre_establecimiento.delete(0, tk.END)
            ent_nombre_establecimiento.insert(0, datos_edicion.get("nombre_establecimiento", "") or "")
            ent_comites.delete(0, tk.END)
            ent_comites.insert(0, datos_edicion.get("comites_salud", "") or "")
            ent_lugar.delete(0, tk.END)
            ent_lugar.insert(0, datos_edicion.get("lugar", "") or "")

            # Cargar participantes por categoría (reemplazando valores por defecto)
            self.ent_medicos.delete(0, tk.END)
            self.ent_medicos.insert(0, str(datos_edicion.get("medicos", 0) or 0))
            self.ent_promotores.delete(0, tk.END)
            self.ent_promotores.insert(0, str(datos_edicion.get("promotores_salud", 0) or 0))
            self.ent_voceros_comite.delete(0, tk.END)
            self.ent_voceros_comite.insert(0, str(datos_edicion.get("voceros_comite_salud", 0) or 0))
            self.ent_vocero_consejo.delete(0, tk.END)
            self.ent_vocero_consejo.insert(0, str(datos_edicion.get("vocero_consejo_direccion", 0) or 0))
            self.ent_coordinador.delete(0, tk.END)
            self.ent_coordinador.insert(0, str(datos_edicion.get("coordinador_docencia", 0) or 0))
            self.ent_autoridades.delete(0, tk.END)
            self.ent_autoridades.insert(0, str(datos_edicion.get("autoridades_presentes", 0) or 0))
            self.ent_otros_actores.delete(0, tk.END)
            self.ent_otros_actores.insert(0, str(datos_edicion.get("otros_actores", 0) or 0))
            self.ent_personas_comunidad.delete(0, tk.END)
            self.ent_personas_comunidad.insert(0, str(datos_edicion.get("personas_comunidad", 0) or 0))
            self.ent_estudiantes.delete(0, tk.END)
            self.ent_estudiantes.insert(0, str(datos_edicion.get("estudiantes_aspirantes", 0) or 0))

            # Mostrar total en el label (no es un input editable)
            # Recalcular total a partir de los campos por categoría
            try:
                self._actualizar_total_participantes()
            except Exception:
                pass
            # Reemplazar contenido del textarea (limpiando placeholder si existe)
            try:
                txt_desc.delete("1.0", "end")
            except Exception:
                pass
            txt_desc.insert("1.0", datos_edicion.get("descripcion", "") or "")

        def guardar():
            id_asic = self.asic_map.get(combo_asic.get())
            id_tipo = self.tipo_map.get(combo_tipo.get())
            f_ini   = ent_fecha_inicio.get().strip()
            f_fin   = ent_fecha_fin.get().strip()

            ok, msg = self.controller.guardar_actividad(
                id_asic=id_asic,
                id_tipo=id_tipo,
                fecha_inicio=f_ini,
                fecha_fin=f_fin,
                estado=self._valor_entry(ent_estado),
                municipio=self._valor_entry(ent_municipio),
                parroquia=self._valor_entry(ent_parroquia),
                establecimiento_salud=self._valor_entry(ent_establecimiento),
                nombre_establecimiento=self._valor_entry(ent_nombre_establecimiento),
                comites_salud=self._valor_entry(ent_comites),
                lugar=self._valor_entry(ent_lugar),
                descripcion=txt_desc.get("1.0", "end-1c"),
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
                evidencias_temporales=evidencias_locales_nuevas if id_actividad_edicion is None else None
            )
            if ok:
                messagebox.showinfo("Exito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_datos_tabla()
            else:
                lbl_error.configure(text=msg)

        ctk.CTkButton(marco_pie_formulario,
                  text="Crear Actividad" if datos_edicion is None else "Guardar Cambios",
                      font=("Arial", 11, "bold"), fg_color=t["accent"],
                      hover_color=t["accent_dim"], corner_radius=8, command=guardar
                  ).pack(fill="x", ipady=8)

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

    def _abrir_form_nueva(self):
        self._abrir_formulario()

    def _editar_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona una actividad de la tabla para editar.")
            return
        valores = self.tabla.item(seleccion[0])["values"]
        id_actividad = valores[0]
        try:
            act = self.controller.actividad_dao.obtener_por_id(id_actividad)
            if not act:
                messagebox.showerror("Error", "No se pudo recuperar la informacion de la actividad.")
                return
            self._abrir_formulario(act)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrio un error al obtener la actividad: {str(e)}")

    def _eliminar_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona una actividad de la tabla para eliminar.")
            return
        valores     = self.tabla.item(seleccion[0])["values"]
        id_actividad = valores[0]
        tipo_act     = valores[2]
        fecha_act    = valores[3]

        if messagebox.askyesno("Confirmar eliminacion",
                               f"¿Deseas eliminar la actividad '{tipo_act}' del dia {fecha_act}?\nEsta accion no se puede deshacer de forma directa."):
            try:
                ok, msg = self.controller.eliminar_actividad(id_actividad)
                if ok:
                    messagebox.showinfo("Exito", msg)
                    self._cargar_datos_tabla()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la actividad: {str(e)}")

    def _descargar_plantilla(self):
        if not os.path.exists(TEMPLATE_PATH):
            messagebox.showerror("Plantilla no encontrada",
                                 f"No se encontro la plantilla en:\n{TEMPLATE_PATH}\n\n"
                                 "Asegurate de que el archivo exista en esa ruta.")
            return

        destino = filedialog.asksaveasfilename(
            title="Guardar plantilla como...",
            defaultextension=".xlsx",
            initialfile="plantilla_importacion.xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
        )
        if destino:
            import shutil
            shutil.copy2(TEMPLATE_PATH, destino)
            messagebox.showinfo("Plantilla guardada", f"Plantilla guardada en:\n{destino}")

    def _abrir_modal_importar(self):
        self._ImportarModal(self)

    class _ImportarModal:
        def __init__(self, parent_view):
            self.parent_view = parent_view
            self.parent = parent_view.parent
            self.t = parent_view.t
            self.controller = parent_view.controller
            self.auth = parent_view.controller.actividad_dao.auth if hasattr(parent_view.controller.actividad_dao, 'auth') else None
            from db import AuthController
            self.auth_ctrl = AuthController()
            self.usuario = self.auth_ctrl.obtener_usuario_actual()
            self._ruta_archivo = None
            self._resultado_previo = None

            self._construir_modal()
            self._mostrar_paso1()

        def _construir_modal(self):
            t = self.t
            self.ventana = ctk.CTkToplevel(self.parent)
            self.ventana.title("Importar Actividades desde Excel")
            self.ventana.geometry("750x650")
            self.ventana.resizable(False, False)
            self.ventana.configure(fg_color=t["bg_surface"])
            self.ventana.grab_set()

            self.ventana.update_idletasks()
            x = (self.ventana.winfo_screenwidth() // 2) - 375
            y = (self.ventana.winfo_screenheight() // 2) - 325
            self.ventana.geometry(f"+{x}+{y}")

            header = ctk.CTkFrame(self.ventana, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(15, 5))

            ctk.CTkLabel(header, text="📥 Importar Actividades desde Excel",
                         font=("Arial", 14, "bold"), text_color=t["text_primary"]).pack(side="left")

            ctk.CTkButton(header, text="✕", width=30, height=30,
                          fg_color="transparent", hover_color=t["bg_hover"],
                          text_color=t["text_primary"], corner_radius=6,
                          command=self.ventana.destroy).pack(side="right")

            ctk.CTkLabel(self.ventana,
                         text="Importa actividades en bloque subiendo un archivo .xlsx con el formato de la plantilla.",
                         font=("Arial", 9), text_color=t["text_muted"],
                         ).pack(anchor="w", padx=20, pady=(0, 10))

            self._frame_pasos = ctk.CTkFrame(self.ventana, fg_color="transparent")
            self._frame_pasos.pack(fill="both", expand=True, padx=20, pady=(0, 15))

            btn_frame = ctk.CTkFrame(self.ventana, fg_color="transparent")
            btn_frame.pack(fill="x", padx=20, pady=(0, 15))

            self._btn_cerrar = ctk.CTkButton(btn_frame, text="Cerrar",
                                             font=("Arial", 10), fg_color=t["bg_card"],
                                             hover_color=t["bg_hover"], corner_radius=8,
                                             command=self.ventana.destroy)
            self._btn_cerrar.pack(side="right")

        def _limpiar_pasos(self):
            for w in self._frame_pasos.winfo_children():
                w.destroy()

        def _mostrar_paso1(self):
            t = self.t
            self._limpiar_pasos()
            self._ruta_archivo = None
            self._resultado_previo = None

            card = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"], corner_radius=10)
            card.pack(fill="x", padx=10)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=20)

            ctk.CTkLabel(inner, text="Paso 1 de 3 — Seleccionar archivo Excel",
                         font=("Arial", 11, "bold"), text_color=t["text_primary"]).pack(anchor="w", pady=(0, 4))

            ctk.CTkLabel(inner,
                         text="El archivo debe seguir la plantilla descargable y contener al menos: FECHA, ASIC, ACTIVIDAD DESARROLLADA, TEMA TRATADO, LUGAR/UBICACIÓN y TOTAL DE ASISTENCIA.",
                         font=("Arial", 8), text_color=t["text_muted"],
                         wraplength=650, justify="left").pack(anchor="w", pady=(0, 15))

            self._lbl_ruta = ctk.CTkLabel(inner, text="Ningún archivo seleccionado",
                                          font=("Arial", 9, "italic"), text_color=t["text_muted"])
            self._lbl_ruta.pack(anchor="w", pady=(0, 12))

            fila_botones = ctk.CTkFrame(inner, fg_color="transparent")
            fila_botones.pack(anchor="w")

            ctk.CTkButton(fila_botones, text="📂 Examinar…",
                          font=("Arial", 9), fg_color=t["bg_card"],
                          hover_color=t["bg_hover"], text_color=t["text_primary"],
                          corner_radius=8, command=self._seleccionar_archivo).pack(side="left", padx=(0, 10))

            self._btn_previsualizar = ctk.CTkButton(
                fila_botones, text="▶ Previsualizar",
                font=("Arial", 9, "bold"), fg_color=t["bg_hover"],
                hover_color=t["bg_hover"], text_color=t["text_dim"],
                text_color_disabled=t["text_dim"], corner_radius=8,
                state="disabled", command=self._iniciar_previo)
            self._btn_previsualizar.pack(side="left")

        def _seleccionar_archivo(self):
            t = self.t
            ruta = filedialog.askopenfilename(
                title="Seleccionar archivo Excel",
                filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")],
                parent=self.ventana
            )
            if ruta:
                self._ruta_archivo = ruta
                nombre = os.path.basename(ruta)
                self._lbl_ruta.configure(text=f"📄 {nombre}  ({ruta})", text_color=t["text_primary"])
                self._btn_previsualizar.configure(
                    state="normal", fg_color=t["accent"],
                    hover_color=t["accent_dim"], text_color=t["text_primary"])

        def _iniciar_previo(self):
            self._btn_previsualizar.configure(state="disabled", text="Procesando…")
            self.ventana.configure(cursor="wait")

            def _tarea():
                try:
                    from db import ExcelService
                    svc = ExcelService(id_usuario_registro=self.usuario["id_usuario"])
                    resultado = svc.previsualizar(self._ruta_archivo)
                    self.ventana.after(0, lambda: self._mostrar_paso2(resultado))
                except Exception as exc:
                    self.ventana.after(0, lambda e=exc: self._error_previo(e))

            threading.Thread(target=_tarea, daemon=True).start()

        def _error_previo(self, exc):
            self.ventana.configure(cursor="")
            messagebox.showerror("Error al leer el archivo",
                                 f"No se pudo procesar el archivo:\n\n{exc}", parent=self.ventana)
            self._btn_previsualizar.configure(state="normal", text="▶ Previsualizar",
                                              fg_color=self.t["bg_hover"],
                                              text_color=self.t["text_dim"])

        def _mostrar_paso2(self, resultado):
            t = self.t
            self.ventana.configure(cursor="")
            self._resultado_previo = resultado
            self._limpiar_pasos()

            validas = resultado["filas_validas"]
            errores = resultado["filas_error"]
            total = resultado["total_filas"]

            card_resumen = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"], corner_radius=10)
            card_resumen.pack(fill="x", pady=(0, 10), padx=10)

            inner = ctk.CTkFrame(card_resumen, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=12)

            ctk.CTkLabel(inner, text="Paso 2 de 3 — Resultado del análisis",
                         font=("Arial", 11, "bold"), text_color=t["text_primary"]).pack(anchor="w", pady=(0, 8))

            fila_resumen = ctk.CTkFrame(inner, fg_color="transparent")
            fila_resumen.pack(anchor="w")

            def _chip(parent, texto, color):
                chip = ctk.CTkFrame(parent, fg_color=color, corner_radius=6)
                chip.pack(side="left", padx=(0, 8))
                ctk.CTkLabel(chip, text=texto, font=("Arial", 8, "bold"),
                             text_color=t["text_primary"]).pack(padx=8, pady=3)

            _chip(fila_resumen, f"📄 Total filas: {total}", t["bg_card"])
            _chip(fila_resumen, f"✅ Válidas: {len(validas)}", t["success"])
            _chip(fila_resumen, f"❌ Con errores: {len(errores)}",
                  t["red"] if errores else t["bg_hover"])

            if validas:
                self._seccion_tabla("Filas listas para importar", t["success"], validas, "validas")
            if errores:
                self._seccion_tabla("Filas con errores (no se importarán)", t["red"], errores, "errores")

            card_acciones = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"], corner_radius=10)
            card_acciones.pack(fill="x", padx=10, pady=(8, 0))

            inner_acc = ctk.CTkFrame(card_acciones, fg_color="transparent")
            inner_acc.pack(fill="x", padx=15, pady=12)

            ctk.CTkButton(inner_acc, text="← Seleccionar otro archivo",
                          font=("Arial", 9), fg_color=t["bg_card"],
                          hover_color=t["bg_hover"], text_color=t["text_primary"],
                          corner_radius=8, command=self._mostrar_paso1).pack(side="left", padx=(0, 10))

            if validas:
                ctk.CTkButton(inner_acc,
                              text=f"✔ Importar {len(validas)} actividades",
                              font=("Arial", 9, "bold"), fg_color=t["success"],
                              hover_color=t["success_dim"], text_color=t["text_primary"],
                              corner_radius=8, command=self._confirmar_importar).pack(side="left")
            else:
                ctk.CTkLabel(inner_acc,
                             text="No hay filas válidas para importar. Corrige el archivo y vuelve a intentarlo.",
                             font=("Arial", 8, "italic"), text_color=t["red"]).pack(side="left")

        def _seccion_tabla(self, titulo, color_titulo, filas, modo):
            t = self.t
            marco = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"], corner_radius=10)
            marco.pack(fill="both", expand=(modo == "validas"), pady=(0, 8), padx=10)

            inner = ctk.CTkFrame(marco, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=10, pady=8)

            ctk.CTkLabel(inner, text=titulo, font=("Arial", 9, "bold"),
                         text_color=color_titulo).pack(anchor="w", pady=(0, 4))

            if modo == "validas":
                columnas = ("fila", "asic", "tipo", "fecha_inicio", "fecha_fin", "lugar", "participantes")
            else:
                columnas = ("fila", "asic", "tipo", "fecha_inicio", "errores")

            tree_frame = ctk.CTkFrame(inner, fg_color="transparent")
            tree_frame.pack(fill="both", expand=True)

            style = ttk.Style()
            style.theme_use("clam")
            style.configure("ImportModal.Treeview",
                            background=t["bg_base"], foreground=t["text_primary"],
                            fieldbackground=t["bg_base"], rowheight=24)
            style.configure("ImportModal.Treeview.Heading",
                            background=t["bg_card"], foreground=t["text_primary"],
                            font=("Arial", 9, "bold"), relief="flat")
            style.map("ImportModal.Treeview",
                      background=[("selected", t["accent"])],
                      foreground=[("selected", t["text_primary"])])

            tree = ttk.Treeview(tree_frame, columns=columnas, show="headings",
                                style="ImportModal.Treeview", height=min(len(filas), 8))

            col_ancho = {"fila": 40, "asic": 150, "tipo": 130, "fecha_inicio": 90,
                         "fecha_fin": 90, "lugar": 150, "participantes": 80, "errores": 320}
            col_labels = {"fila": "#", "asic": "ASIC", "tipo": "Tipo Actividad",
                          "fecha_inicio": "Fecha Inicio", "fecha_fin": "Fecha Fin",
                          "lugar": "Lugar", "participantes": "Partic.", "errores": "Errores detectados"}

            for col in columnas:
                tree.heading(col, text=col_labels[col])
                tree.column(col, width=col_ancho[col], minwidth=40, anchor="w")

            for fila in filas:
                dc = fila.get("datos_crudos", {})
                if modo == "validas":
                    valores = (
                        fila["numero_fila"],
                        dc.get("asic", ""),
                        dc.get("tipo_actividad", ""),
                        str(fila["fecha_inicio"]) if fila["fecha_inicio"] else dc.get("fecha_inicio", ""),
                        str(fila["fecha_fin"]) if fila["fecha_fin"] else dc.get("fecha_fin", ""),
                        fila["lugar"],
                        fila["participantes"],
                    )
                else:
                    valores = (
                        fila["numero_fila"],
                        dc.get("asic", ""),
                        dc.get("tipo_actividad", ""),
                        dc.get("fecha_inicio", ""),
                        " | ".join(fila.get("errores", [])),
                    )
                tree.insert("", "end", values=valores)

            scrolly = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            scrollx = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
            scrolly.pack(side="right", fill="y")
            scrollx.pack(side="bottom", fill="x")
            tree.pack(fill="both", expand=True)

        def _confirmar_importar(self):
            validas = self._resultado_previo["filas_validas"]
            if messagebox.askyesno("Confirmar importación",
                                   f"Se importarán {len(validas)} actividades en la base de datos.\n\n¿Deseas continuar?",
                                   parent=self.ventana):
                self._ejecutar_importacion(validas)

        def _ejecutar_importacion(self, filas_validas):
            self.ventana.configure(cursor="wait")

            def _tarea():
                try:
                    from db import ExcelService
                    svc = ExcelService(id_usuario_registro=self.usuario["id_usuario"])
                    resultado = svc.importar(filas_validas)
                    self.ventana.after(0, lambda r=resultado: self._mostrar_paso3(r))
                except Exception as exc:
                    self.ventana.after(0, lambda e=exc: self._error_importar(e))

            threading.Thread(target=_tarea, daemon=True).start()

        def _error_importar(self, exc):
            self.ventana.configure(cursor="")
            messagebox.showerror("Error al importar",
                                 f"Ocurrió un error durante la importación:\n\n{exc}", parent=self.ventana)

        def _mostrar_paso3(self, resultado):
            t = self.t
            self.ventana.configure(cursor="")
            self._limpiar_pasos()

            insertadas = resultado["insertadas"]
            errores_bd = resultado["errores_al_insertar"]

            card = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"], corner_radius=10)
            card.pack(fill="x", padx=10)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=25, pady=25)

            icono = "✅" if not errores_bd else "⚠️"
            color = t["success"] if not errores_bd else t["amber"]
            titulo = "Importación completada" if not errores_bd else "Importación completada con advertencias"

            ctk.CTkLabel(inner, text=f"{icono}  {titulo}",
                         font=("Arial", 13, "bold"), text_color=color).pack(anchor="w", pady=(0, 10))

            ctk.CTkLabel(inner, text=f"Se insertaron correctamente {insertadas} actividades.",
                         font=("Arial", 10), text_color=t["text_primary"]).pack(anchor="w")

            if errores_bd:
                ctk.CTkLabel(inner,
                             text=f"{len(errores_bd)} actividades no pudieron insertarse (ver detalles abajo).",
                             font=("Arial", 9), text_color=t["red"]).pack(anchor="w", pady=(4, 0))
                for err in errores_bd:
                    ctk.CTkLabel(inner, text=f"  • Fila {err['numero_fila']}: {err['error']}",
                                 font=("Arial", 8), text_color=t["red"]).pack(anchor="w")

            ctk.CTkButton(inner, text="↩ Hacer otra importación",
                          font=("Arial", 9), fg_color=t["bg_card"],
                          hover_color=t["bg_hover"], text_color=t["text_primary"],
                          corner_radius=8, command=self._mostrar_paso1).pack(anchor="w", pady=(18, 0))

            ctk.CTkButton(inner, text="Cerrar",
                          font=("Arial", 9, "bold"), fg_color=t["accent"],
                          hover_color=t["accent_dim"], text_color=t["text_primary"],
                          corner_radius=8, command=lambda: (self.ventana.destroy(), self.parent_view._cargar_datos_tabla())
                          ).pack(anchor="w", pady=(8, 0))
