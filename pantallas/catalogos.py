# ============================================================
# pantallas/catalogos.py
# Vista para gestionar los catálogos del sistema:
#   - ASIC (Áreas de Salud Integral Comunitaria)
#   - Tipos de Actividad
#
# Tiene dos modos: puede mostrar solo ASIC, solo Tipos,
# o ambos en pestañas (modo "catalogos").
# ============================================================

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from db import CatalogoController
from themes import THEMES


class CatalogoView:
    """
    Vista de catálogos con dos pestañas: ASIC y Tipos de Actividad.
    Se carga dentro del área de contenido de la ventana principal.
    """

    def __init__(self, parent, modo="catalogos", theme="dark"):
        self.parent     = parent
        self.controller = CatalogoController()
        self.modo       = modo
        self.t          = THEMES[theme]

        self._construir_ui()

    def _construir_ui(self):
        t = self.t

        titulo      = "Catálogos de ASIC"              if self.modo == "asic"   else \
                      "Catálogos de Tipos de Actividad" if self.modo == "tipos"  else \
                      "Catálogos"
        descripcion = "Gestiona los ASIC del sistema."  if self.modo == "asic"   else \
                      "Gestiona los tipos de actividad del sistema." if self.modo == "tipos" else \
                      "Gestiona las Áreas de Salud (ASIC) y los tipos de actividad del sistema."

        ctk.CTkLabel(self.parent, text=titulo,
                 font=("Arial", 18, "bold"), text_color=t["text_primary"]
                 ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(self.parent, text=descripcion,
                 font=("Arial", 10), text_color=t["text_muted"]
                 ).pack(anchor="w", padx=30, pady=(0, 15))

        if self.modo == "asic":
            self._construir_tab_asic(self.parent)
        elif self.modo == "tipos":
            self._construir_tab_tipos(self.parent)
        else:
            style = ttk.Style()
            style.theme_use("default")
            style.configure("TNotebook", background=t["bg_base"], borderwidth=0)
            style.configure("TNotebook.Tab",
                            background=t["bg_surface"],
                            foreground=t["text_muted"], padding=[16, 8], font=("Arial", 10))
            style.map("TNotebook.Tab",
                      background=[("selected", t["bg_card"])],
                      foreground=[("selected", t["text_primary"])])

            self.notebook = ttk.Notebook(self.parent)
            self.notebook.pack(fill="both", expand=True, padx=30, pady=(0, 20))

            tab_asic = ctk.CTkFrame(self.notebook, fg_color=t["bg_base"])
            self.notebook.add(tab_asic, text="  🏥  ASIC  ")
            self._construir_tab_asic(tab_asic)

            tab_tipos = ctk.CTkFrame(self.notebook, fg_color=t["bg_base"])
            self.notebook.add(tab_tipos, text="  📂  Tipos de Actividad  ")
            self._construir_tab_tipos(tab_tipos)

    def _construir_tab_asic(self, parent):
        t = self.t

        barra = ctk.CTkFrame(parent, fg_color="transparent")
        barra.pack(fill="x", pady=(15, 10), padx=10)

        ctk.CTkButton(barra, text="+ Nuevo ASIC",
                  font=("Arial", 10, "bold"), fg_color=t["accent"],
                  hover_color=t["accent_dim"], corner_radius=8,
                  command=self._abrir_form_asic
                  ).pack(side="left")

        ctk.CTkButton(barra, text="Actualizar",
                  font=("Arial", 10), fg_color=t["bg_card"],
                  hover_color=t["bg_hover"], corner_radius=8,
                  command=self._cargar_asic
                  ).pack(side="left", padx=(8, 0))

        marco_tabla = ctk.CTkFrame(parent, fg_color="transparent")
        marco_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columnas = ("id", "codigo", "nombre", "municipio", "parroquia")
        self.tabla_asic = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=15)

        style = ttk.Style()
        style.configure("ASIC.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=30, font=("Arial", 10))
        style.configure("ASIC.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        font=("Arial", 10, "bold"), relief="flat")
        style.map("ASIC.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["text_primary"])])

        self.tabla_asic.configure(style="ASIC.Treeview")

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

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_asic.yview)
        self.tabla_asic.configure(yscrollcommand=scroll.set)
        self.tabla_asic.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        barra_acciones = ctk.CTkFrame(parent, fg_color="transparent")
        barra_acciones.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(barra_acciones, text="Editar seleccionado",
                  font=("Arial", 10), fg_color=t["accent_dim"],
                  hover_color=t["accent"], corner_radius=8,
                  command=self._editar_asic
                  ).pack(side="left")

        ctk.CTkButton(barra_acciones, text="Eliminar seleccionado",
                  font=("Arial", 10), fg_color=t["red_bg"],
                  hover_color=t["red"], corner_radius=8,
                  command=self._eliminar_asic
                  ).pack(side="left", padx=(8, 0))

        self._cargar_asic()

    def _cargar_asic(self):
        for item in self.tabla_asic.get_children():
            self.tabla_asic.delete(item)
        for asic in self.controller.listar_asic():
            self.tabla_asic.insert("", "end", values=(
                asic["id_asic"],
                asic["codigo"],
                asic["nombre"],
                asic.get("municipio", ""),
                asic.get("parroquia", "")
            ))

    def _abrir_form_asic(self, datos=None):
        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Nuevo ASIC" if datos is None else "Editar ASIC")
        ventana.geometry("420x410")
        ventana.resizable(False, False)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.grab_set()

        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth()  // 2) - 210
        y = (ventana.winfo_screenheight() // 2) - 205
        ventana.geometry(f"+{x}+{y}")

        ctk.CTkLabel(ventana,
                 text="Nuevo ASIC" if datos is None else "Editar ASIC",
                 font=("Arial", 14, "bold"), text_color=t["text_primary"]
                 ).pack(pady=(20, 15))

        def campo(label_texto, valor_inicial=""):
            marco = ctk.CTkFrame(ventana, fg_color="transparent")
            marco.pack(fill="x", padx=25, pady=4)
            ctk.CTkLabel(marco, text=label_texto, font=("Arial", 9, "bold"),
                     text_color=t["text_muted"], anchor="w").pack(fill="x")
            entrada = ctk.CTkEntry(marco, font=("Arial", 11), fg_color=t["bg_card"],
                                   text_color=t["text_primary"],
                                   border_color=t["border"], corner_radius=6)
            entrada.insert(0, valor_inicial)
            entrada.pack(fill="x", pady=(2, 0))
            return entrada

        e_codigo    = campo("Código *",   datos["codigo"]            if datos else "")
        e_nombre    = campo("Nombre *",   datos["nombre"]            if datos else "")
        e_municipio = campo("Municipio",  datos.get("municipio", "") if datos else "")
        e_parroquia = campo("Parroquia",  datos.get("parroquia", "") if datos else "")

        lbl_error = ctk.CTkLabel(ventana, text="", font=("Arial", 9),
                             text_color=t["red"])
        lbl_error.pack(pady=(4, 0))

        def guardar():
            id_asic = datos["id_asic"] if datos else None
            ok, msg = self.controller.guardar_asic(
                e_codigo.get(), e_nombre.get(),
                e_municipio.get(), e_parroquia.get(), id_asic
            )
            if ok:
                messagebox.showinfo("Exito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_asic()
            else:
                lbl_error.configure(text=msg)

        ctk.CTkButton(ventana, text="Guardar",
                  font=("Arial", 11, "bold"), fg_color=t["accent"],
                  hover_color=t["accent_dim"], corner_radius=8, command=guardar
                  ).pack(fill="x", padx=25, pady=(10, 0), ipady=8)

    def _editar_asic(self):
        seleccion = self.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.tabla_asic.item(seleccion[0])["values"]
        datos   = {"id_asic": valores[0], "codigo": valores[1],
                   "nombre":  valores[2], "municipio": valores[3], "parroquia": valores[4]}
        self._abrir_form_asic(datos)

    def _eliminar_asic(self):
        seleccion = self.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.tabla_asic.item(seleccion[0])["values"]
        id_asic = valores[0]
        nombre  = valores[2]
        if messagebox.askyesno("Confirmar eliminacion",
                               f"¿Deseas eliminar el ASIC '{nombre}'?\nEsta accion no se puede deshacer."):
            ok, msg = self.controller.eliminar_asic(id_asic)
            if ok:
                messagebox.showinfo("Exito", msg)
                self._cargar_asic()
            else:
                messagebox.showerror("Error", msg)

    def _construir_tab_tipos(self, parent):
        t = self.t

        barra = ctk.CTkFrame(parent, fg_color="transparent")
        barra.pack(fill="x", pady=(15, 10), padx=10)

        ctk.CTkButton(barra, text="+ Nuevo Tipo",
                  font=("Arial", 10, "bold"), fg_color=t["accent"],
                  hover_color=t["accent_dim"], corner_radius=8,
                  command=self._abrir_form_tipo
                  ).pack(side="left")

        ctk.CTkButton(barra, text="Actualizar",
                  font=("Arial", 10), fg_color=t["bg_card"],
                  hover_color=t["bg_hover"], corner_radius=8,
                  command=self._cargar_tipos
                  ).pack(side="left", padx=(8, 0))

        marco_tabla = ctk.CTkFrame(parent, fg_color="transparent")
        marco_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columnas = ("id", "codigo", "nombre", "descripcion")
        self.tabla_tipos = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=15)

        style = ttk.Style()
        style.configure("Tipos.Treeview",
                        background=t["bg_base"], foreground=t["text_primary"],
                        fieldbackground=t["bg_base"], rowheight=30, font=("Arial", 10))
        style.configure("Tipos.Treeview.Heading",
                        background=t["bg_card"], foreground=t["text_primary"],
                        font=("Arial", 10, "bold"), relief="flat")
        style.map("Tipos.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["text_primary"])])

        self.tabla_tipos.configure(style="Tipos.Treeview")

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

        barra_acciones = ctk.CTkFrame(parent, fg_color="transparent")
        barra_acciones.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(barra_acciones, text="Editar seleccionado",
                  font=("Arial", 10), fg_color=t["accent_dim"],
                  hover_color=t["accent"], corner_radius=8,
                  command=self._editar_tipo
                  ).pack(side="left")

        ctk.CTkButton(barra_acciones, text="Eliminar seleccionado",
                  font=("Arial", 10), fg_color=t["red_bg"],
                  hover_color=t["red"], corner_radius=8,
                  command=self._eliminar_tipo
                  ).pack(side="left", padx=(8, 0))

        self._cargar_tipos()

    def _cargar_tipos(self):
        for item in self.tabla_tipos.get_children():
            self.tabla_tipos.delete(item)
        for tipo in self.controller.listar_tipos():
            self.tabla_tipos.insert("", "end", values=(
                tipo["id_tipo"],
                tipo["codigo"],
                tipo["nombre"],
                tipo.get("descripcion", "") or ""
            ))

    def _abrir_form_tipo(self, datos=None):
        t = self.t
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Nuevo Tipo" if datos is None else "Editar Tipo")
        ventana.geometry("420x360")
        ventana.resizable(False, False)
        ventana.configure(fg_color=t["bg_surface"])
        ventana.grab_set()

        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth()  // 2) - 210
        y = (ventana.winfo_screenheight() // 2) - 180
        ventana.geometry(f"+{x}+{y}")

        ctk.CTkLabel(ventana,
                 text="Nuevo Tipo" if datos is None else "Editar Tipo",
                 font=("Arial", 14, "bold"), text_color=t["text_primary"]
                 ).pack(pady=(20, 15))

        def campo(label_texto, valor_inicial=""):
            marco = ctk.CTkFrame(ventana, fg_color="transparent")
            marco.pack(fill="x", padx=25, pady=4)
            ctk.CTkLabel(marco, text=label_texto, font=("Arial", 9, "bold"),
                     text_color=t["text_muted"], anchor="w").pack(fill="x")
            entrada = ctk.CTkEntry(marco, font=("Arial", 11), fg_color=t["bg_card"],
                                   text_color=t["text_primary"],
                                   border_color=t["border"], corner_radius=6)
            entrada.insert(0, valor_inicial)
            entrada.pack(fill="x", pady=(2, 0))
            return entrada

        e_codigo      = campo("Código *",    datos["codigo"]              if datos else "")
        e_nombre      = campo("Nombre *",    datos["nombre"]              if datos else "")
        e_descripcion = campo("Descripción", datos.get("descripcion", "") if datos else "")

        lbl_error = ctk.CTkLabel(ventana, text="", font=("Arial", 9),
                             text_color=t["red"])
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
                lbl_error.configure(text=msg)

        ctk.CTkButton(ventana, text="Guardar",
                  font=("Arial", 11, "bold"), fg_color=t["accent"],
                  hover_color=t["accent_dim"], corner_radius=8, command=guardar
                  ).pack(fill="x", padx=25, pady=(10, 0), ipady=8)

    def _editar_tipo(self):
        seleccion = self.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.tabla_tipos.item(seleccion[0])["values"]
        datos   = {"id_tipo": valores[0], "codigo": valores[1],
                   "nombre":  valores[2], "descripcion": valores[3]}
        self._abrir_form_tipo(datos)

    def _eliminar_tipo(self):
        seleccion = self.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.tabla_tipos.item(seleccion[0])["values"]
        id_tipo = valores[0]
        nombre  = valores[2]
        if messagebox.askyesno("Confirmar eliminacion",
                               f"¿Deseas eliminar el tipo '{nombre}'?"):
            ok, msg = self.controller.eliminar_tipo(id_tipo)
            if ok:
                messagebox.showinfo("Exito", msg)
                self._cargar_tipos()
            else:
                messagebox.showerror("Error", msg)
