"""
DAO para la tabla actividad.
Migración a BaseDAO manteniendo API idéntica al legacy.
"""

from datetime import date, datetime
from typing import Optional, Dict, Any, List

from ..base_dao import BaseDAO
from ..connection import transaccion, ejecutar_consulta


class ActividadDAO(BaseDAO):
    """Data Access Object para actividades de salud."""
    
    TABLA = "actividad"
    CAMPOS = [
        "id_asic", "id_tipo", "id_usuario_registro", "fecha",
        "estado", "municipio", "parroquia", "establecimiento_salud",
        "nombre_establecimiento", "comites_salud", "tema",
        "cant_medicos", "cant_promotores_salud", "cant_voceros_comite_salud",
        "cant_vocero_consejo_direccion", "cant_coordinador_docencia",
        "cant_autoridades", "cant_otros_actores",
        "cant_personas_comunidad", "cant_estudiantes_aspirantes",
        "total_participantes", "eliminado", "created_at"
    ]
    CAMPO_ID = "id_actividad"

    @staticmethod
    def _parse_fecha(fecha=None) -> date:
        if fecha is None:
            raise ValueError("Debe proporcionarse una fecha válida")
        if isinstance(fecha, str):
            fecha = fecha.strip()
            for formato in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(fecha, formato).date()
                except ValueError:
                    continue
            raise ValueError(f"Fecha inválida: {fecha}")
        if isinstance(fecha, (datetime, date)):
            return fecha.date() if isinstance(fecha, datetime) else fecha
        raise ValueError("Debe proporcionarse una fecha válida")

    def _select_base(self) -> str:
        return """
            SELECT a.id_actividad, a.id_asic, a.id_tipo, a.id_usuario_registro,
                   a.fecha,
                   a.estado, a.municipio, a.parroquia, a.establecimiento_salud,
                   a.nombre_establecimiento, a.comites_salud,
                   a.tema AS tema,
                   a.cant_medicos,
                   a.cant_promotores_salud,
                   a.cant_voceros_comite_salud,
                   a.cant_vocero_consejo_direccion,
                   a.cant_coordinador_docencia,
                   a.cant_autoridades,
                   a.cant_otros_actores,
                   a.cant_personas_comunidad,
                   a.cant_estudiantes_aspirantes,
                   a.total_participantes,
                   a.created_at,
                   asic.nombre AS asic_nombre,
                   ta.nombre AS tipo_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM actividad a
            JOIN asic ON a.id_asic = asic.id_asic
            JOIN tipo_actividad ta ON a.id_tipo = ta.id_tipo
            JOIN usuario u ON a.id_usuario_registro = u.id_usuario
        """
    
    def obtener_todas(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene todas las actividades no eliminadas, con filtros opcionales."""
        sql = self._select_base() + " WHERE a.eliminado = FALSE"
        params = []
        
        if filtros:
            if filtros.get("id_asic"):
                sql += " AND a.id_asic = %s"
                params.append(filtros["id_asic"])
            if filtros.get("id_tipo"):
                sql += " AND a.id_tipo = %s"
                params.append(filtros["id_tipo"])
            if filtros.get("fecha_desde"):
                sql += " AND a.fecha >= %s"
                params.append(filtros["fecha_desde"])
            if filtros.get("fecha_hasta"):
                sql += " AND a.fecha <= %s"
                params.append(filtros["fecha_hasta"])
        
        sql += " ORDER BY a.fecha DESC, a.id_actividad DESC"
        
        return ejecutar_consulta(sql, tuple(params), obtener_todos=True)
    
    def obtener_por_id(self, id_actividad: int) -> Optional[Dict[str, Any]]:
        sql = self._select_base() + " WHERE a.id_actividad = %s AND a.eliminado = FALSE"
        return ejecutar_consulta(sql, (id_actividad,), obtener_uno=True)
    
    def crear(
        self,
        id_asic: int,
        id_tipo: int,
        id_usuario_registro: int,
        fecha=None,
        estado: str = "",
        municipio: str = "",
        parroquia: str = "",
        establecimiento_salud: str = "",
        nombre_establecimiento: str = "",
        comites_salud: str = "",
        tema: str = "",
        medicos: int = 0,
        promotores_salud: int = 0,
        voceros_comite_salud: int = 0,
        vocero_consejo_direccion: int = 0,
        coordinador_docencia: int = 0,
        autoridades_presentes: int = 0,
        otros_actores: int = 0,
        personas_comunidad: int = 0,
        estudiantes_aspirantes: int = 0,
        participantes: int = 0,
        total_participantes: Optional[int] = None,
        connection=None
    ) -> int:
        fecha_bd = self._parse_fecha(fecha).strftime("%Y-%m-%d")
        owns_connection = connection is None
        conn = connection or transaccion().__enter__()

        if owns_connection:
            with transaccion() as tx_conn:
                return self._crear_con_conexion(
                    tx_conn, id_asic, id_tipo, id_usuario_registro, fecha_bd,
                    estado, municipio, parroquia, establecimiento_salud,
                    nombre_establecimiento, comites_salud, tema,
                    medicos, promotores_salud, voceros_comite_salud,
                    vocero_consejo_direccion, coordinador_docencia,
                    autoridades_presentes, otros_actores,
                    personas_comunidad, estudiantes_aspirantes,
                    total_participantes if total_participantes is not None else participantes
                )
        else:
            return self._crear_con_conexion(
                conn, id_asic, id_tipo, id_usuario_registro, fecha_bd,
                estado, municipio, parroquia, establecimiento_salud,
                nombre_establecimiento, comites_salud, tema,
                medicos, promotores_salud, voceros_comite_salud,
                vocero_consejo_direccion, coordinador_docencia,
                autoridades_presentes, otros_actores,
                personas_comunidad, estudiantes_aspirantes,
                total_participantes if total_participantes is not None else participantes
            )

    def _crear_con_conexion(self, conn, *args) -> int:
        cursor = conn.cursor()
        tema_texto = str(args[11]).strip() if args[11] is not None else ""

        sql = """
            INSERT INTO actividad (
                id_asic, id_tipo, id_usuario_registro,
                fecha,
                estado, municipio, parroquia, establecimiento_salud,
                nombre_establecimiento, comites_salud,
                tema,
                cant_medicos, cant_promotores_salud, cant_voceros_comite_salud,
                cant_vocero_consejo_direccion, cant_coordinador_docencia,
                cant_autoridades, cant_otros_actores,
                cant_personas_comunidad, cant_estudiantes_aspirantes,
                total_participantes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, args)
        return cursor.lastrowid

    def actualizar(
        self,
        id_actividad: int,
        id_asic: int,
        id_tipo: int,
        fecha=None,
        estado: str = "",
        municipio: str = "",
        parroquia: str = "",
        establecimiento_salud: str = "",
        nombre_establecimiento: str = "",
        comites_salud: str = "",
        tema: str = "",
        medicos: int = 0,
        promotores_salud: int = 0,
        voceros_comite_salud: int = 0,
        vocero_consejo_direccion: int = 0,
        coordinador_docencia: int = 0,
        autoridades_presentes: int = 0,
        otros_actores: int = 0,
        personas_comunidad: int = 0,
        estudiantes_aspirantes: int = 0,
        participantes: int = 0,
        total_participantes: Optional[int] = None
    ) -> bool:
        """Actualiza una actividad existente."""
        fecha_bd = self._parse_fecha(fecha).strftime("%Y-%m-%d")
        tema_texto = str(tema).strip() if tema is not None else ""
        
        sql = """
            UPDATE actividad
            SET id_asic = %s, id_tipo = %s, fecha = %s,
                estado = %s, municipio = %s, parroquia = %s, establecimiento_salud = %s,
                nombre_establecimiento = %s, comites_salud = %s,
                tema = %s,
                cant_medicos = %s, cant_promotores_salud = %s, cant_voceros_comite_salud = %s,
                cant_vocero_consejo_direccion = %s, cant_coordinador_docencia = %s,
                cant_autoridades = %s, cant_otros_actores = %s,
                cant_personas_comunidad = %s, cant_estudiantes_aspirantes = %s,
                total_participantes = %s
            WHERE id_actividad = %s
        """
        params = (
            id_asic, id_tipo, fecha_bd,
            estado, municipio, parroquia, establecimiento_salud,
            nombre_establecimiento, comites_salud,
            tema_texto,
            medicos, promotores_salud, voceros_comite_salud,
            vocero_consejo_direccion, coordinador_docencia,
            autoridades_presentes, otros_actores,
            personas_comunidad, estudiantes_aspirantes,
            total_participantes if total_participantes is not None else participantes,
            id_actividad,
        )
        
        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.rowcount > 0

    def eliminar(self, id_actividad: int) -> bool:
        return self.eliminar_por_id(id_actividad, borrado_fisico=False, campo_eliminado="eliminado")

    def eliminar_por_id(self, id_actividad: int, borrado_fisico: bool = False, campo_eliminado: str = "eliminado") -> bool:
        if borrado_fisico:
            sql = f"DELETE FROM {self.TABLA} WHERE {self.CAMPO_ID} = %s"
        else:
            sql = f"UPDATE {self.TABLA} SET {campo_eliminado} = TRUE WHERE {self.CAMPO_ID} = %s"

        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (id_actividad,))
            return cursor.rowcount > 0

    def verificar_duplicado(
        self,
        id_asic: int,
        id_tipo: int,
        fecha,
        tema: Optional[str] = None,
        excluir_id: Optional[int] = None
    ) -> bool:
        tema_normalizado = str(tema).strip() if tema is not None else ""
        desc_normalizada = " ".join(tema_normalizado.lower().split())[:100]
        fecha_bd = self._parse_fecha(fecha).strftime("%Y-%m-%d")

        sql = """
            SELECT id_actividad, tema
            FROM actividad
            WHERE id_asic = %s AND id_tipo = %s AND fecha = %s AND eliminado = FALSE
        """
        params: List[Any] = [id_asic, id_tipo, fecha_bd]

        if excluir_id is not None:
            sql += " AND id_actividad != %s"
            params.append(excluir_id)

        resultados = ejecutar_consulta(sql, tuple(params), obtener_todos=True)

        for registro in resultados:
            reg_desc = " ".join((registro.get("tema") or "").lower().strip().split())[:100]
            if reg_desc == desc_normalizada:
                return True
        return False