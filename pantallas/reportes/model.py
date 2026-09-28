from db import AuthController, AsicDAO, ConsolidacionService, PDFService


class ModeloReporte:
    """Capa de acceso a datos y servicios de consolidación/exportación."""

    def __init__(self):
        self.auth = AuthController()
        self.usuario = self.auth.obtener_usuario_actual()

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

    def generar_word(self, previo, ruta):
        PDFService().generar_word(previo, ruta)


__all__ = ["ModeloReporte"]
