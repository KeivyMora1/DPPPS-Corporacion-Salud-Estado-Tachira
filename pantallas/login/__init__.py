from .model import ModeloLogin
from .view import VistaLogin
from .controller import ControladorLogin


class LoginView:
    """Compatibilidad con la API anterior del proyecto.

    La versión histórica del proyecto esperaba que esta clase instanciara el
    controlador y construyera la vista. Mantener este wrapper evita romper la
    entrada principal de la app sin tocar la lógica de negocio.
    """

    def __init__(self, root, al_iniciar_sesion):
        self.root = root
        self.controlador = ControladorLogin(root, al_iniciar_sesion)
        self.vista = self.controlador.vista

    def __getattr__(self, name):
        return getattr(self.vista, name)


__all__ = [
    "ModeloLogin",
    "VistaLogin",
    "ControladorLogin",
    "LoginView",
]
