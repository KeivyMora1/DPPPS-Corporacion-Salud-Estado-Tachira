import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
import threading
import customtkinter as ctk

from db import AuthController
from utils import query, scalar
from ui_helpers import (
    frame, frame_transparent, label, label_title, label_subtitle,
    separator, scrollable_frame, treeview_style, card_with_accent
)


class DashboardView:

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        self._scroll = scrollable_frame(parent)
        self._scroll.pack(fill="both", expand=True)

        self._construir_esqueleto()
        threading.Thread(target=self._cargar_metricas, daemon=True).start()

    def _alpha_color(self, hex_color, alpha):
        # Map named colors to hex
        color_map = {
            "gray40": "#666666",
            "gray20": "#333333",
            "gray15": "#262626",
            "gray25": "#404040",
            "gray30": "#4d4d4d",
        }
        hex_color = color_map.get(hex_color, hex_color)
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        bg = "#26405E"
        br = int(bg[1:3], 16)
        bg_ = int(bg[3:5], 16)
        bb = int(bg[5:7], 16)
        cr = int(r * alpha + br * (1 - alpha))
        cg = int(g * alpha + bg_ * (1 - alpha))
        cb = int(b * alpha + bb * (1 - alpha))
        return f"#{cr:02x}{cg:02x}{cb:02x}"

    def _construir_esqueleto(self):
        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"
        hoy = datetime.now()

        # ── Welcome header ─────────────────────────────────
        header_wrap = frame_transparent(self._scroll)
        header_wrap.pack(fill="x", padx=32, pady=(24, 0))

        left_info = frame_transparent(header_wrap)
        left_info.pack(side="left")

        label_title(left_info, f"Bienvenido, {nombre}").pack(anchor="w")
        label_subtitle(left_info, "Panel de control de gestión mensual").pack(anchor="w", pady=(2, 0))

        # Date badge (rounded)
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        fecha_str = f"{dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"

        date_badge = ctk.CTkFrame(header_wrap, fg_color=self._alpha_color("#613BE3", 0.1), corner_radius=10)
        date_badge.pack(side="right", padx=(12, 0))

        label(date_badge, f"📅  {fecha_str}", font_size=11).pack(padx=16, pady=8)

        # Separator
        separator(self._scroll, horizontal=True, fg_color="gray40").pack(fill="x", padx=32, pady=(16, 20))

        # ── KPI Cards ──────────────────────────────────────
        kpi_row = frame_transparent(self._scroll)
        kpi_row.pack(fill="x", padx=32, pady=(0, 20))

        self._kpi_vars = {}
        kpis = [
            ("act_mes",  "ACTIVIDADES DEL MES",  "#613BE3", "▲"),
            ("part_mes", "PARTICIPANTES DEL MES", "#317E87", "▲"),
        ]
        for clave, label_text, color, arrow in kpis:
            var = tk.StringVar(value="—")
            self._kpi_vars[clave] = var
            self._crear_kpi_card(kpi_row, label_text, var, color, arrow)

        # ── Table card ─────────────────────────────────────
        table_card = card_with_accent(self._scroll, fg_color="gray25", corner_radius=14)
        table_card.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        table_header = frame_transparent(table_card)
        table_header.pack(fill="x", padx=20, pady=(14, 10))

        left_header = frame_transparent(table_header)
        left_header.pack(side="left")

        icon_box = ctk.CTkLabel(
            left_header, text="⏰",
            font=("Segoe UI", 18), text_color="#613BE3",
            width=34, height=34,
            fg_color=self._alpha_color("#613BE3", 0.12),
            corner_radius=8,
        )
        icon_box.pack(side="left", padx=(0, 10))

        label(left_header, "Últimas actividades", font_size=13, bold=True).pack(side="left")

        ver_todas = label(table_header, "Ver todas  →", font_size=10, bold=True, cursor="hand2", text_color="#613BE3")
        ver_todas.pack(side="right")

        separator(table_card, horizontal=True, fg_color="gray40").pack(fill="x", padx=20)

        self._crear_tabla(table_card)

    def _crear_kpi_card(self, parent, label_text, var, color, arrow):
        card = card_with_accent(parent, fg_color="gray25", corner_radius=14)
        # accent bar
        accent_bar = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=2)
        accent_bar.pack(fill="x", padx=16, pady=(12, 0))

        card.pack(side="left", fill="x", expand=True, padx=(0, 12))

        inner = frame_transparent(card)
        inner.pack(fill="x", padx=20, pady=(14, 16))

        top_row = frame_transparent(inner)
        top_row.pack(fill="x")

        left_col = frame_transparent(top_row)
        left_col.pack(side="left", fill="x", expand=True)

        label(left_col, label_text, font_size=10, bold=True).pack(anchor="w")
        label(left_col, "", font_size=36, bold=True, textvariable=var).pack(anchor="w", pady=(4, 0))

        icon_box = ctk.CTkLabel(
            top_row, text=arrow,
            font=("Segoe UI", 22), text_color=color,
            width=50, height=50,
            fg_color=self._alpha_color(color, 0.12),
            corner_radius=14,
        )
        icon_box.pack(side="right", anchor="ne")

        trend = frame_transparent(inner)
        trend.pack(fill="x", pady=(12, 0))

        label(trend, f"{arrow}  0% incremento", font_size=9, bold=True, text_color="#317E87").pack(side="left")
        label(trend, "desde el mes anterior", font_size=9).pack(side="left", padx=(6, 0))

    def _crear_tabla(self, parent):
        cols = ("asic", "tipo", "fecha", "lugar", "participantes")
        labs = ("ASIC", "TIPO", "FECHA", "LUGAR", "PARTICIPANTES")
        anchs = (160, 140, 90, 160, 100)

        treeview_style("Dash", 44)

        alt_bg = self._alpha_color("gray40", 0.15)

        style = ttk.Style()
        style.configure("Dash.Treeview",
                        background="gray20", foreground="white",
                        fieldbackground="gray20", rowheight=44,
                        font=("Segoe UI", 10), borderwidth=0,
                        padding=(10, 0))
        style.configure("Dash.Treeview.Heading",
                        background=self._alpha_color("#613BE3", 0.08),
                        foreground="gray70",
                        relief="flat", font=("Segoe UI", 9, "bold"),
                        borderwidth=0, padding=(10, 10))
        style.map("Dash.Treeview",
                  background=[("selected", "#4e2fb8"),
                              ("!selected", alt_bg)],
                  foreground=[("selected", "#FFFFFF")])
        style.layout("Dash.Treeview", [
            ("Dash.Treeview.treearea", {"sticky": "nswe"})
        ])

        cont = frame_transparent(parent)
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
                var.set("—")
        except Exception:
            pass