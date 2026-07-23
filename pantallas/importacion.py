# ============================================================
# pantallas/importacion.py
# Vista de importación masiva de actividades desde Excel.
#
# Flujo de 3 pasos:
#   Paso 1 — Seleccionar archivo Excel
#   Paso 2 — Previsualización (tabla de filas válidas + errores)
#   Paso 3 — Confirmación e inserción
# ============================================================

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

from db import AuthController, ExcelService, TEMPLATE_PATH
from themes import THEMES


class ImportacionView:
    """
    Sección de importación masiva desde Excel.
    Se monta como hijo del área de contenido de MainView.
    """

    def __init__(self, parent: tk.Frame, theme="dark"):
        self.parent  = parent
        self.auth    = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()
        self.t       = THEMES[theme]

        self._ruta_archivo:    str | None  = None
        self._resultado_previo: dict | None = None

        self._construir_ui()

    def _construir_ui(self):
        t = self.t

        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))

        ctk.CTkLabel(header, text="📥  Importación Masiva desde Excel",
                     font=("Arial", 17, "bold"), text_color=t["text_primary"],
                     ).pack(side="left")

        ctk.CTkButton(header, text="⬇  Descargar Plantilla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], text_color=t["text_primary"],
                      corner_radius=8, command=self._descargar_plantilla,
                      ).pack(side="right")

        ctk.CTkLabel(self.parent,
                     text="Importa actividades en bloque subiendo un archivo .xlsx con el formato de la plantilla.",
                     font=("Arial", 10), text_color=t["text_muted"],
                     ).pack(anchor="w", padx=30, pady=(0, 18))

        self._frame_pasos = ctk.CTkFrame(self.parent, fg_color="transparent")
        self._frame_pasos.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._mostrar_paso1()

    def _mostrar_paso1(self):
        t = self.t
        self._limpiar_pasos()
        self._ruta_archivo     = None
        self._resultado_previo = None

        card = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"],
                            corner_radius=10)
        card.pack(fill="x", padx=15)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=30)

        ctk.CTkLabel(inner, text="Paso 1 de 3 — Seleccionar archivo Excel",
                     font=("Arial", 12, "bold"), text_color=t["text_primary"],
                     ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(inner,
                     text="El archivo debe seguir la plantilla descargable y contener al menos FECHA, ASIC, ACTIVIDAD DESARROLLADA, TEMA TRATADO, LUGAR/UBICACIÓN y TOTAL DE ASISTENCIA.",
                     font=("Arial", 9), text_color=t["text_muted"],
                     wraplength=700, justify="left",
                     ).pack(anchor="w", pady=(0, 20))

        self._lbl_ruta = ctk.CTkLabel(inner, text="Ningún archivo seleccionado",
                                      font=("Arial", 10, "italic"),
                                      text_color=t["text_muted"])
        self._lbl_ruta.pack(anchor="w", pady=(0, 15))

        fila_botones = ctk.CTkFrame(inner, fg_color="transparent")
        fila_botones.pack(anchor="w")

        ctk.CTkButton(fila_botones, text="📂  Examinar…",
                      font=("Arial", 10), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], text_color=t["text_primary"],
                      corner_radius=8, command=self._seleccionar_archivo,
                      ).pack(side="left", padx=(0, 12))

        self._btn_previsualizar = ctk.CTkButton(
            fila_botones, text="▶  Previsualizar",
            font=("Arial", 10, "bold"), fg_color=t["bg_hover"],
            hover_color=t["bg_hover"], text_color=t["text_dim"],
            text_color_disabled=t["text_dim"], corner_radius=8,
            state="disabled", command=self._iniciar_previo,
        )
        self._btn_previsualizar.pack(side="left")

    def _seleccionar_archivo(self):
        t = self.t
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self._ruta_archivo = ruta
            nombre = os.path.basename(ruta)
            self._lbl_ruta.configure(text=f"📄 {nombre}  ({ruta})",
                                     text_color=t["text_primary"])
            self._btn_previsualizar.configure(
                state="normal", fg_color=t["accent"],
                hover_color=t["accent_dim"], text_color=t["text_primary"],
            )

    def _iniciar_previo(self):
        self._btn_previsualizar.configure(state="disabled", text="Procesando…")
        self.parent.configure(cursor="wait")

        def _tarea():
            try:
                svc      = ExcelService(id_usuario_registro=self.usuario["id_usuario"])
                resultado = svc.previsualizar(self._ruta_archivo)
                self.parent.after(0, lambda: self._mostrar_paso2(resultado))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: self._error_previo(e))

        threading.Thread(target=_tarea, daemon=True).start()

    def _error_previo(self, exc: Exception):
        self.parent.configure(cursor="")
        messagebox.showerror("Error al leer el archivo",
                             f"No se pudo procesar el archivo:\n\n{exc}")
        self._btn_previsualizar.configure(state="normal", text="▶  Previsualizar",
                                          fg_color=self.t["bg_hover"],
                                          text_color=self.t["text_dim"])

    def _mostrar_paso2(self, resultado: dict):
        t = self.t
        self.parent.configure(cursor="")
        self._resultado_previo = resultado
        self._limpiar_pasos()

        validas = resultado["filas_validas"]
        errores = resultado["filas_error"]
        total   = resultado["total_filas"]

        card_resumen = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"],
                                    corner_radius=10)
        card_resumen.pack(fill="x", pady=(0, 12), padx=15)

        inner = ctk.CTkFrame(card_resumen, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(inner, text="Paso 2 de 3 — Resultado del análisis",
                     font=("Arial", 12, "bold"), text_color=t["text_primary"],
                     ).pack(anchor="w", pady=(0, 10))

        fila_resumen = ctk.CTkFrame(inner, fg_color="transparent")
        fila_resumen.pack(anchor="w")

        self._chip(fila_resumen, f"📄 Total filas: {total}",         t["bg_card"])
        self._chip(fila_resumen, f"✅ Válidas: {len(validas)}",      t["success"])
        self._chip(fila_resumen, f"❌ Con errores: {len(errores)}",
                   t["red"] if errores else t["bg_hover"])

        if validas:
            self._seccion_tabla("Filas listas para importar",
                                t["success"], validas, "validas")
        if errores:
            self._seccion_tabla("Filas con errores (no se importarán)",
                                t["red"], errores, "errores")

        card_acciones = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"],
                                     corner_radius=10)
        card_acciones.pack(fill="x", padx=15, pady=(8, 0))

        inner_acc = ctk.CTkFrame(card_acciones, fg_color="transparent")
        inner_acc.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(inner_acc, text="← Seleccionar otro archivo",
                      font=("Arial", 10), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], text_color=t["text_primary"],
                      corner_radius=8, command=self._mostrar_paso1,
                      ).pack(side="left", padx=(0, 10))

        if validas:
            ctk.CTkButton(inner_acc,
                          text=f"✔  Importar {len(validas)} actividades",
                          font=("Arial", 10, "bold"), fg_color=t["success"],
                          hover_color=t["success_dim"],
                          text_color=t["text_primary"], corner_radius=8,
                          command=self._confirmar_importar,
                          ).pack(side="left")
        else:
            ctk.CTkLabel(inner_acc,
                         text="No hay filas válidas para importar. Corrige el archivo y vuelve a intentarlo.",
                         font=("Arial", 9, "italic"), text_color=t["red"],
                         ).pack(side="left")

    def _seccion_tabla(self, titulo: str, color_titulo: str, filas: list, modo: str):
        t = self.t
        marco = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"],
                             corner_radius=10)
        marco.pack(fill="both", expand=(modo == "validas"), pady=(0, 10), padx=15)

        inner = ctk.CTkFrame(marco, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)

        ctk.CTkLabel(inner, text=titulo, font=("Arial", 10, "bold"),
                     text_color=color_titulo,
                     ).pack(anchor="w", pady=(0, 6))

        if modo == "validas":
            columnas = ("fila", "asic", "tipo", "fecha_inicio", "fecha_fin", "lugar", "participantes")
        else:
            columnas = ("fila", "asic", "tipo", "fecha_inicio", "errores")

        tree_frame = ctk.CTkFrame(inner, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Import.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=24)
        style.configure("Import.Treeview.Heading",
                        background="#c00000", foreground="white",
                        relief="flat")
        style.map("Import.Treeview", background=[("selected", t["bg_card"])])

        tree = ttk.Treeview(tree_frame, columns=columnas, show="headings",
                            style="Import.Treeview", height=min(len(filas), 8))

        col_ancho  = {"fila": 50, "asic": 160, "tipo": 140, "fecha_inicio": 100,
                      "fecha_fin": 100, "lugar": 160, "participantes": 90, "errores": 350}
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
                    str(fila["fecha_fin"])    if fila["fecha_fin"]    else dc.get("fecha_fin", ""),
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

        scrolly = ttk.Scrollbar(tree_frame, orient="vertical",   command=tree.yview)
        scrollx = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrolly.pack(side="right",  fill="y")
        scrollx.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

    def _confirmar_importar(self):
        validas = self._resultado_previo["filas_validas"]
        if messagebox.askyesno("Confirmar importación",
                               f"Se importarán {len(validas)} actividades en la base de datos.\n\n"
                               "¿Deseas continuar?"):
            self._ejecutar_importacion(validas)

    def _ejecutar_importacion(self, filas_validas: list):
        self.parent.configure(cursor="wait")

        def _tarea():
            try:
                svc      = ExcelService(id_usuario_registro=self.usuario["id_usuario"])
                resultado = svc.importar(filas_validas)
                self.parent.after(0, lambda r=resultado: self._mostrar_paso3(r))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: self._error_importar(e))

        threading.Thread(target=_tarea, daemon=True).start()

    def _error_importar(self, exc: Exception):
        self.parent.configure(cursor="")
        messagebox.showerror("Error al importar",
                             f"Ocurrió un error durante la importación:\n\n{exc}")

    def _mostrar_paso3(self, resultado: dict):
        t = self.t
        self.parent.configure(cursor="")
        self._limpiar_pasos()

        insertadas  = resultado["insertadas"]
        errores_bd  = resultado["errores_al_insertar"]

        card = ctk.CTkFrame(self._frame_pasos, fg_color=t["bg_surface"],
                            corner_radius=10)
        card.pack(fill="x", padx=15)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=30)

        icono  = "✅" if not errores_bd else "⚠️"
        color  = t["success"] if not errores_bd else t["amber"]
        titulo = "Importación completada" if not errores_bd else "Importación completada con advertencias"

        ctk.CTkLabel(inner, text=f"{icono}  {titulo}",
                     font=("Arial", 14, "bold"), text_color=color,
                     ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(inner, text=f"Se insertaron correctamente {insertadas} actividades.",
                     font=("Arial", 11), text_color=t["text_primary"],
                     ).pack(anchor="w")

        if errores_bd:
            ctk.CTkLabel(inner,
                         text=f"{len(errores_bd)} actividades no pudieron insertarse (ver detalles abajo).",
                         font=("Arial", 10), text_color=t["red"],
                         ).pack(anchor="w", pady=(4, 0))
            for err in errores_bd:
                ctk.CTkLabel(inner, text=f"  • Fila {err['numero_fila']}: {err['error']}",
                             font=("Arial", 9), text_color=t["red"],
                             ).pack(anchor="w")

        ctk.CTkButton(inner, text="↩  Hacer otra importación",
                      font=("Arial", 10), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], text_color=t["text_primary"],
                      corner_radius=8, command=self._mostrar_paso1,
                      ).pack(anchor="w", pady=(22, 0))

    def _descargar_plantilla(self):
        if not os.path.exists(TEMPLATE_PATH):
            messagebox.showerror("Plantilla no encontrada",
                                 f"No se encontró la plantilla en:\n{TEMPLATE_PATH}\n\n"
                                 "Asegúrate de que el archivo exista en esa ruta.")
            return

        destino = filedialog.asksaveasfilename(
            title="Guardar plantilla como…",
            defaultextension=".xlsx",
            initialfile="plantilla_importacion.xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
        )
        if destino:
            import shutil
            shutil.copy2(TEMPLATE_PATH, destino)
            messagebox.showinfo("Plantilla guardada", f"Plantilla guardada en:\n{destino}")

    def _limpiar_pasos(self):
        for w in self._frame_pasos.winfo_children():
            w.destroy()

    def _chip(self, parent: ctk.CTkFrame, texto: str, color: str):
        t = self.t
        chip = ctk.CTkFrame(parent, fg_color=color, corner_radius=6)
        chip.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(chip, text=texto, font=("Arial", 9, "bold"),
                     text_color=t["text_primary"]).pack(padx=10, pady=4)
