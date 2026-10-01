import re
import unicodedata
from datetime import date, datetime, timedelta

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from themes import THEME
from ui_helpers import (
    btn_primary,
    date_picker,
    frame,
    frame_transparent,
    label,
    label_subtitle,
    label_title,
    separator,
)
from db import MUNICIPIOS_TACHIRA, VOCERIA_CENTRO_DISPENSADOR_OPCIONES, validar_correo
from utils import set_favicon


def _restar_anios(fecha, anios):
    try:
        return fecha.replace(year=fecha.year - anios)
    except ValueError:
        return fecha.replace(year=fecha.year - anios, day=28)


def _calcular_edad(fecha_nacimiento, hoy=None):
    if not fecha_nacimiento:
        return None
    hoy = hoy or date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


class VistaVoceria:
    """Capa de vista del módulo de vocerías."""

    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self.puede_escribir = controlador.puede_escribir()
        self.t = THEME
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
            width=180,
        )
        self.combo_filtro_asic.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Nombre de comité:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        def validar_nombre_comite(texto):
            return len(texto) <= 40

        vcmd_nombre_comite = (marco_filtros.register(validar_nombre_comite), "%P")
        self.ent_filtro_nombre_comite = ctk.CTkEntry(
            marco_filtros,
            placeholder_text="Nombre de comité",
            font=("Arial", 10),
            fg_color=t["bg_base"],
            text_color=t["text_primary"],
            border_color=t["border"],
            corner_radius=6,
            width=180,
            validate="key",
            validatecommand=vcmd_nombre_comite,
        )
        self.ent_filtro_nombre_comite.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Desde:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.ent_filtro_desde = date_picker(marco_filtros, placeholder="AAAA-MM-DD", width=140, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], default_today=False)
        self.ent_filtro_desde.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Hasta:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.ent_filtro_hasta = date_picker(marco_filtros, placeholder="AAAA-MM-DD", width=140, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], default_today=False)
        self.ent_filtro_hasta.grid(row=0, column=7, padx=5, pady=5)

        nombres_asic = ["Todos"] + sorted(list(self.controlador.asic_map.keys()))
        self.combo_filtro_asic.configure(values=nombres_asic)
        self.combo_filtro_asic.set("Todos")

        ctk.CTkButton(marco_filtros, text="Buscar", font=("Arial", 9, "bold"), fg_color=t["accent"], hover_color=t["accent_dim"], corner_radius=8, command=self.controlador.aplicar_filtros).grid(row=0, column=8, padx=10, pady=5)
        ctk.CTkButton(marco_filtros, text="Limpiar", font=("Arial", 9), fg_color=t["bg_hover"], hover_color=t["border"], corner_radius=8, command=self.controlador.limpiar_filtros).grid(row=0, column=9, padx=2, pady=5)

        marco_acciones_top = ctk.CTkFrame(self.parent, fg_color="transparent")
        marco_acciones_top.pack(fill="x", padx=30, pady=(10, 5))

        if self.puede_escribir:
            ctk.CTkButton(marco_acciones_top, text="+ Registrar Nueva Vocería", font=("Arial", 10, "bold"), fg_color=t["accent"], hover_color=t["accent_dim"], corner_radius=8, command=self.controlador.abrir_form_nueva).pack(side="left")
        ctk.CTkButton(marco_acciones_top, text="Actualizar Tabla", font=("Arial", 9), fg_color=t["bg_card"], hover_color=t["bg_hover"], corner_radius=8, command=self.controlador.cargar_datos_tabla).pack(side="left", padx=10)

        if self.puede_escribir:
            self.btn_editar = ctk.CTkButton(marco_acciones_top, text="Editar", font=("Arial", 9), fg_color=t["accent_dim"], hover_color=t["accent"], corner_radius=8, command=self.controlador.editar_seleccionada)
            self.btn_eliminar = ctk.CTkButton(marco_acciones_top, text="Eliminar", font=("Arial", 9), fg_color=t["red_bg"], hover_color=t["red"], corner_radius=8, command=self.controlador.eliminar_seleccionada)

            self._ocultar_botones_accion()

        ctk.CTkButton(marco_acciones_top, text="📊 Exportar Consolidado", font=("Arial", 9, "bold"), fg_color=t["accent"], hover_color=t["accent_dim"], corner_radius=8, command=self.controlador.exportar_consolidado).pack(side="right", padx=5)
        ctk.CTkButton(marco_acciones_top, text="⬇ Descargar Plantilla", font=("Arial", 9), fg_color=t["bg_card"], hover_color=t["bg_hover"], corner_radius=8, command=self.controlador.descargar_plantilla).pack(side="right", padx=5)
        if self.puede_escribir:
            ctk.CTkButton(marco_acciones_top, text="📥 Importar Vocerías", font=("Arial", 9, "bold"), fg_color=t["success"], hover_color=t["success_dim"], corner_radius=8, command=self.controlador.abrir_modal_importar).pack(side="right")

        marco_tabla = ctk.CTkFrame(self.parent, fg_color="transparent", corner_radius=10)
        marco_tabla.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Voc.Treeview", background=t["bg_base"], foreground=t["text_primary"], fieldbackground=t["bg_base"], rowheight=28, borderwidth=0)
        style.configure("Voc.Treeview.Heading", background=t["bg_card"], foreground=t["text_primary"], font=("Arial", 10, "bold"), relief="flat", borderwidth=0)
        style.map("Voc.Treeview.Heading", background=[("active", t["bg_card"])], foreground=[("active", t["text_primary"])])
        style.map("Voc.Treeview", background=[("selected", t["accent"])], foreground=[("selected", t["text_primary"])])

        columnas = ("asic", "fecha", "cantidad", "estado", "municipio", "parroquia", "nombre_comite")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=12, style="Voc.Treeview")

        self.tabla.heading("asic", text="ASIC", anchor="w")
        self.tabla.heading("fecha", text="Fecha del registro", anchor="w")
        self.tabla.heading("cantidad", text="Cantidad Vocerías", anchor="w")
        self.tabla.heading("estado", text="Estado", anchor="w")
        self.tabla.heading("municipio", text="Municipio", anchor="w")
        self.tabla.heading("parroquia", text="Parroquia", anchor="w")
        self.tabla.heading("nombre_comite", text="Nombre Comité", anchor="w")

        self.tabla.column("asic", width=150, anchor="w")
        self.tabla.column("fecha", width=90, anchor="w")
        self.tabla.column("cantidad", width=100, anchor="w")
        self.tabla.column("estado", width=90, anchor="w")
        self.tabla.column("municipio", width=110, anchor="w")
        self.tabla.column("parroquia", width=110, anchor="w")
        self.tabla.column("nombre_comite", width=180, anchor="w")

        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tabla.bind("<<TreeviewSelect>>", self.controlador.on_seleccion_cambio)
        self.tabla.bind("<Double-1>", self.controlador.abrir_detalle_voceria)
        self.tabla.bind("<Button-1>", self._on_tabla_click, add="+")

    def _on_tabla_click(self, event):
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

    def _bind_click_recursive(self, widget, callback):
        try:
            widget.bind("<Button-1>", callback)
        except Exception:
            pass
        if hasattr(widget, "_canvas") and widget._canvas:
            try:
                widget._canvas.bind("<Button-1>", callback)
            except Exception:
                pass
        if hasattr(widget, "_label") and widget._label:
            try:
                widget._label.bind("<Button-1>", callback)
            except Exception:
                pass
        if hasattr(widget, "_text_label") and widget._text_label:
            try:
                widget._text_label.bind("<Button-1>", callback)
            except Exception:
                pass
        try:
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    continue
                self._bind_click_recursive(child, callback)
        except Exception:
            pass

    def _actualizar_header_item(self, item_data):
        if not item_data or not item_data.get("frame") or not item_data["frame"].winfo_exists():
            return
        w = item_data.get("widgets", {})
        voc_widget = w.get("voceria")
        nom_widget = w.get("nombres")
        voc = voc_widget.get().strip() if (voc_widget and hasattr(voc_widget, "get")) else ""
        nom = nom_widget.get().strip() if (nom_widget and hasattr(nom_widget, "get")) else ""

        if voc and voc not in ("Seleccionar vocería...", "(Sin opciones disponibles)"):
            texto = f"— {voc}" + (f" ({nom})" if nom else "")
            item_data["lbl_voceria_seleccionada"].configure(text=texto)
        elif nom:
            item_data["lbl_voceria_seleccionada"].configure(text=f"— {nom}")
        else:
            item_data["lbl_voceria_seleccionada"].configure(text="")

    def _crear_item_voceria(self, frame_items, items_voceria, vocerias_disponibles, expandido=False):
        if len(items_voceria) >= 10:
            return

        t = self.t
        item_index = len(items_voceria) + 1

        item_frame = ctk.CTkFrame(frame_items, fg_color=t["bg_card"], corner_radius=8, border_width=1, border_color=t["border"])
        item_frame.pack(fill="x", pady=4)

        header = ctk.CTkFrame(item_frame, fg_color=t["bg_surface"], corner_radius=6, cursor="hand2")
        header.pack(fill="x", padx=2, pady=2)

        header_left = ctk.CTkFrame(header, fg_color="transparent", cursor="hand2")
        header_left.pack(side="left", fill="both", expand=True, padx=12, pady=8)

        chevron = ctk.CTkLabel(header_left, text="▼" if expandido else "▶", font=("Arial", 10, "bold"), text_color=t["text_primary"], cursor="hand2")
        chevron.pack(side="left", padx=(0, 8))

        lbl_titulo = ctk.CTkLabel(header_left, text=f"Vocería #{item_index}", font=("Arial", 11, "bold"), text_color=t["text_primary"], cursor="hand2")
        lbl_titulo.pack(side="left")

        lbl_voceria_seleccionada = ctk.CTkLabel(header_left, text="", font=("Arial", 10, "bold"), text_color="#aeb9bc", cursor="hand2")
        lbl_voceria_seleccionada.pack(side="left", padx=(10, 0))

        header_right = ctk.CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right", padx=12, pady=4)

        btn_eliminar = ctk.CTkButton(header_right, text="✕", width=28, height=28, font=("Arial", 10), fg_color=t["red_bg"], hover_color=t["red"], corner_radius=6)
        btn_eliminar.pack(side="left", padx=2)

        item_data_container = {"data": None}
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent", corner_radius=0)
        inner = ctk.CTkFrame(content_frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=(0, 12))

        def toggle_content(event=None):
            item_data = item_data_container["data"]
            if not item_data or not item_data["frame"].winfo_exists():
                return
            if item_data["expandido"]:
                content_frame.pack_forget()
                chevron.configure(text="▶")
                item_data["expandido"] = False
            else:
                content_frame.pack(fill="x", padx=2, pady=(0, 2))
                chevron.configure(text="▼")
                item_data["expandido"] = True

        self._bind_click_recursive(header, toggle_content)

        def _on_field_change(event=None):
            if item_data_container.get("data"):
                self._actualizar_header_item(item_data_container["data"])
            self.controlador._actualizar_estado_botones_formulario()

        fila2 = ctk.CTkFrame(inner, fg_color="transparent")
        fila2.pack(fill="x", pady=3)
        fila2.grid_columnconfigure((0, 1, 2), weight=1, uniform="voceria_fila_datos")

        col_nombres = ctk.CTkFrame(fila2, fg_color="transparent")
        col_nombres.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(col_nombres, text="Nombres y Apellidos *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_nombres = ctk.CTkEntry(
            col_nombres, placeholder_text="Nombres y Apellidos", font=("Arial", 10),
            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"],
            corner_radius=6, validate="key",
            validatecommand=(col_nombres.register(
                lambda texto: len(texto) <= 40 and not any(c.isdigit() or ord(c) < 32 for c in texto)
            ), "%P"),
        )
        ent_nombres.pack(fill="x", pady=(2, 0))

        col_ci = ctk.CTkFrame(fila2, fg_color="transparent")
        col_ci.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(col_ci, text="C.I. *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")

        def formatear_ci(texto):
            if not texto:
                return ""
            solo_digitos = "".join(c for c in texto if c.isdigit())
            if not solo_digitos:
                return ""
            partes = []
            while len(solo_digitos) > 3:
                partes.insert(0, solo_digitos[-3:])
                solo_digitos = solo_digitos[:-3]
            partes.insert(0, solo_digitos)
            return ",".join(partes)

        def validar_ci(texto):
            if texto == "":
                return True
            if not all(c.isdigit() or c == "," for c in texto):
                return False
            solo_digitos = "".join(c for c in texto if c.isdigit())
            return len(solo_digitos) <= 8

        def on_ci_change(event=None):
            actual = ent_ci.get()
            cursor_pos = ent_ci.index(tk.INSERT)
            formateado = formatear_ci(actual)
            if formateado != actual:
                ent_ci.delete(0, tk.END)
                ent_ci.insert(0, formateado)
                try:
                    nueva_pos = cursor_pos + (len(formateado) - len(actual))
                    ent_ci.icursor(max(0, min(nueva_pos, len(formateado))))
                except Exception:
                    pass
            _on_field_change()

        vcmd_ci = (col_ci.register(validar_ci), "%P")
        ent_ci = ctk.CTkEntry(col_ci, placeholder_text="C.I.", font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6, validate="key", validatecommand=vcmd_ci)
        ent_ci.pack(fill="x", pady=(2, 0))
        ent_ci.bind("<KeyRelease>", on_ci_change)
        ent_ci.bind("<FocusOut>", on_ci_change)

        col_tel = ctk.CTkFrame(fila2, fg_color="transparent")
        col_tel.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(col_tel, text="Teléfono *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")

        def validar_tel(texto):
            return texto == "" or (texto.isdigit() and len(texto) <= 12)

        vcmd_tel = (col_tel.register(validar_tel), "%P")
        ent_tel = ctk.CTkEntry(col_tel, placeholder_text="Teléfono", font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6, validate="key", validatecommand=vcmd_tel)
        ent_tel.pack(fill="x", pady=(2, 0))

        fila3 = ctk.CTkFrame(inner, fg_color="transparent")
        fila3.pack(fill="x", pady=3)
        fila3.grid_columnconfigure((0, 1, 2), weight=1, uniform="voceria_fila_datos")

        col_fnac = ctk.CTkFrame(fila3, fg_color="transparent")
        col_fnac.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(col_fnac, text="Fecha Nacimiento *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        hoy = date.today()
        fecha_minima_nacimiento = _restar_anios(hoy, 100) + timedelta(days=1)
        fecha_maxima_nacimiento = _restar_anios(hoy, 18)
        ent_fnac = date_picker(col_fnac, placeholder="AAAA-MM-DD", default_today=False, min_date=fecha_minima_nacimiento, max_date=fecha_maxima_nacimiento, font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_fnac.pack(fill="x", pady=(2, 0))

        col_edad = ctk.CTkFrame(fila3, fg_color="transparent")
        col_edad.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(col_edad, text="Edad *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")

        ent_edad = ctk.CTkEntry(col_edad, placeholder_text="Edad", font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6, state="readonly")
        ent_edad.pack(fill="x", pady=(2, 0))

        def actualizar_edad(event=None):
            fecha_nacimiento = self._parsear_fecha_formulario(ent_fnac.get())
            edad = ""
            edad_calculada = _calcular_edad(fecha_nacimiento)
            if edad_calculada is not None and 18 <= edad_calculada <= 99:
                edad = str(edad_calculada)

            ent_edad.configure(state="normal")
            ent_edad.delete(0, tk.END)
            if edad:
                ent_edad.insert(0, edad)
            ent_edad.configure(state="readonly")
            _on_field_change()

        ent_fnac.set_date_selected_callback(actualizar_edad)

        col_voceria = ctk.CTkFrame(fila3, fg_color="transparent")
        col_voceria.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(col_voceria, text="Vocería *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        valores_iniciales = ["Seleccionar vocería..."] + vocerias_disponibles
        ent_voceria = ctk.CTkOptionMenu(col_voceria, values=valores_iniciales, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        ent_voceria.set("Seleccionar vocería...")
        ent_voceria.pack(fill="x", pady=(2, 0))

        fila4 = ctk.CTkFrame(inner, fg_color="transparent")
        fila4.pack(fill="x", pady=3)
        fila4.grid_columnconfigure((0, 1, 2), weight=1, uniform="voceria_fila_datos")

        col_sexo = ctk.CTkFrame(fila4, fg_color="transparent")
        col_sexo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(col_sexo, text="Sexo *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_sexo = ctk.CTkOptionMenu(col_sexo, values=["M", "F"], fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        ent_sexo.set("M")
        ent_sexo.pack(fill="x", pady=(2, 0))

        col_prof = ctk.CTkFrame(fila4, fg_color="transparent")
        col_prof.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(col_prof, text="Profesión/Oficio *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_prof = ctk.CTkEntry(
            col_prof, placeholder_text="Profesión/Oficio", font=("Arial", 10),
            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"],
            corner_radius=6, validate="key",
            validatecommand=(col_prof.register(lambda texto: len(texto) <= 40), "%P"),
        )
        ent_prof.pack(fill="x", pady=(2, 0))

        col_correo = ctk.CTkFrame(fila4, fg_color="transparent")
        col_correo.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(col_correo, text="Correo *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_correo = ctk.CTkEntry(
            col_correo, placeholder_text="ejemplo@correo.com", font=("Arial", 10),
            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"],
            corner_radius=6, validate="key",
            validatecommand=(col_correo.register(lambda texto: len(texto) <= 120), "%P"),
        )
        ent_correo.pack(fill="x", pady=(2, 0))

        fila5 = ctk.CTkFrame(inner, fg_color="transparent")
        fila5.pack(fill="x", pady=3)

        col_felecc = ctk.CTkFrame(fila5, fg_color="transparent")
        col_felecc.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col_felecc, text="Fecha de Elección *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_felecc = date_picker(col_felecc, max_date=date.today(), font=("Arial", 10), fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"], corner_radius=6)
        ent_felecc.pack(fill="x", pady=(2, 0))

        for ent in (ent_nombres, ent_ci, ent_tel, ent_prof, ent_correo, ent_felecc):
            ent.bind("<KeyRelease>", _on_field_change)
            ent.bind("<FocusOut>", _on_field_change)

        ent_fnac.bind("<KeyRelease>", actualizar_edad)
        ent_fnac.bind("<FocusOut>", actualizar_edad)

        ent_sexo.configure(command=lambda choice: _on_field_change())

        def on_voceria_cambiada(choice):
            self.controlador._actualizar_dropdowns_voceria(items_voceria, vocerias_disponibles)
            _on_field_change()

        ent_voceria.configure(command=on_voceria_cambiada)

        item_data = {
            "frame": item_frame,
            "content_frame": content_frame,
            "header": header,
            "chevron": chevron,
            "lbl_titulo": lbl_titulo,
            "lbl_voceria_seleccionada": lbl_voceria_seleccionada,
            "actualizar_edad": actualizar_edad,
            "btn_eliminar": btn_eliminar,
            "index": item_index,
            "expandido": expandido,
            "widgets": {
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
        items_voceria.append(item_data)

        btn_eliminar.configure(command=lambda: self.controlador._eliminar_item_voceria(item_data, items_voceria, vocerias_disponibles))

        if expandido:
            content_frame.pack(fill="x", padx=2, pady=(0, 2))
            chevron.configure(text="▼")
            item_data["expandido"] = True
        else:
            content_frame.pack_forget()
            chevron.configure(text="▶")
            item_data["expandido"] = False

        return item_data

    def abrir_formulario(self, datos_edicion=None):
        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        set_favicon(ventana)
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

        ctk.CTkLabel(ventana, text="Registrar Vocería CS" if datos_edicion is None else "Editar Vocería CS", font=("Arial", 16, "bold"), text_color=t["text_primary"]).pack(pady=(15, 5))

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

        scroll_frame = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=25, pady=5)

        marco_form = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        marco_form.pack(fill="both", expand=True)

        self.establecimientos_opciones = VOCERIA_CENTRO_DISPENSADOR_OPCIONES

        frame_generales = ctk.CTkFrame(marco_form, fg_color=t["bg_card"], corner_radius=8)
        frame_generales.pack(fill="x", pady=(0, 10))
        inner_gen = ctk.CTkFrame(frame_generales, fg_color="transparent")
        inner_gen.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(inner_gen, text="Datos Generales", font=("Arial", 12, "bold"), text_color=t["text_primary"]).pack(anchor="w", pady=(0, 10))

        fila1 = ctk.CTkFrame(inner_gen, fg_color="transparent")
        fila1.pack(fill="x", pady=5)
        fila1.grid_columnconfigure((0, 1, 2), weight=1, uniform="datos_generales_fila1")

        col_estado = ctk.CTkFrame(fila1, fg_color="transparent")
        col_estado.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(col_estado, text="Estado *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_estado = ctk.CTkOptionMenu(col_estado, values=["Táchira"], fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        self.ent_estado.set("Táchira")
        self.ent_estado.pack(fill="x", pady=(2, 0))

        col_municipio = ctk.CTkFrame(fila1, fg_color="transparent")
        col_municipio.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(col_municipio, text="Municipio *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        municipios = MUNICIPIOS_TACHIRA
        self.ent_municipio = ctk.CTkOptionMenu(col_municipio, values=municipios, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        if municipios:
            self.ent_municipio.set(municipios[0])
        self.ent_municipio.pack(fill="x", pady=(2, 0))

        col_parroquia = ctk.CTkFrame(fila1, fg_color="transparent")
        col_parroquia.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(col_parroquia, text="Parroquia *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_parroquia = ctk.CTkEntry(
            col_parroquia, placeholder_text="Parroquia", font=("Arial", 11),
            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"],
            corner_radius=6, validate="key",
            validatecommand=(col_parroquia.register(lambda texto: len(texto) <= 100), "%P"),
        )
        self.ent_parroquia.pack(fill="x", pady=(2, 0))
        self.ent_parroquia.bind("<KeyRelease>", lambda e: self.controlador._actualizar_estado_botones_formulario())
        self.ent_parroquia.bind("<FocusOut>", lambda e: self.controlador._actualizar_estado_botones_formulario())

        fila2 = ctk.CTkFrame(inner_gen, fg_color="transparent")
        fila2.pack(fill="x", pady=5)
        fila2.grid_columnconfigure((0, 1), weight=1, uniform="datos_generales_fila2")

        col_centro_gen = ctk.CTkFrame(fila2, fg_color="transparent")
        col_centro_gen.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(col_centro_gen, text="Centro dispensador *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_centro_dispensador = ctk.CTkOptionMenu(col_centro_gen, values=self.establecimientos_opciones, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"])
        self.ent_centro_dispensador.set(self.establecimientos_opciones[0])
        self.ent_centro_dispensador.pack(fill="x", pady=(2, 0))

        col_asic = ctk.CTkFrame(fila2, fg_color="transparent")
        col_asic.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(col_asic, text="ASIC *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        nombres_asics = sorted(list(self.controlador.asic_map.keys()))
        self.ent_asic = ctk.CTkOptionMenu(col_asic, values=nombres_asics, fg_color=t["bg_base"], button_color=t["bg_card"], button_hover_color=t["bg_hover"], text_color=t["text_primary"], dropdown_fg_color=t["bg_base"], dropdown_text_color=t["text_primary"], command=lambda c: self.controlador._actualizar_estado_botones_formulario())
        if nombres_asics:
            self.ent_asic.set(nombres_asics[0])
        self.ent_asic.pack(fill="x", pady=(2, 0))

        fila3 = ctk.CTkFrame(inner_gen, fg_color="transparent")
        fila3.pack(fill="x", pady=5)
        fila3.grid_columnconfigure((0, 1), weight=1, uniform="datos_generales_fila3")

        col_nom_centro = ctk.CTkFrame(fila3, fg_color="transparent")
        col_nom_centro.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(col_nom_centro, text="Nombre del Centro *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_nombre_centro = ctk.CTkEntry(
            col_nom_centro, placeholder_text="Nombre del Centro", font=("Arial", 11),
            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"],
            corner_radius=6, validate="key",
            validatecommand=(col_nom_centro.register(lambda texto: len(texto) <= 200), "%P"),
        )
        self.ent_nombre_centro.pack(fill="x", pady=(2, 0))
        self.ent_nombre_centro.bind("<KeyRelease>", lambda e: self.controlador._actualizar_estado_botones_formulario())
        self.ent_nombre_centro.bind("<FocusOut>", lambda e: self.controlador._actualizar_estado_botones_formulario())

        col_nom_comite = ctk.CTkFrame(fila3, fg_color="transparent")
        col_nom_comite.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(col_nom_comite, text="Nombre del Comité *", font=("Arial", 10, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        self.ent_nombre_comite = ctk.CTkEntry(
            col_nom_comite, placeholder_text="Nombre del Comité", font=("Arial", 11),
            fg_color=t["bg_base"], text_color=t["text_primary"], border_color=t["border"],
            corner_radius=6, validate="key",
            validatecommand=(col_nom_comite.register(lambda texto: len(texto) <= 200), "%P"),
        )
        self.ent_nombre_comite.pack(fill="x", pady=(2, 0))
        self.ent_nombre_comite.bind("<KeyRelease>", lambda e: self.controlador._actualizar_estado_botones_formulario())
        self.ent_nombre_comite.bind("<FocusOut>", lambda e: self.controlador._actualizar_estado_botones_formulario())

        self.ent_estado.configure(command=lambda c: self.controlador._actualizar_estado_botones_formulario())
        self.ent_municipio.configure(command=lambda c: self.controlador._actualizar_estado_botones_formulario())
        self.ent_centro_dispensador.configure(command=lambda c: self.controlador._actualizar_estado_botones_formulario())

        ctk.CTkLabel(marco_form, text="Vocerías", font=("Arial", 12, "bold"), text_color=t["text_primary"]).pack(anchor="w", pady=(10, 5))

        self.frame_items = ctk.CTkFrame(marco_form, fg_color="transparent")
        self.frame_items.pack(fill="x", pady=(0, 10))

        self.vocerias_disponibles = [t_v["nombre"] for t_v in self.controlador.modelo.listar_tipos_voceria()]
        if not self.vocerias_disponibles:
            self.vocerias_disponibles = ["Asamblea Comunitaria", "Encuentro de Voceros", "Jornada de Vocería"]

        self.items_voceria = []
        self.controlador._actualizar_estado_botones_formulario()

        self._crear_item_voceria(self.frame_items, self.items_voceria, self.vocerias_disponibles, expandido=True)
        self.controlador._actualizar_dropdowns_voceria(self.items_voceria, self.vocerias_disponibles)
        self.controlador._actualizar_estado_botones_formulario()
        self.controlador._renumerar_items(self.items_voceria)

        self.btn_agregar_item = ctk.CTkButton(marco_form, text="+ Agregar vocería", font=("Arial", 10, "bold"), fg_color=t["success"], hover_color=t["success_dim"], corner_radius=8, command=lambda: self.controlador.agregar_siguiente_voceria(self.frame_items, self.items_voceria, self.vocerias_disponibles))
        self.btn_agregar_item.pack(anchor="w", pady=(10, 15))

        if datos_edicion:
            if datos_edicion.get("estado"):
                self.ent_estado.set(datos_edicion["estado"])
            if datos_edicion.get("municipio"):
                self.ent_municipio.set(datos_edicion["municipio"])
            if datos_edicion.get("parroquia"):
                self.ent_parroquia.delete(0, tk.END)
                self.ent_parroquia.insert(0, datos_edicion["parroquia"])
                self.ent_parroquia.configure(text_color=t["text_primary"])
            if datos_edicion.get("asic_nombre"):
                self.ent_asic.set(datos_edicion["asic_nombre"])
            elif datos_edicion.get("id_asic"):
                for nom, id_a in self.controlador.asic_map.items():
                    if id_a == datos_edicion["id_asic"]:
                        self.ent_asic.set(nom)
                        break
            if datos_edicion.get("centro_dispensador"):
                self.ent_centro_dispensador.set(datos_edicion["centro_dispensador"])
            if datos_edicion.get("nombre_centro"):
                self.ent_nombre_centro.delete(0, tk.END)
                self.ent_nombre_centro.insert(0, datos_edicion["nombre_centro"])
                self.ent_nombre_centro.configure(text_color=t["text_primary"])
            if datos_edicion.get("nombre_comite"):
                self.ent_nombre_comite.delete(0, tk.END)
                self.ent_nombre_comite.insert(0, datos_edicion["nombre_comite"])
                self.ent_nombre_comite.configure(text_color=t["text_primary"])

            for it in list(self.items_voceria):
                it["frame"].destroy()
            self.items_voceria.clear()

            items_existentes = datos_edicion.get("items", [])
            for idx, item_data_raw in enumerate(items_existentes):
                self._crear_item_voceria(self.frame_items, self.items_voceria, self.vocerias_disponibles, expandido=(idx == 0))
                if self.items_voceria:
                    nuevo_item = self.items_voceria[-1]
                    w = nuevo_item["widgets"]
                    if item_data_raw.get("nombres"):
                        w["nombres"].delete(0, tk.END)
                        w["nombres"].insert(0, str(item_data_raw["nombres"]))
                    if item_data_raw.get("ci"):
                        w["ci"].delete(0, tk.END)
                        w["ci"].insert(0, str(item_data_raw["ci"]))
                    if item_data_raw.get("telefono"):
                        w["tel"].delete(0, tk.END)
                        w["tel"].insert(0, str(item_data_raw["telefono"]))
                    if item_data_raw.get("fecha_nacimiento"):
                        fn = item_data_raw["fecha_nacimiento"]
                        if isinstance(fn, (date, datetime)):
                            fn = fn.strftime("%Y-%m-%d")
                        w["fnac"].delete(0, tk.END)
                        w["fnac"].insert(0, str(fn))
                    if item_data_raw.get("tipo_voceria_nombre"):
                        w["voceria"].set(str(item_data_raw["tipo_voceria_nombre"]))
                    elif item_data_raw.get("id_tipo_voceria"):
                        for nom_tipo, id_t in self.controlador.tipo_voceria_map.items():
                            if id_t == item_data_raw["id_tipo_voceria"]:
                                w["voceria"].set(nom_tipo)
                                break
                    if item_data_raw.get("sexo"):
                        w["sexo"].set(str(item_data_raw["sexo"]))
                    if item_data_raw.get("profesion"):
                        w["prof"].delete(0, tk.END)
                        w["prof"].insert(0, str(item_data_raw["profesion"]))
                    if item_data_raw.get("correo"):
                        w["correo"].delete(0, tk.END)
                        w["correo"].insert(0, str(item_data_raw["correo"]))
                    if item_data_raw.get("fechas_eleccion"):
                        fe = item_data_raw["fechas_eleccion"]
                        if isinstance(fe, (date, datetime)):
                            fe = fe.strftime("%Y-%m-%d")
                        w["felecc"].delete(0, tk.END)
                        w["felecc"].insert(0, str(fe))

                    nuevo_item["actualizar_edad"]()
                    self._actualizar_header_item(nuevo_item)

            if not items_existentes:
                self._crear_item_voceria(self.frame_items, self.items_voceria, self.vocerias_disponibles, expandido=True)

            self.controlador._actualizar_dropdowns_voceria(self.items_voceria, self.vocerias_disponibles)
            self.controlador._actualizar_estado_botones_formulario()

        def mostrar_error(mensaje):
            lbl_error.configure(text=mensaje)
            lbl_error.pack(anchor="w", pady=(0, 8), padx=2, ipadx=12, ipady=6, before=self.btn_guardar)

        def guardar():
            lbl_error.pack_forget()
            lbl_error.configure(text="")
            estado = self.ent_estado.get().strip() if hasattr(self, "ent_estado") else ""
            municipio = self.ent_municipio.get().strip() if hasattr(self, "ent_municipio") else ""
            parroquia = self.ent_parroquia.get().strip() if hasattr(self, "ent_parroquia") else ""
            asic = self.ent_asic.get().strip() if hasattr(self, "ent_asic") else ""
            centro_dispensador = self.ent_centro_dispensador.get().strip() if hasattr(self, "ent_centro_dispensador") else ""
            nombre_centro = self.ent_nombre_centro.get().strip() if hasattr(self, "ent_nombre_centro") else ""
            nombre_comite = self.ent_nombre_comite.get().strip() if hasattr(self, "ent_nombre_comite") else ""

            if not estado:
                mostrar_error("⚠ Debe seleccionar el Estado")
                return
            if not municipio:
                mostrar_error("⚠ Debe seleccionar el Municipio")
                return
            if not parroquia:
                mostrar_error("⚠ Debe ingresar la Parroquia")
                self.ent_parroquia.focus_set()
                return
            if not asic or asic not in self.controlador.asic_map:
                mostrar_error("⚠ Debe seleccionar un ASIC válido")
                return
            if not centro_dispensador:
                mostrar_error("⚠ Debe seleccionar el Centro dispensador")
                return
            if not nombre_centro:
                mostrar_error("⚠ Debe ingresar el Nombre del Centro")
                self.ent_nombre_centro.focus_set()
                return
            if not nombre_comite:
                mostrar_error("⚠ Debe ingresar el Nombre del Comité")
                self.ent_nombre_comite.focus_set()
                return

            items_validos = [item for item in self.items_voceria if item["frame"].winfo_exists()]

            nombres_campos = {
                "nombres": "Nombres y Apellidos",
                "ci": "C.I.",
                "tel": "Teléfono",
                "fnac": "Fecha de Nacimiento",
                "edad": "Edad",
                "voceria": "Tipo de Vocería",
                "sexo": "Sexo",
                "prof": "Profesión/Oficio",
                "correo": "Correo Electrónico",
                "felecc": "Fecha de Elección",
            }

            for idx, item in enumerate(items_validos, start=1):
                w = item["widgets"]
                for key, etiqueta in nombres_campos.items():
                    if key == "edad":
                        continue
                    val = w[key].get().strip() if hasattr(w[key], "get") else ""
                    if not val or val in ("(Sin opciones disponibles)", "Seleccionar vocería...", "AAAA-MM-DD", "Edad"):
                        mostrar_error(f"⚠ Vocería #{idx}: Complete el campo '{etiqueta} *'")
                        if hasattr(w[key], "focus_set"):
                            w[key].focus_set()
                        return

                fecha_nacimiento = self._parsear_fecha_formulario(w["fnac"].get())
                edad_por_fecha = _calcular_edad(fecha_nacimiento)
                if edad_por_fecha is None or not 18 <= edad_por_fecha <= 99:
                    mostrar_error(f"⚠ Vocería #{idx}: La Fecha de Nacimiento debe corresponder a una persona entre 18 y 99 años")
                    w["fnac"].focus_set()
                    return
                item["actualizar_edad"]()

                for key, etiqueta in nombres_campos.items():
                    val = w[key].get().strip() if hasattr(w[key], "get") else ""
                    if key == "correo" and not validar_correo(val):
                        mostrar_error(f"⚠ Vocería #{idx}: El Correo Electrónico no es válido")
                        if hasattr(w[key], "focus_set"):
                            w[key].focus_set()
                        return
                    if key == "edad":
                        if not val.isdigit() or len(val) > 2 or int(val) < 18 or int(val) > 99:
                            mostrar_error(f"⚠ Vocería #{idx}: La Edad debe estar entre 18 y 99 años")
                            if hasattr(w[key], "focus_set"):
                                w[key].focus_set()
                            return
                    if key == "ci":
                        ci_digitos = val.replace(",", "")
                        if not ci_digitos.isdigit() or not 7 <= len(ci_digitos) <= 8:
                            mostrar_error(f"⚠ Vocería #{idx}: La C.I. debe tener entre 7 y 8 dígitos")
                            w[key].focus_set()
                            return
                    if key == "tel":
                        if not val.isdigit() or not 11 <= len(val) <= 12:
                            mostrar_error(f"⚠ Vocería #{idx}: El Teléfono debe tener entre 11 y 12 dígitos")
                            if hasattr(w[key], "focus_set"):
                                w[key].focus_set()
                            return
                    if key == "nombres" and not 5 <= len(val) <= 40:
                        mostrar_error(f"⚠ Vocería #{idx}: '{etiqueta}' debe tener entre 5 y 40 caracteres")
                        w[key].focus_set()
                        return
                    if key == "prof" and not 3 <= len(val) <= 40:
                        mostrar_error(f"⚠ Vocería #{idx}: '{etiqueta}' debe tener entre 3 y 40 caracteres")
                        w[key].focus_set()
                        return

                fecha_eleccion = self._parsear_fecha_formulario(w["felecc"].get())
                if not fecha_eleccion or fecha_eleccion > date.today():
                    mostrar_error(f"⚠ Vocería #{idx}: La Fecha de Elección no puede ser futura")
                    w["felecc"].focus_set()
                    return

            if len(items_validos) < 7:
                mostrar_error(f"⚠ Debe agregar al menos 7 vocerías (actual: {len(items_validos)})")
                return

            self.controlador.guardar_voceria(
                ventana, mostrar_error, datos_edicion,
                estado, municipio, parroquia, asic,
                centro_dispensador, nombre_centro, nombre_comite,
                items_validos,
            )

        self.btn_guardar = ctk.CTkButton(marco_pie_formulario, text="Crear Vocería" if datos_edicion is None else "Guardar Cambios", font=("Arial", 11, "bold"), fg_color=t["accent"], hover_color=t["accent_dim"], corner_radius=8, command=guardar, state="normal")
        self.btn_guardar.pack(fill="x", ipady=8)

    @staticmethod
    def _parsear_fecha_formulario(valor):
        try:
            return datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    def mostrar_detalle_voceria(self, voc):
        t = self.t
        items = voc.get("items", [])

        ventana = ctk.CTkToplevel(self.parent)
        set_favicon(ventana)
        ventana.title(f"Detalle del Comité #{voc['id_voceria']} - {voc.get('asic_nombre', '')}")
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

        header_frame = ctk.CTkFrame(ventana, fg_color=t["bg_card"], corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=20, pady=15)

        fecha_registro = voc.get("created_at") or voc.get("fecha_registro", "")
        if hasattr(fecha_registro, "strftime"):
            fecha_registro = fecha_registro.strftime("%d/%m/%Y")

        info_general = [
            ("Comité", voc.get("nombre_comite", "")),
            ("ASIC", voc.get("asic_nombre", "")),
            ("Estado", voc.get("estado", "")),
            ("Municipio", voc.get("municipio", "")),
            ("Parroquia", voc.get("parroquia", "")),
            ("Centro dispensador", voc.get("centro_dispensador", "")),
            ("Nombre del centro", voc.get("nombre_centro", "")),
            ("Fecha de registro", fecha_registro),
        ]
        for column in range(4):
            header_inner.grid_columnconfigure(column, weight=1, uniform="comite_info")

        for index, (label, value) in enumerate(info_general):
            cell = ctk.CTkFrame(header_inner, fg_color="transparent")
            cell.grid(row=index // 4, column=index % 4, sticky="nsew", padx=8, pady=4)
            ctk.CTkLabel(cell, text=label, font=("Arial", 13, "bold"), text_color=t["text_muted"], height=18).pack(anchor="w")
            ctk.CTkFrame(cell, height=1, fg_color=t["border"], corner_radius=0).pack(fill="x", pady=(2, 2))
            ctk.CTkLabel(
                cell, text=str(value or "-"), font=("Arial", 12), text_color=t["text_primary"],
                wraplength=280, justify="left", anchor="w", height=20,
            ).pack(anchor="w", fill="x")

        separator(ventana, horizontal=True, fg_color=t["border"]).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(ventana, text=f"Integrantes del comité ({len(items)})", font=("Arial", 13, "bold"), text_color=t["text_primary"]).pack(anchor="w", padx=20, pady=(10, 5))

        marco_tabla = ctk.CTkFrame(ventana, fg_color="transparent", corner_radius=10)
        marco_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("DetalleItem.Treeview", background=t["bg_base"], foreground=t["text_primary"], fieldbackground=t["bg_base"], font=("Arial", 11), rowheight=30, borderwidth=0)
        style.configure("DetalleItem.Treeview.Heading", background=t["bg_card"], foreground=t["text_primary"], font=("Arial", 11, "bold"), relief="flat", borderwidth=0)
        style.map("DetalleItem.Treeview", background=[("selected", t["accent"])], foreground=[("selected", t["text_primary"])])

        columnas_items = ("tipo_voceria", "nombres", "ci", "telefono", "fecha_nacimiento", "edad", "sexo", "profesion", "correo", "fechas_eleccion")
        labels_items = {
            "tipo_voceria": "Vocería",
            "nombres": "Nombres y Apellidos",
            "ci": "C.I.",
            "telefono": "Teléfono",
            "fecha_nacimiento": "F. Nacimiento",
            "edad": "Edad",
            "sexo": "Sexo",
            "profesion": "Profesión",
            "correo": "Correo",
            "fechas_eleccion": "F. Elección",
        }

        tree = ttk.Treeview(marco_tabla, columns=columnas_items, show="headings", height=15, style="DetalleItem.Treeview")
        configuracion_columnas = {
            "tipo_voceria": (2.8, 250), "nombres": (1.2, 110), "ci": (0.75, 65),
            "telefono": (1.0, 85), "fecha_nacimiento": (1.05, 90), "edad": (0.5, 45),
            "sexo": (0.55, 45), "profesion": (0.95, 80), "correo": (1.2, 100),
            "fechas_eleccion": (1.0, 85),
        }
        for col in columnas_items:
            tree.heading(col, text=labels_items[col])
            tree.column(col, width=100, minwidth=configuracion_columnas[col][1], stretch=False,
                        anchor="w" if col not in ("edad", "sexo") else "center")

        def ajustar_columnas(event):
            ancho_disponible = max(event.width - 4, 0)
            peso_total = sum(configuracion_columnas[col][0] for col in columnas_items)
            for col in columnas_items:
                peso, minimo = configuracion_columnas[col]
                tree.column(col, width=max(minimo, int(ancho_disponible * peso / peso_total)))

        tree.bind("<Configure>", ajustar_columnas)

        for item in items:
            tree.insert("", "end", values=(
                item.get("tipo_voceria_nombre", ""),
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

        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)
        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(marco_tabla, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tree.bind("<Button-1>", self._on_tabla_click, add="+")

        ctk.CTkButton(ventana, text="Cerrar", font=("Arial", 11, "bold"), fg_color=t["accent_dim"], hover_color=t["accent"], corner_radius=8, command=ventana.destroy).pack(pady=(0, 20))


__all__ = ["VistaVoceria"]
