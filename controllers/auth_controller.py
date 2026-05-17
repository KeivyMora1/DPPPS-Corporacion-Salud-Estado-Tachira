# ============================================================
# controllers/auth_controller.py
# Controlador de autenticación.
# Se encarga de verificar las credenciales del usuario
# y guardar la sesión activa.
# ============================================================

from models.usuario import UsuarioDAO

# Variable global que guarda los datos del usuario logueado
# Cuando es None, no hay nadie logueado
sesion_actual = None


class AuthController:
    """
    Maneja el login y logout del sistema.
    """

    def __init__(self):
        self.usuario_dao = UsuarioDAO()

    def login(self, username, password):
        """
        Intenta iniciar sesión con el username y password dados.
        
        Retorna:
            True  → login exitoso, sesion_actual queda guardada
            False → credenciales incorrectas o usuario inactivo
        """
        global sesion_actual

        # Buscamos el usuario en la base de datos
        usuario = self.usuario_dao.obtener_por_username(username)

        if usuario is None:
            # El usuario no existe o está inactivo
            return False

        # Verificamos que la contraseña sea correcta
        password_correcta = self.usuario_dao.verificar_password(
            password,
            usuario["password_hash"]
        )

        if not password_correcta:
            return False

        # Login exitoso: guardamos la sesión
        sesion_actual = {
            "id_usuario": usuario["id_usuario"],
            "username": usuario["username"],
            "nombre_completo": usuario["nombre_completo"],
            "email": usuario["email"]
        }
        return True

    def logout(self):
        """Cierra la sesión actual."""
        global sesion_actual
        sesion_actual = None

    def obtener_usuario_actual(self):
        """Retorna los datos del usuario logueado, o None si no hay sesión."""
        return sesion_actual

    def hay_sesion_activa(self):
        """Retorna True si hay un usuario logueado."""
        return sesion_actual is not None
