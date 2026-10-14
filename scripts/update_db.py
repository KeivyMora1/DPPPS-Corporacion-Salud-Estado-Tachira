#!/usr/bin/env python3
"""Aplica schema.sql a la base de datos usando la configuración del paquete db.

Uso:
  python scripts/update_db.py [--schema PATH] [--backup] [--use-cli]

Opciones:
  --schema PATH   Archivo de schema (default: schema.sql)
  --backup        Hace backup con mysqldump antes de aplicar
  --use-cli       Usa el CLI `mysql` en vez del conector Python
"""
import os
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import mysql.connector
except Exception:
    mysql = None

def load_db_config():
    import db as dbmod
    params = dbmod.DATABASE[dbmod.MODO]
    return params

def do_backup(params, out_path):
    cmd = [
        "mysqldump",
        "-h", params.get("host", "localhost"),
        "-P", str(params.get("port", 3306)),
        "-u", params.get("user", "root"),
        params.get("database")
    ]
    # Verify mysqldump is available; otherwise abort before creating empty file
    import shutil
    if shutil.which("mysqldump") is None:
        print('[ERROR] mysqldump no está en el PATH. Instala MySQL/MariaDB client tools o elimina la opción --backup.')
        sys.exit(2)
    env = os.environ.copy()
    pw = params.get("password")
    if pw:
        env["MYSQL_PWD"] = pw
    with open(out_path, "wb") as f:
        print("[INFO] Ejecutando:", " ".join(cmd))
        subprocess.run(cmd, check=True, stdout=f, env=env)

def apply_with_cli(params, schema_path):
    cmd = [
        "mysql",
        "-h", params.get("host", "localhost"),
        "-P", str(params.get("port", 3306)),
        "-u", params.get("user", "root"),
        params.get("database")
    ]
    env = os.environ.copy()
    pw = params.get("password")
    if pw:
        env["MYSQL_PWD"] = pw
    with open(schema_path, "rb") as f:
        print("[INFO] Aplicando schema con mysql CLI...")
        subprocess.run(cmd, check=True, stdin=f, env=env)
    print("[OK] Schema aplicado (cliente CLI)")

def apply_with_connector(params, schema_path):
    if mysql is None:
        print("[ERROR] mysql.connector no está disponible. Instala 'mysql-connector-python' o usa --use-cli")
        sys.exit(2)
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    print("[INFO] Conectando a la base de datos...")
    conn = mysql.connector.connect(
        host=params.get("host", "localhost"),
        port=params.get("port", 3306),
        user=params.get("user", "root"),
        password=params.get("password", ""),
        database=params.get("database")
    )
    cursor = conn.cursor()
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

        print("[INFO] Ejecutando statements del schema...")
        clean_lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
        clean_sql = "\n".join(clean_lines)
        statements = [s.strip() for s in clean_sql.split(';') if s.strip()]
        for stmt in statements:
            cursor.execute(stmt)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    print("[OK] Schema aplicado (mysql-connector)")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--schema", default="schema.sql")
    p.add_argument("--backup", action="store_true")
    p.add_argument("--py-backup", action="store_true", help="Genera backup usando mysql-connector-python (no requiere mysqldump)")
    p.add_argument("--use-cli", action="store_true")
    args = p.parse_args()

    schema_path = args.schema
    if not os.path.exists(schema_path):
        print(f"[ERROR] No se encontró el archivo de esquema: {schema_path}")
        sys.exit(1)

    params = load_db_config()

    if args.backup:
        backup_file = f"backup_{params.get('database')}.sql"
        try:
            do_backup(params, backup_file)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Falló el backup: {e}")
            sys.exit(2)

    try:
        if args.use_cli:
            apply_with_cli(params, schema_path)
        else:
            apply_with_connector(params, schema_path)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Comando externo falló: {e}")
        sys.exit(3)
    except Exception as e:
        print(f"[ERROR] Error aplicando el schema: {e}")
        sys.exit(4)

if __name__ == "__main__":
    main()
