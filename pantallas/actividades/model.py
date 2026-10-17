from db import ActividadController

class ModeloActividad:
    def __init__(self):
        self.controller = ActividadController()

    def listar_asics(self):
        return self.controller.listar_asics()

    def listar_municipios(self):
        return self.controller.listar_municipios()

    def listar_parroquias(self, id_o_nombre_municipio=None):
        return self.controller.listar_parroquias(id_o_nombre_municipio)

    def listar_ubicaciones_asic(self):
        return self.controller.listar_ubicaciones_asic()

    def listar_tipos_actividad(self):
        return self.controller.listar_tipos_actividad()

    def listar_actividades(self, filtros=None):
        return self.controller.listar_actividades(filtros)

    def guardar_actividad(self, **kwargs):
        return self.controller.guardar_actividad(**kwargs)

    def eliminar_actividad(self, id_actividad):
        return self.controller.eliminar_actividad(id_actividad)

    def obtener_actividad_por_id(self, id_actividad):
        return self.controller.actividad_dao.obtener_por_id(id_actividad)

__all__ = ['ModeloActividad']
