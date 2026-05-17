# ============================================================
# db/connection.py
# Módulo de conexión a la base de datos
# Se encarga de crear y devolver conexiones a MariaDB/MySQL
# usando los parámetros definidos en config/settings.py
# ============================================================

import mysql.connector
from config.settings import DATABASE, MODO


def get_connection():
    """
    Crea y devuelve una conexión a la base de datos.
    Usa el modo definido en settings.py (local o lan).
    
    Ejemplo de uso:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario")
        conn.close()
    """
    # Obtenemos los parámetros según el modo configurado
    params = DATABASE[MODO]

    try:
        # Intentamos conectar a la base de datos
        conn = mysql.connector.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"]
        )
        return conn

    except mysql.connector.Error as error:
        # Si falla la conexión, mostramos el error y lanzamos la excepción
        print(f"[ERROR] No se pudo conectar a la base de datos: {error}")
        raise
