# ============================================================
# views/dashboard_view.py
# Panel de control principal con métricas reales desde BD.
#
# Muestra:
#   - 4 tarjetas de KPI: actividades del mes, participantes del mes,
#     ASIC registradas, informes generados.
#   - Tabla de últimas 8 actividades registradas.
#   - Mini-gráfico de barras (Canvas) de actividades por ASIC
#     en el mes actual.
#   - Accesos rápidos a las secciones principales.
# ============================================================

import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
import threading

from controllers.auth_controller import AuthController
from db.connection import get_connection


# ── Colores ────────────────────────────────────────────────────────────
BG_DARK   = "#1a1a2e"
BG_PANEL  = "#16213e"
BG_CARD   = "#0f3460"
ACCENT    = "#e94560"
GREEN     = "#05c46b"
PURPLE    = "#533483"
GOLD      = "#f0ad4e"
TEXT_LT   = "#ffffff"
TEXT_DIM  = "#8892b0"


def _query(sql: str, params: tuple = ()) -> list:
    """Ejecuta una consulta y devuelve la lista de dicts resultante."""
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def _scalar(sql: str, params: tuple = (), default=0):
    """Ejecuta una consulta escalar y devuelve el primer valor de la primera fila."""
    rows = _query(sql, params)
    if rows:
        return list(rows[0].values())[0] or default
    return default


