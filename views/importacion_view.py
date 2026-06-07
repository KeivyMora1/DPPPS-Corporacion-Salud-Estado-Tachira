# ============================================================
# views/importacion_view.py
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

from config import settings
from controllers.auth_controller import AuthController
from services.excel_service import ExcelService


class ImportacionView:
    """
    Sección de importación masiva desde Excel.
    Se monta como hijo del área de contenido de MainView.
    """

    # Paleta de colores — consistente con el resto del sistema
    BG_DARK   = "#1a1a2e"
    BG_PANEL  = "#16213e"
    BG_CARD   = "#0f3460"
    ACCENT    = "#e94560"
    GREEN     = "#05c46b"
    TEXT_LT   = "#ffffff"
    TEXT_DIM  = "#8892b0"
    BORDER    = "#2a2a4e"

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        # Estado interno
        self._ruta_archivo: str | None = None
        self._resultado_previo: dict | None = None  # salida de ExcelService.previsualizar()

        self._construir_ui()

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _construir_ui(self):
        """Arma el layout principal con encabezado + área de trabajo."""

        # ── Encabezado ──────────────────────────────────────────────────
        header = tk.Frame(self.parent, bg=self.BG_DARK)
        header.pack(fill="x", padx=30, pady=(25, 10))

        tk.Label(
            header,
            text="📥  Importación Masiva desde Excel",
            font=("Arial", 17, "bold"),
            bg=self.BG_DARK, fg=self.TEXT_LT,
        ).pack(side="left")

        # Botón plantilla (esquina derecha del encabezado)
        tk.Button(
            header,
            text="⬇  Descargar Plantilla",
            font=("Arial", 9),
            bg=self.BG_CARD, fg=self.TEXT_LT,
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._descargar_plantilla,
        ).pack(side="right")

        tk.Label(
            self.parent,
            text="Importa actividades en bloque subiendo un archivo .xlsx con el formato de la plantilla.",
            font=("Arial", 10),
            bg=self.BG_DARK, fg=self.TEXT_DIM,
        ).pack(anchor="w", padx=30, pady=(0, 18))

        # ── Contenedor de los tres pasos ───────────────────────────────
        self._frame_pasos = tk.Frame(self.parent, bg=self.BG_DARK)
        self._frame_pasos.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._mostrar_paso1()

    # ------------------------------------------------------------------
    # Paso 1 — Seleccionar archivo
    # ------------------------------------------------------------------

    def _mostrar_paso1(self):
        """Limpia el área de pasos y muestra el selector de archivo."""
        self._limpiar_pasos()
        self._ruta_archivo = None
        self._resultado_previo = None

        card = tk.Frame(self._frame_pasos, bg=self.BG_PANEL, padx=30, pady=30)
        card.pack(fill="x")

        tk.Label(
            card,
            text="Paso 1 de 3 — Seleccionar archivo Excel",
            font=("Arial", 12, "bold"),
            bg=self.BG_PANEL, fg=self.TEXT_LT,
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            card,
            text="El archivo debe tener las columnas: asic, tipo_actividad, fecha_inicio, fecha_fin, lugar, descripcion, participantes.",
            font=("Arial", 9),
            bg=self.BG_PANEL, fg=self.TEXT_DIM,
            wraplength=700, justify="left",
        ).pack(anchor="w", pady=(0, 20))

        # Widget que muestra la ruta seleccionada
        self._lbl_ruta = tk.Label(
            card,
            text="Ningún archivo seleccionado",
            font=("Arial", 10, "italic"),
            bg=self.BG_PANEL, fg=self.TEXT_DIM,
        )
        self._lbl_ruta.pack(anchor="w", pady=(0, 15))

        fila_botones = tk.Frame(card, bg=self.BG_PANEL)
        fila_botones.pack(anchor="w")

        tk.Button(
            fila_botones,
            text="📂  Examinar…",
            font=("Arial", 10),
            bg=self.BG_CARD, fg=self.TEXT_LT,
            relief="flat", cursor="hand2", padx=12, pady=7,
            command=self._seleccionar_archivo,
        ).pack(side="left", padx=(0, 12))

        self._btn_previsualizar = tk.Button(
            fila_botones,
            text="▶  Previsualizar",
            font=("Arial", 10, "bold"),
            bg="#444", fg=self.TEXT_DIM,
            relief="flat", cursor="arrow", padx=12, pady=7,
            state="disabled",
            command=self._iniciar_previo,
        )
        self._btn_previsualizar.pack(side="left")

    def _seleccionar_archivo(self):
        """Abre el diálogo de selección de archivo."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self._ruta_archivo = ruta
            nombre = os.path.basename(ruta)
            self._lbl_ruta.config(text=f"📄 {nombre}  ({ruta})", fg=self.TEXT_LT)
            # Habilitamos el botón de previsualizar
            self._btn_previsualizar.config(
                state="normal", bg=self.BG_CARD, fg=self.TEXT_LT, cursor="hand2"
            )

    # ------------------------------------------------------------------
    # Paso 2 — Previsualización
    # ------------------------------------------------------------------

    def _iniciar_previo(self):
        """Lanza ExcelService.previsualizar() en un hilo para no bloquear la UI."""
        self._btn_previsualizar.config(state="disabled", text="Procesando…")
        self.parent.config(cursor="wait")

        def _tarea():
            try:
                svc = ExcelService(id_usuario_registro=self.usuario["id_usuario"])
                resultado = svc.previsualizar(self._ruta_archivo)
                self.parent.after(0, lambda: self._mostrar_paso2(resultado))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: self._error_previo(e))

        threading.Thread(target=_tarea, daemon=True).start()

    def _error_previo(self, exc: Exception):
        """Muestra el error de lectura del Excel y restaura el paso 1."""
        self.parent.config(cursor="")
        messagebox.showerror(
            "Error al leer el archivo",
            f"No se pudo procesar el archivo:\n\n{exc}",
        )
        self._btn_previsualizar.config(state="normal", text="▶  Previsualizar")

    def _mostrar_paso2(self, resultado: dict):
        """Renderiza las tablas de filas válidas y filas con error."""
        self.parent.config(cursor="")
        self._resultado_previo = resultado
        self._limpiar_pasos()

        validas = resultado["filas_validas"]
        errores = resultado["filas_error"]
        total   = resultado["total_filas"]

        # ── Resumen ─────────────────────────────────────────────────────
        card_resumen = tk.Frame(self._frame_pasos, bg=self.BG_PANEL, padx=20, pady=15)
        card_resumen.pack(fill="x", pady=(0, 12))

        tk.Label(
            card_resumen,
            text="Paso 2 de 3 — Resultado del análisis",
            font=("Arial", 12, "bold"),
            bg=self.BG_PANEL, fg=self.TEXT_LT,
        ).pack(anchor="w", pady=(0, 10))

        fila_resumen = tk.Frame(card_resumen, bg=self.BG_PANEL)
        fila_resumen.pack(anchor="w")

        self._chip(fila_resumen, f"📄 Total filas: {total}",         self.BG_CARD)
        self._chip(fila_resumen, f"✅ Válidas: {len(validas)}",      self.GREEN)
        self._chip(fila_resumen, f"❌ Con errores: {len(errores)}",  self.ACCENT if errores else "#555")

        # ── Tabla filas válidas ──────────────────────────────────────────
        if validas:
            self._seccion_tabla(
                titulo="Filas listas para importar",
                color_titulo=self.GREEN,
                filas=validas,
                modo="validas",
            )

        # ── Tabla filas con errores ──────────────────────────────────────
        if errores:
            self._seccion_tabla(
                titulo="Filas con errores (no se importarán)",
                color_titulo=self.ACCENT,
                filas=errores,
                modo="errores",
            )

        # ── Botones de acción ────────────────────────────────────────────
        card_acciones = tk.Frame(self._frame_pasos, bg=self.BG_PANEL, padx=20, pady=15)
        card_acciones.pack(fill="x", pady=(8, 0))

        tk.Button(
            card_acciones,
            text="← Seleccionar otro archivo",
            font=("Arial", 10),
            bg=self.BG_CARD, fg=self.TEXT_LT,
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._mostrar_paso1,
        ).pack(side="left", padx=(0, 10))

        if validas:
            tk.Button(
                card_acciones,
                text=f"✔  Importar {len(validas)} actividades",
                font=("Arial", 10, "bold"),
                bg=self.GREEN, fg=self.TEXT_LT,
                relief="flat", cursor="hand2", padx=12, pady=7,
                command=self._confirmar_importar,
            ).pack(side="left")
        else:
            tk.Label(
                card_acciones,
                text="No hay filas válidas para importar. Corrige el archivo y vuelve a intentarlo.",
                font=("Arial", 9, "italic"),
                bg=self.BG_PANEL, fg=self.ACCENT,
            ).pack(side="left")

    def _seccion_tabla(self, titulo: str, color_titulo: str, filas: list, modo: str):
        """Renderiza una tarjeta con una tabla Treeview de filas."""

        marco = tk.Frame(self._frame_pasos, bg=self.BG_PANEL, padx=15, pady=12)
        marco.pack(fill="both", expand=(modo == "validas"), pady=(0, 10))

        tk.Label(
            marco,
            text=titulo,
            font=("Arial", 10, "bold"),
            bg=self.BG_PANEL, fg=color_titulo,
        ).pack(anchor="w", pady=(0, 6))

        # Columnas de la tabla
        if modo == "validas":
            columnas = ("fila", "asic", "tipo", "fecha_inicio", "fecha_fin", "lugar", "participantes")
        else:
            columnas = ("fila", "asic", "tipo", "fecha_inicio", "errores")

        tree_frame = tk.Frame(marco, bg=self.BG_PANEL)
        tree_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Import.Treeview",
            background=self.BG_DARK, foreground=self.TEXT_LT,
            fieldbackground=self.BG_DARK, rowheight=24,
        )
        style.configure("Import.Treeview.Heading", background=self.BG_CARD, foreground=self.TEXT_LT, relief="flat")
        style.map("Import.Treeview", background=[("selected", self.BG_CARD)])

        tree = ttk.Treeview(
            tree_frame,
            columns=columnas, show="headings",
            style="Import.Treeview",
            height=min(len(filas), 8),
        )

        col_ancho = {
            "fila": 50, "asic": 160, "tipo": 140,
            "fecha_inicio": 100, "fecha_fin": 100,
            "lugar": 160, "participantes": 90, "errores": 350,
        }
        col_labels = {
            "fila": "#", "asic": "ASIC", "tipo": "Tipo Actividad",
            "fecha_inicio": "Fecha Inicio", "fecha_fin": "Fecha Fin",
            "lugar": "Lugar", "participantes": "Partic.", "errores": "Errores detectados",
        }
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

        # Scrollbars
        scrolly = ttk.Scrollbar(tree_frame, orient="vertical",   command=tree.yview)
        scrollx = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

        scrolly.pack(side="right",  fill="y")
        scrollx.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Paso 3 — Confirmación e inserción
    # ------------------------------------------------------------------

    def _confirmar_importar(self):
        """Pide confirmación al usuario antes de insertar."""
        validas = self._resultado_previo["filas_validas"]
        confirmar = messagebox.askyesno(
            "Confirmar importación",
            f"Se importarán {len(validas)} actividades en la base de datos.\n\n"
            "¿Deseas continuar?",
        )
        if confirmar:
            self._ejecutar_importacion(validas)

    def _ejecutar_importacion(self, filas_validas: list):
        """Llama a ExcelService.importar() en un hilo y muestra el resultado."""
        self.parent.config(cursor="wait")

        def _tarea():
            try:
                svc = ExcelService(id_usuario_registro=self.usuario["id_usuario"])
                resultado = svc.importar(filas_validas)
                self.parent.after(0, lambda r=resultado: self._mostrar_paso3(r))
            except Exception as exc:
                self.parent.after(0, lambda e=exc: self._error_importar(e))

        threading.Thread(target=_tarea, daemon=True).start()

    def _error_importar(self, exc: Exception):
        self.parent.config(cursor="")
        messagebox.showerror("Error al importar", f"Ocurrió un error durante la importación:\n\n{exc}")

    def _mostrar_paso3(self, resultado: dict):
        """Muestra el resumen final de la operación."""
        self.parent.config(cursor="")
        self._limpiar_pasos()

        insertadas = resultado["insertadas"]
        errores_bd = resultado["errores_al_insertar"]

        # ── Tarjeta resultado ────────────────────────────────────────────
        card = tk.Frame(self._frame_pasos, bg=self.BG_PANEL, padx=30, pady=30)
        card.pack(fill="x")

        icono  = "✅" if not errores_bd else "⚠️"
        color  = self.GREEN if not errores_bd else "#f0ad4e"
        titulo = "Importación completada" if not errores_bd else "Importación completada con advertencias"

        tk.Label(
            card,
            text=f"{icono}  {titulo}",
            font=("Arial", 14, "bold"),
            bg=self.BG_PANEL, fg=color,
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            card,
            text=f"Se insertaron correctamente {insertadas} actividades.",
            font=("Arial", 11),
            bg=self.BG_PANEL, fg=self.TEXT_LT,
        ).pack(anchor="w")

        if errores_bd:
            tk.Label(
                card,
                text=f"{len(errores_bd)} actividades no pudieron insertarse (ver detalles abajo).",
                font=("Arial", 10),
                bg=self.BG_PANEL, fg=self.ACCENT,
            ).pack(anchor="w", pady=(4, 0))

            for err in errores_bd:
                tk.Label(
                    card,
                    text=f"  • Fila {err['numero_fila']}: {err['error']}",
                    font=("Arial", 9),
                    bg=self.BG_PANEL, fg=self.ACCENT,
                ).pack(anchor="w")

        # ── Botón para volver ────────────────────────────────────────────
        tk.Button(
            card,
            text="↩  Hacer otra importación",
            font=("Arial", 10),
            bg=self.BG_CARD, fg=self.TEXT_LT,
            relief="flat", cursor="hand2", padx=12, pady=7,
            command=self._mostrar_paso1,
        ).pack(anchor="w", pady=(22, 0))

    # ------------------------------------------------------------------
    # Descarga de plantilla
    # ------------------------------------------------------------------

    def _descargar_plantilla(self):
        """Copia la plantilla Excel a la ubicación que elija el usuario."""
        origen = settings.TEMPLATE_PATH
        if not os.path.exists(origen):
            messagebox.showerror(
                "Plantilla no encontrada",
                f"No se encontró la plantilla en:\n{origen}\n\n"
                "Asegúrate de que el archivo exista en esa ruta.",
            )
            return

        destino = filedialog.asksaveasfilename(
            title="Guardar plantilla como…",
            defaultextension=".xlsx",
            initialfile="plantilla_importacion.xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
        )
        if destino:
            import shutil
            shutil.copy2(origen, destino)
            messagebox.showinfo("Plantilla guardada", f"Plantilla guardada en:\n{destino}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _limpiar_pasos(self):
        """Destruye todos los widgets del área de pasos."""
        for w in self._frame_pasos.winfo_children():
            w.destroy()

    def _chip(self, parent: tk.Frame, texto: str, color: str):
        """Pequeña etiqueta tipo 'chip' de resumen."""
        tk.Label(
            parent,
            text=texto,
            font=("Arial", 9, "bold"),
            bg=color, fg=self.TEXT_LT,
            padx=10, pady=4,
        ).pack(side="left", padx=(0, 8))
