from db import ActividadController

class ModeloTipoActividad:
    def __init__(self):
        self.controller = ActividadController()

    def puede_escribir(self):
        return self.controller.usuario_es_propietario()

    def listar_tipos(self):
        return self.controller.listar_tipos_actividad()

    def crear_tipo(self, nombre):
        return self.controller.crear_tipo_actividad(nombre)

    def actualizar_tipo(self, id_tipo, nombre):
        return self.controller.actualizar_tipo_actividad(id_tipo, nombre)

__all__ = ["ModeloTipoActividad"]
