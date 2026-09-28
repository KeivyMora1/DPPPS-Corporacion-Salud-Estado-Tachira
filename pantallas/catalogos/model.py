from db import CatalogoController

class ModeloCatalogo:
    def __init__(self):
        self.controller = CatalogoController()

    def listar_asic(self):
        return self.controller.listar_asic()

    def guardar_asic(self, codigo, nombre, municipio, parroquia, id_asic=None):
        return self.controller.guardar_asic(codigo, nombre, municipio, parroquia, id_asic)

    def eliminar_asic(self, id_asic):
        return self.controller.eliminar_asic(id_asic)

    def listar_tipos(self):
        return self.controller.listar_tipos()

    def guardar_tipo(self, codigo, nombre, id_tipo=None):
        return self.controller.guardar_tipo(codigo, nombre, id_tipo)

    def eliminar_tipo(self, id_tipo):
        return self.controller.eliminar_tipo(id_tipo)


# ─────────────────────────────────────────────────────────────
# VISTA
# Solo construye la interfaz. No tiene lógica de negocio.
# Recibe al controlador para asignarle las acciones.
# ─────────────────────────────────────────────────────────────

__all__ = ['ModeloCatalogo']