class DashboardView:
    """
    Panel de control principal.
    Se monta como hijo del área de contenido de MainView.
    """

    def __init__(self, parent: tk.Frame):
        self.parent  = parent
        self.auth    = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        # Contenedor principal con scroll
        self._canvas = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
        self._vsb    = ttk.Scrollbar(parent, orient="vertical",
                                     command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)

        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=BG_DARK)
        self._win_id = self._canvas.create_window((0, 0), window=self._inner,
                                                   anchor="nw")

        self._inner.bind("<Configure>", self._on_configure)
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._construir_esqueleto()
        # Cargar métricas en hilo para no bloquear
        threading.Thread(target=self._cargar_metricas, daemon=True).start()

    # ------------------------------------------------------------------
    # Scroll helpers
    # ------------------------------------------------------------------

    def _on_configure(self, _event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._win_id, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    # Construcción del esqueleto (widgets estáticos)
    # ------------------------------------------------------------------

    def _construir_esqueleto(self):
        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"
        hoy    = datetime.now().strftime("%A, %d de %B de %Y")

        # ── Encabezado ──────────────────────────────────────────────
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

        # ── Fila de KPI (4 tarjetas) ─────────────────────────────────
        self._frame_kpi = tk.Frame(self._inner, bg=BG_DARK)
        self._frame_kpi.pack(fill="x", padx=30, pady=(0, 18))

        self._kpi_vars: dict[str, tk.StringVar] = {}
        kpis = [
            ("act_mes",    "📋",  "Actividades\ndel mes",   ACCENT),
            ("part_mes",   "👥",  "Participantes\ndel mes", BG_CARD),
            ("asic_total", "🏥",  "ASIC\nregistradas",      PURPLE),
            ("informes",   "📊",  "Informes\ngenerados",    GREEN),
        ]
        for clave, icono, label, color in kpis:
            var = tk.StringVar(value="…")
            self._kpi_vars[clave] = var
            self._tarjeta_kpi(self._frame_kpi, icono, label, var, color)

        # ── Fila inferior: últimas actividades + gráfico ─────────────
        fila_inf = tk.Frame(self._inner, bg=BG_DARK)
        fila_inf.pack(fill="both", expand=True, padx=30, pady=(0, 18))

        # Tabla últimas actividades (izquierda, 60 %)
        self._frame_tabla = tk.Frame(fila_inf, bg=BG_PANEL, padx=14, pady=12)
        self._frame_tabla.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(self._frame_tabla, text="Últimas actividades registradas",
                 font=("Arial", 10, "bold"), bg=BG_PANEL, fg=TEXT_LT
                 ).pack(anchor="w", pady=(0, 6))
        self._tabla_actividades = self._crear_tabla_actividades(self._frame_tabla)

        # Gráfico por ASIC (derecha, 40 %)
        self._frame_grafico = tk.Frame(fila_inf, bg=BG_PANEL, padx=14, pady=12,
                                       width=320)
        self._frame_grafico.pack(side="left", fill="y")
        self._frame_grafico.pack_propagate(False)
        tk.Label(self._frame_grafico,
                 text="Actividades por ASIC (mes actual)",
                 font=("Arial", 10, "bold"), bg=BG_PANEL, fg=TEXT_LT
                 ).pack(anchor="w", pady=(0, 6))
        self._canvas_graf = tk.Canvas(self._frame_grafico, bg=BG_DARK,
                                      highlightthickness=0, width=290, height=220)
        self._canvas_graf.pack(fill="both", expand=True)

        # ── Accesos rápidos ──────────────────────────────────────────
        self._construir_accesos()

    def _tarjeta_kpi(self, parent: tk.Frame, icono: str, label: str,
                      var: tk.StringVar, color: str):
        card = tk.Frame(parent, bg=color, padx=18, pady=16)
        card.pack(side="left", fill="x", expand=True, padx=(0, 12))

        tk.Label(card, text=icono, font=("Arial", 20),
                 bg=color, fg=TEXT_LT).pack()
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

    def _construir_accesos(self):
        marco = tk.Frame(self._inner, bg=BG_DARK)
        marco.pack(fill="x", padx=30, pady=(0, 24))

        tk.Label(marco, text="Accesos rápidos",
                 font=("Arial", 11, "bold"), bg=BG_DARK, fg=TEXT_LT
                 ).pack(anchor="w", pady=(0, 8))

        fila = tk.Frame(marco, bg=BG_DARK)
        fila.pack(anchor="w")

        accesos = [
            ("📋  Nueva Actividad",  BG_CARD,  "actividades"),
            ("📥  Importar Excel",   PURPLE,   "importar"),
            ("📊  Generar Reporte",  ACCENT,   "reportes"),
            ("🏥  Catálogos",        "#2a4a3a", "asic"),
        ]
        for texto, color, _ in accesos:
            tk.Button(fila, text=texto, font=("Arial", 10),
                      bg=color, fg=TEXT_LT, relief="flat",
                      cursor="hand2", padx=14, pady=8
                      ).pack(side="left", padx=(0, 10))

    # ------------------------------------------------------------------
    # Carga de métricas desde BD (se ejecuta en hilo secundario)
    # ------------------------------------------------------------------

    def _cargar_metricas(self):
        try:
            hoy   = date.today()
            anio  = hoy.year
            mes   = hoy.month
            f_ini = date(anio, mes, 1).strftime("%Y-%m-%d")
            # Último día del mes
            if mes == 12:
                f_fin = date(anio, 12, 31).strftime("%Y-%m-%d")
            else:
                f_fin = date(anio, mes + 1, 1).strftime("%Y-%m-%d")
                # restar 1 día
                import datetime as dt
                f_fin = (dt.date(anio, mes + 1, 1) - dt.timedelta(days=1)).strftime("%Y-%m-%d")

            # KPIs
            act_mes = _scalar(
                "SELECT COUNT(*) FROM actividad "
                "WHERE eliminado=FALSE AND fecha_inicio >= %s AND fecha_inicio <= %s",
                (f_ini, f_fin)
            )
            part_mes = _scalar(
                "SELECT COALESCE(SUM(participantes),0) FROM actividad "
                "WHERE eliminado=FALSE AND fecha_inicio >= %s AND fecha_inicio <= %s",
                (f_ini, f_fin)
            )
            asic_total = _scalar(
                "SELECT COUNT(*) FROM asic WHERE activo=TRUE"
            )
            informes = _scalar(
                "SELECT COUNT(*) FROM informe_consolidado"
            )

            # Últimas 8 actividades
            ultimas = _query("""
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

            # Actividades por ASIC en el mes actual
            por_asic = _query("""
                SELECT asic.nombre AS asic_nombre, COUNT(*) AS total
                FROM actividad a
                JOIN asic ON a.id_asic = asic.id_asic
                WHERE a.eliminado=FALSE
                  AND a.fecha_inicio >= %s AND a.fecha_inicio <= %s
                GROUP BY asic.id_asic, asic.nombre
                ORDER BY total DESC
                LIMIT 8
            """, (f_ini, f_fin))

            # Actualizar UI en el hilo principal
            self.parent.after(0, lambda: self._actualizar_ui(
                act_mes, part_mes, asic_total, informes, ultimas, por_asic
            ))

        except Exception as exc:
            self.parent.after(0, lambda e=exc: self._mostrar_error_metricas(e))

    def _actualizar_ui(self, act_mes, part_mes, asic_total, informes,
                        ultimas, por_asic):
        # KPIs
        self._kpi_vars["act_mes"].set(str(act_mes))
        self._kpi_vars["part_mes"].set(str(part_mes))
        self._kpi_vars["asic_total"].set(str(asic_total))
        self._kpi_vars["informes"].set(str(informes))

        # Tabla últimas actividades
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

        # Gráfico de barras
        self._dibujar_grafico(por_asic)

    def _mostrar_error_metricas(self, exc: Exception):
        for var in self._kpi_vars.values():
            var.set("—")
        # Mostramos el error en el canvas del gráfico
        self._canvas_graf.create_text(
            145, 110,
            text=f"Sin conexión a BD\n{str(exc)[:60]}",
            fill=ACCENT, font=("Arial", 9), justify="center",
        )

    # ------------------------------------------------------------------
    # Gráfico de barras (Canvas nativo)
    # ------------------------------------------------------------------

    def _dibujar_grafico(self, por_asic: list):
        c = self._canvas_graf
        c.delete("all")

        if not por_asic:
            c.create_text(145, 110, text="Sin datos para el mes actual",
                          fill=TEXT_DIM, font=("Arial", 9))
            return

        W = 290
        H = 220
        pad_l = 10   # izquierda
        pad_r = 10   # derecha
        pad_t = 15   # arriba (espacio para valor)
        pad_b = 50   # abajo (espacio para etiquetas)

        max_val  = max(r["total"] for r in por_asic)
        n        = len(por_asic)
        area_w   = W - pad_l - pad_r
        area_h   = H - pad_t - pad_b
        bar_w    = max(8, (area_w // n) - 6)

        # Paleta de colores para las barras
        paleta = [ACCENT, BG_CARD, PURPLE, GREEN, GOLD,
                  "#2196f3", "#ff5722", "#009688"]

        for i, fila in enumerate(por_asic):
            total     = fila["total"]
            nombre    = fila.get("asic_nombre", "")
            color     = paleta[i % len(paleta)]

            x_centro  = pad_l + (area_w / n) * i + (area_w / n) / 2
            bh        = int(area_h * total / max_val) if max_val else 0
            x0        = x_centro - bar_w / 2
            x1        = x_centro + bar_w / 2
            y0        = H - pad_b - bh
            y1        = H - pad_b

            # Barra
            c.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

            # Valor encima de la barra
            c.create_text(x_centro, y0 - 6, text=str(total),
                          fill=TEXT_LT, font=("Arial", 7, "bold"))

            # Etiqueta abajo (recortada a 10 chars)
            etiqueta = (nombre[:10] + "…") if len(nombre) > 10 else nombre
            c.create_text(x_centro, H - pad_b + 8, text=etiqueta,
                          fill=TEXT_DIM, font=("Arial", 7),
                          angle=40, anchor="w")

        # Línea base
        c.create_line(pad_l, H - pad_b, W - pad_r, H - pad_b,
                      fill=TEXT_DIM, width=1)
