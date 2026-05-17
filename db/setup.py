# ============================================================
# db/setup.py
# Script de configuración inicial de la base de datos.
# Ejecutar este archivo UNA SOLA VEZ para:
#   1. Crear todas las tablas
#   2. Insertar el usuario admin con contraseña cifrada
#
# Uso: python db/setup.py
# ============================================================

import sys
import os

# Agregamos la carpeta raíz del proyecto al path de Python.
# Esto es necesario para que Python pueda encontrar los módulos
# como 'config', 'models', etc., sin importar desde dónde se ejecute el script.
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

import mysql.connector
import bcrypt
from config.settings import DATABASE, MODO


def crear_base_de_datos():
    """Crea la base de datos si no existe."""
    params = DATABASE[MODO].copy()
    nombre_bd = params.pop("database")  # Quitamos el nombre de BD para conectar sin ella

    conn = mysql.connector.connect(**params)
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {nombre_bd} "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[OK] Base de datos '{nombre_bd}' lista.")


def ejecutar_schema():
    """Ejecuta el script schema.sql para crear todas las tablas."""
    params = DATABASE[MODO]

    # Leemos el archivo SQL
    ruta_schema = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(ruta_schema, "r", encoding="utf-8") as f:
        sql_completo = f.read()

    conn = mysql.connector.connect(**params)
    cursor = conn.cursor()

    # Dividimos el script en sentencias individuales y ejecutamos una por una
    sentencias = [s.strip() for s in sql_completo.split(";") if s.strip()]
    for sentencia in sentencias:
        try:
            cursor.execute(sentencia)
        except mysql.connector.Error as e:
            # Ignoramos errores de "ya existe" para poder re-ejecutar el setup
            if e.errno not in (1050, 1060, 1061):  # table exists, column exists, duplicate key
                print(f"[ADVERTENCIA] {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("[OK] Tablas creadas correctamente.")


def crear_usuario_admin():
    """Crea el usuario admin con contraseña cifrada si no existe."""
    params = DATABASE[MODO]

    # Pedimos la contraseña por consola
    print("\n--- Configuración del usuario administrador ---")
    password = input("Ingrese la contraseña para el usuario 'admin': ").strip()
    if not password:
        password = "admin123"
        print(f"[INFO] Se usó la contraseña por defecto: admin123")

    # Ciframos la contraseña con bcrypt
    password_bytes = password.encode("utf-8")
    hash_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    conn = mysql.connector.connect(**params)
    cursor = conn.cursor()

    # Verificamos si el admin ya existe
    cursor.execute("SELECT id_usuario FROM usuario WHERE username = 'admin'")
    existe = cursor.fetchone()

    if existe:
        # Actualizamos la contraseña si ya existe
        cursor.execute(
            "UPDATE usuario SET password_hash = %s WHERE username = 'admin'",
            (hash_password,)
        )
        print("[OK] Contraseña del admin actualizada.")
    else:
        # Insertamos el admin nuevo
        cursor.execute(
            """INSERT INTO usuario (username, password_hash, nombre_completo, email)
               VALUES (%s, %s, %s, %s)""",
            ("admin", hash_password, "Administrador del Sistema", "admin@dppps.gob.ve")
        )
        print("[OK] Usuario admin creado.")

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    print("=== Setup inicial del Sistema DPPPS ===\n")
    try:
        crear_base_de_datos()
        ejecutar_schema()
        crear_usuario_admin()
        print("\n[LISTO] Setup completado exitosamente.")
        print("   Ya puedes ejecutar la aplicacion con: python main.py")
    except Exception as e:
        print(f"\n[ERROR] Error durante el setup: {e}")
        print("   Verifica que MariaDB/MySQL este corriendo y los datos en config/settings.py sean correctos.")
