"""
DAO para la tabla comite.
Migración a BaseDAO manteniendo API idéntica al legacy.
"""

from typing import Optional, Dict, Any, List

from ..base_dao import BaseDAO
from ..connection import transaccion, ejecutar_consulta

class ComiteDAO(BaseDAO):
    """Data Access Object para comités de salud."""
    
    TABLA = "comite"
    CAMPOS = [
        "id_asic", "id_usuario_registro", "estado", "municipio", "parroquia",
        "centro_dispensador", "nombre_centro", "nombre_comite", "eliminado", "created_at"
    ]
    CAMPO_ID = "id_comite"
    
    def _select_base(self) -> str:
        """SELECT base con JOINs para obtener nombres relacionados."""
        return """
            SELECT c.*, a.nombre AS asic_nombre, u.nombre_completo AS usuario_nombre
            FROM comite c
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
        """
    
    def obtener_todos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene todos los comités no eliminados, con filtros opcionales."""
        sql = self._select_base() + " WHERE c.eliminado = FALSE"
        params = []
        
        if filtros:
            if filtros.get("id_asic"):
                sql += " AND c.id_asic = %s"
                params.append(filtros["id_asic"])
        
        sql += " ORDER BY c.created_at DESC, c.id_comite DESC"
        
        return ejecutar_consulta(sql, tuple(params), obtener_todos=True)
    
    def obtener_por_id(self, id_comite: int) -> Optional[Dict[str, Any]]:
        """Obtiene un comité por ID con JOINs."""
        sql = self._select_base() + " WHERE c.id_comite = %s AND c.eliminado = FALSE"
        return ejecutar_consulta(sql, (id_comite,), obtener_uno=True)
    
    def crear(
        self,
        id_asic: int,
        id_usuario_registro: int,
        estado: str = "",
        municipio: str = "",
        parroquia: str = "",
        centro_dispensador: str = "",
        nombre_centro: str = "",
        nombre_comite: str = "",
        connection=None
    ) -> int:
        """Crea un nuevo comité. Soporta conexión existente para transacciones."""
        owns_connection = connection is None
        
        if owns_connection:
            with transaccion() as conn:
                return self._crear_con_conexion(
                    conn, id_asic, id_usuario_registro, estado, municipio,
                    parroquia, centro_dispensador, nombre_centro, nombre_comite
                )
        else:
            return self._crear_con_conexion(
                connection, id_asic, id_usuario_registro, estado, municipio,
                parroquia, centro_dispensador, nombre_centro, nombre_comite
            )
    
    def _crear_con_conexion(self, conn, *args) -> int:
        """Helper para ejecutar INSERT con una conexión dada."""
        cursor = conn.cursor()
        sql = """
            INSERT INTO comite (id_asic, id_usuario_registro, estado, municipio, parroquia, 
                                centro_dispensador, nombre_centro, nombre_comite)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, args)
        return cursor.lastrowid
    
    def actualizar(
        self,
        id_comite: int,
        id_asic: int,
        id_usuario_registro: int,
        estado: str = "",
        municipio: str = "",
        parroquia: str = "",
        centro_dispensador: str = "",
        nombre_centro: str = "",
        nombre_comite: str = ""
    ) -> bool:
        """Actualiza un comité existente."""
        sql = """
            UPDATE comite
            SET id_asic = %s, id_usuario_registro = %s, estado = %s, municipio = %s, 
                parroquia = %s, centro_dispensador = %s, nombre_centro = %s, nombre_comite = %s
            WHERE id_comite = %s
        """
        params = (
            id_asic, id_usuario_registro, estado, municipio, parroquia,
            centro_dispensador, nombre_centro, nombre_comite, id_comite
        )
        
        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.rowcount > 0
    
    def eliminar(self, id_comite: int) -> bool:
        """Elimina lógicamente un comité (soft delete)."""
        return self.eliminar_por_id(id_comite, borrado_fisico=False, campo_eliminado="eliminado")
    
    def eliminar_por_id(self, id_comite: int, borrado_fisico: bool = False, campo_eliminado: str = "eliminado") -> bool:
        """Elimina por ID con opción de borrado físico."""
        if borrado_fisico:
            sql = f"DELETE FROM {self.TABLA} WHERE {self.CAMPO_ID} = %s"
        else:
            sql = f"UPDATE {self.TABLA} SET {campo_eliminado} = TRUE WHERE {self.CAMPO_ID} = %s"
        
        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (id_comite,))
            return cursor.rowcount > 0