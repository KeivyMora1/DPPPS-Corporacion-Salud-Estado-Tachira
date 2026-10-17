"""Database initialization helpers and command-line entry point."""

import argparse
from pathlib import Path

import bcrypt
import mysql.connector

from constants import (
    DATABASE,
    EMAIL_PROPIETARIO_PREDETERMINADO,
    MODO,
    PASSWORD_PROPIETARIO_PREDETERMINADO,
    USUARIO_PROPIETARIO_PREDETERMINADO,
)

def crear_base_de_datos() -> None:
    """Create the configured database if it does not already exist."""
    config = DATABASE[MODO].copy()
    database_name = config.pop("database")
    connection = mysql.connector.connect(**config)
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()
    print(f"[OK] Base de datos '{database_name}' lista.")

def ejecutar_schema(ruta_schema: str | Path | None = None) -> None:
    """Apply schema.sql, ignoring only already-existing schema objects."""
    schema_path = (
        Path(ruta_schema)
        if ruta_schema is not None
        else Path(__file__).resolve().parent.parent / "schema.sql"
    )
    sql = schema_path.read_text(encoding="utf-8")
    connection = mysql.connector.connect(**DATABASE[MODO])
    try:
        cursor = connection.cursor()
        try:
            # Migración: si existe la tabla parroquia legada (con id_asic), recrearla con el nuevo esquema
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'parroquia'
                  AND COLUMN_NAME = 'id_asic'
            """)
            if cursor.fetchone()[0] > 0:
                cursor.execute("DROP TABLE IF EXISTS parroquia")

            clean_lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
            clean_sql = "\n".join(clean_lines)
            statements = [statement.strip() for statement in clean_sql.split(";") if statement.strip()]
            for statement in statements:
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as error:
                    if error.errno not in (1050, 1060, 1061):
                        raise
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()
    print("[OK] Tablas creadas correctamente.")

def crear_usuario_propietario() -> None:
    """Create the default owner account when the user table is empty."""
    connection = mysql.connector.connect(**DATABASE[MODO])
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM usuario")
            cantidad_usuarios = cursor.fetchone()[0]
            if cantidad_usuarios:
                print("[INFO] Ya existen usuarios; no se creó el usuario propietario inicial.")
                return

            if not EMAIL_PROPIETARIO_PREDETERMINADO:
                raise ValueError(
                    "Configura OWNER_EMAIL en el archivo .env con un valor no vacío "
                    "antes de crear el usuario propietario."
                )

            password_hash = bcrypt.hashpw(
                PASSWORD_PROPIETARIO_PREDETERMINADO.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")
            cursor.execute(
                """
                INSERT INTO usuario (
                    username, password_hash, nombre_completo, email, rol, email_verificado
                )
                VALUES (%s, %s, %s, %s, 'propietario', TRUE)
                """,
                (
                    USUARIO_PROPIETARIO_PREDETERMINADO,
                    password_hash,
                    "Usuario propietario",
                    EMAIL_PROPIETARIO_PREDETERMINADO,
                ),
            )
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()

    print(
        f"[OK] Usuario propietario creado: "
        f"{USUARIO_PROPIETARIO_PREDETERMINADO}."
    )

def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the DPPPS database.")
    parser.add_argument(
        "--schema",
        type=Path,
        help="Schema file to apply (defaults to the project schema.sql).",
    )
    args = parser.parse_args()

    print("=== Setup inicial del Sistema DPPPS ===\n")
    crear_base_de_datos()
    ejecutar_schema(args.schema)
    crear_usuario_propietario()
    print("\n[LISTO] Setup completado exitosamente.")
    print("   Ya puedes ejecutar la aplicación con: python main.py")

if __name__ == "__main__":
    main()
