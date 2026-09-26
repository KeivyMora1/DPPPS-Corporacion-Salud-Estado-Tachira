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
    entry, combobox, textbox
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
            "Genera informes consolidados por período, exporta el documento en Word "
            "y consulta el historial de informes previos.",
            wraplength=900, justify="left"
        ).pack(anchor="w", padx=30, pady=(0, 14))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Rep.TNotebook",     background="gray15", borderwidth=0)
        style.configure("Rep.TNotebook.Tab", background="gray20",
                        foreground="gray70", padding=[14, 6], font=("Arial", 10))
        style.map("Rep.TNotebook.Tab",
                  background=[("selected", "gray25")],
                  foreground=[("selected", "white")])

        nb = ttk.Notebook(self.parent, style="Rep.TNotebook")
        nb.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._tab_generar = frame(nb, fg_color="gray15")
        nb.add(self._tab_generar, text="  ✨ Generar Informe  ")
        self._construir_tab_generar()

        self._tab_historial = frame(nb, fg_color="gray15")
        nb.add(self._tab_historial, text="  📁 Historial  ")
        nb.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_change(nb))
        self._construir_tab_historial()

    def _on_tab_change(self, nb):
        if nb.index("current") == 1:
            self._cargar_historial()

    def _construir_tab_generar(self):
        self._frame_generar = frame_transparent(self._tab_generar)
        self._frame_generar.pack(fill="both", expand=True)
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

        label(inner, "ASIC (opcional):", font_size=10).grid(row=2, column=0, sticky="w", pady=4)

        self._asic_var = tk.StringVar(value="Todos los ASIC")
        self._asic_map: dict = {"Todos los ASIC": None}
        try:
            for a in AsicDAO().obtener_todos():
                self._asic_map[a["nombre"]] = a["id_asic"]
        except Exception:
            pass

        cb_asic = ttk.Combobox(inner, textvariable=self._asic_var,
                               values=list(self._asic_map.keys()),
                               state="readonly", width=35, font=("Arial", 10))
        cb_asic.grid(row=2, column=1, columnspan=3, sticky="w", padx=8)

        label(inner, "Título del informe:", font_size=10).grid(row=3, column=0, sticky="w", pady=4)
        self._entry_titulo = entry(inner, width=440)
        self._entry_titulo.insert(0, "Informe Consolidado de Actividades")
        self._entry_titulo.grid(row=3, column=1, columnspan=3, sticky="w", padx=8)

        label(inner, "Observaciones:", font_size=10).grid(row=4, column=0, sticky="nw", pady=4)
        self._txt_obs = textbox(inner, height=60, width=440)
        self._txt_obs.grid(row=4, column=1, columnspan=3, sticky="w", padx=8, pady=4)

        btn_secondary(inner, "▶  Generar Vista Previa", self._iniciar_previo).grid(row=5, column=0, columnspan=4, sticky="w", pady=(14, 0))

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
        obs     = self._txt_obs.get("1.0", "end").strip()
        id_asic = self._asic_map.get(self._asic_var.get())

        self.parent.configure(cursor="wait")

        def _tarea():
            try:
                svc = ConsolidacionService(self.usuario["id_usuario"])
                previo = svc.generar_previo(f_ini, f_fin, id_asic)
                previo["titulo"] = titulo
                previo["observaciones"] = obs
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
            btn_primary(inner_act, "💾  Guardar informe en BD", self._guardar_informe).pack(side="left", padx=(0, 10))
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

    def _guardar_informe(self):
        if self.usuario is None:
            messagebox.showwarning("Sesión no activa", "Debes iniciar sesión antes de guardar reportes.")
            return
        if not self._previo:
            return
        titulo = self._previo.get("titulo", "Informe Consolidado")
        try:
            svc   = ConsolidacionService(self.usuario["id_usuario"])
            f_ini = self._previo["fecha_inicio"]
            f_fin = self._previo["fecha_fin"]
            id_periodo = svc.crear_periodo(
                tipo="mensual", anio=f_ini.year,
                mes_inicio=f_ini.month, mes_fin=f_fin.month,
                fecha_inicio=f_ini, fecha_fin=f_fin,
            )
            id_informe = svc.guardar(self._previo, id_periodo, titulo, self._previo.get("observaciones", ""))
            self._id_informe_guardado = id_informe
            messagebox.showinfo("Informe guardado", f"El informe se guardó correctamente (ID #{id_informe}).")
        except Exception as exc:
            messagebox.showerror("Error al guardar", str(exc))

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

    def _construir_tab_historial(self):
        barra = frame_transparent(self._tab_historial)
        barra.pack(fill="x", padx=10, pady=(10, 6))

        btn_secondary(barra, "🔄  Actualizar", self._cargar_historial).pack(side="left", padx=(0, 8))
        btn_success(barra, "📄  Exportar Word", self._exportar_word_historial).pack(side="left", padx=(0, 8))
        btn_danger(barra, "🗑  Eliminar", self._eliminar_historial).pack(side="left")

        cols  = ("id", "titulo", "periodo", "asic", "actividades", "participantes", "generado")
        labs  = ("#", "Título", "Período", "ASIC", "Actividades", "Participantes", "Generado")
        anchs = (50, 240, 130, 150, 90, 100, 130)

        treeview_style("Hist", 24)

        cont = frame_transparent(self._tab_historial)
        cont.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._tree_hist = ttk.Treeview(cont, columns=cols, show="headings", style="Hist.Treeview")
        for col, lab, ancho in zip(cols, labs, anchs):
            self._tree_hist.heading(col, text=lab)
            self._tree_hist.column(col, width=ancho, minwidth=40, anchor="center" if col != "titulo" else "w")

        sy = ttk.Scrollbar(cont, orient="vertical",   command=self._tree_hist.yview)
        sx = ttk.Scrollbar(cont, orient="horizontal", command=self._tree_hist.xview)
        self._tree_hist.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right",  fill="y")
        sx.pack(side="bottom", fill="x")
        self._tree_hist.pack(fill="both", expand=True)

        self._cargar_historial()

    def _cargar_historial(self):
        if self.usuario is None:
            if hasattr(self, "_tree_hist"):
                for row in self._tree_hist.get_children():
                    self._tree_hist.delete(row)
            messagebox.showwarning("Sesión no activa", "Debes iniciar sesión antes de consultar el historial.")
            return

        for row in self._tree_hist.get_children():
            self._tree_hist.delete(row)
        try:
            svc = ConsolidacionService(self.usuario["id_usuario"])
            informes = svc.listar_informes()
            for inf in informes:
                periodo_txt = f"{inf.get('periodo_tipo','').capitalize()} {inf.get('periodo_anio','')}"
                asic_txt = inf.get("asic_nombre") or "General"
                gen_txt  = str(inf.get("fecha_generacion", ""))[:16]
                self._tree_hist.insert("", "end", iid=str(inf["id_informe"]), values=(
                    inf["id_informe"], inf["titulo"], periodo_txt,
                    asic_txt, inf["total_actividades"], inf["total_participantes"], gen_txt,
                ))
        except Exception as exc:
            messagebox.showerror("Error al cargar historial", str(exc))

    def _informe_seleccionado(self) -> int | None:
        sel = self._tree_hist.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un informe de la lista.")
            return None
        return int(sel[0])

    def _exportar_word_historial(self):
        if self.usuario is None:
            messagebox.showwarning("Sesión no activa", "Debes iniciar sesión antes de exportar reportes.")
            return
        id_inf = self._informe_seleccionado()
        if not id_inf:
            return
        nombre = f"informe_{id_inf}_{date.today()}.docx"
        ruta = filedialog.asksaveasfilename(title="Guardar Word como…", defaultextension=".docx", initialfile=nombre, filetypes=[("Word", "*.docx")])
        if not ruta:
            return
        self.parent.configure(cursor="wait")

        def _tarea():
            try:
                svc = ConsolidacionService(self.usuario["id_usuario"])
                datos = svc.obtener_informe_completo(id_inf)
                PDFService().generar_word(datos, ruta)
                self.parent.after(0, lambda: (self.parent.configure(cursor=""), messagebox.showinfo("Word generado", f"Documento Word guardado en:\n{ruta}")))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: (self.parent.configure(cursor=""), messagebox.showerror("Error", str(e))))

        threading.Thread(target=_tarea, daemon=True).start()

    def _eliminar_historial(self):
        if self.usuario is None:
            messagebox.showwarning("Sesión no activa", "Debes iniciar sesión antes de eliminar reportes.")
            return
        id_inf = self._informe_seleccionado()
        if not id_inf:
            return
        if messagebox.askyesno("Confirmar eliminación", f"¿Eliminar el informe #{id_inf}?\nEsta acción no se puede deshacer."):
            try:
                ConsolidacionService(self.usuario["id_usuario"]).eliminar_informe(id_inf)
                self._cargar_historial()
                messagebox.showinfo("Eliminado", f"Informe #{id_inf} eliminado.")
            except Exception as exc:
                messagebox.showerror("Error al eliminar", str(exc))

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