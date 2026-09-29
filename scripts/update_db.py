#!/usr/bin/env python3
"""Aplica schema.sql a la base de datos usando la config de db.py.

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
    env = os.environ.copy()
    pw = params.get("password")
    if pw:
        env["MYSQL_PWD"] = pw
    with open(out_path, "wb") as f:
        print("[INFO] Ejecutando:", " ".join(cmd))
        subprocess.run(cmd, check=True, stdout=f, env=env)
    print(f"[OK] Backup guardado en: {out_path}")

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
    print("[INFO] Ejecutando statements del schema...")
    try:
        statements = [s.strip() for s in sql.split(';') if s.strip()]
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
