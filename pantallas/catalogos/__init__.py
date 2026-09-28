from .controller import ControladorCatalogo
from .model import ModeloCatalogo
from .view import VistaCatalogo


class CatalogoView:
    """Compatibilidad con la API pública del módulo."""

    def __init__(self, parent, modo='catalogos'):
        self._controlador = ControladorCatalogo(parent, modo)


__all__ = [
    'CatalogoView',
    'ModeloCatalogo',
    'VistaCatalogo',
    'ControladorCatalogo',
]
