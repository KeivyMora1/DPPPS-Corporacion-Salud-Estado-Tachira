# ============================================================
# pantallas/reportes.py
# Vista de generación y exportación de informes consolidados.
#
# Flujo de 3 pasos:
#   Paso 1 — Configurar parámetros (rango de fechas, ASIC, título)
#   Paso 2 — Previsualizar resumen del informe
#   Paso 3 — Guardar en BD y/o exportar PDF / Excel
# ============================================================

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import date, datetime
import customtkinter as ctk

from db import AuthController, AsicDAO, ConsolidacionService, PDFService
from ui_helpers import (
    frame, frame_transparent, frame_surface, label, label_title, label_subtitle,
    btn_primary, btn_secondary, btn_danger, btn_success, separator, treeview_style,
    entry, combobox
)

try:
    from tkcalendar import DateEntry
    _TIENE_CALENDAR = True
except ImportError:
    _TIENE_CALENDAR = False


class ReporteView:
    """
    Sección de reportes y consolidación de informes.
    Se monta como hijo del área de contenido de MainView.
    """

    def __init__(self, parent: tk.Frame):
        self.parent  = parent
        self.auth    = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        self._previo:              dict | None = None
        self._id_informe_guardado: int  | None = None

        if self.usuario is None:
            self.parent.after(0, lambda: messagebox.showwarning(
                "Sesión no activa",
                "Debes iniciar sesión antes de acceder a reportes."
            ))

        self._construir_ui()

    def _construir_ui(self):
        header = frame_transparent(self.parent)
        header.pack(fill="x", padx=30, pady=(25, 4))
 
        label_title(header, "📊  Reportes y Consolidación", 17).pack(side="left")
 
        label_subtitle(self.parent,
            "Genera informes consolidados por período y exporta el documento en Word.",
            wraplength=900, justify="left"
        ).pack(anchor="w", padx=30, pady=(0, 14))
 
        self._frame_generar = frame(self.parent, fg_color="gray15")
        self._frame_generar.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self._mostrar_paso1()

    def _mostrar_paso1(self):
        self._limpiar(self._frame_generar)
        self._previo = None
        self._id_informe_guardado = None

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

        label(inner, "ASIC (opcional):\nCtrl+clic para\nseleccionar varios", font_size=10).grid(row=2, column=0, sticky="nw", pady=4)

        self._asic_map: dict = {}          # nombre → id_asic
        self._asic_nombres: list = []      # orden de inserción para el Listbox
        try:
            for a in AsicDAO().obtener_todos():
                self._asic_map[a["nombre"]] = a["id_asic"]
                self._asic_nombres.append(a["nombre"])
        except Exception:
            pass

        lb_frame = tk.Frame(inner, bg="gray20")
        lb_frame.grid(row=2, column=1, columnspan=3, sticky="w", padx=8, pady=4)

        self._lb_asic = tk.Listbox(
            lb_frame,
            selectmode=tk.MULTIPLE,
            height=min(max(len(self._asic_nombres), 4), 8),
            width=40,
            font=("Arial", 10),
            bg="gray25", fg="white",
            selectbackground="#613BE3",
            selectforeground="white",
            relief="flat", borderwidth=0,
            activestyle="none",
        )
        sb_asic = ttk.Scrollbar(lb_frame, orient="vertical", command=self._lb_asic.yview)
        self._lb_asic.configure(yscrollcommand=sb_asic.set)
        for nombre in self._asic_nombres:
            self._lb_asic.insert(tk.END, nombre)
        self._lb_asic.pack(side="left")
        sb_asic.pack(side="left", fill="y")

        label(inner, "(sin selección = todos)", font_size=9, text_color="gray60").grid(
            row=3, column=1, columnspan=3, sticky="w", padx=8
        )

        label(inner, "Título del informe:", font_size=10).grid(row=4, column=0, sticky="w", pady=4)
        self._entry_titulo = entry(inner, width=440)
        self._entry_titulo.insert(0, "Informe Consolidado de Actividades")
        self._entry_titulo.grid(row=4, column=1, columnspan=3, sticky="w", padx=8)

        btn_secondary(inner, "▶  Generar Vista Previa", self._iniciar_previo).grid(row=5, column=0, columnspan=4, sticky="w", pady=(14, 0))

    def _leer_asics_seleccionados(self):
        """Retorna None (todos los ASIC) o una lista de IDs seleccionados."""
        seleccion = self._lb_asic.curselection()
        if not seleccion:
            return None
        ids = []
        for idx in seleccion:
            nombre = self._asic_nombres[idx]
            id_asic = self._asic_map.get(nombre)
            if id_asic is not None:
                ids.append(id_asic)
        return ids if ids else None

    def _date_widget(self, parent):
        if _TIENE_CALENDAR:
            return DateEntry(parent, date_pattern="yyyy-mm-dd",
                             background="gray25", foreground="white",
                             headersbackground="gray15",
                             headersforeground="white",
                             selectbackground="#613BE3", font=("Arial", 10),
                             width=14)
        else:
            w = entry(parent, width=140)
            w.insert(0, date.today().strftime("%Y-%m-%d"))
            return w

    def _leer_fecha(self, widget) -> date | None:
        try:
            return widget.get_date() if _TIENE_CALENDAR else \
                   datetime.strptime(widget.get().strip(), "%Y-%m-%d").date()
        except Exception:
            return None

    def _iniciar_previo(self):
        if self.usuario is None:
            messagebox.showwarning("Sesión no activa", "Debes iniciar sesión antes de generar reportes.")
            return

        f_ini = self._leer_fecha(self._entry_f_ini)
        f_fin = self._leer_fecha(self._entry_f_fin)

        if not f_ini or not f_fin:
            messagebox.showerror("Fecha inválida", "Por favor ingresa ambas fechas válidas (YYYY-MM-DD).")
            return

        if f_fin < f_ini:
            messagebox.showerror("Rango inválido", "La fecha de fin no puede ser anterior a la fecha de inicio.")
            return

        titulo  = self._entry_titulo.get().strip() or "Informe Consolidado"
        id_asic = self._leer_asics_seleccionados()

        self.parent.configure(cursor="wait")

        def _tarea():
            try:
                svc = ConsolidacionService(self.usuario["id_usuario"])
                previo = svc.generar_previo(f_ini, f_fin, id_asic)
                previo["titulo"] = titulo
                previo["observaciones"] = ""
                self.parent.after(0, lambda p=previo: self._mostrar_paso2(p))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: self._error(e))

        threading.Thread(target=_tarea, daemon=True).start()

    def _mostrar_paso2(self, previo: dict):
        self.parent.configure(cursor="")
        self._previo = previo
        self._limpiar(self._frame_generar)

        actividades  = previo["actividades"]
        resumen_asic = previo["resumen_por_asic"]
        resumen_tipo = previo["resumen_por_tipo"]
        total_act    = previo["total_actividades"]
        total_part   = previo["total_participantes"]

        # Botones de acción fijos al final (fuera del scroll)
        card_act = frame_surface(self._frame_generar, fg_color="gray20", corner_radius=10)
        card_act.pack(fill="x", padx=15, pady=(8, 15), side="bottom")

        inner_act = frame_transparent(card_act)
        inner_act.pack(fill="x", padx=20, pady=14)

        btn_secondary(inner_act, "← Volver", self._mostrar_paso1).pack(side="left", padx=(0, 10))

        if total_act > 0:
            btn_success(inner_act, "📄  Exportar Word", self._exportar_word).pack(side="left")

        # Área de contenido con scroll
        scroll = ctk.CTkScrollableFrame(self._frame_generar, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(6, 0))

        # Header con chips
        card_top = frame_surface(scroll, fg_color="gray20", corner_radius=10)
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

        if total_act == 0:
            label(scroll, "⚠  No hay actividades para el período y filtros seleccionados.", font_size=11, text_color="#c45050").pack(pady=20)
        else:
            fila_resumenes = frame_transparent(scroll)
            fila_resumenes.pack(fill="x", pady=(0, 10))
            self._mini_tabla(fila_resumenes, "Por ASIC", resumen_asic, ["ASIC", "Actividades", "Participantes"])
            self._mini_tabla(fila_resumenes, "Por Tipo", resumen_tipo, ["Tipo de Actividad", "Actividades", "Participantes"])

        # Tabla de Vocerías CS
        vocerias = previo.get("vocerias", [])
        if vocerias:
            self._mini_tabla_vocerias(scroll, vocerias)
        elif total_act == 0:
            label(scroll, "⚠  No hay vocerías CS para el período y filtros seleccionados.", font_size=11, text_color="#c45050").pack(pady=10)

    def _mini_tabla(self, parent: ctk.CTkFrame, titulo: str, filas: list, cabeceras: list):
        marco = frame_surface(parent, fg_color="gray20", corner_radius=10)
        marco.pack(side="left", fill="both", expand=True, padx=(0, 8))

        inner = frame_transparent(marco)
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        label(inner, titulo, font_size=10, bold=True).pack(anchor="w", pady=(0, 5))

        cols = tuple(range(len(cabeceras)))
        treeview_style("R", 22)

        tree = ttk.Treeview(inner, columns=cols, show="headings", style="R.Treeview", height=min(len(filas), 7))
        for i, cab in enumerate(cabeceras):
            tree.heading(i, text=cab)
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
        """Deselecciona fila si se hace clic en área vacía de la tabla."""
        tree = event.widget
        item = tree.identify_row(event.y)
        if not item:
            tree.selection_remove(tree.selection())

    def _mini_tabla_vocerias(self, parent: ctk.CTkFrame, vocerias: list):
        marco = frame_surface(parent, fg_color="gray20", corner_radius=10)
        marco.pack(fill="x", pady=(10, 0))

        inner = frame_transparent(marco)
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        label(inner, "Vocerías CS", font_size=10, bold=True).pack(anchor="w", pady=(0, 5))

        cabeceras = ["Fecha", "ASIC", "Cantidad Vocerías", "Municipio", "Parroquia"]
        cols = tuple(range(len(cabeceras)))
        treeview_style("R", 22)

        tree = ttk.Treeview(inner, columns=cols, show="headings", style="R.Treeview", height=min(len(vocerias), 8))
        for i, cab in enumerate(cabeceras):
            tree.heading(i, text=cab)
        tree.column(0, width=100, anchor="w")
        tree.column(1, width=180, anchor="w")
        tree.column(2, width=120, anchor="w")
        tree.column(3, width=120, anchor="w")
        tree.column(4, width=120, anchor="w")

        for voc in vocerias:
            f = voc.get("fecha", "")
            if hasattr(f, "strftime"):
                f = f.strftime("%d/%m/%Y")
            cantidad = voc.get("cantidad_vocerias", 0)
            tree.insert("", "end", values=(
                f,
                voc.get("asic_nombre", ""),
                cantidad,
                voc.get("municipio", ""),
                voc.get("parroquia", ""),
            ))

        sy = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        tree.bind("<Button-1>", self._on_tabla_click, add="+")

    def _exportar_word(self):
        if not self._previo:
            return
        titulo = self._previo.get("titulo", "informe")
        nombre_sugerido = f"{titulo.replace(' ', '_')[:40]}_{date.today()}.docx"
        ruta = filedialog.asksaveasfilename(title="Guardar Word como…", defaultextension=".docx", initialfile=nombre_sugerido, filetypes=[("Word", "*.docx")])
        if not ruta:
            return
        self.parent.configure(cursor="wait")

        def _tarea():
            try:
                PDFService().generar_word(self._previo, ruta)
                self.parent.after(0, lambda: (self.parent.configure(cursor=""), messagebox.showinfo("Word generado", f"Documento Word guardado en:\n{ruta}")))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: (self.parent.configure(cursor=""), messagebox.showerror("Error al generar Word", str(e))))

        threading.Thread(target=_tarea, daemon=True).start()

    def _limpiar(self, frame: ctk.CTkFrame):
        for w in frame.winfo_children():
            w.destroy()

    def _chip(self, parent: ctk.CTkFrame, texto: str, color: str):
        chip = ctk.CTkFrame(parent, fg_color=color, corner_radius=6)
        chip.pack(side="left", padx=(0, 8))
        label(chip, texto, font_size=9, bold=True).pack(padx=10, pady=4)

    def _error(self, exc: Exception):
        self.parent.configure(cursor="")
        messagebox.showerror("Error", str(exc))