# ============================================================
# views/main_view.py
# Ventana principal del sistema DPPPS.
# Aparece después del login exitoso.
# Contiene el menú lateral de navegación y el área de contenido.
# ============================================================

import tkinter as tk
from tkinter import messagebox
from controllers.auth_controller import AuthController
from views.catalogo_view import CatalogoView
from views.actividad_view import ActividadView


class MainView:
    """
    Ventana principal de la aplicación.
    Tiene un panel lateral con el menú de navegación
    y un área central donde se cargan las diferentes secciones.
    """

    # Opciones del menú lateral
    MENU_ITEMS = [
        ("🏠", "Dashboard",    "dashboard"),
        ("📋", "Actividades",  "actividades"),
        ("🏥", "ASIC",         "asic"),
        ("📂", "Tipos",        "tipos"),
        ("📥", "Importar",     "importar"),
        ("📊", "Reportes",     "reportes"),
        ("⚙️", "Configuracion","config"),
    ]

    def __init__(self, root):
        self.root = root
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

        # Guardamos referencia a los botones del menú para cambiar su estilo
        self.botones_menu = {}

        # Configuramos la ventana principal
        self.root.title("DPPPS — Sistema de Consolidacion de Informes")
        self.root.geometry("1100x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#1a1a2e")

        # Centramos la ventana
        self._centrar_ventana(1100, 680)

        # Construimos la interfaz
        self._construir_ui()

        # Mostramos el dashboard por defecto al abrir
        self._navegar("dashboard")

    def _centrar_ventana(self, ancho, alto):
        """Centra la ventana en la pantalla."""
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        x = (ancho_pantalla // 2) - (ancho // 2)
        y = (alto_pantalla // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _construir_ui(self):
        """Construye los 3 paneles: barra superior, menú lateral y área de contenido."""

        # ===== BARRA SUPERIOR =====
        barra_top = tk.Frame(self.root, bg="#0f3460", height=55)
        barra_top.pack(fill="x", side="top")
        barra_top.pack_propagate(False)

        tk.Label(
            barra_top,
            text="DPPPS — Sistema de Informes Gerenciales",
            font=("Arial", 13, "bold"),
            bg="#0f3460",
            fg="#ffffff"
        ).pack(side="left", padx=20, pady=15)

        # Nombre del usuario logueado
        nombre = self.usuario["nombre_completo"] if self.usuario else "Usuario"
        tk.Label(
            barra_top,
            text=f"Admin: {nombre}",
            font=("Arial", 10),
            bg="#0f3460",
            fg="#8892b0"
        ).pack(side="right", padx=10, pady=15)

        # Botón de cerrar sesión
        btn_logout = tk.Button(
            barra_top,
            text="Salir",
            font=("Arial", 9),
            bg="#e94560",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=10,
            command=self._cerrar_sesion
        )
        btn_logout.pack(side="right", padx=10, pady=12)

        # ===== CONTENEDOR PRINCIPAL (menú + contenido) =====
        contenedor = tk.Frame(self.root, bg="#1a1a2e")
        contenedor.pack(fill="both", expand=True)

        # ===== MENÚ LATERAL =====
        self.panel_menu = tk.Frame(contenedor, bg="#16213e", width=200)
        self.panel_menu.pack(fill="y", side="left")
        self.panel_menu.pack_propagate(False)

        for icono, nombre_item, clave in self.MENU_ITEMS:
            btn = tk.Button(
                self.panel_menu,
                text=f"  {icono}  {nombre_item}",
                font=("Arial", 11),
                bg="#16213e",
                fg="#8892b0",
                relief="flat",
                anchor="w",
                cursor="hand2",
                padx=10,
                pady=14,
                command=lambda c=clave: self._navegar(c)
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#0f3460", fg="#ffffff") if b.cget("bg") != "#e94560" else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#16213e", fg="#8892b0") if b.cget("bg") != "#e94560" else None)
            self.botones_menu[clave] = btn

        # ===== ÁREA DE CONTENIDO =====
        self.area_contenido = tk.Frame(contenedor, bg="#1a1a2e")
        self.area_contenido.pack(fill="both", expand=True)

    def _navegar(self, seccion):
        """Cambia la sección visible y resalta el botón activo en el menú."""
        # Limpiamos el contenido actual
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        # Resaltamos el botón activo
        for clave, btn in self.botones_menu.items():
            if clave == seccion:
                btn.config(bg="#e94560", fg="#ffffff")
            else:
                btn.config(bg="#16213e", fg="#8892b0")

        # Cargamos la vista correspondiente
        if seccion == "dashboard":
            self._mostrar_dashboard()
        elif seccion in ("asic", "tipos"):
            # Ambas secciones abren la misma vista de catálogos (con pestañas)
            CatalogoView(self.area_contenido)
        elif seccion == "actividades":
            ActividadView(self.area_contenido)
        elif seccion == "importar":
            self._mostrar_placeholder("Importar Excel", "Aqui ira la importacion masiva desde Excel.")
        elif seccion == "reportes":
            self._mostrar_placeholder("Reportes", "Aqui iran los reportes y exportaciones.")
        elif seccion == "config":
            self._mostrar_placeholder("Configuracion", "Aqui ira la configuracion del sistema.")

    def _mostrar_dashboard(self):
        """Pantalla de inicio con tarjetas de resumen."""
        tk.Label(
            self.area_contenido,
            text=f"Bienvenido, {self.usuario['nombre_completo']}",
            font=("Arial", 18, "bold"),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack(anchor="w", padx=30, pady=(30, 5))

        tk.Label(
            self.area_contenido,
            text="Panel de control — Sistema de Consolidacion de Informes DPPPS",
            font=("Arial", 11),
            bg="#1a1a2e",
            fg="#8892b0"
        ).pack(anchor="w", padx=30, pady=(0, 30))

        # Tarjetas de resumen
        marco_tarjetas = tk.Frame(self.area_contenido, bg="#1a1a2e")
        marco_tarjetas.pack(fill="x", padx=30)

        tarjetas = [
            ("Actividades\ndel mes",    "0", "#e94560"),
            ("Participantes\ndel mes",  "0", "#0f3460"),
            ("ASIC\nregistradas",       "0", "#533483"),
            ("Informes\ngenerados",     "0", "#05c46b"),
        ]

        for titulo, valor, color in tarjetas:
            tarjeta = tk.Frame(marco_tarjetas, bg=color, padx=20, pady=20)
            tarjeta.pack(side="left", padx=10, fill="x", expand=True)
            tk.Label(tarjeta, text=valor,  font=("Arial", 22, "bold"), bg=color, fg="#ffffff").pack()
            tk.Label(tarjeta, text=titulo, font=("Arial", 9),          bg=color, fg="#cccccc").pack()

        # Cuadro informativo
        marco_info = tk.Frame(self.area_contenido, bg="#16213e", padx=25, pady=20)
        marco_info.pack(fill="x", padx=30, pady=30)

        tk.Label(
            marco_info,
            text="El sistema esta listo.",
            font=("Arial", 12, "bold"),
            bg="#16213e", fg="#ffffff"
        ).pack(anchor="w")

        tk.Label(
            marco_info,
            text="Usa el menu lateral para navegar.\n"
                 "Empieza registrando los ASIC y tipos de actividad antes de cargar registros.",
            font=("Arial", 10),
            bg="#16213e", fg="#8892b0",
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

    def _mostrar_placeholder(self, titulo, descripcion):
        """Pantalla temporal para secciones aún no desarrolladas."""
        tk.Label(
            self.area_contenido,
            text=titulo,
            font=("Arial", 18, "bold"),
            bg="#1a1a2e", fg="#ffffff"
        ).pack(anchor="w", padx=30, pady=(30, 5))

        tk.Label(
            self.area_contenido,
            text=descripcion,
            font=("Arial", 11),
            bg="#1a1a2e", fg="#8892b0"
        ).pack(anchor="w", padx=30)

        tk.Label(
            self.area_contenido,
            text="En desarrollo...",
            font=("Arial", 30),
            bg="#1a1a2e", fg="#0f3460"
        ).pack(expand=True)

    def _cerrar_sesion(self):
        """Cierra sesión y vuelve al login."""
        confirmar = messagebox.askyesno("Cerrar sesion", "Estas seguro de que quieres salir?")
        if confirmar:
            self.auth.logout()
            self.root.destroy()
            import main
            main.iniciar_app()
