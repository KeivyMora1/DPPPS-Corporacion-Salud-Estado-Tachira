from tkinter import messagebox

from .model import ModeloCuentas
from .view import VistaCuentas


class ControladorCuentas:
    def __init__(self, parent):
        self.modelo = ModeloCuentas()
        if not self.modelo.puede_administrar():
            raise PermissionError("Solo el usuario propietario puede acceder a Cuentas.")
        self.vista = VistaCuentas(parent, self)
        self.cargar_cuentas()

    def puede_administrar(self):
        return self.modelo.puede_administrar()

    def cargar_cuentas(self):
        try:
            cuentas = self.modelo.listar_cuentas()
            self.vista.mostrar_cuentas(cuentas)
        except Exception as exc:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron cargar las cuentas: {exc}",
            )

    def crear_cuenta(self, nombre, apellido, email, password, username, administrador):
        if not self.puede_administrar():
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el usuario propietario puede crear cuentas.",
            )
            return

        try:
            respuesta = self.modelo.crear_cuenta(
                nombre,
                apellido,
                email,
                password,
                username,
                administrador,
            )
        except Exception as exc:
            messagebox.showerror("Crear cuenta", f"No se pudo crear la cuenta: {exc}")
            return
        if not respuesta["success"]:
            messagebox.showerror("Crear cuenta", respuesta["message"])
            return

        messagebox.showinfo("Crear cuenta", respuesta["message"])
        self.vista.cerrar_editor()
        self.cargar_cuentas()

    def abrir_formulario(self):
        if self.puede_administrar():
            self.vista.abrir_formulario()


__all__ = ["ControladorCuentas"]
