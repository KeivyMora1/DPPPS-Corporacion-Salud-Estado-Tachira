# ============================================================
# views/actividad_view.py
# Vista para gestionar las Actividades de Salud del sistema.
# Contiene la barra de filtros, la tabla de visualización,
# y la ventana emergente para crear/editar actividades.
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from controllers.actividad_controller import ActividadController

# Intentamos importar DateEntry de tkcalendar para mejorar la experiencia de usuario
try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False


class ActividadView:
    """
    Vista principal de Actividades.
    Se carga en el panel de contenido de la ventana principal.
    """

    def __init__(self, parent):
        self.parent = parent
        self.controller = ActividadController()
        
        # Mapeos de nombres de combo a IDs
        self.asic_map = {}
        self.tipo_map = {}
        
        # Cargar catálogos iniciales
        self._cargar_catalogos()

        # Construir la interfaz de usuario
        self._construir_ui()

    def _cargar_catalogos(self):
        """Obtiene las listas de ASIC y tipos de actividad para los Combobox."""
        try:
            # Cargar ASIC
            asics = self.controller.listar_asics()
            self.asic_map = {a["nombre"]: a["id_asic"] for a in asics}
            
            # Cargar Tipos de Actividad
            tipos = self.controller.listar_tipos_actividad()
            self.tipo_map = {t["nombre"]: t["id_tipo"] for t in tipos}
        except Exception as e:
            messagebox.showerror("Error de base de datos", f"No se pudieron cargar los catalogos: {str(e)}")

    def _construir_ui(self):
        """Dibuja todos los componentes de la vista en el panel padre."""
        
        # --- TÍTULO DE LA SECCIÓN ---
        tk.Label(
            self.parent,
            text="Registro de Actividades",
            font=("Arial", 18, "bold"),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack(anchor="w", padx=30, pady=(25, 2))

        tk.Label(
            self.parent,
            text="Administra, busca y registra las jornadas y actividades medicas de las ASIC.",
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="#8892b0"
        ).pack(anchor="w", padx=30, pady=(0, 15))

        # --- PANEL DE FILTROS ---
        marco_filtros = tk.LabelFrame(
            self.parent,
            text=" Filtros de Busqueda ",
            font=("Arial", 9, "bold"),
            bg="#16213e",
            fg="#ccd6f6",
            padx=15,
            pady=10,
            relief="flat"
        )
        marco_filtros.pack(fill="x", padx=30, pady=(0, 10))

        # Filtro: ASIC
        tk.Label(marco_filtros, text="ASIC:", font=("Arial", 9, "bold"), bg="#16213e", fg="#8892b0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_filtro_asic = ttk.Combobox(marco_filtros, state="readonly", width=22, font=("Arial", 10))
        self.combo_filtro_asic.grid(row=0, column=1, padx=5, pady=5)
        
        # Filtro: Tipo de Actividad
        tk.Label(marco_filtros, text="Tipo:", font=("Arial", 9, "bold"), bg="#16213e", fg="#8892b0").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_filtro_tipo = ttk.Combobox(marco_filtros, state="readonly", width=22, font=("Arial", 10))
        self.combo_filtro_tipo.grid(row=0, column=3, padx=5, pady=5)

        # Filtro: Fecha Desde
        tk.Label(marco_filtros, text="Desde:", font=("Arial", 9, "bold"), bg="#16213e", fg="#8892b0").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.ent_filtro_desde = tk.Entry(marco_filtros, width=12, font=("Arial", 10), bg="#0f3460", fg="#ffffff", relief="flat", bd=3)
        self.ent_filtro_desde.insert(0, "")
        self.ent_filtro_desde.grid(row=0, column=5, padx=5, pady=5)
        # Pequeño tooltip / placeholder implícito
        self.ent_filtro_desde.bind("<FocusIn>", lambda e: self._limpiar_placeholder_fecha(self.ent_filtro_desde))
        self.ent_filtro_desde.bind("<FocusOut>", lambda e: self._poner_placeholder_fecha(self.ent_filtro_desde))
        self._poner_placeholder_fecha(self.ent_filtro_desde)

        # Filtro: Fecha Hasta
        tk.Label(marco_filtros, text="Hasta:", font=("Arial", 9, "bold"), bg="#16213e", fg="#8892b0").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.ent_filtro_hasta = tk.Entry(marco_filtros, width=12, font=("Arial", 10), bg="#0f3460", fg="#ffffff", relief="flat", bd=3)
        self.ent_filtro_hasta.insert(0, "")
        self.ent_filtro_hasta.grid(row=0, column=7, padx=5, pady=5)
        self.ent_filtro_hasta.bind("<FocusIn>", lambda e: self._limpiar_placeholder_fecha(self.ent_filtro_hasta))
        self.ent_filtro_hasta.bind("<FocusOut>", lambda e: self._poner_placeholder_fecha(self.ent_filtro_hasta))
        self._poner_placeholder_fecha(self.ent_filtro_hasta)

        # Llenar combos de filtros
        nombres_asic = ["Todos"] + sorted(list(self.asic_map.keys()))
        nombres_tipo = ["Todos"] + sorted(list(self.tipo_map.keys()))
        self.combo_filtro_asic["values"] = nombres_asic
        self.combo_filtro_asic.current(0)
        self.combo_filtro_tipo["values"] = nombres_tipo
        self.combo_filtro_tipo.current(0)

        # Botones de Filtro
        btn_filtrar = tk.Button(
            marco_filtros,
            text="Buscar",
            font=("Arial", 9, "bold"),
            bg="#e94560",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12,
            command=self._aplicar_filtros
        )
        btn_filtrar.grid(row=0, column=8, padx=10, pady=5)

        btn_limpiar = tk.Button(
            marco_filtros,
            text="Limpiar",
            font=("Arial", 9),
            bg="#333333",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=10,
            command=self._limpiar_filtros
        )
        btn_limpiar.grid(row=0, column=9, padx=2, pady=5)

        # --- BOTÓN NUEVA ACTIVIDAD ---
        marco_acciones_top = tk.Frame(self.parent, bg="#1a1a2e")
        marco_acciones_top.pack(fill="x", padx=30, pady=(10, 5))

        tk.Button(
            marco_acciones_top,
            text="+ Registrar Nueva Actividad",
            font=("Arial", 10, "bold"),
            bg="#e94560",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=7,
            command=self._abrir_form_nueva
        ).pack(side="left")

        tk.Button(
            marco_acciones_top,
            text="Actualizar Tabla",
            font=("Arial", 9),
            bg="#0f3460",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
            command=self._cargar_datos_tabla
        ).pack(side="left", padx=10)

        # --- TABLA DE ACTIVIDADES ---
        marco_tabla = tk.Frame(self.parent, bg="#1a1a2e")
        marco_tabla.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        # Columnas de la tabla
        columnas = ("id", "asic", "tipo", "fecha_inicio", "fecha_fin", "lugar", "participantes", "registrador")
        self.tabla = ttk.Treeview(
            marco_tabla,
            columns=columnas,
            show="headings",
            height=12
        )

        # Configurar encabezados
        self.tabla.heading("id",           text="ID")
        self.tabla.heading("asic",         text="ASIC")
        self.tabla.heading("tipo",         text="Tipo de Actividad")
        self.tabla.heading("fecha_inicio", text="F. Inicio")
        self.tabla.heading("fecha_fin",    text="F. Fin")
        self.tabla.heading("lugar",        text="Lugar")
        self.tabla.heading("participantes",text="Part.")
        self.tabla.heading("registrador",  text="Registrado Por")

        # Configurar anchos y alineaciones
        self.tabla.column("id",            width=45,  anchor="center")
        self.tabla.column("asic",          width=180, anchor="w")
        self.tabla.column("tipo",          width=180, anchor="w")
        self.tabla.column("fecha_inicio",  width=90,  anchor="center")
        self.tabla.column("fecha_fin",     width=90,  anchor="center")
        self.tabla.column("lugar",         width=140, anchor="w")
        self.tabla.column("participantes", width=60,  anchor="center")
        self.tabla.column("registrador",   width=120, anchor="w")

        # Scrollbars
        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # --- ACCIONES DE EDICIÓN Y ELIMINACIÓN ---
        marco_acciones_bottom = tk.Frame(self.parent, bg="#1a1a2e")
        marco_acciones_bottom.pack(fill="x", padx=30, pady=(0, 20))

        tk.Button(
            marco_acciones_bottom,
            text="Editar Seleccionada",
            font=("Arial", 10),
            bg="#533483",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=7,
            command=self._editar_seleccionada
        ).pack(side="left")

        tk.Button(
            marco_acciones_bottom,
            text="Eliminar Seleccionada",
            font=("Arial", 10),
            bg="#333333",
            fg="#ff6b6b",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=7,
            command=self._eliminar_seleccionada
        ).pack(side="left", padx=10)

        # Cargar los datos iniciales
        self._cargar_datos_tabla()

    # --- CONTROL DE PLACEHOLDERS EN FILTROS ---
    def _poner_placeholder_fecha(self, entrada):
        if entrada.get() == "":
            entrada.insert(0, "AAAA-MM-DD")
            entrada.config(fg="#8892b0")

    def _limpiar_placeholder_fecha(self, entrada):
        if entrada.get() == "AAAA-MM-DD":
            entrada.delete(0, tk.END)
            entrada.config(fg="#ffffff")

    # --- LÓGICA DE FILTRADO ---
    def _aplicar_filtros(self):
        """Lee los campos de filtro y actualiza la tabla."""
        asic_sel = self.combo_filtro_asic.get()
        tipo_sel = self.combo_filtro_tipo.get()
        f_desde = self.ent_filtro_desde.get().strip()
        f_hasta = self.ent_filtro_hasta.get().strip()

        filtros = {}

        if asic_sel != "Todos":
            filtros["id_asic"] = self.asic_map.get(asic_sel)
        
        if tipo_sel != "Todos":
            filtros["id_tipo"] = self.tipo_map.get(tipo_sel)

        # Validar y agregar fechas de filtro
        if f_desde and f_desde != "AAAA-MM-DD":
            try:
                datetime.strptime(f_desde, "%Y-%m-%d")
                filtros["fecha_desde"] = f_desde
            except ValueError:
                messagebox.showerror("Error en Filtros", "La fecha 'Desde' debe tener el formato AAAA-MM-DD (ej: 2026-05-17).")
                return
        
        if f_hasta and f_hasta != "AAAA-MM-DD":
            try:
                datetime.strptime(f_hasta, "%Y-%m-%d")
                filtros["fecha_hasta"] = f_hasta
            except ValueError:
                messagebox.showerror("Error en Filtros", "La fecha 'Hasta' debe tener el formato AAAA-MM-DD (ej: 2026-05-17).")
                return

        self._cargar_datos_tabla(filtros)

    def _limpiar_filtros(self):
        """Reinicia todos los filtros a su estado por defecto."""
        self.combo_filtro_asic.current(0)
        self.combo_filtro_tipo.current(0)
        
        self.ent_filtro_desde.delete(0, tk.END)
        self._poner_placeholder_fecha(self.ent_filtro_desde)
        
        self.ent_filtro_hasta.delete(0, tk.END)
        self._poner_placeholder_fecha(self.ent_filtro_hasta)
        
        self._cargar_datos_tabla()

    def _cargar_datos_tabla(self, filtros=None):
        """Carga las actividades de la BD y las inserta en la tabla."""
        # Limpiar la tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            # Obtener datos
            lista = self.controller.listar_actividades(filtros)
            
            for act in lista:
                # Formatear fechas para mostrar en la interfaz
                f_ini = act["fecha_inicio"]
                f_fin = act["fecha_fin"]
                
                if isinstance(f_ini, (date, datetime)):
                    f_ini = f_ini.strftime("%d/%m/%Y")
                if isinstance(f_fin, (date, datetime)):
                    f_fin = f_fin.strftime("%d/%m/%Y")

                self.tabla.insert("", "end", values=(
                    act["id_actividad"],
                    act["asic_nombre"],
                    act["tipo_nombre"],
                    f_ini,
                    f_fin,
                    act["lugar"] or "",
                    act["participantes"],
                    act["usuario_nombre"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrio un error al cargar las actividades: {str(e)}")

    # --- VENTANA EMERGENTE: FORMULARIO ---
    def _abrir_formulario(self, datos_edicion=None):
        """
        Abre la ventana emergente para crear o editar una actividad.
        Si datos_edicion tiene información, carga los valores para edición.
        """
        ventana = tk.Toplevel(self.parent)
        ventana.title("Registrar Actividad" if datos_edicion is None else "Editar Actividad")
        ventana.geometry("500x550")
        ventana.resizable(False, False)
        ventana.configure(bg="#16213e")
        ventana.grab_set()  # Modal: bloquea interacción con la ventana de atrás

        # Centrar la ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - 250
        y = (ventana.winfo_screenheight() // 2) - 275
        ventana.geometry(f"+{x}+{y}")

        # Título
        lbl_titulo = tk.Label(
            ventana,
            text="Registrar Actividad" if datos_edicion is None else "Editar Actividad",
            font=("Arial", 14, "bold"),
            bg="#16213e", fg="#ffffff"
        )
        lbl_titulo.pack(pady=(15, 10))

        # --- ELEMENTOS DEL FORMULARIO ---
        # Panel interno con scroll si fuera necesario, pero cabe justo en 550px
        marco_form = tk.Frame(ventana, bg="#16213e")
        marco_form.pack(fill="both", expand=True, padx=25, pady=5)

        # 1. ASIC (Dropdown)
        tk.Label(marco_form, text="ASIC *", font=("Arial", 9, "bold"), bg="#16213e", fg="#ccd6f6").pack(anchor="w", pady=(5, 2))
        combo_asic = ttk.Combobox(marco_form, state="readonly", font=("Arial", 10))
        combo_asic.pack(fill="x")
        nombres_asics = sorted(list(self.asic_map.keys()))
        combo_asic["values"] = nombres_asics

        # 2. Tipo de Actividad (Dropdown)
        tk.Label(marco_form, text="Tipo de Actividad *", font=("Arial", 9, "bold"), bg="#16213e", fg="#ccd6f6").pack(anchor="w", pady=(10, 2))
        combo_tipo = ttk.Combobox(marco_form, state="readonly", font=("Arial", 10))
        combo_tipo.pack(fill="x")
        nombres_tipos = sorted(list(self.tipo_map.keys()))
        combo_tipo["values"] = nombres_tipos

        # Marco para Fechas
        marco_fechas = tk.Frame(marco_form, bg="#16213e")
        marco_fechas.pack(fill="x", pady=10)

        # 3. Fecha Inicio
        col_izq = tk.Frame(marco_fechas, bg="#16213e")
        col_izq.pack(side="left", fill="x", expand=True, padx=(0, 10)) # padding derecho
        tk.Label(col_izq, text="Fecha de Inicio *", font=("Arial", 9, "bold"), bg="#16213e", fg="#ccd6f6").pack(anchor="w")
        
        # 4. Fecha Fin
        col_der = tk.Frame(marco_fechas, bg="#16213e")
        col_der.pack(side="right", fill="x", expand=True)
        tk.Label(col_der, text="Fecha de Fin *", font=("Arial", 9, "bold"), bg="#16213e", fg="#ccd6f6").pack(anchor="w")

        # Widget de fecha según disponibilidad de tkcalendar
        if HAS_TKCALENDAR:
            ent_fecha_ini = DateEntry(col_izq, font=("Arial", 10), background="#0f3460", foreground="white", borderwidth=0, date_pattern="yyyy-mm-dd")
            ent_fecha_ini.pack(fill="x", pady=(2, 0))
            
            ent_fecha_fin = DateEntry(col_der, font=("Arial", 10), background="#0f3460", foreground="white", borderwidth=0, date_pattern="yyyy-mm-dd")
            ent_fecha_fin.pack(fill="x", pady=(2, 0))
        else:
            # Fallback simple
            ent_fecha_ini = tk.Entry(col_izq, font=("Arial", 10), bg="#0f3460", fg="#ffffff", relief="flat", bd=5)
            ent_fecha_ini.pack(fill="x", pady=(2, 0))
            ent_fecha_ini.insert(0, date.today().strftime("%Y-%m-%d"))

            ent_fecha_fin = tk.Entry(col_der, font=("Arial", 10), bg="#0f3460", fg="#ffffff", relief="flat", bd=5)
            ent_fecha_fin.pack(fill="x", pady=(2, 0))
            ent_fecha_fin.insert(0, date.today().strftime("%Y-%m-%d"))

        # Marco para Lugar y Participantes
        marco_lugar_part = tk.Frame(marco_form, bg="#16213e")
        marco_lugar_part.pack(fill="x", pady=5)

        # 5. Lugar
        col_lug = tk.Frame(marco_lugar_part, bg="#16213e")
        col_lug.pack(side="left", fill="x", expand=True)
        tk.Label(col_lug, text="Lugar / Centro de Salud", font=("Arial", 9, "bold"), bg="#16213e", fg="#ccd6f6").pack(anchor="w")
        ent_lugar = tk.Entry(col_lug, font=("Arial", 10), bg="#0f3460", fg="#ffffff", relief="flat", bd=5)
        ent_lugar.pack(fill="x", pady=(2, 0))

        # 6. Participantes
        col_part = tk.Frame(marco_lugar_part, bg="#16213e")
        col_part.pack(side="right", fill="x", expand=False, padx=(15, 0))
        tk.Label(col_part, text="Participantes *", font=("Arial", 9, "bold"), bg="#16213e", fg="#ccd6f6").pack(anchor="w")
        ent_participantes = tk.Entry(col_part, font=("Arial", 10), bg="#0f3460", fg="#ffffff", relief="flat", bd=5, width=12, justify="center")
        ent_participantes.pack(fill="x", pady=(2, 0))
        ent_participantes.insert(0, "0")

        # 7. Descripción (Caja de Texto)
        tk.Label(marco_form, text="Descripcion de la Actividad *", font=("Arial", 9, "bold"), bg="#16213e", fg="#ccd6f6").pack(anchor="w", pady=(10, 2))
        
        marco_txt = tk.Frame(marco_form, bg="#0f3460")
        marco_txt.pack(fill="both", expand=True)
        
        txt_desc = tk.Text(marco_txt, font=("Arial", 10), bg="#0f3460", fg="#ffffff", relief="flat", height=4, insertbackground="#ffffff", wrap="word")
        txt_desc.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        scroll_txt = ttk.Scrollbar(marco_txt, orient="vertical", command=txt_desc.yview)
        txt_desc.configure(yscrollcommand=scroll_txt.set)
        scroll_txt.pack(side="right", fill="y")

        # Mensaje de Error
        lbl_error = tk.Label(ventana, text="", font=("Arial", 9), bg="#16213e", fg="#e94560")
        lbl_error.pack(pady=3)

        # Si es edición, cargamos los datos
        id_actividad_edicion = None
        if datos_edicion:
            id_actividad_edicion = datos_edicion["id_actividad"]
            
            # Seleccionar en combo ASIC
            if datos_edicion["asic_nombre"] in nombres_asics:
                combo_asic.set(datos_edicion["asic_nombre"])
            
            # Seleccionar en combo Tipo
            if datos_edicion["tipo_nombre"] in nombres_tipos:
                combo_tipo.set(datos_edicion["tipo_nombre"])
            
            # Poner fechas
            if HAS_TKCALENDAR:
                ent_fecha_ini.set_date(datos_edicion["fecha_inicio"])
                ent_fecha_fin.set_date(datos_edicion["fecha_fin"])
            else:
                ent_fecha_ini.delete(0, tk.END)
                ent_fecha_ini.insert(0, datos_edicion["fecha_inicio"])
                ent_fecha_fin.delete(0, tk.END)
                ent_fecha_fin.insert(0, datos_edicion["fecha_fin"])

            # Lugar
            ent_lugar.insert(0, datos_edicion["lugar"])
            
            # Participantes
            ent_participantes.delete(0, tk.END)
            ent_participantes.insert(0, str(datos_edicion["participantes"]))
            
            # Descripción
            txt_desc.insert("1.0", datos_edicion["descripcion"])

        # Función de Guardado
        def guardar():
            # Obtener IDs a partir de los nombres seleccionados
            asic_sel = combo_asic.get()
            tipo_sel = combo_tipo.get()
            
            id_asic = self.asic_map.get(asic_sel)
            id_tipo = self.tipo_map.get(tipo_sel)
            
            # Obtener fechas
            f_ini = ent_fecha_ini.get_date() if HAS_TKCALENDAR else ent_fecha_ini.get()
            f_fin = ent_fecha_fin.get_date() if HAS_TKCALENDAR else ent_fecha_fin.get()

            # Obtener otros datos
            lugar_val = ent_lugar.get()
            part_val = ent_participantes.get()
            desc_val = txt_desc.get("1.0", "end-1c")

            # Enviar al controlador
            ok, msg = self.controller.guardar_actividad(
                id_asic=id_asic,
                id_tipo=id_tipo,
                fecha_inicio=f_ini,
                fecha_fin=f_fin,
                lugar=lugar_val,
                descripcion=desc_val,
                participantes=part_val,
                id_actividad=id_actividad_edicion
            )

            if ok:
                messagebox.showinfo("Exito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_datos_tabla()  # Recargar tabla principal
            else:
                lbl_error.config(text=msg)

        # Botón Guardar
        btn_guardar = tk.Button(
            ventana,
            text="Guardar Actividad",
            font=("Arial", 11, "bold"),
            bg="#e94560", fg="#ffffff",
            relief="flat", cursor="hand2",
            command=guardar
        )
        btn_guardar.pack(fill="x", padx=25, pady=(5, 15), ipady=8)

    def _abrir_form_nueva(self):
        """Abre el formulario vacío para registrar una nueva actividad."""
        self._abrir_formulario()

    def _editar_seleccionada(self):
        """Obtiene el registro seleccionado y abre el formulario de edición cargado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona una actividad de la tabla para editar.")
            return

        valores = self.tabla.item(seleccion[0])["values"]
        id_actividad = valores[0]

        # Buscamos la información completa de la actividad en la base de datos
        try:
            act = self.controller.actividad_dao.obtener_por_id(id_actividad)
            if not act:
                messagebox.showerror("Error", "No se pudo recuperar la informacion de la actividad.")
                return

            self._abrir_formulario(act)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrio un error al obtener la actividad: {str(e)}")

    def _eliminar_seleccionada(self):
        """Elimina de forma lógica (soft delete) la actividad seleccionada."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona una actividad de la tabla para eliminar.")
            return

        valores = self.tabla.item(seleccion[0])["values"]
        id_actividad = valores[0]
        tipo_act = valores[2]
        fecha_act = valores[3]

        confirmar = messagebox.askyesno(
            "Confirmar eliminacion",
            f"¿Deseas eliminar la actividad '{tipo_act}' del dia {fecha_act}?\nEsta accion no se puede deshacer de forma directa."
        )

        if confirmar:
            try:
                ok, msg = self.controller.eliminar_actividad(id_actividad)
                if ok:
                    messagebox.showinfo("Exito", msg)
                    self._cargar_datos_tabla()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la actividad: {str(e)}")
