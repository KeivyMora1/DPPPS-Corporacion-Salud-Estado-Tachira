from db import VoceriaController


class ModeloVoceria:
    """Capa de acceso a datos de vocerías."""

    def __init__(self):
        self.controller = VoceriaController()

    def listar_asics(self):
        return self.controller.listar_asics()

    def listar_ubicaciones_asic(self):
        return self.controller.listar_ubicaciones_asic()

    def listar_tipos_voceria(self):
        return self.controller.listar_tipos_voceria()

    def listar_vocerias(self, filtros=None):
        return self.controller.listar_vocerias(filtros)

    def guardar_voceria(self, **kwargs):
        return self.controller.guardar_voceria(**kwargs)

    def eliminar_voceria(self, id_voceria):
        return self.controller.eliminar_voceria(id_voceria)

    def obtener_voceria_completa(self, id_voceria):
        return self.controller.obtener_voceria_completa(id_voceria)


__all__ = ["ModeloVoceria"]
