from pantallas.actividades.controller import ControladorActividad
from pantallas.actividades.model import ModeloActividad
from pantallas.actividades.view import VistaActividad
from pantallas.catalogos.controller import ControladorCatalogo
from pantallas.catalogos.model import ModeloCatalogo
from pantallas.catalogos.view import VistaCatalogo


def _tiene_origen_legacy(clase):
    for base in clase.__bases__:
        if getattr(base, "__module__", "").endswith(".actividades") or getattr(base, "__module__", "").endswith(".catalogos"):
            return True
    return False


def test_actividades_no_heredan_del_archivo_compatibilidad():
    assert not _tiene_origen_legacy(ControladorActividad)
    assert not _tiene_origen_legacy(ModeloActividad)
    assert not _tiene_origen_legacy(VistaActividad)


def test_catalogos_no_heredan_del_archivo_compatibilidad():
    assert not _tiene_origen_legacy(ControladorCatalogo)
    assert not _tiene_origen_legacy(ModeloCatalogo)
    assert not _tiene_origen_legacy(VistaCatalogo)
