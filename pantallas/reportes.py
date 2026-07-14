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
from themes import THEMES

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

    def __init__(self, parent: tk.Frame, theme="dark"):
        self.parent  = parent
        self.auth    = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()
        self.t       = THEMES[theme]

        self._previo:              dict | None = None
        self._id_informe_guardado: int  | None = None

        self._construir_ui()

    def _construir_ui(self):
        t = self.t

        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 4))

        ctk.CTkLabel(header, text="📊  Reportes y Consolidación",
                     font=("Arial", 17, "bold"), text_color=t["text_primary"]
                     ).pack(side="left")

        ctk.CTkLabel(self.parent,
                     text="Genera informes consolidados por período, exporta en PDF o Excel "
                          "y consulta el historial de informes previos.",
                     font=("Arial", 10), text_color=t["text_muted"],
                     wraplength=900, justify="left"
                     ).pack(anchor="w", padx=30, pady=(0, 14))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Rep.TNotebook",     background=t["bg_base"], borderwidth=0)
        style.configure("Rep.TNotebook.Tab", background=t["bg_surface"],
                        foreground=t["text_muted"],
                        padding=[14, 6], font=("Arial", 10))
        style.map("Rep.TNotebook.Tab",
                  background=[("selected", t["bg_card"])],
                  foreground=[("selected", t["text_primary"])])

        nb = ttk.Notebook(self.parent, style="Rep.TNotebook")
        nb.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._tab_generar = ctk.CTkFrame(nb, fg_color=t["bg_base"])
        nb.add(self._tab_generar, text="  ✨ Generar Informe  ")
        self._construir_tab_generar()

        self._tab_historial = ctk.CTkFrame(nb, fg_color=t["bg_base"])
        nb.add(self._tab_historial, text="  📁 Historial  ")
        nb.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_change(nb))
        self._construir_tab_historial()

    def _on_tab_change(self, nb):
        if nb.index("current") == 1:
            self._cargar_historial()

    def _construir_tab_generar(self):
        t = self.t
        self._frame_generar = ctk.CTkFrame(self._tab_generar, fg_color="transparent")
        self._frame_generar.pack(fill="both", expand=True)
        self._mostrar_paso1()

    def _mostrar_paso1(self):
        t = self.t
        self._limpiar(self._frame_generar)
        self._previo              = None
        self._id_informe_guardado = None

        card = ctk.CTkFrame(self._frame_generar, fg_color=t["bg_surface"],
                            corner_radius=10)
        card.pack(fill="x", padx=15, pady=(8, 0))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(inner, text="Paso 1 de 3 — Configurar parámetros del informe",
                     font=("Arial", 12, "bold"), text_color=t["text_primary"]
                     ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 14))

        ctk.CTkLabel(inner, text="Fecha inicio:", font=("Arial", 10),
                     text_color=t["text_muted"]
                     ).grid(row=1, column=0, sticky="w", pady=4)
        self._entry_f_ini = self._date_widget(inner)
        self._entry_f_ini.grid(row=1, column=1, sticky="w", padx=(8, 30))

        ctk.CTkLabel(inner, text="Fecha fin:", font=("Arial", 10),
                     text_color=t["text_muted"]
                     ).grid(row=1, column=2, sticky="w", pady=4)
        self._entry_f_fin = self._date_widget(inner)
        self._entry_f_fin.grid(row=1, column=3, sticky="w", padx=8)

        ctk.CTkLabel(inner, text="ASIC (opcional):", font=("Arial", 10),
                     text_color=t["text_muted"]
                     ).grid(row=2, column=0, sticky="w", pady=4)

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

        ctk.CTkLabel(inner, text="Título del informe:", font=("Arial", 10),
                     text_color=t["text_muted"]
                     ).grid(row=3, column=0, sticky="w", pady=4)
        self._entry_titulo = ctk.CTkEntry(inner, font=("Arial", 10), width=440,
                                          fg_color=t["bg_base"],
                                          text_color=t["text_primary"],
                                          border_color=t["bg_card"],
                                          corner_radius=6)
        self._entry_titulo.insert(0, "Informe Consolidado de Actividades")
        self._entry_titulo.grid(row=3, column=1, columnspan=3, sticky="w", padx=8)

        ctk.CTkLabel(inner, text="Observaciones:", font=("Arial", 10),
                     text_color=t["text_muted"]
                     ).grid(row=4, column=0, sticky="nw", pady=4)
        self._txt_obs = ctk.CTkTextbox(inner, font=("Arial", 10), width=440,
                                       height=60, fg_color=t["bg_base"],
                                       text_color=t["text_primary"],
                                       corner_radius=6, border_width=1,
                                       border_color=t["bg_card"])
        self._txt_obs.grid(row=4, column=1, columnspan=3, sticky="w", padx=8, pady=4)

        ctk.CTkButton(inner, text="▶  Generar Vista Previa",
                      font=("Arial", 10, "bold"), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], text_color=t["text_primary"],
                      corner_radius=8, command=self._iniciar_previo
                      ).grid(row=5, column=0, columnspan=4, sticky="w", pady=(14, 0))

    def _date_widget(self, parent):
        t = self.t
        if _TIENE_CALENDAR:
            return DateEntry(parent, date_pattern="yyyy-mm-dd",
                             background=t["bg_card"], foreground=t["text_primary"],
                             headersbackground=t["bg_base"],
                             headersforeground=t["text_primary"],
                             selectbackground=t["accent"], font=("Arial", 10),
                             width=14)
        else:
            w = ctk.CTkEntry(parent, font=("Arial", 10), width=140,
                             fg_color=t["bg_base"], text_color=t["text_primary"],
                             border_color=t["bg_card"], corner_radius=6)
            w.insert(0, date.today().strftime("%Y-%m-%d"))
            return w

    def _leer_fecha(self, widget) -> date | None:
        try:
            return widget.get_date() if _TIENE_CALENDAR else \
                   datetime.strptime(widget.get().strip(), "%Y-%m-%d").date()
        except Exception:
            return None

    def _iniciar_previo(self):
        f_ini = self._leer_fecha(self._entry_f_ini)
        f_fin = self._leer_fecha(self._entry_f_fin)

        if not f_ini or not f_fin:
            messagebox.showerror("Fechas inválidas",
                                 "Por favor ingresa fechas válidas (YYYY-MM-DD).")
            return
        if f_ini > f_fin:
            messagebox.showerror("Fechas inválidas",
                                 "La fecha de inicio no puede ser posterior a la de fin.")
            return

        titulo  = self._entry_titulo.get().strip() or "Informe Consolidado"
        obs     = self._txt_obs.get("1.0", "end").strip()
        id_asic = self._asic_map.get(self._asic_var.get())

        self.parent.config(cursor="wait")

        def _tarea():
            try:
                svc   = ConsolidacionService(self.usuario["id_usuario"])
                previo = svc.generar_previo(f_ini, f_fin, id_asic)
                previo["titulo"]        = titulo
                previo["observaciones"] = obs
                self.parent.after(0, lambda p=previo: self._mostrar_paso2(p))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: self._error(e))

        threading.Thread(target=_tarea, daemon=True).start()

    def _mostrar_paso2(self, previo: dict):
        t = self.t
        self.parent.config(cursor="")
        self._previo = previo
        self._limpiar(self._frame_generar)

        actividades  = previo["actividades"]
        resumen_asic = previo["resumen_por_asic"]
        resumen_tipo = previo["resumen_por_tipo"]
        total_act    = previo["total_actividades"]
        total_part   = previo["total_participantes"]

        card_top = ctk.CTkFrame(self._frame_generar, fg_color=t["bg_surface"],
                                corner_radius=10)
        card_top.pack(fill="x", padx=15, pady=(6, 0))

        inner_top = ctk.CTkFrame(card_top, fg_color="transparent")
        inner_top.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(inner_top, text="Paso 2 de 3 — Vista previa del informe",
                     font=("Arial", 12, "bold"), text_color=t["text_primary"]
                     ).pack(anchor="w", pady=(0, 8))

        chips = ctk.CTkFrame(inner_top, fg_color="transparent")
        chips.pack(anchor="w")
        self._chip(chips, f"📋 Actividades: {total_act}",    t["bg_card"])
        self._chip(chips, f"👥 Participantes: {total_part}",  t["accent"])
        self._chip(chips, f"📅 {previo['fecha_inicio']} → {previo['fecha_fin']}",
                   t["success_dim"])
        if previo.get("asic_nombre"):
            self._chip(chips, f"🏥 {previo['asic_nombre']}", t["red_bg"])

        if total_act == 0:
            ctk.CTkLabel(self._frame_generar,
                         text="⚠  No hay actividades para el período y filtros seleccionados.",
                         font=("Arial", 11), text_color=t["red"]
                         ).pack(pady=20)
        else:
            fila_resumenes = ctk.CTkFrame(self._frame_generar, fg_color="transparent")
            fila_resumenes.pack(fill="x", padx=15, pady=(10, 0))
            self._mini_tabla(fila_resumenes, "Por ASIC", resumen_asic,
                             ["ASIC", "Actividades", "Participantes"])
            self._mini_tabla(fila_resumenes, "Por Tipo", resumen_tipo,
                             ["Tipo de Actividad", "Actividades", "Participantes"])
            self._tabla_detalle_tk(previo)

        card_act = ctk.CTkFrame(self._frame_generar, fg_color=t["bg_surface"],
                                corner_radius=10)
        card_act.pack(fill="x", padx=15, pady=(8, 0))

        inner_act = ctk.CTkFrame(card_act, fg_color="transparent")
        inner_act.pack(fill="x", padx=20, pady=14)

        ctk.CTkButton(inner_act, text="← Volver",
                      font=("Arial", 10), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], text_color=t["text_primary"],
                      corner_radius=8, command=self._mostrar_paso1
                      ).pack(side="left", padx=(0, 10))

        if total_act > 0:
            ctk.CTkButton(inner_act, text="💾  Guardar informe en BD",
                          font=("Arial", 10), fg_color=t["accent"],
                          hover_color=t["accent_dim"], text_color=t["text_primary"],
                          corner_radius=8, command=self._guardar_informe
                          ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(inner_act, text="📄  Exportar PDF",
                          font=("Arial", 10, "bold"), fg_color=t["red"],
                          hover_color="#a83e3e", text_color=t["text_primary"],
                          corner_radius=8, command=self._exportar_pdf
                          ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(inner_act, text="📊  Exportar Excel",
                          font=("Arial", 10), fg_color=t["success"],
                          hover_color=t["success_dim"], text_color=t["text_primary"],
                          corner_radius=8, command=self._exportar_excel
                          ).pack(side="left")

    def _mini_tabla(self, parent: ctk.CTkFrame, titulo: str, filas: list,
                    cabeceras: list):
        t = self.t
        marco = ctk.CTkFrame(parent, fg_color=t["bg_surface"], corner_radius=10)
        marco.pack(side="left", fill="both", expand=True, padx=(0, 8))

        inner = ctk.CTkFrame(marco, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        ctk.CTkLabel(inner, text=titulo, font=("Arial", 10, "bold"),
                     text_color=t["text_primary"]).pack(anchor="w", pady=(0, 5))

        cols  = tuple(range(len(cabeceras)))
        style = ttk.Style()
        style.configure("R.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=22)
        style.configure("R.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        relief="flat")
        style.map("R.Treeview", background=[("selected", t["bg_card"])])

        tree = ttk.Treeview(inner, columns=cols, show="headings",
                            style="R.Treeview", height=min(len(filas), 7))
        for i, cab in enumerate(cabeceras):
            tree.heading(i, text=cab)
            tree.column(i, width=(200 if i == 0 else 100),
                        anchor="center" if i > 0 else "w")

        for fila in filas:
            nombre = fila.get("nombre") or fila.get("asic_nombre", "")
            tree.insert("", "end", values=(nombre,
                                           fila["total_actividades"],
                                           fila["total_participantes"]))
        sy = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    def _tabla_detalle_tk(self, previo: dict):
        t = self.t
        marco = ctk.CTkFrame(self._frame_generar, fg_color=t["bg_surface"],
                             corner_radius=10)
        marco.pack(fill="both", expand=True, padx=15, pady=(8, 0))

        inner = ctk.CTkFrame(marco, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        ctk.CTkLabel(inner,
                     text=f"Detalle de actividades ({previo['total_actividades']})",
                     font=("Arial", 10, "bold"), text_color=t["text_primary"]
                     ).pack(anchor="w", pady=(0, 5))

        cols  = ("asic", "tipo", "fecha_inicio", "fecha_fin", "lugar", "participantes", "descripcion")
        labs  = ("ASIC", "Tipo", "Fecha Ini.", "Fecha Fin", "Lugar", "Partic.", "Descripción")
        anchs = (150, 140, 90, 90, 140, 70, 350)

        style = ttk.Style()
        style.configure("Det.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=22)
        style.configure("Det.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        relief="flat")

        cont = ctk.CTkFrame(inner, fg_color="transparent")
        cont.pack(fill="both", expand=True)

        tree = ttk.Treeview(cont, columns=cols, show="headings",
                            style="Det.Treeview", height=10)
        for col, lab, ancho in zip(cols, labs, anchs):
            tree.heading(col, text=lab)
            tree.column(col, width=ancho, minwidth=50, anchor="w")

        for act in previo["actividades"]:
            tree.insert("", "end", values=(
                act.get("asic_nombre",  ""),
                act.get("tipo_nombre",  ""),
                str(act.get("fecha_inicio", "")),
                str(act.get("fecha_fin",    "")),
                act.get("lugar", ""),
                act.get("participantes", 0),
                act.get("descripcion", "")[:80],
            ))

        sy = ttk.Scrollbar(cont, orient="vertical",   command=tree.yview)
        sx = ttk.Scrollbar(cont, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right",  fill="y")
        sx.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

    def _guardar_informe(self):
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
            id_informe = svc.guardar(
                self._previo, id_periodo, titulo,
                self._previo.get("observaciones", "")
            )
            self._id_informe_guardado = id_informe
            messagebox.showinfo("Informe guardado",
                                f"El informe se guardó correctamente (ID #{id_informe}).")
        except Exception as exc:
            messagebox.showerror("Error al guardar", str(exc))

    def _exportar_pdf(self):
        if not self._previo:
            return
        titulo          = self._previo.get("titulo", "informe")
        nombre_sugerido = f"{titulo.replace(' ', '_')[:40]}_{date.today()}.pdf"
        ruta = filedialog.asksaveasfilename(
            title="Guardar PDF como…", defaultextension=".pdf",
            initialfile=nombre_sugerido, filetypes=[("PDF", "*.pdf")]
        )
        if not ruta:
            return
        self.parent.config(cursor="wait")

        def _tarea():
            try:
                PDFService().generar_pdf(self._previo, ruta)
                self.parent.after(0, lambda: (
                    self.parent.config(cursor=""),
                    messagebox.showinfo("PDF generado", f"PDF guardado en:\n{ruta}")
                ))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: (
                    self.parent.config(cursor=""),
                    messagebox.showerror("Error al generar PDF", str(e))
                ))
        threading.Thread(target=_tarea, daemon=True).start()

    def _exportar_excel(self):
        if not self._previo:
            return
        titulo          = self._previo.get("titulo", "informe")
        nombre_sugerido = f"{titulo.replace(' ', '_')[:40]}_{date.today()}.xlsx"
        ruta = filedialog.asksaveasfilename(
            title="Guardar Excel como…", defaultextension=".xlsx",
            initialfile=nombre_sugerido, filetypes=[("Excel", "*.xlsx")]
        )
        if not ruta:
            return
        self.parent.config(cursor="wait")

        def _tarea():
            try:
                PDFService().generar_excel(self._previo, ruta)
                self.parent.after(0, lambda: (
                    self.parent.config(cursor=""),
                    messagebox.showinfo("Excel generado", f"Excel guardado en:\n{ruta}")
                ))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: (
                    self.parent.config(cursor=""),
                    messagebox.showerror("Error al generar Excel", str(e))
                ))
        threading.Thread(target=_tarea, daemon=True).start()

    def _construir_tab_historial(self):
        t = self.t
        barra = ctk.CTkFrame(self._tab_historial, fg_color="transparent")
        barra.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkButton(barra, text="🔄  Actualizar",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], text_color=t["text_primary"],
                      corner_radius=8, command=self._cargar_historial
                      ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(barra, text="📄  Exportar PDF",
                      font=("Arial", 9), fg_color=t["red"],
                      hover_color="#a83e3e", text_color=t["text_primary"],
                      corner_radius=8, command=self._exportar_pdf_historial
                      ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(barra, text="📊  Exportar Excel",
                      font=("Arial", 9), fg_color=t["success"],
                      hover_color=t["success_dim"], text_color=t["text_primary"],
                      corner_radius=8, command=self._exportar_excel_historial
                      ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(barra, text="🗑  Eliminar",
                      font=("Arial", 9), fg_color=t["red_bg"],
                      hover_color=t["red"], text_color=t["red_fg"],
                      corner_radius=8, command=self._eliminar_historial
                      ).pack(side="left")

        cols  = ("id", "titulo", "periodo", "asic", "actividades", "participantes", "generado")
        labs  = ("#", "Título", "Período", "ASIC", "Actividades", "Participantes", "Generado")
        anchs = (50, 240, 130, 150, 90, 100, 130)

        style = ttk.Style()
        style.configure("Hist.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=24)
        style.configure("Hist.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        relief="flat")
        style.map("Hist.Treeview", background=[("selected", t["bg_card"])])

        cont = ctk.CTkFrame(self._tab_historial, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._tree_hist = ttk.Treeview(cont, columns=cols, show="headings",
                                       style="Hist.Treeview")
        for col, lab, ancho in zip(cols, labs, anchs):
            self._tree_hist.heading(col, text=lab)
            self._tree_hist.column(col, width=ancho, minwidth=40,
                                   anchor="center" if col != "titulo" else "w")

        sy = ttk.Scrollbar(cont, orient="vertical",   command=self._tree_hist.yview)
        sx = ttk.Scrollbar(cont, orient="horizontal", command=self._tree_hist.xview)
        self._tree_hist.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right",  fill="y")
        sx.pack(side="bottom", fill="x")
        self._tree_hist.pack(fill="both", expand=True)

        self._cargar_historial()

    def _cargar_historial(self):
        for row in self._tree_hist.get_children():
            self._tree_hist.delete(row)
        try:
            svc     = ConsolidacionService(self.usuario["id_usuario"])
            informes = svc.listar_informes()
            for inf in informes:
                periodo_txt = (f"{inf.get('periodo_tipo','').capitalize()} "
                               f"{inf.get('periodo_anio','')}")
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

    def _exportar_pdf_historial(self):
        id_inf = self._informe_seleccionado()
        if not id_inf:
            return
        nombre = f"informe_{id_inf}_{date.today()}.pdf"
        ruta = filedialog.asksaveasfilename(
            title="Guardar PDF como…", defaultextension=".pdf",
            initialfile=nombre, filetypes=[("PDF", "*.pdf")])
        if not ruta:
            return
        self.parent.config(cursor="wait")

        def _tarea():
            try:
                svc  = ConsolidacionService(self.usuario["id_usuario"])
                datos = svc.obtener_informe_completo(id_inf)
                PDFService().generar_pdf(datos, ruta)
                self.parent.after(0, lambda: (
                    self.parent.config(cursor=""),
                    messagebox.showinfo("PDF generado", f"PDF guardado en:\n{ruta}")
                ))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: (
                    self.parent.config(cursor=""),
                    messagebox.showerror("Error", str(e))
                ))
        threading.Thread(target=_tarea, daemon=True).start()

    def _exportar_excel_historial(self):
        id_inf = self._informe_seleccionado()
        if not id_inf:
            return
        nombre = f"informe_{id_inf}_{date.today()}.xlsx"
        ruta = filedialog.asksaveasfilename(
            title="Guardar Excel como…", defaultextension=".xlsx",
            initialfile=nombre, filetypes=[("Excel", "*.xlsx")])
        if not ruta:
            return
        self.parent.config(cursor="wait")

        def _tarea():
            try:
                svc   = ConsolidacionService(self.usuario["id_usuario"])
                datos = svc.obtener_informe_completo(id_inf)
                PDFService().generar_excel(datos, ruta)
                self.parent.after(0, lambda: (
                    self.parent.config(cursor=""),
                    messagebox.showinfo("Excel generado", f"Excel guardado en:\n{ruta}")
                ))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: (
                    self.parent.config(cursor=""),
                    messagebox.showerror("Error", str(e))
                ))
        threading.Thread(target=_tarea, daemon=True).start()

    def _eliminar_historial(self):
        id_inf = self._informe_seleccionado()
        if not id_inf:
            return
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Eliminar el informe #{id_inf}?\nEsta acción no se puede deshacer."):
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
        t = self.t
        chip = ctk.CTkFrame(parent, fg_color=color, corner_radius=6)
        chip.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(chip, text=texto, font=("Arial", 9, "bold"),
                     text_color=t["text_primary"]).pack(padx=10, pady=4)

    def _error(self, exc: Exception):
        self.parent.config(cursor="")
        messagebox.showerror("Error", str(exc))
