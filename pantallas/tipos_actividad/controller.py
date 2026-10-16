from tkinter import messagebox

from .model import ModeloTipoActividad
from .view import VistaTipoActividad


class ControladorTipoActividad:
    def __init__(self, parent):
        self.modelo = ModeloTipoActividad()
        self.vista = VistaTipoActividad(parent, self)
        self.cargar_tipos()

    def puede_escribir(self):
        return self.modelo.puede_escribir()

    def cargar_tipos(self):
        try:
            tipos = self.modelo.listar_tipos()
            self.vista.mostrar_tipos(tipos)
        except Exception as exc:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron cargar los tipos de actividad: {exc}",
            )

    def guardar_tipo(self, nombre, id_tipo=None):
        try:
            if id_tipo is None:
                ok, mensaje = self.modelo.crear_tipo(nombre)
            else:
                ok, mensaje = self.modelo.actualizar_tipo(id_tipo, nombre)
        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"No se pudo guardar el tipo de actividad: {exc}",
            )
            return

        if not ok:
            messagebox.showwarning("No se pudo guardar", mensaje)
            return

        self.vista.cerrar_editor()
        self.cargar_tipos()


__all__ = ["ControladorTipoActividad"]
