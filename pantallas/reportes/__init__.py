from .controller import ControladorReporte
from .model import ModeloReporte
from .view import VistaReporte


class ReporteView:
    """Compatibilidad con la API pública del módulo."""

    def __init__(self, parent):
        self._controlador = ControladorReporte(parent)


__all__ = [
    "ReporteView",
    "ModeloReporte",
    "VistaReporte",
    "ControladorReporte",
]
