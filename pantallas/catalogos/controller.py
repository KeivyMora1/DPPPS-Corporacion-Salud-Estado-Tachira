from tkinter import messagebox

from .model import ModeloCatalogo
from .view import VistaCatalogo

class ControladorCatalogo:
    def __init__(self, parent, modo="catalogos"):
        self.modelo = ModeloCatalogo()
        self.vista = VistaCatalogo(parent, self, modo)

    def cargar_asic(self):
        for item in self.vista.tabla_asic.get_children():
            self.vista.tabla_asic.delete(item)
        for asic in self.modelo.listar_asic():
            self.vista.tabla_asic.insert("", "end", values=(
                asic["id_asic"],
                asic["codigo"],
                asic["nombre"],
                asic.get("municipio", ""),
                asic.get("parroquia", "")
            ))

    def abrir_form_asic(self, datos=None):
        self.vista.abrir_formulario_asic(datos)

    def guardar_asic(self, codigo, nombre, municipio, parroquia, id_asic=None):
        return self.modelo.guardar_asic(codigo, nombre, municipio, parroquia, id_asic)

    def editar_asic(self):
        seleccion = self.vista.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.vista.tabla_asic.item(seleccion[0])["values"]
        datos = {"id_asic": valores[0], "codigo": valores[1],
                 "nombre":  valores[2], "municipio": valores[3], "parroquia": valores[4]}
        self.vista.abrir_formulario_asic(datos)

    def eliminar_asic(self):
        seleccion = self.vista.tabla_asic.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un ASIC de la tabla primero.")
            return
        valores = self.vista.tabla_asic.item(seleccion[0])["values"]
        id_asic = valores[0]
        nombre  = valores[2]
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Deseas eliminar el ASIC '{nombre}'?\nEsta acción no se puede deshacer."):
            ok, msg = self.modelo.eliminar_asic(id_asic)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_asic()
            else:
                messagebox.showerror("Error", msg)

    def cargar_tipos(self):
        for item in self.vista.tabla_tipos.get_children():
            self.vista.tabla_tipos.delete(item)
        for tipo in self.modelo.listar_tipos():
            self.vista.tabla_tipos.insert("", "end", values=(
                tipo["id_tipo"],
                tipo["codigo"],
                tipo["nombre"]
            ))

    def abrir_form_tipo(self, datos=None):
        self.vista.abrir_formulario_tipo(datos)

    def guardar_tipo(self, codigo, nombre, id_tipo=None):
        return self.modelo.guardar_tipo(codigo, nombre, id_tipo)

    def editar_tipo(self):
        seleccion = self.vista.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.vista.tabla_tipos.item(seleccion[0])["values"]
        datos = {"id_tipo": valores[0], "codigo": valores[1], "nombre": valores[2]}
        self.vista.abrir_formulario_tipo(datos)

    def eliminar_tipo(self):
        seleccion = self.vista.tabla_tipos.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un tipo de la tabla primero.")
            return
        valores = self.vista.tabla_tipos.item(seleccion[0])["values"]
        id_tipo = valores[0]
        nombre  = valores[2]
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Deseas eliminar el tipo '{nombre}'?"):
            ok, msg = self.modelo.eliminar_tipo(id_tipo)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_tipos()
            else:
                messagebox.showerror("Error", msg)

__all__ = ['ControladorCatalogo']
