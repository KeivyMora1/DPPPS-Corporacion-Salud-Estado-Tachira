"""
DAO para las tablas comite y voceria (vocerías CS).
Migración a BaseDAO manteniendo API idéntica al legacy.
"""

from typing import Optional, Dict, Any, List

from ..connection import transaccion, ejecutar_consulta

from .comite_dao import ComiteDAO


class VoceriaDAO:
    def __init__(self):
        self.comite_dao = ComiteDAO()

    def obtener_todas(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT c.id_comite AS id_voceria,
                   c.created_at AS fecha_registro,
                   COUNT(v.id_voceria) AS cantidad_vocerias,
                   c.estado,
                   c.municipio,
                   c.parroquia,
                   c.nombre_comite,
                   c.nombre_centro,
                   c.centro_dispensador,
                   a.nombre AS asic_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM comite c
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
            LEFT JOIN voceria v ON v.id_comite = c.id_comite AND v.eliminado = FALSE
            WHERE c.eliminado = FALSE
        """
        params = []

        if filtros:
            if filtros.get("id_asic"):
                sql += " AND c.id_asic = %s"
                params.append(filtros["id_asic"])
            if filtros.get("id_tipo"):
                sql += """ AND EXISTS (
                    SELECT 1 FROM voceria v2
                    WHERE v2.id_comite = c.id_comite
                    AND v2.id_tipo_voceria = %s
                    AND v2.eliminado = FALSE
                )"""
                params.append(filtros["id_tipo"])
            if filtros.get("nombre_comite"):
                sql += " AND c.nombre_comite LIKE %s"
                params.append(f"%{filtros['nombre_comite']}%")
            if filtros.get("fecha_desde"):
                sql += " AND DATE(c.created_at) >= %s"
                params.append(filtros["fecha_desde"])
            if filtros.get("fecha_hasta"):
                sql += " AND DATE(c.created_at) <= %s"
                params.append(filtros["fecha_hasta"])

        sql += " GROUP BY c.id_comite ORDER BY c.created_at DESC, c.id_comite DESC"

        return ejecutar_consulta(sql, tuple(params), obtener_todos=True)

    def obtener_por_id(self, id_voceria: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT v.*, c.*, tv.nombre AS tipo_nombre, a.nombre AS asic_nombre, u.nombre_completo AS usuario_nombre
            FROM voceria v
            JOIN comite c ON v.id_comite = c.id_comite
            JOIN tipo_voceria tv ON v.id_tipo_voceria = tv.id_tipo
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
            WHERE v.id_voceria = %s AND v.eliminado = FALSE AND c.eliminado = FALSE
        """
        return ejecutar_consulta(sql, (id_voceria,), obtener_uno=True)

    def obtener_con_items(self, id_comite: int) -> Optional[Dict[str, Any]]:
        sql_comite = """
            SELECT c.*, a.nombre AS asic_nombre, u.nombre_completo AS usuario_nombre
            FROM comite c
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
            WHERE c.id_comite = %s AND c.eliminado = FALSE
        """
        comite = ejecutar_consulta(sql_comite, (id_comite,), obtener_uno=True)
        if not comite:
            return None

        sql_voceros = """
            SELECT v.*, tv.nombre AS tipo_voceria_nombre
            FROM voceria v
            JOIN tipo_voceria tv ON v.id_tipo_voceria = tv.id_tipo
            WHERE v.id_comite = %s AND v.eliminado = FALSE
        """
        voceros = ejecutar_consulta(sql_voceros, (id_comite,), obtener_todos=True)

        comite["items"] = voceros
        comite["id_voceria"] = comite["id_comite"]
        tipos_unicos = list(dict.fromkeys(
            v.get("tipo_voceria_nombre", "") for v in voceros if v.get("tipo_voceria_nombre")
        ))
        comite["tipo_nombre"] = ", ".join(tipos_unicos) if tipos_unicos else ""
        return comite

    def crear(
        self,
        id_asic: int,
        id_tipo: int,
        id_usuario_registro: int,
        estado: str,
        municipio: str,
        parroquia: str,
        centro_dispensador: str,
        nombre_centro: str,
        nombre_comite: str,
        items: List[Dict[str, Any]],
        connection=None
    ) -> int:
        owns_connection = connection is None

        if owns_connection:
            with transaccion() as conn:
                return self._crear_con_conexion(
                    conn, id_asic, id_tipo, id_usuario_registro,
                    estado, municipio, parroquia, centro_dispensador,
                    nombre_centro, nombre_comite, items
                )
        else:
            return self._crear_con_conexion(
                connection, id_asic, id_tipo, id_usuario_registro,
                estado, municipio, parroquia, centro_dispensador,
                nombre_centro, nombre_comite, items
            )

    def _crear_con_conexion(self, conn, *args) -> int:
        (id_asic, id_tipo, id_usuario_registro, estado, municipio, parroquia,
         centro_dispensador, nombre_centro, nombre_comite, items) = args

        cursor = conn.cursor()

        id_comite = self.comite_dao.crear(
            id_asic=id_asic,
            id_usuario_registro=id_usuario_registro,
            estado=estado or "",
            municipio=municipio or "",
            parroquia=parroquia or "",
            centro_dispensador=centro_dispensador or "",
            nombre_centro=nombre_centro or "",
            nombre_comite=nombre_comite or "",
            connection=conn
        )

        if items:
            sql = """
                INSERT INTO voceria (
                    id_comite, id_tipo_voceria, nombres, ci, telefono,
                    fecha_nacimiento, edad, sexo, profesion, correo, fechas_eleccion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for item in items:
                cursor.execute(sql, (
                    id_comite,
                    item.get("id_tipo_voceria") or id_tipo,
                    item.get("nombres"),
                    item.get("ci"),
                    item.get("telefono"),
                    item.get("fecha_nacimiento"),
                    item.get("edad"),
                    item.get("sexo"),
                    item.get("profesion"),
                    item.get("correo"),
                    item.get("fechas_eleccion"),
                ))

        return id_comite

    def actualizar(
        self,
        id_voceria: int,
        id_asic: int,
        id_tipo: int,
        estado: str,
        municipio: str,
        parroquia: str,
        centro_dispensador: str,
        nombre_centro: str,
        nombre_comite: str,
        items: List[Dict[str, Any]]
    ) -> bool:
        with transaccion() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE comite
                    SET id_asic = %s, estado = %s, municipio = %s, parroquia = %s,
                        centro_dispensador = %s, nombre_centro = %s, nombre_comite = %s
                    WHERE id_comite = %s
                    """,
                    (id_asic, estado, municipio, parroquia, centro_dispensador,
                     nombre_centro, nombre_comite, id_voceria)
                )

                cursor.execute("UPDATE voceria SET eliminado = TRUE WHERE id_comite = %s", (id_voceria,))

                if items:
                    sql = """
                        INSERT INTO voceria (
                            id_comite, id_tipo_voceria, nombres, ci, telefono,
                            fecha_nacimiento, edad, sexo, profesion, correo, fechas_eleccion
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    for item in items:
                        cursor.execute(sql, (
                            id_voceria,
                            item.get("id_tipo_voceria") or id_tipo,
                            item.get("nombres"),
                            item.get("ci"),
                            item.get("telefono"),
                            item.get("fecha_nacimiento"),
                            item.get("edad"),
                            item.get("sexo"),
                            item.get("profesion"),
                            item.get("correo"),
                            item.get("fechas_eleccion"),
                        ))

                return True
            except Exception:
                return False

    def eliminar(self, id_voceria: int) -> bool:
        with transaccion() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE comite SET eliminado = TRUE WHERE id_comite = %s", (id_voceria,))
                cursor.execute("UPDATE voceria SET eliminado = TRUE WHERE id_comite = %s", (id_voceria,))
                return True
            except Exception:
                return False