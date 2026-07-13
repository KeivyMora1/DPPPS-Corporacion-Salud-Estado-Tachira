# ============================================================
# pantallas/dashboard.py
# Panel de control principal con métricas reales desde BD.
#
# Muestra:
#   - 2 tarjetas de KPI: actividades del mes, participantes del mes.
#   - Tabla de últimas 8 actividades registradas.
# ============================================================

import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
import threading

from db import AuthController
from utils import query, scalar

# Colores
BG_DARK  = "#1a1a2e"
BG_PANEL = "#16213e"
BG_CARD  = "#0f3460"
ACCENT   = "#e94560"
GREEN    = "#05c46b"
PURPLE   = "#533483"
GOLD     = "#f0ad4e"
TEXT_LT  = "#ffffff"
TEXT_DIM = "#8892b0"


class DashboardView:
    """
    Panel de control principal.
    Se monta como hijo del área de contenido de MainView.
    """

    def __init__(self, parent: tk.Frame, theme: str = "dark"):
        self.parent  = parent
        self.auth    = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()
        self.theme   = theme

        # Contenedor principal con scroll
        self._canvas = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
        self._vsb    = ttk.Scrollbar(parent, orient="vertical",
                                     command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)

        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner  = tk.Frame(self._canvas, bg=BG_DARK)
        self._win_id = self._canvas.create_window((0, 0), window=self._inner,
                                                   anchor="nw")

        self._inner.bind("<Configure>", self._on_configure)
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._construir_esqueleto()
        # Cargar métricas en hilo para no bloquear la UI
        threading.Thread(target=self._cargar_metricas, daemon=True).start()

    # ── Scroll helpers ─────────────────────────────────────────────────

    def _on_configure(self, _event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._win_id, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Construcción del esqueleto (widgets estáticos) ─────────────────

    def _construir_esqueleto(self):
        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"
        hoy    = datetime.now().strftime("%A, %d de %B de %Y")

        # Encabezado
        enc = tk.Frame(self._inner, bg=BG_DARK)
        enc.pack(fill="x", padx=30, pady=(22, 4))

        tk.Label(enc, text=f"👋  Bienvenido, {nombre}",
                 font=("Arial", 18, "bold"), bg=BG_DARK, fg=TEXT_LT
                 ).pack(side="left")
        tk.Label(enc, text=hoy, font=("Arial", 10),
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="right", pady=6)

        tk.Label(self._inner,
                 text="Panel de control — Sistema de Consolidación DPPPS",
                 font=("Arial", 10), bg=BG_DARK, fg=TEXT_DIM
                 ).pack(anchor="w", padx=30, pady=(0, 16))

        # Fila de KPI (2 tarjetas)
        self._frame_kpi = tk.Frame(self._inner, bg=BG_DARK)
        self._frame_kpi.pack(fill="x", padx=30, pady=(0, 18))

        self._kpi_vars: dict = {}
        kpis = [
            ("act_mes",  "📋", "Actividades\ndel mes",   ACCENT),
            ("part_mes", "👥", "Participantes\ndel mes", BG_CARD),
        ]
        for clave, icono, label, color in kpis:
            var = tk.StringVar(value="…")
            self._kpi_vars[clave] = var
            self._tarjeta_kpi(self._frame_kpi, icono, label, var, color)

        # Fila inferior: últimas actividades
        fila_inf = tk.Frame(self._inner, bg=BG_DARK)
        fila_inf.pack(fill="both", expand=True, padx=30, pady=(0, 18))

        self._frame_tabla = tk.Frame(fila_inf, bg=BG_PANEL, padx=14, pady=12)
        self._frame_tabla.pack(fill="both", expand=True)
        tk.Label(self._frame_tabla, text="Últimas actividades registradas",
                 font=("Arial", 10, "bold"), bg=BG_PANEL, fg=TEXT_LT
                 ).pack(anchor="w", pady=(0, 6))
        self._tabla_actividades = self._crear_tabla_actividades(self._frame_tabla)

    def _tarjeta_kpi(self, parent: tk.Frame, icono: str, label: str,
                     var: tk.StringVar, color: str):
        card = tk.Frame(parent, bg=color, padx=18, pady=16)
        card.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(card, text=icono, font=("Arial", 20), bg=color, fg=TEXT_LT).pack()
        tk.Label(card, textvariable=var, font=("Arial", 26, "bold"),
                 bg=color, fg=TEXT_LT).pack()
        tk.Label(card, text=label, font=("Arial", 8),
                 bg=color, fg="#cccccc", justify="center").pack()

    def _crear_tabla_actividades(self, parent: tk.Frame) -> ttk.Treeview:
        cols  = ("asic", "tipo", "fecha", "lugar", "participantes")
        labs  = ("ASIC", "Tipo", "Fecha", "Lugar", "Partic.")
        anchs = (140, 130, 85, 120, 60)

        style = ttk.Style()
        style.configure("Dash.Treeview",
                        background=BG_DARK, foreground=TEXT_LT,
                        fieldbackground=BG_DARK, rowheight=22)
        style.configure("Dash.Treeview.Heading",
                        background=BG_CARD, foreground=TEXT_LT, relief="flat")
        style.map("Dash.Treeview", background=[("selected", BG_CARD)])

        cont = tk.Frame(parent, bg=BG_PANEL)
        cont.pack(fill="both", expand=True)

        tree = ttk.Treeview(cont, columns=cols, show="headings",
                            style="Dash.Treeview", height=10)
        for col, lab, ancho in zip(cols, labs, anchs):
            tree.heading(col, text=lab)
            tree.column(col, width=ancho, minwidth=40, anchor="w")

        sx = ttk.Scrollbar(cont, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=sx.set)
        sx.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        return tree

    # ── Carga de métricas desde BD (hilo secundario) ───────────────────

    def _cargar_metricas(self):
        try:
            hoy  = date.today()
            anio = hoy.year
            mes  = hoy.month
            f_ini = date(anio, mes, 1).strftime("%Y-%m-%d")

            import datetime as dt
            if mes == 12:
                f_fin = date(anio, 12, 31).strftime("%Y-%m-%d")
            else:
                f_fin = (dt.date(anio, mes + 1, 1) - dt.timedelta(days=1)).strftime("%Y-%m-%d")

            act_mes = scalar(
                "SELECT COUNT(*) FROM actividad "
                "WHERE eliminado=FALSE AND fecha_inicio >= %s AND fecha_inicio <= %s",
                (f_ini, f_fin)
            )
            part_mes = scalar(
                "SELECT COALESCE(SUM(participantes),0) FROM actividad "
                "WHERE eliminado=FALSE AND fecha_inicio >= %s AND fecha_inicio <= %s",
                (f_ini, f_fin)
            )
            ultimas = query("""
                SELECT a.fecha_inicio, a.lugar, a.participantes,
                       asic.nombre AS asic_nombre,
                       ta.nombre   AS tipo_nombre
                FROM actividad a
                JOIN asic          ON a.id_asic = asic.id_asic
                JOIN tipo_actividad ta ON a.id_tipo = ta.id_tipo
                WHERE a.eliminado = FALSE
                ORDER BY a.created_at DESC
                LIMIT 8
            """)

            self.parent.after(0, lambda: self._actualizar_ui(act_mes, part_mes, ultimas))

        except Exception as exc:
            self.parent.after(0, lambda e=exc: self._mostrar_error_metricas(e))

    def _actualizar_ui(self, act_mes, part_mes, ultimas):
        self._kpi_vars["act_mes"].set(str(act_mes))
        self._kpi_vars["part_mes"].set(str(part_mes))

        for row in self._tabla_actividades.get_children():
            self._tabla_actividades.delete(row)
        for act in ultimas:
            self._tabla_actividades.insert("", "end", values=(
                act.get("asic_nombre", ""),
                act.get("tipo_nombre", ""),
                str(act.get("fecha_inicio", ""))[:10],
                act.get("lugar", ""),
                act.get("participantes", 0),
            ))

    def _mostrar_error_metricas(self, exc: Exception):
        for var in self._kpi_vars.values():
            var.set("—")
