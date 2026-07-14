import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from datetime import date, datetime
import threading

from db import AuthController
from utils import query, scalar
from themes import THEMES


class DashboardView:

    def __init__(self, parent: tk.Frame, theme: str = "dark"):
        self.parent = parent
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()
        self.theme = theme
        self.t = THEMES[theme]

        self._scroll = ctk.CTkScrollableFrame(
            parent, fg_color=self.t["bg_base"],
            scrollbar_fg_color=self.t["bg_base"],
            scrollbar_button_color=self.t["bg_sidebar"],
            scrollbar_button_hover_color=self.t["border"],
        )
        self._scroll.pack(fill="both", expand=True)

        self._construir_esqueleto()
        threading.Thread(target=self._cargar_metricas, daemon=True).start()

    def _construir_esqueleto(self):
        t = self.t
        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"
        hoy = datetime.now()

        # ── Welcome header ─────────────────────────────────
        header_wrap = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header_wrap.pack(fill="x", padx=32, pady=(24, 0))

        left_info = ctk.CTkFrame(header_wrap, fg_color="transparent")
        left_info.pack(side="left")

        ctk.CTkLabel(
            left_info, text=f"Bienvenido, {nombre}",
            font=("Segoe UI", 20, "bold"), text_color=t["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_info, text="Panel de control de gesti\u00f3n mensual",
            font=("Segoe UI", 10), text_color=t["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Date badge (rounded)
        dias = ["Lunes", "Martes", "Mi\u00e9rcoles", "Jueves", "Viernes", "S\u00e1bado", "Domingo"]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        fecha_str = f"{dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"

        date_badge = ctk.CTkFrame(header_wrap, fg_color=self._alpha_color(t["accent"], 0.1),
                                  corner_radius=10)
        date_badge.pack(side="right", padx=(12, 0))

        ctk.CTkLabel(
            date_badge, text=f"\U0001f4c5  {fecha_str}",
            font=("Segoe UI", 11), text_color=t["text_primary"],
        ).pack(padx=16, pady=8)

        # Separator
        sep1 = ctk.CTkFrame(self._scroll, fg_color=t["border"], height=1)
        sep1.pack(fill="x", padx=32, pady=(16, 20))

        # ── KPI Cards ──────────────────────────────────────
        kpi_row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        kpi_row.pack(fill="x", padx=32, pady=(0, 20))

        self._kpi_vars = {}
        kpis = [
            ("act_mes",  "ACTIVIDADES DEL MES",  t["accent"], "\u25B2"),
            ("part_mes", "PARTICIPANTES DEL MES", t["success"], "\u25B2"),
        ]
        for clave, label, color, arrow in kpis:
            var = tk.StringVar(value="\u2014")
            self._kpi_vars[clave] = var
            self._crear_kpi_card(kpi_row, label, var, color, arrow)

        # ── Table card ─────────────────────────────────────
        table_card = ctk.CTkFrame(self._scroll, fg_color=t["bg_card"],
                                  corner_radius=14)
        table_card.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        accent_bar = ctk.CTkFrame(table_card, fg_color=t["accent"], height=4,
                                  corner_radius=2)
        accent_bar.pack(fill="x", padx=16, pady=(12, 0))

        table_header = ctk.CTkFrame(table_card, fg_color="transparent")
        table_header.pack(fill="x", padx=20, pady=(14, 10))

        left_header = ctk.CTkFrame(table_header, fg_color="transparent")
        left_header.pack(side="left")

        icon_box = ctk.CTkLabel(
            left_header, text="\u23F0",
            font=("Segoe UI", 18), text_color=t["accent"],
            width=34, height=34,
            fg_color=self._alpha_color(t["accent"], 0.12),
            corner_radius=8,
        )
        icon_box.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            left_header, text="\u00daltimas actividades",
            font=("Segoe UI", 13, "bold"), text_color=t["text_primary"],
        ).pack(side="left")

        ver_todas = ctk.CTkLabel(
            table_header, text="Ver todas  \u2192",
            font=("Segoe UI", 10, "bold"), text_color=t["accent"],
            cursor="hand2",
        )
        ver_todas.pack(side="right")

        sep2 = ctk.CTkFrame(table_card, fg_color=t["border"], height=1)
        sep2.pack(fill="x", padx=20)

        self._crear_tabla(table_card)

    def _alpha_color(self, hex_color, alpha):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        bg = self.t["bg_card"]
        br = int(bg[1:3], 16)
        bg_ = int(bg[3:5], 16)
        bb = int(bg[5:7], 16)
        cr = int(r * alpha + br * (1 - alpha))
        cg = int(g * alpha + bg_ * (1 - alpha))
        cb = int(b * alpha + bb * (1 - alpha))
        return f"#{cr:02x}{cg:02x}{cb:02x}"

    def _crear_kpi_card(self, parent, label, var, color, arrow):
        t = self.t

        card = ctk.CTkFrame(parent, fg_color=t["bg_card"],
                            corner_radius=14)
        card.pack(side="left", fill="x", expand=True, padx=(0, 12))

        accent_bar = ctk.CTkFrame(card, fg_color=color, height=4,
                                  corner_radius=2)
        accent_bar.pack(fill="x", padx=16, pady=(12, 0))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=(14, 16))

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        left_col = ctk.CTkFrame(top_row, fg_color="transparent")
        left_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_col, text=label,
            font=("Segoe UI", 10, "bold"), text_color=t["text_muted"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_col, textvariable=var,
            font=("Segoe UI", 36, "bold"), text_color=t["text_primary"],
        ).pack(anchor="w", pady=(4, 0))

        icon_box = ctk.CTkLabel(
            top_row, text=arrow,
            font=("Segoe UI", 22), text_color=color,
            width=50, height=50,
            fg_color=self._alpha_color(color, 0.12),
            corner_radius=14,
        )
        icon_box.pack(side="right", anchor="ne")

        trend = ctk.CTkFrame(inner, fg_color="transparent")
        trend.pack(fill="x", pady=(12, 0))

        ctk.CTkLabel(
            trend, text=f"{arrow}  0% incremento",
            font=("Segoe UI", 9, "bold"), text_color=t["success"],
        ).pack(side="left")

        ctk.CTkLabel(
            trend, text="desde el mes anterior",
            font=("Segoe UI", 9), text_color=t["text_muted"],
        ).pack(side="left", padx=(6, 0))

    def _crear_tabla(self, parent):
        t = self.t
        cols = ("asic", "tipo", "fecha", "lugar", "participantes")
        labs = ("ASIC", "TIPO", "FECHA", "LUGAR", "PARTICIPANTES")
        anchs = (160, 140, 90, 160, 100)

        style = ttk.Style()
        style.theme_use("clam")

        alt_bg = self._alpha_color(t["border"], 0.15)

        style.configure("Dash.Treeview",
                        background=t["bg_card"], foreground=t["text_primary"],
                        fieldbackground=t["bg_card"], rowheight=44,
                        font=("Segoe UI", 10), borderwidth=0,
                        padding=(10, 0))
        style.configure("Dash.Treeview.Heading",
                        background=self._alpha_color(t["accent"], 0.08),
                        foreground=t["text_muted"],
                        relief="flat", font=("Segoe UI", 9, "bold"),
                        borderwidth=0, padding=(10, 10))
        style.map("Dash.Treeview",
                  background=[("selected", t["accent_dim"]),
                              ("!selected", alt_bg)],
                  foreground=[("selected", "#FFFFFF")])
        style.layout("Dash.Treeview", [
            ("Dash.Treeview.treearea", {"sticky": "nswe"})
        ])

        cont = ctk.CTkFrame(parent, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tree = ttk.Treeview(cont, columns=cols, show="headings",
                            style="Dash.Treeview", height=8)
        for col, lab, ancho in zip(cols, labs, anchs):
            tree.heading(col, text=lab)
            tree.column(col, width=ancho, minwidth=40, anchor="w")

        sy = ttk.Scrollbar(cont, orient="vertical", command=tree.yview)
        sx = ttk.Scrollbar(cont, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        cont.grid_rowconfigure(0, weight=1)
        cont.grid_columnconfigure(0, weight=1)

        self._tree = tree

    def _cargar_metricas(self):
        try:
            hoy = date.today()
            anio = hoy.year
            mes = hoy.month
            f_ini = date(anio, mes, 1).strftime("%Y-%m-%d")

            import datetime as dt
            if mes == 12:
                f_fin = date(anio, 12, 31).strftime("%Y-%m-%d")
            else:
                f_fin = (dt.date(anio, mes + 1, 1) - dt.timedelta(days=1)).strftime("%Y-%m-%d")

            act_mes = scalar(
                "SELECT COUNT(*) FROM actividad "
                "WHERE eliminado=FALSE AND fecha_inicio >= %s AND fecha_inicio <= %s",
                (f_ini, f_fin),
            )
            part_mes = scalar(
                "SELECT COALESCE(SUM(participantes),0) FROM actividad "
                "WHERE eliminado=FALSE AND fecha_inicio >= %s AND fecha_inicio <= %s",
                (f_ini, f_fin),
            )
            ultimas = query("""
                SELECT a.fecha_inicio, a.lugar, a.participantes,
                       asic.nombre    AS asic_nombre,
                       ta.nombre      AS tipo_nombre
                FROM actividad a
                JOIN asic            ON a.id_asic = asic.id_asic
                JOIN tipo_actividad  ta ON a.id_tipo = ta.id_tipo
                WHERE a.eliminado = FALSE
                ORDER BY a.created_at DESC
                LIMIT 8
            """)

            self.parent.after(0, lambda: self._actualizar_ui(act_mes, part_mes, ultimas))

        except Exception as exc:
            self.parent.after(0, lambda e=exc: self._mostrar_error(e))

    def _actualizar_ui(self, act_mes, part_mes, ultimas):
        try:
            self._kpi_vars["act_mes"].set(str(act_mes))
            self._kpi_vars["part_mes"].set(str(part_mes))

            for row in self._tree.get_children():
                self._tree.delete(row)
            for act in ultimas:
                self._tree.insert("", "end", values=(
                    act.get("asic_nombre", ""),
                    act.get("tipo_nombre", ""),
                    str(act.get("fecha_inicio", ""))[:10],
                    act.get("lugar", ""),
                    act.get("participantes", 0),
                ))
        except Exception:
            pass

    def _mostrar_error(self, exc: Exception):
        try:
            for var in self._kpi_vars.values():
                var.set("\u2014")
        except Exception:
            pass
