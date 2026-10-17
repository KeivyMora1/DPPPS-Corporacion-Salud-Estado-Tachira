from contextlib import contextmanager
from typing import Generator, Optional
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import MySQLConnection

from constants import MODO, DATABASE

_pool: Optional[MySQLConnectionPool] = None

def _crear_pool() -> MySQLConnectionPool:
    config = DATABASE[MODO].copy()
    config["use_pure"] = True
    return MySQLConnectionPool(
        pool_name="dppps_pool",
        pool_size=10,
        pool_reset_session=True,
        **config
    )

def obtener_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = _crear_pool()
    return _pool

def reiniciar_pool() -> None:
    global _pool
    if _pool is not None:
        try:
            _pool.close()
        except Exception:
            pass
    _pool = _crear_pool()

@contextmanager
def conexion() -> Generator[MySQLConnection, None, None]:
    pool = obtener_pool()
    conn = pool.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@contextmanager
def transaccion() -> Generator[MySQLConnection, None, None]:
    with conexion() as conn:
        yield conn

def obtener_conexion_directa() -> MySQLConnection:
    return obtener_pool().get_connection()

def ejecutar_consulta(
    sql: str,
    parametros: tuple = (),
    obtener_uno: bool = False,
    obtener_todos: bool = False,
    diccionario: bool = True
):
    with conexion() as conn:
        cursor = conn.cursor(dictionary=diccionario)
        cursor.execute(sql, parametros)

        if obtener_uno:
            return cursor.fetchone()
        if obtener_todos:
            return cursor.fetchall()

        return cursor.lastrowid