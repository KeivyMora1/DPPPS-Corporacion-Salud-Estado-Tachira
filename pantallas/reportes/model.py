from db import AuthController, AsicDAO, ConsolidacionService, InformeWordService, ReporteSemanalService


class ModeloReporte:
    """Capa de acceso a datos y servicios de consolidación/exportación."""

    def __init__(self):
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()
        self.servicio_semanal = ReporteSemanalService()

    def get_usuario(self):
        return self.usuario

    def listar_asics(self):
        asic_map = {}
        asic_nombres = []
        try:
            for a in AsicDAO().obtener_todos():
                asic_map[a["nombre"]] = a["id_asic"]
                asic_nombres.append(a["nombre"])
        except Exception:
            pass
        return asic_map, asic_nombres

    def generar_previo(self, f_ini, f_fin, id_asic, titulo):
        svc = ConsolidacionService(self.usuario["id_usuario"])
        previo = svc.generar_previo(f_ini, f_fin, id_asic)
        previo["titulo"] = titulo
        previo["observaciones"] = ""
        return previo

    def generar_docx(self, previo, ruta):
        InformeWordService().generar_docx(previo, ruta)

    def obtener_semana_de_fecha(self, fecha):
        return self.servicio_semanal.obtener_semana_de_fecha(fecha)

    def generar_ranking_semanal(self, fecha_inicio, fecha_fin):
        return self.servicio_semanal.obtener_ranking_semanal(fecha_inicio, fecha_fin)

    def generar_docx_semanal(self, mes_nombre: str, numero_semana: int, ranking: list, ruta_salida: str):
        return self.servicio_semanal.generar_docx(mes_nombre, numero_semana, ranking, ruta_salida)


__all__ = ["ModeloReporte"]


