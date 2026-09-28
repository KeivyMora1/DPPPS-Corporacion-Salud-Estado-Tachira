from .controller import ControladorActividad
from .model import ModeloActividad
from .view import VistaActividad


class ActividadView:
    """Compatibilidad con la API pública del módulo."""

    def __init__(self, parent):
        self._controlador = ControladorActividad(parent)


__all__ = [
    'ActividadView',
    'ModeloActividad',
    'VistaActividad',
    'ControladorActividad',
]
