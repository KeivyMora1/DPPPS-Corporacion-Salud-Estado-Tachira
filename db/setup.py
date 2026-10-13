"""Database initialization helpers and command-line entry point."""

import argparse
from pathlib import Path

import mysql.connector

from constants import DATABASE, MODO


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
            statements = [statement.strip() for statement in sql.split(";") if statement.strip()]
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
    print("\n[LISTO] Setup completado exitosamente.")
    print("   Ya puedes ejecutar la aplicación con: python main.py")


if __name__ == "__main__":
    main()
