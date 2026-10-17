from ...daos import ActividadDAO, AsicDAO, VoceriaDAO

class ConsolidacionService:
    def __init__(self, id_usuario: int):
        self.id_usuario = id_usuario
        self._actividad_dao = ActividadDAO()
        self._asic_dao = AsicDAO()
        self._voceria_dao = VoceriaDAO()

    def generar_previo(self, fecha_inicio, fecha_fin, id_asic=None) -> dict:
        actividades = self._obtener_actividades(fecha_inicio, fecha_fin, id_asic)
        total_act = len(actividades)
        total_part = sum(a["total_participantes"] for a in actividades)
        resumen_tipo = self._agrupar(actividades, "tipo_nombre")
        resumen_asic = self._agrupar(actividades, "asic_nombre")

        vocerias = self._obtener_vocerias(fecha_inicio, fecha_fin, id_asic)

        asic_nombre = None
        if id_asic:
            ids = id_asic if isinstance(id_asic, list) else [id_asic]
            nombres = []
            for aid in ids:
                asic = self._asic_dao.obtener_por_id(aid)
                if asic:
                    nombres.append(asic["nombre"])
            asic_nombre = ", ".join(nombres) if nombres else str(ids)

        return {
            "actividades": actividades,
            "resumen_por_tipo": resumen_tipo,
            "resumen_por_asic": resumen_asic,
            "total_actividades": total_act,
            "total_participantes": total_part,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "id_asic": id_asic,
            "asic_nombre": asic_nombre,
            "vocerias": vocerias,
        }

    def _obtener_actividades(self, fecha_inicio, fecha_fin, id_asic) -> list:
        filtros_base = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        if not id_asic:
            return self._actividad_dao.obtener_todas(filtros_base)

        ids = id_asic if isinstance(id_asic, list) else [id_asic]
        if len(ids) == 1:
            filtros = dict(filtros_base)
            filtros["id_asic"] = ids[0]
            return self._actividad_dao.obtener_todas(filtros)

        vistas = {}
        for aid in ids:
            filtros = dict(filtros_base)
            filtros["id_asic"] = aid
            for act in self._actividad_dao.obtener_todas(filtros):
                vistas[act["id_actividad"]] = act
        return sorted(vistas.values(), key=lambda a: (str(a.get("fecha", "")), a["id_actividad"]), reverse=True)

    def _obtener_vocerias(self, fecha_inicio, fecha_fin, id_asic) -> list:
        filtros_base = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        if not id_asic:
            return self._voceria_dao.obtener_todas(filtros_base)

        ids = id_asic if isinstance(id_asic, list) else [id_asic]
        if len(ids) == 1:
            filtros = dict(filtros_base)
            filtros["id_asic"] = ids[0]
            return self._voceria_dao.obtener_todas(filtros)

        vistas = {}
        for aid in ids:
            filtros = dict(filtros_base)
            filtros["id_asic"] = aid
            for voc in self._voceria_dao.obtener_todas(filtros):
                vistas[voc["id_voceria"]] = voc
        return sorted(vistas.values(), key=lambda v: (str(v.get("fecha_registro", "")), v["id_voceria"]), reverse=True)

    @staticmethod
    def _agrupar(actividades: list, campo_grupo: str) -> list:
        grupos = {}
        for act in actividades:
            clave = act.get(campo_grupo) or "Sin clasificar"
            if clave not in grupos:
                grupos[clave] = {"nombre": clave, "total_actividades": 0, "total_participantes": 0}
            grupos[clave]["total_actividades"] += 1
            grupos[clave]["total_participantes"] += act.get("total_participantes", 0)
        return sorted(grupos.values(), key=lambda x: x["nombre"])
