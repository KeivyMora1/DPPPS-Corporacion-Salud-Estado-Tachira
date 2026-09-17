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
from ui_helpers import (
    frame, frame_transparent, label, label_title, label_subtitle,
    btn_primary, btn_secondary, btn_danger, separator, treeview_style
)


class CatalogoView:
    """
    Vista de catálogos con dos pestañas: ASIC y Tipos de Actividad.
    Se carga dentro del área de contenido de la ventana principal.
    """

    def __init__(self, parent, modo="catalogos"):
        self.parent     = parent
        self.controller = CatalogoController()
        self.modo       = modo

        self._construir_ui()

    def _construir_ui(self):
        titulo = {
            "asic": "Catálogos de ASIC",
            "tipos": "Catálogos de Tipos de Actividad",
        }.get(self.modo, "Catálogos")

        descripcion = {
            "asic": "Gestiona los ASIC del sistema.",
            "tipos": "Gestiona los tipos de actividad del sistema.",
        }.get(self.modo, "Gestiona las Áreas de Salud (ASIC) y los tipos de actividad del sistema.")

        label_title(self.parent, titulo).pack(anchor="w", padx=30, pady=(25, 2))
        label_subtitle(self.parent, descripcion).pack(anchor="w", padx=30, pady=(0, 15))

        if self.modo == "asic":
            self._construir_tab_asic(self.parent)
        elif self.modo == "tipos":
            self._construir_tab_tipos(self.parent)
        else:
            style = ttk.Style()
            style.theme_use("default")
            style.configure("TNotebook", background="gray15", borderwidth=0)
            style.configure("TNotebook.Tab",
                            background="gray20",
                            foreground="gray70", padding=[16, 8], font=("Arial", 10))
            style.map("TNotebook.Tab",
                      background=[("selected", "gray25")],
                      foreground=[("selected", "white")])

            self.notebook = ttk.Notebook(self.parent)
            self.notebook.pack(fill="both", expand=True, padx=30, pady=(0, 20))

            tab_asic = frame(self.notebook, fg_color="gray15")
            self.notebook.add(tab_asic, text="  🏥  ASIC  ")
            self._construir_tab_asic(tab_asic)

            tab_tipos = frame(self.notebook, fg_color="gray15")
            self.notebook.add(tab_tipos, text="  📂  Tipos de Actividad  ")
            self._construir_tab_tipos(tab_tipos)

    def _crear_barra_acciones(self, parent, btn_nuevo_text, cmd_nuevo, cmd_actualizar):
        barra = frame_transparent(parent)
        barra.pack(fill="x", pady=(15, 10), padx=10)

        btn_primary(barra, btn_nuevo_text, cmd_nuevo).pack(side="left")
        btn_secondary(barra, "Actualizar", cmd_actualizar).pack(side="left", padx=(8, 0))
        return barra

    def _crear_tabla(self, parent, columnas, headings, widths, estilo_nombre):
        treeview_style(estilo_nombre, 30)

        marco_tabla = frame_transparent(parent)
        marco_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tree = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=15, style=f"{estilo_nombre}.Treeview")
        for col, heading, width in zip(columnas, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor="center" if col in ("id", "codigo") else "w")

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _crear_barra_botones(self, parent, cmd_editar, cmd_eliminar):
        barra = frame_transparent(parent)
        barra.pack(fill="x", padx=10, pady=(5, 10))

        btn_secondary(barra, "Editar seleccionado", cmd_editar).pack(side="left")
        btn_danger(barra, "Eliminar seleccionado", cmd_eliminar).pack(side="left", padx=(8, 0))
        return barra

    def _construir_tab_asic(self, parent):
        self._crear_barra_acciones(parent, "+ Nuevo ASIC", self._abrir_form_asic, self._cargar_asic)

        self.tabla_asic = self._crear_tabla(
            parent,
            ("id", "codigo", "nombre", "municipio", "parroquia"),
            ("ID", "Código", "Nombre", "Municipio", "Parroquia"),
            (50, 100, 250, 150, 150),
            "ASIC"
        )

        self._crear_barra_botones(parent, self._editar_asic, self._eliminar_asic)
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
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Nuevo ASIC" if datos is None else "Editar ASIC")
        ventana.geometry("420x410")
        ventana.resizable(False, False)
        ventana.configure(fg_color="gray20")
        ventana.grab_set()
        self._centrar_ventana(ventana, 420, 410)

        label(ventana, ventana.title(), font_size=14, bold=True).pack(pady=(20, 15))

        def campo(label_texto, valor_inicial=""):
            marco = frame_transparent(ventana)
            marco.pack(fill="x", padx=25, pady=4)
            label(marco, label_texto, font_size=9, bold=True).pack(fill="x")
            entrada = ctk.CTkEntry(marco, font=("Arial", 11), corner_radius=6)
            entrada.insert(0, valor_inicial)
            entrada.pack(fill="x", pady=(2, 0))
            return entrada

        e_codigo    = campo("Código *",   datos["codigo"]            if datos else "")
        e_nombre    = campo("Nombre *",   datos["nombre"]            if datos else "")
        e_municipio = campo("Municipio",  datos.get("municipio", "") if datos else "")
        e_parroquia = campo("Parroquia",  datos.get("parroquia", "") if datos else "")

        lbl_error = label(ventana, "", font_size=9, text_color="#c45050")
        lbl_error.pack(pady=(4, 0))

        def guardar():
            id_asic = datos["id_asic"] if datos else None
            ok, msg = self.controller.guardar_asic(
                e_codigo.get(), e_nombre.get(),
                e_municipio.get(), e_parroquia.get(), id_asic
            )
            if ok:
                messagebox.showinfo("Éxito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_asic()
            else:
                lbl_error.configure(text=msg)

        btn_primary(ventana, "Guardar", guardar).pack(fill="x", padx=25, pady=(10, 0), ipady=8)

    def _centrar_ventana(self, ventana, w, h):
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth()  // 2) - (w // 2)
        y = (ventana.winfo_screenheight() // 2) - (h // 2)
        ventana.geometry(f"+{x}+{y}")

    def _editar_asic(self):
        seleccion = self.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.tabla_asic.item(seleccion[0])["values"]
        datos = {"id_asic": valores[0], "codigo": valores[1],
                 "nombre":  valores[2], "municipio": valores[3], "parroquia": valores[4]}
        self._abrir_form_asic(datos)

    def _eliminar_asic(self):
        seleccion = self.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.tabla_asic.item(seleccion[0])["values"]
        id_asic = valores[0]
        nombre  = valores[2]
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Deseas eliminar el ASIC '{nombre}'?\nEsta acción no se puede deshacer."):
            ok, msg = self.controller.eliminar_asic(id_asic)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self._cargar_asic()
            else:
                messagebox.showerror("Error", msg)

    def _construir_tab_tipos(self, parent):
        self._crear_barra_acciones(parent, "+ Nuevo Tipo", self._abrir_form_tipo, self._cargar_tipos)

        self.tabla_tipos = self._crear_tabla(
            parent,
            ("id", "codigo", "nombre"),
            ("ID", "Código", "Nombre"),
            (50, 120, 320),
            "Tipos"
        )

        self._crear_barra_botones(parent, self._editar_tipo, self._eliminar_tipo)
        self._cargar_tipos()

    def _cargar_tipos(self):
        for item in self.tabla_tipos.get_children():
            self.tabla_tipos.delete(item)
        for tipo in self.controller.listar_tipos():
            self.tabla_tipos.insert("", "end", values=(
                tipo["id_tipo"],
                tipo["codigo"],
                tipo["nombre"]
            ))

    def _abrir_form_tipo(self, datos=None):
        ventana = ctk.CTkToplevel(self.parent)
        ventana.title("Nuevo Tipo" if datos is None else "Editar Tipo")
        ventana.geometry("420x260")
        ventana.resizable(False, False)
        ventana.configure(fg_color="gray20")
        ventana.grab_set()
        self._centrar_ventana(ventana, 420, 260)

        label(ventana, ventana.title(), font_size=14, bold=True).pack(pady=(20, 15))

        def campo(label_texto, valor_inicial=""):
            marco = frame_transparent(ventana)
            marco.pack(fill="x", padx=25, pady=4)
            label(marco, label_texto, font_size=9, bold=True).pack(fill="x")
            entrada = ctk.CTkEntry(marco, font=("Arial", 11), corner_radius=6)
            entrada.insert(0, valor_inicial)
            entrada.pack(fill="x", pady=(2, 0))
            return entrada

        e_codigo = campo("Código *", datos["codigo"] if datos else "")
        e_nombre = campo("Nombre *", datos["nombre"] if datos else "")

        lbl_error = label(ventana, "", font_size=9, text_color="#c45050")
        lbl_error.pack(pady=(4, 0))

        def guardar():
            id_tipo = datos["id_tipo"] if datos else None
            ok, msg = self.controller.guardar_tipo(
                e_codigo.get(), e_nombre.get(), id_tipo
            )
            if ok:
                messagebox.showinfo("Éxito", msg, parent=ventana)
                ventana.destroy()
                self._cargar_tipos()
            else:
                lbl_error.configure(text=msg)

        btn_primary(ventana, "Guardar", guardar).pack(fill="x", padx=25, pady=(10, 0), ipady=8)

    def _editar_tipo(self):
        seleccion = self.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.tabla_tipos.item(seleccion[0])["values"]
        datos = {"id_tipo": valores[0], "codigo": valores[1], "nombre": valores[2]}
        self._abrir_form_tipo(datos)

    def _eliminar_tipo(self):
        seleccion = self.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.tabla_tipos.item(seleccion[0])["values"]
        id_tipo = valores[0]
        nombre  = valores[2]
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Deseas eliminar el tipo '{nombre}'?"):
            ok, msg = self.controller.eliminar_tipo(id_tipo)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self._cargar_tipos()
            else:
                messagebox.showerror("Error", msg)