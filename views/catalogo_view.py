# ============================================================
# views/catalogo_view.py
# Vista para gestionar los catálogos del sistema:
#   - ASIC (Áreas de Salud Integral Comunitaria)
#   - Tipos de Actividad
#
# Tiene dos pestañas (tabs), una para cada catálogo.
# Cada pestaña muestra una tabla con los registros
# y botones para crear, editar y eliminar.
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.catalogo_controller import CatalogoController


class CatalogoView:
    """
    Vista de catálogos con dos pestañas: ASIC y Tipos de Actividad.
    Se carga dentro del área de contenido de la ventana principal.
    """

    def __init__(self, parent):
        """
        parent → El frame del área de contenido donde se dibuja esta vista.
        """
        self.parent = parent
        self.controller = CatalogoController()

        self._construir_ui()

    def _construir_ui(self):
        """Construye el encabezado y las dos pestañas."""

        # --- Título de la sección ---
        tk.Label(
            self.parent,
            text="Catálogos",
            font=("Arial", 18, "bold"),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack(anchor="w", padx=30, pady=(25, 2))

        tk.Label(
            self.parent,
            text="Gestiona las Áreas de Salud (ASIC) y los tipos de actividad del sistema.",
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="#8892b0"
        ).pack(anchor="w", padx=30, pady=(0, 15))

        # --- Pestañas (Notebook) ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#16213e",
                        foreground="#8892b0",
                        padding=[16, 8],
                        font=("Arial", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", "#0f3460")],
                  foreground=[("selected", "#ffffff")])

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Pestaña 1: ASIC
        tab_asic = tk.Frame(self.notebook, bg="#1a1a2e")
        self.notebook.add(tab_asic, text="  🏥  ASIC  ")
        self._construir_tab_asic(tab_asic)

        # Pestaña 2: Tipos de Actividad
        tab_tipos = tk.Frame(self.notebook, bg="#1a1a2e")
        self.notebook.add(tab_tipos, text="  📂  Tipos de Actividad  ")
        self._construir_tab_tipos(tab_tipos)

    # ==========================================================
    # PESTAÑA: ASIC
    # ==========================================================

    def _construir_tab_asic(self, parent):
        """Construye el contenido de la pestaña ASIC."""

        # --- Barra de botones ---
        barra = tk.Frame(parent, bg="#1a1a2e")
        barra.pack(fill="x", pady=(15, 10), padx=10)

        tk.Button(
            barra,
            text="+ Nuevo ASIC",
            font=("Arial", 10, "bold"),
            bg="#e94560",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12, pady=6,
            command=self._abrir_form_asic
        ).pack(side="left")

        tk.Button(
            barra,
            text="Actualizar",
            font=("Arial", 10),
            bg="#0f3460",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12, pady=6,
            command=self._cargar_asic
        ).pack(side="left", padx=(8, 0))

        # --- Tabla de ASIC ---
        marco_tabla = tk.Frame(parent, bg="#1a1a2e")
        marco_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Columnas de la tabla
        columnas = ("id", "codigo", "nombre", "municipio", "parroquia")
        self.tabla_asic = ttk.Treeview(
            marco_tabla,
            columns=columnas,
            show="headings",
            height=15
        )

        # Configuramos el estilo de la tabla
        style = ttk.Style()
        style.configure("Treeview",
                        background="#16213e",
                        foreground="#ffffff",
                        fieldbackground="#16213e",
                        rowheight=30,
                        font=("Arial", 10))
        style.configure("Treeview.Heading",
                        background="#0f3460",
                        foreground="#ffffff",
                        font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#e94560")])

        # Definimos encabezados y anchos de columna
        self.tabla_asic.heading("id",        text="ID")
        self.tabla_asic.heading("codigo",    text="Código")
        self.tabla_asic.heading("nombre",    text="Nombre")
        self.tabla_asic.heading("municipio", text="Municipio")
        self.tabla_asic.heading("parroquia", text="Parroquia")

        self.tabla_asic.column("id",        width=50,  anchor="center")
        self.tabla_asic.column("codigo",    width=100, anchor="center")
        self.tabla_asic.column("nombre",    width=250)
        self.tabla_asic.column("municipio", width=150)
        self.tabla_asic.column("parroquia", width=150)

        # Scrollbar vertical
        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_asic.yview)
        self.tabla_asic.configure(yscrollcommand=scroll.set)

        self.tabla_asic.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # --- Botones Editar / Eliminar (debajo de la tabla) ---
        barra_acciones = tk.Frame(parent, bg="#1a1a2e")
        barra_acciones.pack(fill="x", padx=10, pady=(5, 10))

        tk.Button(
            barra_acciones,
            text="Editar seleccionado",
            font=("Arial", 10),
            bg="#533483",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12, pady=6,
            command=self._editar_asic
        ).pack(side="left")

        tk.Button(
            barra_acciones,
            text="Eliminar seleccionado",
            font=("Arial", 10),
            bg="#333333",
            fg="#ff6b6b",
            relief="flat",
            cursor="hand2",
            padx=12, pady=6,
            command=self._eliminar_asic
        ).pack(side="left", padx=(8, 0))

        # Cargamos los datos al iniciar
        self._cargar_asic()

    def _cargar_asic(self):
        """Recarga la tabla de ASIC desde la base de datos."""
        # Limpiamos la tabla
        for item in self.tabla_asic.get_children():
            self.tabla_asic.delete(item)

        # Cargamos los datos del controlador
        lista = self.controller.listar_asic()
        for asic in lista:
            self.tabla_asic.insert("", "end", values=(
                asic["id_asic"],
                asic["codigo"],
                asic["nombre"],
                asic.get("municipio", ""),
                asic.get("parroquia", "")
            ))

    def _abrir_form_asic(self, datos=None):
        """
        Abre una ventana emergente para crear o editar un ASIC.
        Si 'datos' viene con valores, es edición. Si no, es creación.
        """
        ventana = tk.Toplevel(self.parent)
        ventana.title("Nuevo ASIC" if datos is None else "Editar ASIC")
        ventana.geometry("420x340")
        ventana.resizable(False, False)
        ventana.configure(bg="#16213e")
        ventana.grab_set()  # Bloquea la ventana principal mientras este popup está abierto

        # Centramos el popup
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - 210
        y = (ventana.winfo_screenheight() // 2) - 170
        ventana.geometry(f"+{x}+{y}")

        # Título del popup
        tk.Label(
            ventana,
            text="Nuevo ASIC" if datos is None else "Editar ASIC",
            font=("Arial", 14, "bold"),
            bg="#16213e", fg="#ffffff"
        ).pack(pady=(20, 15))

        # Función auxiliar para crear un campo de formulario
        def campo(label_texto, valor_inicial=""):
            marco = tk.Frame(ventana, bg="#16213e")
            marco.pack(fill="x", padx=25, pady=4)
            tk.Label(marco, text=label_texto, font=("Arial", 9, "bold"),
                     bg="#16213e", fg="#ccd6f6", anchor="w").pack(fill="x")
            entrada = tk.Entry(marco, font=("Arial", 11), bg="#0f3460",
                               fg="#ffffff", insertbackground="#ffffff",
                               relief="flat", bd=6)
            entrada.insert(0, valor_inicial)
            entrada.pack(fill="x", pady=(2, 0))
            return entrada

        # Campos del formulario
        e_codigo    = campo("Código *", datos["codigo"]    if datos else "")
        e_nombre    = campo("Nombre *", datos["nombre"]    if datos else "")
        e_municipio = campo("Municipio", datos.get("municipio", "") if datos else "")
        e_parroquia = campo("Parroquia", datos.get("parroquia", "") if datos else "")

        # Mensaje de error
        lbl_error = tk.Label(ventana, text="", font=("Arial", 9),
                             bg="#16213e", fg="#e94560")
        lbl_error.pack(pady=(4, 0))

        def guardar():
            id_asic = datos["id_asic"] if datos else None
            ok, msg = self.controller.guardar_asic(
                e_codigo.get(), e_nombre.get(),
                e_municipio.get(), e_parroquia.get(),
                id_asic
            )
            if ok:
                messagebox.showinfo("Exito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_asic()  # Recargamos la tabla
            else:
                lbl_error.config(text=msg)

        tk.Button(
            ventana,
            text="Guardar",
            font=("Arial", 11, "bold"),
            bg="#e94560", fg="#ffffff",
            relief="flat", cursor="hand2",
            command=guardar
        ).pack(fill="x", padx=25, pady=(10, 0), ipady=8)

    def _editar_asic(self):
        """Abre el formulario de edición con los datos del ASIC seleccionado."""
        seleccion = self.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.tabla_asic.item(seleccion[0])["values"]
        datos = {
            "id_asic":   valores[0],
            "codigo":    valores[1],
            "nombre":    valores[2],
            "municipio": valores[3],
            "parroquia": valores[4]
        }
        self._abrir_form_asic(datos)

    def _eliminar_asic(self):
        """Elimina (desactiva) el ASIC seleccionado en la tabla."""
        seleccion = self.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.tabla_asic.item(seleccion[0])["values"]
        id_asic = valores[0]
        nombre  = valores[2]

        confirmar = messagebox.askyesno(
            "Confirmar eliminacion",
            f"¿Deseas eliminar el ASIC '{nombre}'?\nEsta accion no se puede deshacer."
        )
        if confirmar:
            ok, msg = self.controller.eliminar_asic(id_asic)
            if ok:
                messagebox.showinfo("Exito", msg)
                self._cargar_asic()
            else:
                messagebox.showerror("Error", msg)

    # ==========================================================
    # PESTAÑA: TIPOS DE ACTIVIDAD
    # (misma estructura que ASIC pero más simple)
    # ==========================================================

    def _construir_tab_tipos(self, parent):
        """Construye el contenido de la pestaña Tipos de Actividad."""

        barra = tk.Frame(parent, bg="#1a1a2e")
        barra.pack(fill="x", pady=(15, 10), padx=10)

        tk.Button(
            barra,
            text="+ Nuevo Tipo",
            font=("Arial", 10, "bold"),
            bg="#e94560", fg="#ffffff",
            relief="flat", cursor="hand2",
            padx=12, pady=6,
            command=self._abrir_form_tipo
        ).pack(side="left")

        tk.Button(
            barra,
            text="Actualizar",
            font=("Arial", 10),
            bg="#0f3460", fg="#ffffff",
            relief="flat", cursor="hand2",
            padx=12, pady=6,
            command=self._cargar_tipos
        ).pack(side="left", padx=(8, 0))

        marco_tabla = tk.Frame(parent, bg="#1a1a2e")
        marco_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columnas = ("id", "codigo", "nombre", "descripcion")
        self.tabla_tipos = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=15)

        self.tabla_tipos.heading("id",          text="ID")
        self.tabla_tipos.heading("codigo",      text="Código")
        self.tabla_tipos.heading("nombre",      text="Nombre")
        self.tabla_tipos.heading("descripcion", text="Descripción")

        self.tabla_tipos.column("id",          width=50,  anchor="center")
        self.tabla_tipos.column("codigo",      width=100, anchor="center")
        self.tabla_tipos.column("nombre",      width=220)
        self.tabla_tipos.column("descripcion", width=350)

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_tipos.yview)
        self.tabla_tipos.configure(yscrollcommand=scroll.set)
        self.tabla_tipos.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        barra_acciones = tk.Frame(parent, bg="#1a1a2e")
        barra_acciones.pack(fill="x", padx=10, pady=(5, 10))

        tk.Button(
            barra_acciones,
            text="Editar seleccionado",
            font=("Arial", 10),
            bg="#533483", fg="#ffffff",
            relief="flat", cursor="hand2",
            padx=12, pady=6,
            command=self._editar_tipo
        ).pack(side="left")

        tk.Button(
            barra_acciones,
            text="Eliminar seleccionado",
            font=("Arial", 10),
            bg="#333333", fg="#ff6b6b",
            relief="flat", cursor="hand2",
            padx=12, pady=6,
            command=self._eliminar_tipo
        ).pack(side="left", padx=(8, 0))

        self._cargar_tipos()

    def _cargar_tipos(self):
        """Recarga la tabla de tipos desde la base de datos."""
        for item in self.tabla_tipos.get_children():
            self.tabla_tipos.delete(item)

        lista = self.controller.listar_tipos()
        for tipo in lista:
            self.tabla_tipos.insert("", "end", values=(
                tipo["id_tipo"],
                tipo["codigo"],
                tipo["nombre"],
                tipo.get("descripcion", "") or ""
            ))

    def _abrir_form_tipo(self, datos=None):
        """Popup para crear o editar un tipo de actividad."""
        ventana = tk.Toplevel(self.parent)
        ventana.title("Nuevo Tipo" if datos is None else "Editar Tipo")
        ventana.geometry("420x320")
        ventana.resizable(False, False)
        ventana.configure(bg="#16213e")
        ventana.grab_set()

        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - 210
        y = (ventana.winfo_screenheight() // 2) - 160
        ventana.geometry(f"+{x}+{y}")

        tk.Label(
            ventana,
            text="Nuevo Tipo" if datos is None else "Editar Tipo",
            font=("Arial", 14, "bold"),
            bg="#16213e", fg="#ffffff"
        ).pack(pady=(20, 15))

        def campo(label_texto, valor_inicial=""):
            marco = tk.Frame(ventana, bg="#16213e")
            marco.pack(fill="x", padx=25, pady=4)
            tk.Label(marco, text=label_texto, font=("Arial", 9, "bold"),
                     bg="#16213e", fg="#ccd6f6", anchor="w").pack(fill="x")
            entrada = tk.Entry(marco, font=("Arial", 11), bg="#0f3460",
                               fg="#ffffff", insertbackground="#ffffff",
                               relief="flat", bd=6)
            entrada.insert(0, valor_inicial)
            entrada.pack(fill="x", pady=(2, 0))
            return entrada

        e_codigo      = campo("Código *",     datos["codigo"]      if datos else "")
        e_nombre      = campo("Nombre *",     datos["nombre"]      if datos else "")
        e_descripcion = campo("Descripción",  datos.get("descripcion", "") if datos else "")

        lbl_error = tk.Label(ventana, text="", font=("Arial", 9),
                             bg="#16213e", fg="#e94560")
        lbl_error.pack(pady=(4, 0))

        def guardar():
            id_tipo = datos["id_tipo"] if datos else None
            ok, msg = self.controller.guardar_tipo(
                e_codigo.get(), e_nombre.get(), e_descripcion.get(), id_tipo
            )
            if ok:
                messagebox.showinfo("Exito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_tipos()
            else:
                lbl_error.config(text=msg)

        tk.Button(
            ventana,
            text="Guardar",
            font=("Arial", 11, "bold"),
            bg="#e94560", fg="#ffffff",
            relief="flat", cursor="hand2",
            command=guardar
        ).pack(fill="x", padx=25, pady=(10, 0), ipady=8)

    def _editar_tipo(self):
        """Abre el formulario de edición con los datos del tipo seleccionado."""
        seleccion = self.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.tabla_tipos.item(seleccion[0])["values"]
        datos = {
            "id_tipo":     valores[0],
            "codigo":      valores[1],
            "nombre":      valores[2],
            "descripcion": valores[3]
        }
        self._abrir_form_tipo(datos)

    def _eliminar_tipo(self):
        """Elimina (desactiva) el tipo seleccionado."""
        seleccion = self.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.tabla_tipos.item(seleccion[0])["values"]
        id_tipo = valores[0]
        nombre  = valores[2]

        confirmar = messagebox.askyesno(
            "Confirmar eliminacion",
            f"¿Deseas eliminar el tipo '{nombre}'?"
        )
        if confirmar:
            ok, msg = self.controller.eliminar_tipo(id_tipo)
            if ok:
                messagebox.showinfo("Exito", msg)
                self._cargar_tipos()
            else:
                messagebox.showerror("Error", msg)
