import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from themes import THEME
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
        header.pack(fill="x", padx=30, pady=(25, 4))

        label_title(header, "📊  Reportes y Consolidación", 17).pack(side="left")

        label_subtitle(
            self.parent,
            "Genera informes consolidados por período y exporta el documento en Word.",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", padx=30, pady=(0, 14))

        self._frame_generar = frame(self.parent, fg_color="gray15")
        self._frame_generar.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self.mostrar_paso1()

    def mostrar_paso1(self):
        self._limpiar(self._frame_generar)

        card = frame_surface(self._frame_generar, fg_color="gray20", corner_radius=10)
        card.pack(fill="x", padx=15, pady=(8, 0))

        inner = frame_transparent(card)
        inner.pack(fill="x", padx=25, pady=20)

        label(inner, "Paso 1 de 3 — Configurar parámetros del informe", font_size=12, bold=True).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 14))

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
