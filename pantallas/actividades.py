# ============================================================
# pantallas/actividades.py
# Vista para gestionar las Actividades de Salud del sistema.
# Contiene la barra de filtros, la tabla de visualización,
# y la ventana emergente para crear/editar actividades.
# ============================================================

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from db import ActividadController, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB
import os

from themes import THEMES

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

    def __init__(self, parent, theme="dark"):
        self.parent     = parent
        self.controller = ActividadController()
        self.t          = THEMES[theme]

        self.asic_map = {}
        self.tipo_map = {}

        self._cargar_catalogos()
        self._construir_ui()

    def _cargar_catalogos(self):
        try:
            asics = self.controller.listar_asics()
            self.asic_map = {a["nombre"]: a["id_asic"] for a in asics}

            tipos = self.controller.listar_tipos_actividad()
            self.tipo_map = {t["nombre"]: t["id_tipo"] for t in tipos}
        except Exception as e:
            messagebox.showerror("Error de base de datos", f"No se pudieron cargar los catalogos: {str(e)}")

    def _construir_ui(self):
        t = self.t

        ctk.CTkLabel(
            self.parent, text="Registro de Actividades",
            font=("Arial", 18, "bold"), text_color=t["text_primary"]
        ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(
            self.parent,
            text="Administra, busca y registra las jornadas y actividades medicas de las ASIC.",
            font=("Arial", 10), text_color=t["text_muted"]
        ).pack(anchor="w", padx=30, pady=(0, 15))

        marco_filtros = ctk.CTkFrame(
            self.parent, fg_color=t["bg_surface"], corner_radius=10,
            border_width=1, border_color=t["border"]
        )
        marco_filtros.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(marco_filtros, text="ASIC:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_filtro_asic = ttk.Combobox(marco_filtros, state="readonly", width=22, font=("Arial", 10))
        self.combo_filtro_asic.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Tipo:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_filtro_tipo = ttk.Combobox(marco_filtros, state="readonly", width=22, font=("Arial", 10))
        self.combo_filtro_tipo.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(marco_filtros, text="Desde:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.ent_filtro_desde = ctk.CTkEntry(marco_filtros, width=130, font=("Arial", 10),
                                              fg_color=t["bg_card"], text_color=t["text_primary"],
                                              border_color=t["border"], corner_radius=6)
        self.ent_filtro_desde.grid(row=0, column=5, padx=5, pady=5)
        self.ent_filtro_desde.bind("<FocusIn>",  lambda e: self._limpiar_placeholder_fecha(self.ent_filtro_desde))
        self.ent_filtro_desde.bind("<FocusOut>", lambda e: self._poner_placeholder_fecha(self.ent_filtro_desde))
        self._poner_placeholder_fecha(self.ent_filtro_desde)

        ctk.CTkLabel(marco_filtros, text="Hasta:", font=("Arial", 9, "bold"), text_color=t["text_muted"]).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.ent_filtro_hasta = ctk.CTkEntry(marco_filtros, width=130, font=("Arial", 10),
                                              fg_color=t["bg_card"], text_color=t["text_primary"],
                                              border_color=t["border"], corner_radius=6)
        self.ent_filtro_hasta.grid(row=0, column=7, padx=5, pady=5)
        self.ent_filtro_hasta.bind("<FocusIn>",  lambda e: self._limpiar_placeholder_fecha(self.ent_filtro_hasta))
        self.ent_filtro_hasta.bind("<FocusOut>", lambda e: self._poner_placeholder_fecha(self.ent_filtro_hasta))
        self._poner_placeholder_fecha(self.ent_filtro_hasta)

        nombres_asic = ["Todos"] + sorted(list(self.asic_map.keys()))
        nombres_tipo = ["Todos"] + sorted(list(self.tipo_map.keys()))
        self.combo_filtro_asic["values"] = nombres_asic
        self.combo_filtro_asic.current(0)
        self.combo_filtro_tipo["values"] = nombres_tipo
        self.combo_filtro_tipo.current(0)

        ctk.CTkButton(marco_filtros, text="Buscar", font=("Arial", 9, "bold"),
                      fg_color=t["accent"], hover_color=t["accent_dim"],
                      corner_radius=8, command=self._aplicar_filtros
                      ).grid(row=0, column=8, padx=10, pady=5)

        ctk.CTkButton(marco_filtros, text="Limpiar", font=("Arial", 9),
                      fg_color=t["bg_hover"], hover_color=t["border"],
                      corner_radius=8, command=self._limpiar_filtros
                      ).grid(row=0, column=9, padx=2, pady=5)

        marco_acciones_top = ctk.CTkFrame(self.parent, fg_color="transparent")
        marco_acciones_top.pack(fill="x", padx=30, pady=(10, 5))

        ctk.CTkButton(marco_acciones_top, text="+ Registrar Nueva Actividad",
                      font=("Arial", 10, "bold"), fg_color=t["accent"],
                      hover_color=t["accent_dim"], corner_radius=8,
                      command=self._abrir_form_nueva
                      ).pack(side="left")

        ctk.CTkButton(marco_acciones_top, text="Actualizar Tabla",
                      font=("Arial", 9), fg_color=t["bg_card"],
                      hover_color=t["bg_hover"], corner_radius=8,
                      command=self._cargar_datos_tabla
                      ).pack(side="left", padx=10)

        marco_tabla = ctk.CTkFrame(self.parent, fg_color="transparent", corner_radius=10)
        marco_tabla.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        columnas = ("id", "asic", "tipo", "fecha_inicio", "fecha_fin", "lugar", "participantes", "registrador")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=12)

        self.tabla.heading("id",            text="ID")
        self.tabla.heading("asic",          text="ASIC")
        self.tabla.heading("tipo",          text="Tipo de Actividad")
        self.tabla.heading("fecha_inicio",  text="F. Inicio")
        self.tabla.heading("fecha_fin",     text="F. Fin")
        self.tabla.heading("lugar",         text="Lugar")
        self.tabla.heading("participantes", text="Part.")
        self.tabla.heading("registrador",   text="Registrado Por")

        self.tabla.column("id",            width=45,  anchor="center")
        self.tabla.column("asic",          width=180, anchor="w")
        self.tabla.column("tipo",          width=180, anchor="w")
        self.tabla.column("fecha_inicio",  width=90,  anchor="center")
        self.tabla.column("fecha_fin",     width=90,  anchor="center")
        self.tabla.column("lugar",         width=140, anchor="w")
        self.tabla.column("participantes", width=60,  anchor="center")
        self.tabla.column("registrador",   width=120, anchor="w")

        style = ttk.Style()
        style.configure("Act.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=28)
        style.configure("Act.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        font=("Arial", 10, "bold"), relief="flat")
        style.map("Act.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["text_primary"])])

        self.tabla.configure(style="Act.Treeview")

        scroll_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        marco_acciones_bottom = ctk.CTkFrame(self.parent, fg_color="transparent")
        marco_acciones_bottom.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(marco_acciones_bottom, text="Editar Seleccionada",
                      font=("Arial", 10), fg_color=t["accent_dim"],
                      hover_color=t["accent"], corner_radius=8,
                      command=self._editar_seleccionada
                      ).pack(side="left")

        ctk.CTkButton(marco_acciones_bottom, text="Eliminar Seleccionada",
                      font=("Arial", 10), fg_color=t["red_bg"],
                      hover_color=t["red"], corner_radius=8,
                      command=self._eliminar_seleccionada
                      ).pack(side="left", padx=10)

        self._cargar_datos_tabla()

    def _poner_placeholder_fecha(self, entrada):
        t = self.t
        if entrada.get() == "":
            entrada.insert(0, "AAAA-MM-DD")
            entrada.configure(text_color=t["text_dim"])

    def _limpiar_placeholder_fecha(self, entrada):
        t = self.t
        if entrada.get() == "AAAA-MM-DD":
            entrada.delete(0, tk.END)
            entrada.configure(text_color=t["text_primary"])

    def _aplicar_filtros(self):
        asic_sel = self.combo_filtro_asic.get()
        tipo_sel = self.combo_filtro_tipo.get()
        f_desde  = self.ent_filtro_desde.get().strip()
        f_hasta  = self.ent_filtro_hasta.get().strip()

        filtros = {}

        if asic_sel != "Todos":
            filtros["id_asic"] = self.asic_map.get(asic_sel)
        if tipo_sel != "Todos":
            filtros["id_tipo"] = self.tipo_map.get(tipo_sel)

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
        self.combo_filtro_asic.current(0)
        self.combo_filtro_tipo.current(0)
        self.ent_filtro_desde.delete(0, tk.END)
        self._poner_placeholder_fecha(self.ent_filtro_desde)
        self.ent_filtro_hasta.delete(0, tk.END)
        self._poner_placeholder_fecha(self.ent_filtro_hasta)
        self._cargar_datos_tabla()

    def _cargar_datos_tabla(self, filtros=None):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            lista = self.controller.listar_actividades(filtros)
            for act in lista:
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

    def _abrir_formulario(self, datos_edicion=None):
        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Registrar Actividad" if datos_edicion is None else "Editar Actividad")
        ventana.geometry("520x680")
        ventana.resizable(False, False)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.grab_set()

        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth()  // 2) - 260
        y = (ventana.winfo_screenheight() // 2) - 340
        ventana.geometry(f"+{x}+{y}")

        ctk.CTkLabel(ventana,
                 text="Registrar Actividad" if datos_edicion is None else "Editar Actividad",
                 font=("Arial", 14, "bold"), text_color=t["text_primary"]
                 ).pack(pady=(15, 5))

        marco_form = ctk.CTkFrame(ventana, fg_color="transparent")
        marco_form.pack(fill="both", expand=True, padx=25, pady=5)

        ctk.CTkLabel(marco_form, text="ASIC *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(2, 2))
        combo_asic = ttk.Combobox(marco_form, state="readonly", font=("Arial", 10))
        combo_asic.pack(fill="x")
        nombres_asics = sorted(list(self.asic_map.keys()))
        combo_asic["values"] = nombres_asics

        ctk.CTkLabel(marco_form, text="Tipo de Actividad *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))
        combo_tipo = ttk.Combobox(marco_form, state="readonly", font=("Arial", 10))
        combo_tipo.pack(fill="x")
        nombres_tipos = sorted(list(self.tipo_map.keys()))
        combo_tipo["values"] = nombres_tipos

        marco_fechas = ctk.CTkFrame(marco_form, fg_color="transparent")
        marco_fechas.pack(fill="x", pady=8)

        col_izq = ctk.CTkFrame(marco_fechas, fg_color="transparent")
        col_izq.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(col_izq, text="Fecha de Inicio *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")

        col_der = ctk.CTkFrame(marco_fechas, fg_color="transparent")
        col_der.pack(side="right", fill="x", expand=True)
        ctk.CTkLabel(col_der, text="Fecha de Fin *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")

        if HAS_TKCALENDAR:
            ent_fecha_ini = DateEntry(col_izq, font=("Arial", 10), background=t["bg_card"], foreground=t["text_primary"], borderwidth=0, date_pattern="yyyy-mm-dd")
            ent_fecha_ini.pack(fill="x", pady=(2, 0))
            ent_fecha_fin = DateEntry(col_der, font=("Arial", 10), background=t["bg_card"], foreground=t["text_primary"], borderwidth=0, date_pattern="yyyy-mm-dd")
            ent_fecha_fin.pack(fill="x", pady=(2, 0))
        else:
            ent_fecha_ini = ctk.CTkEntry(col_izq, font=("Arial", 10), fg_color=t["bg_card"], text_color=t["text_primary"],
                                         border_color=t["border"], corner_radius=6)
            ent_fecha_ini.pack(fill="x", pady=(2, 0))
            ent_fecha_ini.insert(0, date.today().strftime("%Y-%m-%d"))
            ent_fecha_fin = ctk.CTkEntry(col_der, font=("Arial", 10), fg_color=t["bg_card"], text_color=t["text_primary"],
                                         border_color=t["border"], corner_radius=6)
            ent_fecha_fin.pack(fill="x", pady=(2, 0))
            ent_fecha_fin.insert(0, date.today().strftime("%Y-%m-%d"))

        marco_lug_part = ctk.CTkFrame(marco_form, fg_color="transparent")
        marco_lug_part.pack(fill="x", pady=4)

        col_lug = ctk.CTkFrame(marco_lug_part, fg_color="transparent")
        col_lug.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(col_lug, text="Lugar / Centro de Salud", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_lugar = ctk.CTkEntry(col_lug, font=("Arial", 10), fg_color=t["bg_card"], text_color=t["text_primary"],
                                 border_color=t["border"], corner_radius=6)
        ent_lugar.pack(fill="x", pady=(2, 0))

        col_part = ctk.CTkFrame(marco_lug_part, fg_color="transparent")
        col_part.pack(side="right", fill="x", expand=False, padx=(15, 0))
        ctk.CTkLabel(col_part, text="Participantes *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w")
        ent_participantes = ctk.CTkEntry(col_part, font=("Arial", 10), fg_color=t["bg_card"], text_color=t["text_primary"],
                                         border_color=t["border"], corner_radius=6, width=120)
        ent_participantes.pack(fill="x", pady=(2, 0))
        ent_participantes.insert(0, "0")

        ctk.CTkLabel(marco_form, text="Descripcion de la Actividad *", font=("Arial", 9, "bold"), text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))
        marco_txt = ctk.CTkFrame(marco_form, fg_color=t["bg_card"], corner_radius=6)
        marco_txt.pack(fill="x")
        txt_desc = tk.Text(marco_txt, font=("Arial", 10), bg=t["bg_card"], fg=t["text_primary"], relief="flat", height=3, insertbackground=t["text_primary"], wrap="word")
        txt_desc.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scroll_txt = ttk.Scrollbar(marco_txt, orient="vertical", command=txt_desc.yview)
        txt_desc.configure(yscrollcommand=scroll_txt.set)
        scroll_txt.pack(side="right", fill="y")

        marco_evidencias = ctk.CTkFrame(
            marco_form, fg_color=t["bg_surface"], corner_radius=10,
            border_width=1, border_color=t["border"]
        )
        marco_evidencias.pack(fill="x", pady=(10, 2))

        ctk.CTkLabel(marco_evidencias, text=" Evidencias / Adjuntos ",
                     font=("Arial", 9, "bold"), text_color=t["text_muted"]
                     ).pack(anchor="w", padx=10, pady=(5, 0))

        marco_ev_content = ctk.CTkFrame(marco_evidencias, fg_color="transparent")
        marco_ev_content.pack(fill="x", padx=10, pady=5)

        marco_lista_ev = ctk.CTkFrame(marco_ev_content, fg_color=t["bg_card"], corner_radius=6)
        marco_lista_ev.pack(side="left", fill="both", expand=True)
        listbox_evidencias = tk.Listbox(marco_lista_ev, font=("Arial", 9), bg=t["bg_card"], fg=t["text_primary"],
                                        selectbackground=t["accent"], relief="flat", height=3)
        listbox_evidencias.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scroll_ev = ttk.Scrollbar(marco_lista_ev, orient="vertical", command=listbox_evidencias.yview)
        listbox_evidencias.configure(yscrollcommand=scroll_ev.set)
        scroll_ev.pack(side="right", fill="y")

        marco_btns_ev = ctk.CTkFrame(marco_ev_content, fg_color="transparent")
        marco_btns_ev.pack(side="right", padx=(10, 0), fill="y")

        evidencias_locales_nuevas = []
        evidencias_existentes     = []
        id_actividad_edicion      = datos_edicion["id_actividad"] if datos_edicion else None

        def refrescar_lista_evidencias():
            listbox_evidencias.delete(0, tk.END)
            if id_actividad_edicion:
                evidencias_existentes.clear()
                try:
                    for ev in self.controller.listar_evidencias_de_actividad(id_actividad_edicion):
                        evidencias_existentes.append(ev)
                        listbox_evidencias.insert(tk.END, ev["nombre_archivo"])
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudieron cargar los adjuntos: {str(e)}", parent=ventana)
            else:
                for ruta in evidencias_locales_nuevas:
                    listbox_evidencias.insert(tk.END, os.path.basename(ruta))

        def adjuntar_archivo():
            ruta = filedialog.askopenfilename(
                title="Seleccionar evidencia",
                filetypes=[("Archivos permitidos", "*.jpg;*.jpeg;*.png;*.pdf;*.docx"),
                           ("Imagenes", "*.jpg;*.jpeg;*.png"),
                           ("Documentos", "*.pdf;*.docx"),
                           ("Todos los archivos", "*.*")],
                parent=ventana
            )
            if not ruta:
                return
            ext = os.path.splitext(ruta)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                messagebox.showerror("Error", f"Extension no permitida ({ext}). Permitidas: {', '.join(ALLOWED_EXTENSIONS)}", parent=ventana)
                return
            if os.path.getsize(ruta) > MAX_FILE_SIZE_MB * 1024 * 1024:
                messagebox.showerror("Error", f"El archivo supera el tamano maximo de {MAX_FILE_SIZE_MB} MB.", parent=ventana)
                return

            if id_actividad_edicion:
                ok_ev, msg_ev = self.controller.procesar_y_guardar_evidencia(id_actividad_edicion, ruta)
                if ok_ev:
                    messagebox.showinfo("Exito", msg_ev, parent=ventana)
                    refrescar_lista_evidencias()
                else:
                    messagebox.showerror("Error", msg_ev, parent=ventana)
            else:
                if ruta in evidencias_locales_nuevas:
                    messagebox.showwarning("Atencion", "Este archivo ya ha sido seleccionado.", parent=ventana)
                    return
                evidencias_locales_nuevas.append(ruta)
                refrescar_lista_evidencias()

        def quitar_archivo():
            seleccion = listbox_evidencias.curselection()
            if not seleccion:
                messagebox.showwarning("Atencion", "Selecciona un archivo de la lista para quitar.", parent=ventana)
                return
            idx = seleccion[0]
            if id_actividad_edicion:
                ev = evidencias_existentes[idx]
                if messagebox.askyesno("Confirmar eliminacion",
                                       f"¿Deseas eliminar permanentemente el archivo '{ev['nombre_archivo']}' del servidor?",
                                       parent=ventana):
                    ok_del, msg_del = self.controller.eliminar_evidencia(ev["id_evidencia"])
                    if ok_del:
                        messagebox.showinfo("Exito", msg_del, parent=ventana)
                        refrescar_lista_evidencias()
                    else:
                        messagebox.showerror("Error", msg_del, parent=ventana)
            else:
                evidencias_locales_nuevas.pop(idx)
                refrescar_lista_evidencias()

        ctk.CTkButton(marco_btns_ev, text="+ Adjuntar", font=("Arial", 9, "bold"),
                      fg_color=t["bg_card"], hover_color=t["bg_hover"],
                      corner_radius=8, command=adjuntar_archivo).pack(fill="x", pady=2)
        ctk.CTkButton(marco_btns_ev, text="- Quitar", font=("Arial", 9),
                      fg_color=t["red_bg"], hover_color=t["red"],
                      corner_radius=8, command=quitar_archivo).pack(fill="x", pady=2)

        refrescar_lista_evidencias()

        lbl_error = ctk.CTkLabel(ventana, text="", font=("Arial", 9), text_color=t["red"])
        lbl_error.pack(pady=3)

        if datos_edicion:
            if datos_edicion["asic_nombre"] in nombres_asics:
                combo_asic.set(datos_edicion["asic_nombre"])
            if datos_edicion["tipo_nombre"] in nombres_tipos:
                combo_tipo.set(datos_edicion["tipo_nombre"])
            if HAS_TKCALENDAR:
                ent_fecha_ini.set_date(datos_edicion["fecha_inicio"])
                ent_fecha_fin.set_date(datos_edicion["fecha_fin"])
            else:
                ent_fecha_ini.delete(0, tk.END)
                ent_fecha_ini.insert(0, datos_edicion["fecha_inicio"])
                ent_fecha_fin.delete(0, tk.END)
                ent_fecha_fin.insert(0, datos_edicion["fecha_fin"])
            ent_lugar.insert(0, datos_edicion["lugar"])
            ent_participantes.delete(0, tk.END)
            ent_participantes.insert(0, str(datos_edicion["participantes"]))
            txt_desc.insert("1.0", datos_edicion["descripcion"])

        def guardar():
            id_asic = self.asic_map.get(combo_asic.get())
            id_tipo = self.tipo_map.get(combo_tipo.get())
            f_ini   = ent_fecha_ini.get_date() if HAS_TKCALENDAR else ent_fecha_ini.get()
            f_fin   = ent_fecha_fin.get_date() if HAS_TKCALENDAR else ent_fecha_fin.get()

            ok, msg = self.controller.guardar_actividad(
                id_asic=id_asic,
                id_tipo=id_tipo,
                fecha_inicio=f_ini,
                fecha_fin=f_fin,
                lugar=ent_lugar.get(),
                descripcion=txt_desc.get("1.0", "end-1c"),
                participantes=ent_participantes.get(),
                id_actividad=id_actividad_edicion,
                evidencias_temporales=evidencias_locales_nuevas if id_actividad_edicion is None else None
            )
            if ok:
                messagebox.showinfo("Exito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_datos_tabla()
            else:
                lbl_error.configure(text=msg)

        ctk.CTkButton(ventana, text="Guardar Actividad",
                      font=("Arial", 11, "bold"), fg_color=t["accent"],
                      hover_color=t["accent_dim"], corner_radius=8, command=guardar
                      ).pack(fill="x", padx=25, pady=(5, 15), ipady=8)

    def _abrir_form_nueva(self):
        self._abrir_formulario()

    def _editar_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona una actividad de la tabla para editar.")
            return
        valores = self.tabla.item(seleccion[0])["values"]
        id_actividad = valores[0]
        try:
            act = self.controller.actividad_dao.obtener_por_id(id_actividad)
            if not act:
                messagebox.showerror("Error", "No se pudo recuperar la informacion de la actividad.")
                return
            self._abrir_formulario(act)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrio un error al obtener la actividad: {str(e)}")

    def _eliminar_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona una actividad de la tabla para eliminar.")
            return
        valores     = self.tabla.item(seleccion[0])["values"]
        id_actividad = valores[0]
        tipo_act     = valores[2]
        fecha_act    = valores[3]

        if messagebox.askyesno("Confirmar eliminacion",
                               f"¿Deseas eliminar la actividad '{tipo_act}' del dia {fecha_act}?\nEsta accion no se puede deshacer de forma directa."):
            try:
                ok, msg = self.controller.eliminar_actividad(id_actividad)
                if ok:
                    messagebox.showinfo("Exito", msg)
                    self._cargar_datos_tabla()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la actividad: {str(e)}")
