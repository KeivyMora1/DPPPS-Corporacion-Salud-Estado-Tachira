from db import AuthController


class ModeloCuentas:
    def __init__(self):
        self.auth = AuthController()

    def puede_administrar(self):
        usuario = self.auth.obtener_usuario_actual()
        return bool(usuario and usuario.get("rol") == "propietario")

    def listar_cuentas(self):
        return self.auth.listar_cuentas()

    def crear_cuenta(
        self, nombre, apellido, email, password, username,
        cuenta_administrador=False,
    ):
        return self.auth.crear_cuenta(
            nombre,
            apellido,
            email,
            password,
            username=username,
            cuenta_administrador=cuenta_administrador,
        )


__all__ = ["ModeloCuentas"]
