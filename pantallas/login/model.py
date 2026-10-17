from db import AuthController

class ModeloLogin:
    def __init__(self):
        self.auth = AuthController()

    def login(self, email, password):
        return self.auth.login(email, password)

    def autenticar_pendiente_verificacion(self, credencial, password):
        return self.auth.autenticar_pendiente_verificacion(credencial, password)

    def registrar_usuario(self, nombre, apellido, email, password, username=None,
                          cuenta_administrador=False, password_propietario=None):
        return self.auth.registrar_usuario(
            nombre, apellido, email, password, username=username,
            cuenta_administrador=cuenta_administrador,
            password_propietario=password_propietario,
        )

    def verificar_email(self, email, codigo):
        return self.auth.verificar_email(email, codigo)

    def reenviar_codigo_verificacion(self, email):
        return self.auth.reenviar_codigo_verificacion(email)

    def solicitar_recuperacion(self, email):
        return self.auth.solicitar_recuperacion(email)

    def obtener_usuario_por_email(self, email):
        return self.auth.usuario_dao.obtener_por_email(email)

    def cambiar_password_con_codigo(self, email, codigo, nueva_password):
        return self.auth.cambiar_password_con_codigo(email, codigo, nueva_password)

__all__ = ["ModeloLogin"]
