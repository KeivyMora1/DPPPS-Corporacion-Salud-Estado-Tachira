from .controller import ControladorVoceria
from .model import ModeloVoceria
from .view import VistaVoceria


class VoceriaView:
    """Compatibilidad con la API pública del módulo."""

    def __init__(self, parent):
        self._controlador = ControladorVoceria(parent)


__all__ = [
    "VoceriaView",
    "ModeloVoceria",
    "VistaVoceria",
    "ControladorVoceria",
]
