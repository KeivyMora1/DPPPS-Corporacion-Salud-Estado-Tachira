# ============================================================
# services/consolidacion_service.py
# Servicio de consolidación de informes.
#
# Responsabilidades:
#   1. Consultar actividades en un rango de fechas (y ASIC opcional)
#   2. Calcular totales: actividades, participantes, desglose por tipo
#   3. Guardar el informe consolidado + detalle en BD
#   4. Devolver el informe listo para exportación (PDF / Excel)
# ============================================================

from datetime import date
from models.actividad import ActividadDAO
from models.asic import AsicDAO
from models.informe import InformeDAO, PeriodoDAO


class ConsolidacionService:
    """
    Genera y persiste informes consolidados de actividades
    para un período y (opcionalmente) un ASIC concreto.
    """

    def __init__(self, id_usuario: int):
        """
        :param id_usuario: ID del usuario que genera el informe.
        """
        self.id_usuario = id_usuario
        self._actividad_dao = ActividadDAO()
        self._asic_dao = AsicDAO()
        self._informe_dao = InformeDAO()
        self._periodo_dao = PeriodoDAO()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def generar_previo(self, fecha_inicio: date, fecha_fin: date,
                       id_asic: int | None = None) -> dict:
        """
        Calcula el resumen SIN guardar en BD.
        Retorna un dict listo para mostrar en la UI y luego pasarlo a `guardar`.

        Estructura del retorno:
        {
          "actividades":        list[dict],   # filas completas de cada actividad
          "resumen_por_tipo":   list[dict],   # {tipo_nombre, total_act, total_part}
          "resumen_por_asic":   list[dict],   # {asic_nombre, total_act, total_part}
          "total_actividades":  int,
          "total_participantes":int,
          "fecha_inicio":       date,
          "fecha_fin":          date,
          "id_asic":            int | None,
          "asic_nombre":        str | None,
        }
        """
        actividades = self._obtener_actividades(fecha_inicio, fecha_fin, id_asic)

        total_act  = len(actividades)
        total_part = sum(a["participantes"] for a in actividades)

        resumen_tipo = self._agrupar(actividades, "tipo_nombre")
        resumen_asic = self._agrupar(actividades, "asic_nombre")

        asic_nombre = None
        if id_asic:
            asic = self._asic_dao.obtener_por_id(id_asic)
            asic_nombre = asic["nombre"] if asic else str(id_asic)

        return {
            "actividades":         actividades,
            "resumen_por_tipo":    resumen_tipo,
            "resumen_por_asic":    resumen_asic,
            "total_actividades":   total_act,
            "total_participantes": total_part,
            "fecha_inicio":        fecha_inicio,
            "fecha_fin":           fecha_fin,
            "id_asic":             id_asic,
            "asic_nombre":         asic_nombre,
        }

    def guardar(self, previo: dict, id_periodo: int,
                titulo: str, observaciones: str = "") -> int:
        """
        Persiste el informe en BD a partir de los datos del previo.
        Retorna el id_informe generado.
        """
        actividades    = previo["actividades"]
        id_asic        = previo["id_asic"]
        total_act      = previo["total_actividades"]
        total_part     = previo["total_participantes"]

        # 1. Insertar cabecera del informe
        id_informe = self._informe_dao.crear(
            id_periodo=id_periodo,
            id_asic=id_asic,
            titulo=titulo,
            total_actividades=total_act,
            total_participantes=total_part,
            observaciones=observaciones,
            id_usuario_generador=self.id_usuario,
        )

        # 2. Insertar detalle (relación informe ↔ actividades)
        ids_actividades = [a["id_actividad"] for a in actividades]
        self._informe_dao.insertar_detalle(id_informe, ids_actividades)

        return id_informe

    def listar_informes(self) -> list:
        """Retorna todos los informes generados (para el historial)."""
        return self._informe_dao.obtener_todos()

    def obtener_informe_completo(self, id_informe: int) -> dict:
        """
        Retorna la cabecera + detalle de actividades + resumen por ASIC
        de un informe ya guardado.  Útil para regenerar el PDF.
        """
        cabecera    = self._informe_dao.obtener_por_id(id_informe)
        detalle     = self._informe_dao.obtener_detalle(id_informe)
        resumen_asic = self._informe_dao.obtener_resumen_por_asic(id_informe)
        resumen_tipo = self._agrupar(detalle, "tipo_nombre")

        return {
            "cabecera":           cabecera,
            "actividades":        detalle,
            "resumen_por_asic":   resumen_asic,
            "resumen_por_tipo":   resumen_tipo,
            "total_actividades":  cabecera["total_actividades"],
            "total_participantes":cabecera["total_participantes"],
        }

    def listar_periodos(self) -> list:
        """Retorna todos los períodos registrados."""
        return self._periodo_dao.obtener_todos()

    def crear_periodo(self, tipo: str, anio: int, mes_inicio: int,
                      mes_fin: int, fecha_inicio: date, fecha_fin: date) -> int:
        """Crea un nuevo período de consolidación."""
        return self._periodo_dao.crear(tipo, anio, mes_inicio, mes_fin,
                                       fecha_inicio, fecha_fin)

    def eliminar_informe(self, id_informe: int):
        """Elimina un informe y su detalle de la BD."""
        self._informe_dao.eliminar(id_informe)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _obtener_actividades(self, fecha_inicio: date, fecha_fin: date,
                             id_asic: int | None) -> list:
        """
        Usa ActividadDAO con filtros de fecha y ASIC.
        ActividadDAO.obtener_todas() acepta {id_asic, fecha_desde, fecha_hasta}.
        """
        filtros = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        if id_asic:
            filtros["id_asic"] = id_asic

        return self._actividad_dao.obtener_todas(filtros)

    @staticmethod
    def _agrupar(actividades: list, campo_grupo: str) -> list:
        """
        Agrupa actividades por un campo y calcula totales.
        Retorna lista de dicts: {campo_grupo, total_actividades, total_participantes}
        """
        grupos: dict[str, dict] = {}
        for act in actividades:
            clave = act.get(campo_grupo) or "Sin clasificar"
            if clave not in grupos:
                grupos[clave] = {"nombre": clave, "total_actividades": 0, "total_participantes": 0}
            grupos[clave]["total_actividades"]  += 1
            grupos[clave]["total_participantes"] += act.get("participantes", 0)

        return sorted(grupos.values(), key=lambda x: x["nombre"])
