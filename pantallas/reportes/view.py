import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

try:
    from tkcalendar import Calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False


from constants import THEME
from ui_helpers import (
    btn_success,
    btn_secondary,
    date_picker,
    frame,
    frame_surface,
    frame_transparent,
    label,
    label_subtitle,
    label_title,
    multiselect_option_menu,
)


class VistaReporte:
    def __init__(self, parent, controlador):
        self.parent = parent
        self.controlador = controlador
        self._construir_ui()

    def _construir_ui(self):
        header = frame_transparent(self.parent)
        header.pack(fill="x", padx=30, pady=(20, 4))

        label_title(header, "📊  Reportes y Consolidación", 17).pack(side="left")

        label_subtitle(
            self.parent,
            "Genera informes consolidados por período y reportes semanales con exportación a Word.",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", padx=30, pady=(0, 10))

        # Contenedor desplazable para albergar las dos cajas cómodamente
        self._scroll_container = ctk.CTkScrollableFrame(self.parent, fg_color="gray15")
        self._scroll_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._frame_generar = frame_transparent(self._scroll_container)
        self._frame_generar.pack(fill="x", expand=True)
        self.mostrar_paso1()

        self._construir_caja_semanal()

    def mostrar_paso1(self):
        self._limpiar(self._frame_generar)

        card = frame_surface(self._frame_generar, fg_color="gray20", corner_radius=10)
        card.pack(fill="x", padx=15, pady=(8, 0))

        inner = frame_transparent(card)
        inner.pack(fill="x", padx=25, pady=20)

        label(inner, "Informe Consolidado por Período", font_size=13, bold=True).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 14))

        label(inner, "Fecha inicio:", font_size=10).grid(row=1, column=0, sticky="w", pady=4)
        self._entry_f_ini = self._date_widget(inner)
        self._entry_f_ini.grid(row=1, column=1, sticky="w", padx=(8, 30))

        label(inner, "Fecha fin:", font_size=10).grid(row=1, column=2, sticky="w", pady=4, padx=(20, 0))
        self._entry_f_fin = self._date_widget(inner)
        self._entry_f_fin.grid(row=1, column=3, sticky="w", padx=(8, 30))

        label(inner, "ASIC (opcional):", font_size=10).grid(row=2, column=0, sticky="w", pady=6)

        self._asic_map, self._asic_nombres = self.controlador.modelo.listar_asics()

        t = THEME
        self._combo_asic = multiselect_option_menu(
            inner,
            values=self._asic_nombres,
            placeholder="Todos",
            width=440,
            fg_color=t["bg_base"],
            button_color=t["bg_card"],
            button_hover_color=t["bg_hover"],
            text_color=t["text_primary"],
            dropdown_fg_color=t["bg_base"],
            dropdown_text_color=t["text_primary"],
            border_color=t["border"],
            corner_radius=6,
        )
        self._combo_asic.grid(row=2, column=1, columnspan=3, sticky="w", padx=8, pady=6)

        label(inner, "Título del informe:", font_size=10).grid(row=3, column=0, sticky="w", pady=4)
        validar_titulo = inner.register(lambda texto: len(texto) <= 200)
        self._entry_titulo = ctk.CTkEntry(
            inner,
            width=440,
            font=("Arial", 11),
            fg_color=t["bg_base"],
            text_color=t["text_primary"],
            border_color=t["border"],
            corner_radius=6,
            validate="key",
            validatecommand=(validar_titulo, "%P"),
        )
        self._entry_titulo.insert(0, "Informe Consolidado de Actividades")
        self._entry_titulo.grid(row=3, column=1, columnspan=3, sticky="w", padx=8)

        btn_secondary(inner, "▶  Generar Vista Previa", self.controlador.iniciar_previo).grid(row=4, column=0, columnspan=4, sticky="w", pady=(14, 0))

    def _construir_caja_semanal(self):
        t = THEME
        hoy = datetime.now()

        card_semanal = frame_surface(self._scroll_container, fg_color="gray20", corner_radius=10)
        card_semanal.pack(fill="x", padx=15, pady=(16, 15))

        inner = frame_transparent(card_semanal)
        inner.pack(fill="x", padx=25, pady=20)

        label(inner, "Reporte Semanal de Actividades por ASIC", font_size=13, bold=True).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6)
        )
        label_subtitle(
            inner,
            "Selecciona el año y la semana deseada mediante el calendario para generar el reporte ordenado por actividades.",
            font_size=10,
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 14))

        # Selector de Año (desde 2020 hasta el año actual)
        label(inner, "Año:", font_size=10).grid(row=2, column=0, sticky="w", pady=6)
        anios = [str(y) for y in range(2020, hoy.year + 1)]
        self._combo_anio = ctk.CTkComboBox(
            inner,
            values=anios,
            width=110,
            fg_color=t["bg_base"],
            border_color=t["border"],
            button_color=t["bg_card"],
            command=self._al_cambiar_anio_semanal,
        )
        self._combo_anio.set(str(hoy.year))
        self._combo_anio.grid(row=2, column=1, sticky="w", padx=(8, 20), pady=6)

        # Selector interactivo de Semana (tipo input de fecha con calendario)
        label(inner, "Semana:", font_size=10).grid(row=2, column=2, sticky="w", pady=6)

        # Widget estilo input de fecha para la semana
        self._frame_input_semana = ctk.CTkFrame(
            inner,
            fg_color="#20053D",
            border_color="#345572",
            border_width=2,
            corner_radius=6,
            height=28,
            width=360,
        )
        self._frame_input_semana.grid(row=2, column=3, sticky="w", padx=(8, 10), pady=6)
        self._frame_input_semana.grid_columnconfigure(0, weight=1)

        self._entry_semana = ctk.CTkEntry(
            self._frame_input_semana,
            font=("Arial", 10),
            fg_color="#20053D",
            text_color="#CBE1DB",
            border_width=0,
            height=24,
            width=300,
        )
        self._entry_semana.grid(row=0, column=0, sticky="ew", padx=(8, 2), pady=2)
        self._entry_semana.configure(state="readonly")

        self._btn_cal_semana = ctk.CTkButton(
            self._frame_input_semana,
            text="📅",
            width=26,
            height=22,
            font=("Segoe UI Emoji", 11),
            fg_color="transparent",
            hover_color="#2f4d6a",
            text_color="#CBE1DB",
            corner_radius=4,
            command=self._toggle_calendario_semana,
        )
        self._btn_cal_semana.grid(row=0, column=1, padx=(0, 4), pady=2)

        self._crear_popup_calendario_semana()

        # Inicializar con la semana actual
        semana_inicial = self.controlador.modelo.obtener_semana_de_fecha(date.today())
        if semana_inicial:
            self._semana_seleccionada = semana_inicial
            self._actualizar_texto_input_semana(semana_inicial)
        else:
            self._semana_seleccionada = None

        # Botón de descarga
        btn_success(
            inner,
            "📥  Descargar Reporte Semanal",
            self._ejecutar_descarga_semanal,
        ).grid(row=3, column=0, columnspan=4, sticky="w", pady=(16, 0))

    def _crear_popup_calendario_semana(self):
        if not HAS_CALENDAR:
            self._top_cal_semana = None
            self._cal_widget_semana = None
            self._btn_cal_semana.configure(state="disabled")
            return

        self._top_cal_semana = tk.Toplevel(self._frame_input_semana)
        self._top_cal_semana.withdraw()
        self._top_cal_semana.overrideredirect(True)

        # Destruir ventana emergente si se destruye el widget contenedor
        self._frame_input_semana.bind(
            "<Destroy>",
            lambda e: self._top_cal_semana.destroy() if getattr(self, "_top_cal_semana", None) else None,
            add="+",
        )

        hoy = date.today()
        self._cal_widget_semana = Calendar(
            self._top_cal_semana,
            date_pattern="yyyy-mm-dd",
            year=hoy.year,
            month=hoy.month,
            firstweekday="monday",
            showweeknumbers=True,
            background="#26405E",
            foreground="#CBE1DB",
            headersbackground="#20053D",
            headersforeground="#CBE1DB",
            selectbackground="#613BE3",
            selectforeground="white",
            normalbackground="#20053D",
            normalforeground="#CBE1DB",
            weekendbackground="#26405E",
            weekendforeground="#CBE1DB",
            othermonthforeground="#5a7a85",
            othermonthbackground="#1a2f45",
            font=("Arial", 9),
        )
        self._cal_widget_semana.pack()
        self._cal_widget_semana.bind("<<CalendarSelected>>", self._al_seleccionar_fecha_calendario)

    def _toggle_calendario_semana(self):
        if not getattr(self, "_top_cal_semana", None) or not getattr(self, "_cal_widget_semana", None):
            return

        if self._top_cal_semana.winfo_ismapped():
            self._top_cal_semana.withdraw()
            return

        # Sincronizar el año o fecha seleccionada
        try:
            if hasattr(self, "_semana_seleccionada") and self._semana_seleccionada:
                d = self._semana_seleccionada["fecha_inicio"]
                self._cal_widget_semana.selection_set(d)
            else:
                anio_sel = int(self._combo_anio.get())
                self._cal_widget_semana.selection_set(date(anio_sel, 1, 1))
        except Exception:
            pass

        self._frame_input_semana.update_idletasks()
        x = self._frame_input_semana.winfo_rootx()
        y = self._frame_input_semana.winfo_rooty() + self._frame_input_semana.winfo_height() + 2
        self._top_cal_semana.geometry(f"+{x}+{y}")
        self._top_cal_semana.deiconify()
        self._top_cal_semana.lift()
        self._top_cal_semana.attributes("-topmost", True)
        self._bind_click_fuera_calendario_semana()

    def _bind_click_fuera_calendario_semana(self):
        top_win = self._frame_input_semana.winfo_toplevel()

        def _check_click(e):
            if not self._top_cal_semana or not self._top_cal_semana.winfo_ismapped():
                try:
                    top_win.unbind("<ButtonPress-1>", click_id)
                except Exception:
                    pass
                return
            try:
                x, y = self._top_cal_semana.winfo_pointerxy()
                xc = self._top_cal_semana.winfo_rootx()
                yc = self._top_cal_semana.winfo_rooty()
                w = self._top_cal_semana.winfo_width()
                h = self._top_cal_semana.winfo_height()
                if not (xc <= x <= xc + w and yc <= y <= yc + h):
                    bx = self._btn_cal_semana.winfo_rootx()
                    by = self._btn_cal_semana.winfo_rooty()
                    bw = self._btn_cal_semana.winfo_width()
                    bh = self._btn_cal_semana.winfo_height()
                    if not (bx <= x <= bx + bw and by <= y <= by + bh):
                        self._top_cal_semana.withdraw()
                        top_win.unbind("<ButtonPress-1>", click_id)
            except Exception:
                pass

        click_id = top_win.bind("<ButtonPress-1>", _check_click, add="+")

    def _al_seleccionar_fecha_calendario(self, event=None):
        if not self._cal_widget_semana:
            return
        sel = self._cal_widget_semana.selection_get()
        if sel:
            info = self.controlador.modelo.obtener_semana_de_fecha(sel)
            if info:
                self._semana_seleccionada = info
                self._actualizar_texto_input_semana(info)
                # Actualizar el combobox de año si el usuario seleccionó una fecha de otro año
                str_year = str(info["year"])
                if str_year in self._combo_anio.cget("values"):
                    self._combo_anio.set(str_year)

        if self._top_cal_semana:
            self._top_cal_semana.withdraw()

    def _al_cambiar_anio_semanal(self, nuevo_anio_str):
        try:
            nuevo_anio = int(nuevo_anio_str)
            if hasattr(self, "_semana_seleccionada") and self._semana_seleccionada:
                mes = self._semana_seleccionada["month"]
                dia = min(self._semana_seleccionada["fecha_inicio"].day, 28)
                nueva_fecha = date(nuevo_anio, mes, dia)
            else:
                nueva_fecha = date(nuevo_anio, 1, 1)

            info = self.controlador.modelo.obtener_semana_de_fecha(nueva_fecha)
            if info:
                self._semana_seleccionada = info
                self._actualizar_texto_input_semana(info)
        except Exception:
            pass

    def _actualizar_texto_input_semana(self, info):
        # Muestra en el input: Semana X (DD/MM al DD/MM) - MES AÑO
        texto = f"{info['etiqueta']}  •  {info['mes_nombre']} {info['year']}"
        self._entry_semana.configure(state="normal")
        self._entry_semana.delete(0, tk.END)
        self._entry_semana.insert(0, texto)
        self._entry_semana.configure(state="readonly")

    def _ejecutar_descarga_semanal(self):
        semana_info = getattr(self, "_semana_seleccionada", None)
        if not semana_info:
            messagebox.showwarning(
                "Semana no seleccionada",
                "Por favor selecciona una semana en el calendario antes de exportar.",
            )
            return

        self.controlador.exportar_reporte_semanal(semana_info)



    def leer_asics_seleccionados(self):
        seleccionados = self._combo_asic.get_selected()
        if not seleccionados:
            return None
        ids = [self._asic_map[nom] for nom in seleccionados if nom in self._asic_map]
        return ids if ids else None

    def leer_fecha(self, widget):
        try:
            if hasattr(widget, "get_date"):
                d = widget.get_date()
                if d:
                    return d
            val = widget.get().strip()
            if val and val != "AAAA-MM-DD":
                return datetime.strptime(val, "%Y-%m-%d").date()
            return None
        except Exception:
            return None

    def _date_widget(self, parent):
        return date_picker(
            parent,
            width=150,
            font=("Arial", 10),
            fg_color="#20053D",
            text_color="#CBE1DB",
            border_color="#345572",
            corner_radius=6,
        )

    def mostrar_paso2(self, previo):
        self.parent.configure(cursor="")
        self._limpiar(self._frame_generar)

        actividades = previo["actividades"]
        resumen_asic = previo["resumen_por_asic"]
        resumen_tipo = previo["resumen_por_tipo"]
        total_act = previo["total_actividades"]
        total_part = previo["total_participantes"]

        card_act = frame_surface(self._frame_generar, fg_color="gray20", corner_radius=10)
        card_act.pack(fill="x", padx=15, pady=(8, 15), side="bottom")

        inner_act = frame_transparent(card_act)
        inner_act.pack(fill="x", padx=20, pady=14)

        btn_secondary(inner_act, "← Volver", self.mostrar_paso1).pack(side="left", padx=(0, 10))

        if total_act > 0:
            btn_success(inner_act, "📄  Exportar Word", self.controlador.exportar_word).pack(side="left")

        contenido = frame_transparent(self._frame_generar)
        contenido.pack(fill="both", expand=True, padx=15, pady=(6, 0))

        card_top = frame_surface(contenido, fg_color="gray20", corner_radius=10)
        card_top.pack(fill="x", pady=(0, 10))

        inner_top = frame_transparent(card_top)
        inner_top.pack(fill="x", padx=20, pady=14)

        label(inner_top, "Paso 2 de 3 — Vista previa del informe", font_size=12, bold=True).pack(anchor="w", pady=(0, 8))

        chips = frame_transparent(inner_top)
        chips.pack(anchor="w")
        self._chip(chips, f"📋 Actividades: {total_act}", "gray25")
        self._chip(chips, f"👥 Participantes: {total_part}", "#613BE3")
        self._chip(chips, f"📅 {previo['fecha_inicio']} → {previo['fecha_fin']}", "#266470")
        if previo.get("asic_nombre"):
            self._chip(chips, f"🏥 {previo['asic_nombre']}", "#30152a")

        self._configurar_estilo_tablas()
        panel_tablas = frame_transparent(contenido)
        panel_tablas.pack(fill="both", expand=True, pady=(0, 10))

        if total_act == 0:
            label(panel_tablas, "⚠  No hay actividades para el período y filtros seleccionados.", font_size=11, text_color="#c45050").pack(pady=20)
        else:
            fila_resumenes = frame_transparent(panel_tablas)
            fila_resumenes.pack(fill="both", expand=True, pady=(0, 10))
            self._mini_tabla(fila_resumenes, "Por ASIC", resumen_asic, ["ASIC", "Actividades", "Participantes"])
            self._mini_tabla(fila_resumenes, "Por Tipo", resumen_tipo, ["Tipo de Actividad", "Actividades", "Participantes"])

        vocerias = previo.get("vocerias", [])
        if vocerias:
            self._mini_tabla_vocerias(panel_tablas, vocerias)
        else:
            label(panel_tablas, "⚠  No hay vocerías CS para el período y filtros seleccionados.", font_size=11, text_color="#c45050").pack(pady=10)

    def _configurar_estilo_tablas(self):
        t = THEME
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "R.Treeview",
            background=t["bg_base"],
            foreground=t["text_primary"],
            fieldbackground=t["bg_base"],
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "R.Treeview.Heading",
            background=t["bg_card"],
            foreground=t["text_primary"],
            font=("Arial", 10, "bold"),
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "R.Treeview.Heading",
            background=[("active", t["bg_card"])],
            foreground=[("active", t["text_primary"])],
        )
        style.map(
            "R.Treeview",
            background=[("selected", t["accent"])],
            foreground=[("selected", t["text_primary"])],
        )

    def _mini_tabla(self, parent, titulo, filas, cabeceras):
        marco = frame_surface(parent, fg_color="gray20", corner_radius=10)
        marco.pack(side="left", fill="both", expand=True, padx=(0, 8))

        inner = frame_transparent(marco)
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        label(inner, titulo, font_size=10, bold=True).pack(anchor="w", pady=(0, 5))

        cols = tuple(range(len(cabeceras)))

        tree = ttk.Treeview(inner, columns=cols, show="headings", style="R.Treeview", height=min(len(filas), 7))
        for i, cab in enumerate(cabeceras):
            tree.heading(i, text=cab, anchor="w")
            tree.column(i, width=(200 if i == 0 else 100), anchor="center" if i > 0 else "w")

        for fila in filas:
            nombre = fila.get("nombre") or fila.get("asic_nombre", "")
            tree.insert("", "end", values=(nombre, fila["total_actividades"], fila["total_participantes"]))

        sy = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        tree.bind("<Button-1>", self._on_tabla_click, add="+")

    def _on_tabla_click(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if not item:
            tree.selection_remove(tree.selection())

    def _mini_tabla_vocerias(self, parent, vocerias):
        marco = frame_surface(parent, fg_color="gray20", corner_radius=10)
        marco.pack(fill="both", expand=True)

        inner = frame_transparent(marco)
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        label(inner, "Vocerías CS", font_size=10, bold=True).pack(anchor="w", pady=(0, 5))

        cabeceras = ["Fecha", "ASIC", "Cantidad Vocerías", "Municipio", "Parroquia"]
        cols = tuple(range(len(cabeceras)))

        tree = ttk.Treeview(inner, columns=cols, show="headings", style="R.Treeview", height=min(len(vocerias), 8))
        for i, cab in enumerate(cabeceras):
            tree.heading(i, text=cab, anchor="w")
        tree.column(0, width=100, anchor="w")
        tree.column(1, width=180, anchor="w")
        tree.column(2, width=120, anchor="w")
        tree.column(3, width=120, anchor="w")
        tree.column(4, width=120, anchor="w")

        for voc in vocerias:
            f = voc.get("fecha_registro", "")
            if hasattr(f, "strftime"):
                f = f.strftime("%d/%m/%Y")
            cantidad = voc.get("cantidad_vocerias", 0)
            tree.insert(
                "",
                "end",
                values=(
                    f,
                    voc.get("asic_nombre", ""),
                    cantidad,
                    voc.get("municipio", ""),
                    voc.get("parroquia", ""),
                ),
            )

        sy = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        tree.bind("<Button-1>", self._on_tabla_click, add="+")

    def _limpiar(self, frame_widget):
        for w in frame_widget.winfo_children():
            w.destroy()

    def _chip(self, parent, texto, color):
        chip = ctk.CTkFrame(parent, fg_color=color, corner_radius=6)
        chip.pack(side="left", padx=(0, 8))
        label(chip, texto, font_size=9, bold=True).pack(padx=10, pady=4)

    def mostrar_error(self, exc):
        self.parent.configure(cursor="")
        messagebox.showerror("Error", str(exc))


__all__ = ["VistaReporte"]
