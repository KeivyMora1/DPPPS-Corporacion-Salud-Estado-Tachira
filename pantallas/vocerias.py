# ============================================================
# pantallas/vocerias.py
# Vista para gestionar las Vocerías CS del sistema.
# Similar a ActividadView: filtros, tabla y formulario modal.
# ============================================================

import customtkinter as ctk
import re
import unicodedata
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import shutil

from db import VoceriaController, ASIC_PREDETERMINADOS, VOCERIA_TEMPLATE_PATH, build_voceria_template
from themes import THEME
from ui_helpers import (
    frame, frame_transparent, label, label_title, label_subtitle,
    btn_primary, btn_secondary, btn_danger, btn_success,
    separator, treeview_style, entry_with_placeholder,
    spinbox_numeric, combobox, date_picker, entry_numeric
)


class VoceriaView:
    """
    Vista principal de Vocerías CS.
    Se carga en el panel de contenido de la ventana principal.
    """

    def __init__(self, parent):
        self.parent = parent
        self.controller = VoceriaController()
        self.t = THEME

        self.asic_map = {}
        self.tipo_map = {}

        self._cargar_catalogos()
        self._construir_ui()

    @staticmethod
    def _normalizar_texto(valor):
        if valor is None:
            return ""
        valor = unicodedata.normalize("NFKD", str(valor))
        valor = valor.encode("ascii", "ignore").decode("ascii")
        valor = valor.lower().strip()
        valor = re.sub(r"\s+", " ", valor)
        return valor

    def _cargar_catalogos(self):
        try:
            asics = self.controller.listar_asics()
            self.asic_map = {a["nombre"]: a["id_asic"] for a in asics}

            tipos = self.controller.listar_tipos_voceria()
            self.tipo_map = {t["nombre"]: t["id_tipo"] for t in tipos}
            self.tipo_voceria_map = {t["nombre"]: t["id_tipo"] for t in tipos}
            self.tipo_voceria_map_normalizada = {
                self._normalizar_texto(nombre): id_tipo
                for nombre, id_tipo in self.tipo_voceria_map.items()
            }
        except Exception as e:
            messagebox.showerror("Error de base de datos", f"No se pudieron cargar los catálogos: {str(e)}")

    def _construir_ui(self):
        t = self.t

        ctk.CTkLabel(
            self.parent, text="Vocerías CS",
            font=("Arial", 18, "bold"), text_color=t["text_primary"]
        ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(
            self.parent,
            text="Administra, busca y registra vocerías de los comités de salud.",
            font=("Arial", 10), text_color=t["text_muted"]
        ).pack(anchor="w", padx=30, pady=(0, 15))

        # ── Filtros ────────────────────────────────────────────
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

        # ── Acciones ──────────────────────────────────────────
        marco_acciones_top = ctk.CTkFrame(self.parent, fg_color="transparent")
        marco_acciones_top.pack(fill="x", padx=30, pady=(10, 5))

        ctk.CTkButton(marco_acciones_top, text="+ Registrar Nueva Vocería",
                      font=("Arial", 10, "bold"), fg_color=t["accent"],
                      hover_color=t["accent_dim"], corner_radius=8,
                      command=self._abrir_form_nueva
                      ).pack(side="left")

        ctk.CTkButton(marco_acciones_top, text="Actualizar Tabla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], corner_radius=8,
                      command=self._cargar_datos_tabla
                      ).pack(side="left", padx=10)

        self.btn_editar = ctk.CTkButton(marco_acciones_top, text="Editar",
                      font=("Arial", 9), fg_color=t["accent_dim"],
                      hover_color=t["accent"], corner_radius=8,
                      command=self._editar_seleccionada,
                      state="disabled")
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = ctk.CTkButton(marco_acciones_top, text="Eliminar",
                      font=("Arial", 9), fg_color=t["red_bg"],
                      hover_color=t["red"], corner_radius=8,
                      command=self._eliminar_seleccionada,
                      state="disabled")
        self.btn_eliminar.pack(side="left", padx=5)

        ctk.CTkButton(marco_acciones_top, text="⬇ Descargar Plantilla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], corner_radius=8,
                      command=self._descargar_plantilla
                      ).pack(side="right", padx=5)

        ctk.CTkButton(marco_acciones_top, text="📥 Importar Vocerías",
                      font=("Arial", 9, "bold"), fg_color=t["success"],
                      hover_color=t["success_dim"], corner_radius=8,
                      command=self._abrir_modal_importar
                      ).pack(side="right")

        # ── Tabla ─────────────────────────────────────────────
        marco_tabla = ctk.CTkFrame(self.parent, fg_color="transparent", corner_radius=10)
        marco_tabla.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        # Configurar estilo ANTES de crear el Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Voc.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=28,
                        borderwidth=0)
        style.configure("Voc.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        font=("Arial", 10, "bold"), relief="flat", borderwidth=0)
        style.map("Voc.Treeview.Heading",
                  background=[("active", t["bg_card"])],
                  foreground=[("active", t["text_primary"])])
        style.map("Voc.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["text_primary"])])

        columnas = (
            "id", "asic", "tipo", "fecha", "estado", "municipio", "parroquia",
            "tema", "descripcion"
        )
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=12, style="Voc.Treeview")

        self.tabla.heading("id",              text="#")
        self.tabla.heading("asic",            text="ASIC")
        self.tabla.heading("tipo",            text="Tipo Vocería")
        self.tabla.heading("fecha",           text="Fecha")
        self.tabla.heading("estado",          text="Estado")
        self.tabla.heading("municipio",       text="Municipio")
        self.tabla.heading("parroquia",       text="Parroquia")
        self.tabla.heading("tema",            text="Tema")
        self.tabla.heading("descripcion",     text="Descripción")

        self.tabla.column("id",             width=40,  anchor="center")
        self.tabla.column("asic",           width=150, anchor="w")
        self.tabla.column("tipo",           width=160, anchor="w")
        self.tabla.column("fecha",          width=90,  anchor="center")
        self.tabla.column("estado",         width=90,  anchor="w")
        self.tabla.column("municipio",      width=110, anchor="w")
        self.tabla.column("parroquia",      width=110, anchor="w")
        self.tabla.column("tema",           width=200, anchor="w")
        self.tabla.column("descripcion",    width=250, anchor="w")

        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tabla.bind("<<TreeviewSelect>>", self._on_seleccion_cambio)
        self.tabla.bind("<Double-1>", self._abrir_detalle_voceria)

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
            lista = self.controller.listar_vocerias(filtros)
            for voc in lista:
                f_ini = voc["fecha"]
                if isinstance(f_ini, (date, datetime)):
                    f_ini = f_ini.strftime("%d/%m/%Y")

                self.tabla.insert("", "end", iid=str(voc["id_voceria"]), values=(
                    voc["id_voceria"],
                    voc.get("asic_nombre", ""),
                    voc.get("tipo_nombre", ""),
                    f_ini,
                    voc.get("estado", ""),
                    voc.get("municipio", ""),
                    voc.get("parroquia", ""),
                    voc.get("tema", ""),
                    voc.get("descripcion", ""),
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las vocerías: {str(e)}")

    def _abrir_formulario(self, datos_edicion=None):
        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Registrar Vocería CS" if datos_edicion is None else "Editar Vocería CS")
        ventana.resizable(True, True)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.grab_set()

        ventana.update_idletasks()
        screen_w = ventana.winfo_screenwidth()
        screen_h = ventana.winfo_screenheight()

        ancho = 900
        alto = screen_h - 80

        x = (screen_w // 2) - (ancho // 2)
        y = 10
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        ctk.CTkLabel(ventana,
             text="Registrar Vocería CS" if datos_edicion is None else "Editar Vocería CS",
             font=("Arial", 16, "bold"), text_color=t["text_primary"]
             ).pack(pady=(15, 5))

        marco_pie_formulario = ctk.CTkFrame(ventana, fg_color="transparent")
        marco_pie_formulario.pack(side="bottom", fill="x", padx=25, pady=(5, 15))

        lbl_error = ctk.CTkLabel(marco_pie_formulario, text="", font=("Arial", 9), text_color=t["red"])
        lbl_error.pack(pady=(0, 3))

        # Nota informativa
        self.lbl_nota_min = ctk.CTkLabel(marco_pie_formulario, 
            text="⚠ Debe agregar al menos 7 vocerías (máx. 10)", 
            font=("Arial", 9), text_color=t["text_muted"])
        self.lbl_nota_min.pack(pady=(0, 3))

        # Scrollable frame for form
        scroll_frame = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=25, pady=5)

        marco_form = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        marco_form.pack(fill="both", expand=True)

        # ===== CAMPOS GENERALES =====
        frame_generales = ctk.CTkFrame(marco_form, fg_color=t["bg_card"], corner_radius=8)
        frame_generales.pack(fill="x", pady=(0, 10))
        inner_gen = ctk.CTkFrame(frame_generales, fg_color="transparent")
        inner_gen.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(inner_gen, text="Datos Generales", font=("Arial", 12, "bold"), text_color=t["text_primary"]).pack(anchor="w", pady=(0, 10))

        # Fila 1: Estado, Municipio, Parroquia, ASIC
        fila1 = ctk.CTkFrame(inner_gen, fg_color="transparent")
        fila1.pack(fill="x", pady=5)

        # Estado
        col_estado = ctk.CTkFrame(fila1, fg_color="transparent")
        col_estado.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_estado, text="Estado *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_estado = ctk.CTkOptionMenu(col_estado, values=["Táchira"], fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        self.ent_estado.set("Táchira")
        self.ent_estado.pack(fill="x", pady=(2, 0))

        # Municipio
        col_municipio = ctk.CTkFrame(fila1, fg_color="transparent")
        col_municipio.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_municipio, text="Municipio *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        municipios = [nombre for _, nombre in ASIC_PREDETERMINADOS]
        self.ent_municipio = ctk.CTkOptionMenu(col_municipio, values=municipios, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        if municipios:
            self.ent_municipio.set(municipios[0])
        self.ent_municipio.pack(fill="x", pady=(2, 0))

        # Parroquia
        col_parroquia = ctk.CTkFrame(fila1, fg_color="transparent")
        col_parroquia.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_parroquia, text="Parroquia *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_parroquia = ctk.CTkEntry(col_parroquia, font=("Arial", 11), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        self.ent_parroquia.pack(fill="x", pady=(2, 0))
        self._poner_placeholder_entry(self.ent_parroquia, "Parroquia")
        self.ent_parroquia.bind("<FocusIn>", lambda e: self._limpiar_placeholder_entry(self.ent_parroquia, "Parroquia"))
        self.ent_parroquia.bind("<FocusOut>", lambda e: self._poner_placeholder_entry(self.ent_parroquia, "Parroquia"))

        # ASIC
        col_asic = ctk.CTkFrame(fila1, fg_color="transparent")
        col_asic.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_asic, text="ASIC *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        nombres_asics = sorted(list(self.asic_map.keys()))
        self.ent_asic = ctk.CTkOptionMenu(col_asic, values=nombres_asics, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        if nombres_asics:
            self.ent_asic.set(nombres_asics[0])
        self.ent_asic.pack(fill="x", pady=(2, 0))

        # Fila 2: Fecha
        fila2 = ctk.CTkFrame(inner_gen, fg_color="transparent")
        fila2.pack(fill="x", pady=5)

        col_fecha = ctk.CTkFrame(fila2, fg_color="transparent")
        col_fecha.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_fecha, text="Fecha *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_fecha = date_picker(col_fecha, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        self.ent_fecha.pack(fill="x", pady=(2, 0))

        # ===== VOCERÍAS (ACORDEÓN) =====
        ctk.CTkLabel(marco_form, text="Vocerías", font=("Arial", 12, "bold"), text_color=t["text_primary"]).pack(anchor="w", pady=(10, 5))

        # Contenedor de items
        self.frame_items = ctk.CTkFrame(marco_form, fg_color="transparent")
        self.frame_items.pack(fill="x", pady=(0, 10))

        # Lista de vocerías disponibles (usar el catálogo real de la BD para evitar mismatch con los IDs)
        self.vocerias_disponibles = [
            t["nombre"] for t in self.controller.listar_tipos_voceria()
        ]
        if not self.vocerias_disponibles:
            self.vocerias_disponibles = [
                "Asamblea Comunitaria",
                "Encuentro de Voceros",
                "Jornada de Vocería",
            ]

        # Opciones de establecimientos (mismo que actividades)
        self.establecimientos_opciones = [
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
            "Hospitales TIPO IV"
        ]

        self.items_voceria = []  # lista de dicts con widgets de cada item
        self._actualizar_estado_botones()

        # Crear primer item expandido
        self._crear_item_voceria(expandido=True)

        # Botón para agregar más items (al final)
        self.btn_agregar_item = ctk.CTkButton(marco_form, text="+ Agregar vocería", font=("Arial", 10, "bold"),
            fg_color=t["success"], hover_color=t["success_dim"], corner_radius=8, command=self._agregar_siguiente_voceria)
        self.btn_agregar_item.pack(anchor="w", pady=(10, 15))

        def guardar():
            # Validar al menos 1 item
            items_validos = [item for item in self.items_voceria if item["frame"].winfo_exists()]
            if len(items_validos) < 1:
                lbl_error.configure(text="Debe agregar al menos 1 vocero")
                return
            # Validar todos los campos obligatorios
            if not self._verificar_todos_campos_llenos():
                lbl_error.configure(text="Complete todos los campos obligatorios y evite vocerías duplicadas")
                return
            
            # Recopilar datos generales
            id_asic = self.asic_map.get(self.ent_asic.get())
            fecha = self.ent_fecha.get().strip()
            estado = self.ent_estado.get()
            municipio = self.ent_municipio.get()
            parroquia = self.ent_parroquia.get().strip()
            
            # Recopilar items
            items = []
            for item in self.items_voceria:
                if not item["frame"].winfo_exists():
                    continue
                w = item["widgets"]
                valor_voceria = (w["voceria"].get() or "").strip()
                id_tipo_voceria = (
                    self.tipo_voceria_map.get(valor_voceria)
                    or self.tipo_voceria_map_normalizada.get(self._normalizar_texto(valor_voceria))
                )

                item_data = {
                    "nombre_comite": w["comite"].get().strip(),
                    "centro_dispensador": w["centro"].get(),
                    "nombre_centro": w["nom_centro"].get().strip(),
                    "nombres": w["nombres"].get().strip(),
                    "ci": w["ci"].get().strip(),
                    "telefono": w["tel"].get().strip(),
                    "fecha_nacimiento": w["fnac"].get().strip(),
                    "edad": w["edad"].get().strip(),
                    "id_tipo_voceria": id_tipo_voceria,
                    "sexo": w["sexo"].get(),
                    "profesion": w["prof"].get().strip(),
                    "correo": w["correo"].get().strip(),
                    "fechas_eleccion": w["felecc"].get().strip(),
                }
                items.append(item_data)

            id_tipo = None
            if items:
                id_tipo = items[0].get("id_tipo_voceria") or next(iter(self.tipo_voceria_map.values()), None)

            tema = "Vocería CS"
            descripcion = f"Registro de vocería del municipio {municipio or 'N/A'} para {fecha}"

            # Llamar al controller
            ok, msg = self.controller.guardar_voceria(
                id_asic=id_asic,
                id_tipo=id_tipo,
                fecha=fecha,
                estado=estado,
                municipio=municipio,
                parroquia=parroquia,
                tema=tema,
                descripcion=descripcion,
                items=items,
                id_voceria=None
            )
            if ok:
                messagebox.showinfo("Éxito", msg)
                ventana.destroy()
                self._cargar_datos_tabla()
            else:
                lbl_error.configure(text=msg)

        self.btn_guardar = ctk.CTkButton(marco_pie_formulario,
                  text="Crear Vocería" if datos_edicion is None else "Guardar Cambios",
                      font=("Arial", 11, "bold"), fg_color=t["accent"],
                      hover_color=t["accent_dim"], corner_radius=8, command=guardar, state="disabled")
        self.btn_guardar.pack(fill="x", ipady=8)

    # ===== MÉTODOS PARA ITEMS DINÁMICOS DE VOCERÍA =====
    def _crear_item_voceria(self, expandido=False):
        """Crea un item de vocería estilo acordeón."""
        if len(self.items_voceria) >= 10:
            return

        t = self.t
        item_index = len(self.items_voceria) + 1
        item_id = f"voceria_{item_index}"

        # Frame principal del item - color ligeramente más oscuro
        item_frame = ctk.CTkFrame(self.frame_items, fg_color="#1e3a56", corner_radius=8, border_width=1, border_color=t["border"])
        item_frame.pack(fill="x", pady=4)

        # Header del acordeón (siempre visible) - clickeable para expandir/contraer
        header = ctk.CTkFrame(item_frame, fg_color=t["bg_surface"], corner_radius=6, cursor="hand2")
        header.pack(fill="x", padx=2, pady=2)

        header_left = ctk.CTkFrame(header, fg_color="transparent", cursor="hand2")
        header_left.pack(side="left", fill="y", padx=12, pady=8)

        # Indicador expandir/contraer + título
        self._chevron_label = ctk.CTkLabel(header_left, text="▼", font=("Arial", 10, "bold"), text_color=t["text_primary"], cursor="hand2")
        self._chevron_label.pack(side="left", padx=(0, 8))

        lbl_titulo = ctk.CTkLabel(header_left, text=f"Vocería #{item_index}", font=("Arial", 11, "bold"), text_color=t["text_primary"], cursor="hand2")
        lbl_titulo.pack(side="left")

        # Mostrar vocería seleccionada en el header cuando esté seleccionada
        lbl_voceria_seleccionada = ctk.CTkLabel(header_left, text="", font=("Arial", 9), text_color=t["text_muted"], cursor="hand2")
        lbl_voceria_seleccionada.pack(side="left", padx=(10, 0))

        header_right = ctk.CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right", padx=12, pady=4)

        # Botón eliminar
        btn_eliminar = ctk.CTkButton(header_right, text="✕", width=28, height=28, font=("Arial", 10),
            fg_color=t["red_bg"], hover_color=t["red"], corner_radius=6)
        btn_eliminar.pack(side="left", padx=2)

        # Contenido colapsable - con animación
        # Contenedor mutable para item_data (necesario para closure)
        def _validar_y_actualizar(e=None):
            self._actualizar_estado_botones()

        item_data_container = {"data": None}

        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent", corner_radius=0, height=0)
        content_frame.pack_propagate(False)  # Para poder controlar altura

        inner = ctk.CTkFrame(content_frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=(0, 12))

        # Función toggle SIN animación
        def toggle_content():
            item_data = item_data_container["data"]
            if item_data["expandido"]:
                # Contraer instantáneamente
                content_frame.pack_forget()
                chevron.configure(text="▶")
                item_data["expandido"] = False
            else:
                # Expandir instantáneamente
                content_frame.pack(fill="x", padx=2, pady=(0, 2))
                chevron.configure(text="▼")
                item_data["expandido"] = True
                self._verificar_auto_expandir()

        chevron = self._chevron_label

        # Fila 1: Nombre Comité, Centro Salud, Nombre Centro
        fila1 = ctk.CTkFrame(inner, fg_color="transparent")
        fila1.pack(fill="x", pady=3)

        # Nombre Comité
        col_comite = ctk.CTkFrame(fila1, fg_color="transparent")
        col_comite.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_comite, text="Nombre del Comité *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_comite = ctk.CTkEntry(col_comite, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_comite.pack(fill="x", pady=(2, 0))
        ent_comite.bind("<KeyRelease>", _validar_y_actualizar)

        # Centro dispensador
        col_centro = ctk.CTkFrame(fila1, fg_color="transparent")
        col_centro.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_centro, text="Centro dispensador *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_centro = ctk.CTkOptionMenu(col_centro, values=self.establecimientos_opciones, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        ent_centro.set(self.establecimientos_opciones[0])
        ent_centro.pack(fill="x", pady=(2, 0))

        # Nombre Centro
        col_nom_centro = ctk.CTkFrame(fila1, fg_color="transparent")
        col_nom_centro.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_nom_centro, text="Nombre del Centro *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_nom_centro = ctk.CTkEntry(col_nom_centro, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_nom_centro.pack(fill="x", pady=(2, 0))

        # Fila 2: Nombres y Apellidos, C.I., Teléfono
        fila2 = ctk.CTkFrame(inner, fg_color="transparent")
        fila2.pack(fill="x", pady=3)

        col_nombres = ctk.CTkFrame(fila2, fg_color="transparent")
        col_nombres.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_nombres, text="Nombres y Apellidos *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_nombres = ctk.CTkEntry(col_nombres, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_nombres.pack(fill="x", pady=(2, 0))

        col_ci = ctk.CTkFrame(fila2, fg_color="transparent")
        col_ci.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_ci, text="C.I. *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_ci = ctk.CTkEntry(col_ci, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_ci.pack(fill="x", pady=(2, 0))

        col_tel = ctk.CTkFrame(fila2, fg_color="transparent")
        col_tel.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_tel, text="Teléfono *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_tel = ctk.CTkEntry(col_tel, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_tel.pack(fill="x", pady=(2, 0))

        # Fila 3: Fecha Nacimiento, Edad
        fila3 = ctk.CTkFrame(inner, fg_color="transparent")
        fila3.pack(fill="x", pady=3)

        col_fnac = ctk.CTkFrame(fila3, fg_color="transparent")
        col_fnac.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_fnac, text="Fecha Nacimiento *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_fnac = date_picker(col_fnac, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_fnac.pack(fill="x", pady=(2, 0))

        col_edad = ctk.CTkFrame(fila3, fg_color="transparent")
        col_edad.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_edad, text="Edad *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_edad = entry_numeric(col_edad, placeholder="Edad", max_digits=3, fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"])
        ent_edad.pack(fill="x", pady=(2, 0))

        # Vocería (dropdown sin repetir)
        col_voceria = ctk.CTkFrame(fila3, fg_color="transparent")
        col_voceria.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_voceria, text="Vocería *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        vocs_disponibles = self.vocerias_disponibles
        valores = ["Seleccionar vocería..."] + vocs_disponibles
        ent_voceria = ctk.CTkOptionMenu(col_voceria, values=valores, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        ent_voceria.set("Seleccionar vocería...")
        
        # Actualizar dropdowns cuando se selecciona una vocería
        def on_voceria_change(choice):
            if choice != "Seleccionar vocería...":
                self._actualizar_dropdowns_voceria()
        ent_voceria.configure(command=on_voceria_change)
        
        ent_voceria.pack(fill="x", pady=(2, 0))

        # Fila 4: Sexo, Profesión/Oficio, Correo
        fila4 = ctk.CTkFrame(inner, fg_color="transparent")
        fila4.pack(fill="x", pady=3)

        col_sexo = ctk.CTkFrame(fila4, fg_color="transparent")
        col_sexo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_sexo, text="Sexo *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_sexo = ctk.CTkOptionMenu(col_sexo, values=["M", "F"], fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        ent_sexo.set("M")
        ent_sexo.pack(fill="x", pady=(2, 0))

        col_prof = ctk.CTkFrame(fila4, fg_color="transparent")
        col_prof.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(col_prof, text="Profesión/Oficio", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_prof = ctk.CTkEntry(col_prof, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_prof.pack(fill="x", pady=(2, 0))

        col_correo = ctk.CTkFrame(fila4, fg_color="transparent")
        col_correo.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col_correo, text="Correo", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_correo = ctk.CTkEntry(col_correo, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_correo.pack(fill="x", pady=(2, 0))

        # Fila 5: Fechas de Elección
        fila5 = ctk.CTkFrame(inner, fg_color="transparent")
        fila5.pack(fill="x", pady=3)

        col_felecc = ctk.CTkFrame(fila5, fg_color="transparent")
        col_felecc.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_felecc, text="Fechas de Elección *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_felecc = date_picker(col_felecc, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_felecc.pack(fill="x", pady=(2, 0))

        # Guardar referencias
        item_data = {
            "frame": item_frame,
            "content_frame": content_frame,
            "header": header,
            "chevron": chevron,
            "lbl_titulo": lbl_titulo,
            "lbl_voceria_seleccionada": lbl_voceria_seleccionada,
            "btn_eliminar": btn_eliminar,
            "index": item_index,
            "expandido": expandido,
            "widgets": {
                "comite": ent_comite,
                "centro": ent_centro,
                "nom_centro": ent_nom_centro,
                "nombres": ent_nombres,
                "ci": ent_ci,
                "tel": ent_tel,
                "fnac": ent_fnac,
                "edad": ent_edad,
                "voceria": ent_voceria,
                "sexo": ent_sexo,
                "prof": ent_prof,
                "correo": ent_correo,
                "felecc": ent_felecc,
            },
        }
        item_data_container["data"] = item_data
        self.items_voceria.append(item_data)

        # Configurar comando del botón eliminar ahora que item_data existe
        btn_eliminar.configure(command=lambda: self._eliminar_item_voceria(item_data))

        # Estado inicial
        if expandido:
            content_frame.pack(fill="x", padx=2, pady=(0, 2))
            # Forzar actualización para obtener altura real
            content_frame.update_idletasks()
            inner.update_idletasks()
            target_height = inner.winfo_reqheight()
            content_frame.configure(height=target_height)
            chevron.configure(text="▼")
            item_data["expandido"] = True
        else:
            chevron.configure(text="▶")
            item_data["expandido"] = False

        # Actualizar botones
        self._actualizar_estado_botones()
        self._renumerar_items()

    def _agregar_siguiente_voceria(self):
        """Agrega la siguiente vocería (llamado desde botón + en header)."""
        # Crear el nuevo item primero (con valores actuales)
        self._crear_item_voceria(expandido=True)
        # Luego actualizar TODOS los dropdowns para excluir opciones ya seleccionadas
        self._actualizar_dropdowns_voceria()

    def _eliminar_item_voceria(self, item_data):
        """Elimina un item de vocería."""
        item_data["frame"].destroy()
        self.items_voceria.remove(item_data)
        self._actualizar_dropdowns_voceria()
        self._actualizar_estado_botones()
        self._renumerar_items()

    def _obtener_vocerias_disponibles(self):
        """Retorna lista de vocerías no usadas en otros items."""
        usadas = set()
        for item in self.items_voceria:
            if item["frame"].winfo_exists():
                val = item["widgets"]["voceria"].get()
                if val and val not in ("(Sin opciones disponibles)", "Seleccionar vocería..."):
                    usadas.add(val)
        return [v for v in self.vocerias_disponibles if v not in usadas]

    def _actualizar_dropdowns_voceria(self):
        """Actualiza los dropdowns de vocería en todos los items."""
        disponibles = self._obtener_vocerias_disponibles()
        for item in self.items_voceria:
            if not item["frame"].winfo_exists():
                continue
            widget = item["widgets"]["voceria"]
            val_actual = widget.get()
            # Reconfigurar valores con placeholder
            valores = ["Seleccionar vocería..."] + (disponibles if disponibles else [])
            widget.configure(values=valores)
            if val_actual == "Seleccionar vocería..." or val_actual == "(Sin opciones disponibles)":
                widget.set("Seleccionar vocería...")
            elif val_actual in disponibles:
                widget.set(val_actual)
            else:
                # val_actual no está en disponibles (ya usado por OTRO item o por este mismo)
                # Si es una selección válida, la mantenemos
                widget.set(val_actual)
            if disponibles:
                widget.configure(state="normal")
            else:
                widget.configure(state="disabled")

    def _actualizar_estado_botones(self):
        """Habilita/deshabilita botones según cantidad de items y validación de campos."""
        count = len([i for i in self.items_voceria if i["frame"].winfo_exists()])
        
        # Verificar si todos los items tienen todos los campos obligatorios llenos
        todos_llenos = self._verificar_todos_campos_llenos()
        
        # Actualizar borde de cada item según su estado
        self._actualizar_bordes_items()
        
        # Botón eliminar siempre habilitado
        for item in self.items_voceria:
            if item["frame"].winfo_exists():
                item["btn_eliminar"].configure(state="normal")
        
        # Botón agregar al final - verificar que el widget aún existe
        if hasattr(self, 'btn_agregar_item') and self.btn_agregar_item.winfo_exists():
            self.btn_agregar_item.configure(state="normal" if count < 10 else "disabled")
        
        # Botón guardar: habilitado solo si >=1 items Y todos los campos llenos
        if hasattr(self, 'btn_guardar') and self.btn_guardar.winfo_exists():
            if count >= 1 and todos_llenos:
                self.btn_guardar.configure(state="normal")
                self.lbl_nota_min.configure(text="✓ Vocerías completas", text_color=self.t["success"])
            elif count >= 1:
                self.btn_guardar.configure(state="disabled")
                self.lbl_nota_min.configure(text="⚠ Complete todos los campos obligatorios", text_color=self.t["amber"])
            else:
                self.btn_guardar.configure(state="disabled")
                self.lbl_nota_min.configure(text=f"⚠ Debe agregar al menos 1 vocero (actual: {count}/1)", text_color=self.t["text_muted"])
    
    def _verificar_item_completo(self, item):
        """Verifica si un item individual tiene todos sus campos obligatorios llenos."""
        if not item["frame"].winfo_exists():
            return False
        widgets = item["widgets"]
        for key, widget in widgets.items():
            # Todos los campos son obligatorios
            val = ""
            if hasattr(widget, "get"):
                val = widget.get().strip()
            if not val or val in ("(Sin opciones disponibles)", "Seleccionar vocería..."):
                return False
        return True
    
    def _actualizar_bordes_items(self):
        """Actualiza el color del borde de cada item según su completitud."""
        for item in self.items_voceria:
            if not item["frame"].winfo_exists():
                continue
            completo = self._verificar_item_completo(item)
            color = "#317E87" if completo else "#c45050"  # Verde si completo, rojo si incompleto
            item["frame"].configure(border_color=color)
    
    def _verificar_todos_campos_llenos(self):
        """Verifica que todos los items tengan todos los campos obligatorios llenos."""
        for item in self.items_voceria:
            if not item["frame"].winfo_exists():
                continue
            widgets = item["widgets"]
            # Verificar cada campo obligatorio
            for key, widget in widgets.items():
                val = ""
                if hasattr(widget, "get"):
                    val = widget.get().strip()
                if not val or val in ("(Sin opciones disponibles)", "Seleccionar vocería..."):
                    return False
        return True

    def _renumerar_items(self):
        """Actualiza los números de los items."""
        for idx, item in enumerate(self.items_voceria):
            if item["frame"].winfo_exists():
                item["index"] = idx + 1
                item["lbl_titulo"].configure(text=f"Vocería #{idx + 1}")
                # Botón eliminar siempre habilitado
                item["btn_eliminar"].configure(state="normal")

    def _verificar_auto_expandir(self):
        """Si el último item expandido se llena, sugiere el siguiente."""
        pass

    def _animar_altura(self, frame, inicio, fin, callback=None, duracion=250, pasos=20):
        """Animación suave de altura para un frame con easing (ease-in-out)."""
        if inicio == fin:
            if callback:
                callback()
            return
        
        delay = duracion // pasos
        
        def ease_in_out_cubic(t):
            """Easing function: ease-in-out cubic"""
            return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        
        def _paso(i=0):
            if i >= pasos:
                frame.configure(height=fin)
                if callback:
                    callback()
                return
            
            # Progreso normalizado (0 a 1) con easing
            t = i / pasos
            eased_t = ease_in_out_cubic(t)
            actual = inicio + (fin - inicio) * eased_t
            frame.configure(height=int(actual))
            frame.after(delay, lambda: _paso(i + 1))
        
        _paso()

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

    def _poner_placeholder_fecha(self, entry_widget):
        placeholder = "AAAA-MM-DD"
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)
            entry_widget.configure(text_color=self.t["text_dim"])
        entry_widget._placeholder_text = placeholder

    def _abrir_form_nueva(self):
        self._abrir_formulario()

    def _editar_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una vocería de la tabla para editar.")
            return
        id_voceria = int(seleccion[0])
        try:
            voc = self.controller.obtener_voceria_completa(id_voceria)
            if not voc:
                messagebox.showerror("Error", "No se pudo recuperar la información de la vocería.")
                return
            self._abrir_formulario(voc)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener la vocería: {str(e)}")

    def _eliminar_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una vocería de la tabla para eliminar.")
            return
        id_voceria = int(seleccion[0])
        valores     = self.tabla.item(seleccion[0])["values"]
        tipo_act    = valores[1]
        fecha_act   = valores[2]

        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Deseas eliminar la vocería '{tipo_act}' del día {fecha_act}?\nEsta acción no se puede deshacer."):
            try:
                ok, msg = self.controller.eliminar_voceria(id_voceria)
                if ok:
                    messagebox.showinfo("Éxito", msg)
                    self._cargar_datos_tabla()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la vocería: {str(e)}")

    def _on_seleccion_cambio(self, event=None):
        seleccion = self.tabla.selection()
        estado = "normal" if seleccion else "disabled"
        self.btn_editar.configure(state=estado)
        self.btn_eliminar.configure(state=estado)

    def _abrir_detalle_voceria(self, event=None):
        """Abre ventana con el detalle de los items (voceros) de la vocería seleccionada."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        id_voceria = int(seleccion[0])
        
        try:
            voc = self.controller.obtener_voceria_completa(id_voceria)
            if not voc:
                messagebox.showerror("Error", "No se pudo recuperar la información de la vocería.")
                return
            
            self._mostrar_detalle_voceria(voc)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener el detalle: {str(e)}")

    def _mostrar_detalle_voceria(self, voc):
        """Muestra ventana modal con el detalle de los items (voceros) de la vocería."""
        t = self.t
        items = voc.get("items", [])
        
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title(f"Detalle de Vocería #{voc['id_voceria']} - {voc.get('asic_nombre', '')}")
        ventana.resizable(True, True)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.grab_set()

        ventana.update_idletasks()
        screen_w = ventana.winfo_screenwidth()
        screen_h = ventana.winfo_screenheight()
        ancho = 1000
        alto = screen_h - 100
        x = (screen_w // 2) - (ancho // 2)
        y = 10
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Header con info general
        header_frame = ctk.CTkFrame(ventana, fg_color=t["bg_card"], corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=20, pady=15)

        # Info general en grid
        info_general = [
            ("ASIC:", voc.get("asic_nombre", "")),
            ("Tipo:", voc.get("tipo_nombre", "")),
            ("Fecha:", voc.get("fecha", "")),
            ("Estado:", voc.get("estado", "")),
            ("Municipio:", voc.get("municipio", "")),
            ("Parroquia:", voc.get("parroquia", "")),
            ("Tema:", voc.get("tema", "")),
            ("Descripción:", voc.get("descripcion", "")),
        ]

        for i, (label, value) in enumerate(info_general):
            row = i // 4
            col = (i % 4) * 2
            ctk.CTkLabel(header_inner, text=label, font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=row, column=col, sticky="w", padx=(0, 5), pady=3)
            ctk.CTkLabel(header_inner, text=str(value), font=("Arial", 9), text_color=t["text_primary"]).grid(row=row, column=col+1, sticky="w", padx=(0, 20), pady=3)

        # Separador
        separator(ventana, horizontal=True, fg_color=t["border"]).pack(fill="x", padx=20, pady=(0, 10))

        # Label "Voceros/Items"
        ctk.CTkLabel(ventana, text=f"Voceros/Items ({len(voc.get('items', []))})", font=("Arial", 12, "bold"), text_color=t["text_primary"]).pack(anchor="w", padx=20, pady=(10, 5))

        # Tabla de items
        marco_tabla = ctk.CTkFrame(ventana, fg_color="transparent", corner_radius=10)
        marco_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("DetalleItem.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=28,
                        borderwidth=0)
        style.configure("DetalleItem.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        font=("Arial", 10, "bold"), relief="flat", borderwidth=0)
        style.map("DetalleItem.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["text_primary"])])

        columnas_items = (
            "tipo_voceria", "nombre_comite", "centro_dispensador", "nombre_centro",
            "nombres", "ci", "telefono", "fecha_nacimiento", "edad",
            "sexo", "profesion", "correo", "fechas_eleccion"
        )
        
        labels_items = {
            "tipo_voceria": "Vocería",
            "nombre_comite": "Comité",
            "centro_dispensador": "Centro Dispensador",
            "nombre_centro": "Nombre Centro",
            "nombres": "Nombres y Apellidos",
            "ci": "C.I.",
            "telefono": "Teléfono",
            "fecha_nacimiento": "F. Nacimiento",
            "edad": "Edad",
            "sexo": "Sexo",
            "profesion": "Profesión",
            "correo": "Correo",
            "fechas_eleccion": "F. Elección"
        }

        tree = ttk.Treeview(marco_tabla, columns=columnas_items, show="headings", height=15, style="DetalleItem.Treeview")
        
        for col in columnas_items:
            tree.heading(col, text=labels_items[col])
            tree.column(col, width=100, minwidth=80, anchor="w" if col not in ("edad", "sexo") else "center")

        for item in items:
            tree.insert("", "end", values=(
                item.get("tipo_voceria_nombre", ""),
                item.get("nombre_comite", ""),
                item.get("centro_dispensador", ""),
                item.get("nombre_centro", ""),
                item.get("nombres", ""),
                item.get("ci", ""),
                item.get("telefono", ""),
                item.get("fecha_nacimiento", ""),
                item.get("edad", ""),
                item.get("sexo", ""),
                item.get("profesion", ""),
                item.get("correo", ""),
                item.get("fechas_eleccion", ""),
            ))

        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(marco_tabla, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        # Botón cerrar
        ctk.CTkButton(ventana, text="Cerrar", font=("Arial", 11, "bold"),
                      fg_color=t["accent_dim"], hover_color=t["accent"],
                      corner_radius=8, command=ventana.destroy).pack(pady=(0, 20))

    def _descargar_plantilla(self):
        if not os.path.exists(VOCERIA_TEMPLATE_PATH):
            try:
                build_voceria_template(VOCERIA_TEMPLATE_PATH)
            except Exception as e:
                messagebox.showerror("Plantilla no disponible",
                                     f"No se pudo crear la plantilla de vocerías:\n{str(e)}")
                return

        destino = filedialog.asksaveasfilename(
            title="Guardar plantilla de vocerías como...",
            defaultextension=".xlsx",
            initialfile="FORMATO DE DATA COMITES 2026.xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
        )
        if destino:
            shutil.copy2(VOCERIA_TEMPLATE_PATH, destino)
            messagebox.showinfo("Plantilla guardada",
                                f"Plantilla de vocerías guardada en:\n{destino}")

    def _abrir_modal_importar(self):
        messagebox.showinfo("Importar", "Función de importar en desarrollo.")