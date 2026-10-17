"""
Clase base para Data Access Objects (DAO).
Proporciona operaciones CRUD genéricas y manejo de conexiones centralizado.
"""

from typing import Any, Optional, List, Dict, Tuple
from contextlib import contextmanager

from .connection import conexion, transaccion, ejecutar_consulta, MySQLConnection

class BaseDAO:
    """
    Clase base para DAOs con operaciones CRUD comunes.

    Las subclases deben definir:
        - TABLA: nombre de la tabla en la BD
        - CAMPOS: lista de nombres de columnas (sin id autoincremental)
        - CAMPO_ID: nombre de la columna PK (default: 'id')
    """

    TABLA: str = ""
    CAMPOS: List[str] = []
    CAMPO_ID: str = "id"

    def __init__(self):
        if not self.TABLA:
            raise NotImplementedError("Subclase debe definir TABLA")
        if not self.CAMPOS:
            raise NotImplementedError("Subclase debe definir CAMPOS")

    def obtener_todos(
        self,
        orden_por: str = "",
        donde: str = "",
        parametros: Tuple = (),
        limite: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {self.TABLA}"
        if donde:
            sql += f" WHERE {donde}"
        if orden_por:
            sql += f" ORDER BY {orden_por}"
        if limite:
            sql += f" LIMIT {limite}"

        return ejecutar_consulta(sql, parametros, obtener_todos=True)

    def obtener_por_id(self, id_valor: Any) -> Optional[Dict[str, Any]]:
        sql = f"SELECT * FROM {self.TABLA} WHERE {self.CAMPO_ID} = %s"
        return ejecutar_consulta(sql, (id_valor,), obtener_uno=True)

    def obtener_uno(self, donde: str, parametros: Tuple = ()) -> Optional[Dict[str, Any]]:
        sql = f"SELECT * FROM {self.TABLA} WHERE {donde} LIMIT 1"
        return ejecutar_consulta(sql, parametros, obtener_uno=True)

    def contar(self, donde: str = "", parametros: Tuple = ()) -> int:
        sql = f"SELECT COUNT(*) AS total FROM {self.TABLA}"
        if donde:
            sql += f" WHERE {donde}"
        resultado = ejecutar_consulta(sql, parametros, obtener_uno=True)
        return resultado["total"] if resultado else 0

    def existe(self, donde: str, parametros: Tuple = ()) -> bool:
        return self.contar(donde, parametros) > 0

    def crear(self, datos: Dict[str, Any], conexion_existente: Optional[MySQLConnection] = None) -> int:
        campos = [c for c in self.CAMPOS if c in datos and datos[c] is not None]
        if not campos:
            raise ValueError("No hay campos válidos para insertar")

        placeholders = ", ".join(["%s"] * len(campos))
        sql = f"INSERT INTO {self.TABLA} ({', '.join(campos)}) VALUES ({placeholders})"
        valores = tuple(datos[c] for c in campos)

        if conexion_existente:
            cursor = conexion_existente.cursor()
            cursor.execute(sql, valores)
            return cursor.lastrowid

        return ejecutar_consulta(sql, valores)

    def crear_muchos(self, lista_datos: List[Dict[str, Any]]) -> List[int]:
        ids = []
        with transaccion() as conn:
            for datos in lista_datos:
                ids.append(self.crear(datos, conexion_existente=conn))
        return ids

    def actualizar(
        self,
        id_valor: Any,
        datos: Dict[str, Any],
        conexion_existente: Optional[MySQLConnection] = None
    ) -> bool:
        campos_validos = [c for c in self.CAMPOS if c in datos and datos[c] is not None]
        if not campos_validos:
            raise ValueError("No hay campos válidos para actualizar")

        set_clause = ", ".join([f"{c} = %s" for c in campos_validos])
        sql = f"UPDATE {self.TABLA} SET {set_clause} WHERE {self.CAMPO_ID} = %s"
        valores = tuple(datos[c] for c in campos_validos) + (id_valor,)

        if conexion_existente:
            cursor = conexion_existente.cursor()
            cursor.execute(sql, valores)
            return cursor.rowcount > 0

        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, valores)
            return cursor.rowcount > 0

    def actualizar_por(
        self,
        donde: str,
        parametros_where: Tuple,
        datos: Dict[str, Any]
    ) -> int:
        campos_validos = [c for c in self.CAMPOS if c in datos and datos[c] is not None]
        if not campos_validos:
            raise ValueError("No hay campos válidos para actualizar")

        set_clause = ", ".join([f"{c} = %s" for c in campos_validos])
        sql = f"UPDATE {self.TABLA} SET {set_clause} WHERE {donde}"
        valores = tuple(datos[c] for c in campos_validos) + parametros_where

        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, valores)
            return cursor.rowcount

    def eliminar(
        self,
        id_valor: Any,
        borrado_fisico: bool = False,
        campo_eliminado: str = "eliminado"
    ) -> bool:
        if borrado_fisico:
            sql = f"DELETE FROM {self.TABLA} WHERE {self.CAMPO_ID} = %s"
        else:
            sql = f"UPDATE {self.TABLA} SET {campo_eliminado} = TRUE WHERE {self.CAMPO_ID} = %s"

        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (id_valor,))
            return cursor.rowcount > 0

    def eliminar_por_id(
        self,
        id_valor: Any,
        borrado_fisico: bool = False,
        campo_eliminado: str = "eliminado"
    ) -> bool:
        return self.eliminar(id_valor, borrado_fisico=borrado_fisico, campo_eliminado=campo_eliminado)

    def eliminar_por(self, donde: str, parametros: Tuple, borrado_fisico: bool = False, campo_eliminado: str = "eliminado") -> int:
        if borrado_fisico:
            sql = f"DELETE FROM {self.TABLA} WHERE {donde}"
        else:
            sql = f"UPDATE {self.TABLA} SET {campo_eliminado} = TRUE WHERE {donde}"

        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, parametros)
            return cursor.rowcount

    @contextmanager
    def transaccion(self):
        with transaccion() as conn:
            yield conn

    def ejecutar_sql(self, sql: str, parametros: Tuple = (), obtener_todos: bool = False, obtener_uno: bool = False):
        return ejecutar_consulta(sql, parametros, obtener_todos=obtener_todos, obtener_uno=obtener_uno)

    def _construir_where_filtros(self, filtros: Dict[str, Any], prefijo: str = "") -> Tuple[str, Tuple]:
        condiciones = []
        parametros = []

        for campo, valor in filtros.items():
            if valor is None:
                continue
            campo_completo = f"{prefijo}{campo}" if prefijo else campo
            if isinstance(valor, (list, tuple)):
                placeholders = ", ".join(["%s"] * len(valor))
                condiciones.append(f"{campo_completo} IN ({placeholders})")
                parametros.extend(valor)
            else:
                condiciones.append(f"{campo_completo} = %s")
                parametros.append(valor)

        where = " AND ".join(condiciones) if condiciones else ""
        return where, tuple(parametros)


class BaseDAOSinId(BaseDAO):
    """BaseDAO para tablas sin PK autoincremental (ej: tablas de catálogo con PK manual)."""
    CAMPO_ID: str = ""

    def crear(self, datos: Dict[str, Any], conexion_existente: Optional[MySQLConnection] = None) -> Any:
        campos = [c for c in self.CAMPOS if c in datos and datos[c] is not None]
        if not campos:
            raise ValueError("No hay campos válidos para insertar")

        placeholders = ", ".join(["%s"] * len(campos))
        sql = f"INSERT INTO {self.TABLA} ({', '.join(campos)}) VALUES ({placeholders})"
        valores = tuple(datos[c] for c in campos)

        if conexion_existente:
            cursor = conexion_existente.cursor()
            cursor.execute(sql, valores)
            return datos.get(self.CAMPO_ID) if self.CAMPO_ID else cursor.lastrowid

        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, valores)
            return datos.get(self.CAMPO_ID) if self.CAMPO_ID else cursor.lastrowid