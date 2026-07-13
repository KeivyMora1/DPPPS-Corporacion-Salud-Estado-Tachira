# ============================================================
# pantallas/principal.py
# Ventana principal del sistema DPPPS.
# Aparece después del login exitoso.
# Contiene el menú lateral de navegación y el área de contenido.
# ============================================================

import tkinter as tk
from tkinter import messagebox
from db import AuthController
from utils import centrar_ventana


class MainView:
    """
    Ventana principal de la aplicación.
    Tiene un panel lateral con el menú de navegación
    y un área central donde se cargan las diferentes secciones.
    """

    # Opciones del menú lateral
    MENU_ITEMS = [
        ("🏠", "Dashboard",   "dashboard"),
        ("📋", "Actividades", "actividades"),
        ("🏥", "ASIC",        "asic"),
        ("📂", "Tipos",       "tipos"),
        ("📥", "Importar",    "importar"),
        ("📊", "Reportes",    "reportes"),
    ]

    def __init__(self, root):
        self.root = root
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        self.botones_menu  = {}
        self.tema_actual   = "dark"
        self.seccion_actual = "dashboard"

        self.root.title("DPPPS — Sistema de Consolidacion de Informes")
        self.root.geometry("1100x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#1a1a2e")

        centrar_ventana(self.root, 1100, 680)
        self._construir_ui()
        self._navegar("dashboard")

    def _construir_ui(self):
        """Construye los 3 paneles: barra superior, menú lateral y área de contenido."""

        # ── Barra superior ─────────────────────────────────────────────
        barra_top = tk.Frame(self.root, bg="#0f3460", height=55)
        barra_top.pack(fill="x", side="top")
        barra_top.pack_propagate(False)

        tk.Label(
            barra_top,
            text="DPPPS — Sistema de Informes Gerenciales",
            font=("Arial", 13, "bold"),
            bg="#0f3460", fg="#ffffff"
        ).pack(side="left", padx=20, pady=15)

        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"
        tk.Label(
            barra_top,
            text=f"Admin: {nombre}",
            font=("Arial", 10),
            bg="#0f3460", fg="#8892b0"
        ).pack(side="right", padx=10, pady=15)

        btn_logout = tk.Button(
            barra_top, text="Salir",
            font=("Arial", 9),
            bg="#e94560", fg="#ffffff",
            relief="flat", cursor="hand2",
            padx=10,
            command=self._cerrar_sesion
        )
        btn_logout.pack(side="right", padx=10, pady=12)

        # ── Contenedor principal (menú + contenido) ────────────────────
        contenedor = tk.Frame(self.root, bg="#1a1a2e")
        contenedor.pack(fill="both", expand=True)

        # ── Menú lateral ───────────────────────────────────────────────
        self.panel_menu = tk.Frame(contenedor, bg="#16213e", width=200)
        self.panel_menu.pack(fill="y", side="left")
        self.panel_menu.pack_propagate(False)

        for icono, nombre_item, clave in self.MENU_ITEMS:
            btn = tk.Button(
                self.panel_menu,
                text=f"  {icono}  {nombre_item}",
                font=("Arial", 11),
                bg="#16213e", fg="#8892b0",
                relief="flat", anchor="w",
                cursor="hand2",
                padx=10, pady=14,
                command=lambda c=clave: self._navegar(c)
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#0f3460", fg="#ffffff") if b.cget("bg") != "#e94560" else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#16213e", fg="#8892b0") if b.cget("bg") != "#e94560" else None)
            self.botones_menu[clave] = btn

        self.btn_tema = tk.Button(
            self.panel_menu,
            text="🌙 Tema oscuro",
            font=("Arial", 10),
            bg="#0f3460", fg="#ffffff",
            relief="flat", cursor="hand2",
            padx=10, pady=12,
            command=self._alternar_tema
        )
        self.btn_tema.pack(side="bottom", fill="x", padx=10, pady=(20, 14))

        # ── Área de contenido ──────────────────────────────────────────
        self.area_contenido = tk.Frame(contenedor, bg="#1a1a2e")
        self.area_contenido.pack(fill="both", expand=True)

    def _navegar(self, seccion):
        """Cambia la sección visible y resalta el botón activo en el menú."""
        self.seccion_actual = seccion

        # Limpiar el contenido actual
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        # Resaltar el botón activo
        for clave, btn in self.botones_menu.items():
            if clave == seccion:
                btn.config(bg="#e94560", fg="#ffffff")
            else:
                btn.config(bg="#16213e", fg="#8892b0")

        # Importamos aquí para evitar importaciones circulares
        from pantallas.dashboard    import DashboardView
        from pantallas.catalogos    import CatalogoView
        from pantallas.actividades  import ActividadView
        from pantallas.importacion  import ImportacionView
        from pantallas.reportes     import ReporteView

        if seccion == "dashboard":
            DashboardView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "asic":
            CatalogoView(self.area_contenido, modo="asic", theme=self.tema_actual)
        elif seccion == "tipos":
            CatalogoView(self.area_contenido, modo="tipos", theme=self.tema_actual)
        elif seccion == "actividades":
            ActividadView(self.area_contenido, theme=self.tema_actual)
        elif seccion == "importar":
            ImportacionView(self.area_contenido)
        elif seccion == "reportes":
            ReporteView(self.area_contenido)

    def _alternar_tema(self):
        """Cambia entre tema claro y oscuro y recrea la vista actual."""
        self.tema_actual = "light" if self.tema_actual == "dark" else "dark"
        self.btn_tema.config(text="☀️ Tema claro" if self.tema_actual == "dark" else "🌙 Tema oscuro")
        self.root.configure(bg="#f5f7fb" if self.tema_actual == "light" else "#1a1a2e")
        self.panel_menu.configure(bg="#e8edf5" if self.tema_actual == "light" else "#16213e")
        self.area_contenido.configure(bg="#f5f7fb" if self.tema_actual == "light" else "#1a1a2e")
        self._navegar(self.seccion_actual)

    def _cerrar_sesion(self):
        """Cierra sesión y vuelve al login."""
        confirmar = messagebox.askyesno("Cerrar sesion", "Estas seguro de que quieres salir?")
        if confirmar:
            self.auth.logout()
            self.root.destroy()
            import main
            main.iniciar_app()
