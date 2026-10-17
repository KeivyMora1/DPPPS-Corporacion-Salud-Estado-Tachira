"""
DAO para la tabla usuario.
Migración a BaseDAO manteniendo API idéntica al legacy.
"""

import bcrypt
from typing import Optional, Dict, Any, List

from ..base_dao import BaseDAO

class UsuarioDAO(BaseDAO):
    TABLA = "usuario"
    CAMPOS = [
        "username", "password_hash", "nombre_completo", "email",
        "nombre", "apellido", "rol", "email_verificado",
        "codigo_verificacion", "codigo_verificacion_expira",
        "codigo_recuperacion", "codigo_recuperacion_expira",
        "activo", "created_at"
    ]
    CAMPO_ID = "id_usuario"

    def obtener_por_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.obtener_uno("username = %s AND activo = TRUE", (username,))

    def obtener_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        email_norm = (email or "").lower().strip()
        return self.obtener_uno("email = %s AND activo = TRUE", (email_norm,))

    def obtener_propietario(self) -> Optional[Dict[str, Any]]:
        return self.obtener_uno(
            "rol = %s AND activo = TRUE ORDER BY id_usuario LIMIT 1",
            ("propietario",)
        )

    @staticmethod
    def verificar_password(password_plano: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            password_plano.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    def obtener_todos(self) -> List[Dict[str, Any]]:
        return super().obtener_todos(orden_por="nombre_completo")

    def crear(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        nombre_completo: Optional[str] = None,
        email: str = "",
        **kwargs
    ) -> int:
        if username is None:
            username = kwargs.get("username") or (email or "").lower().strip()
        if password is None:
            password = kwargs.get("password", "")
        if nombre_completo is None:
            nombre_completo = kwargs.get("nombre_completo") or ""

        hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        email_normalizada = (email or kwargs.get("email") or "").lower().strip()
        nombre = kwargs.get("nombre", "").strip()
        apellido = kwargs.get("apellido", "").strip()
        codigo_verificacion = kwargs.get("codigo_verificacion", "")
        codigo_verificacion_expira = kwargs.get("codigo_verificacion_expira")
        rol_solicitado = kwargs.get("rol", "lector")
        administrador_autorizado = kwargs.get("administrador_autorizado", False)

        if rol_solicitado not in ("lector", "administrador"):
            raise ValueError("Rol de usuario no válido.")
        if rol_solicitado == "administrador" and not administrador_autorizado:
            raise ValueError("Se requiere autorización del propietario para crear administradores.")

        import db

        conn = db.get_connection()
        cursor = conn.cursor()
        lock_adquirido = False
        try:
            cursor.execute("SELECT GET_LOCK(%s, 10)", ("dppps_registro_usuario",))
            resultado_lock = cursor.fetchone()
            lock_adquirido = bool(resultado_lock and resultado_lock[0] == 1)
            if not lock_adquirido:
                raise RuntimeError("No se pudo asegurar el registro de la cuenta.")

            cursor.execute("SELECT COUNT(*) FROM usuario")
            cantidad_usuarios = cursor.fetchone()[0]
            rol = "propietario" if cantidad_usuarios == 0 else rol_solicitado

            usa_esquema_extendido = bool(
                nombre or apellido or codigo_verificacion or codigo_verificacion_expira is not None
            )

            if usa_esquema_extendido:
                cursor.execute(
                    """
                    INSERT INTO usuario (
                        username, password_hash, nombre_completo, email, nombre, apellido,
                        rol, email_verificado, codigo_verificacion, codigo_verificacion_expira, activo
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, %s, %s, TRUE)
                    """,
                    (
                        username.strip(),
                        hash_pw,
                        nombre_completo or f"{nombre} {apellido}".strip(),
                        email_normalizada,
                        nombre,
                        apellido,
                        rol,
                        codigo_verificacion,
                        codigo_verificacion_expira,
                    )
                )
            else:
                cursor.execute(
                    """INSERT INTO usuario (username, password_hash, nombre_completo, email, rol)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (username, hash_pw, nombre_completo, email_normalizada, rol)
                )

            usuario_id = cursor.lastrowid
            conn.commit()
            return usuario_id
        except Exception:
            conn.rollback()
            raise
        finally:
            if lock_adquirido:
                try:
                    cursor.execute("SELECT RELEASE_LOCK(%s)", ("dppps_registro_usuario",))
                    cursor.fetchone()
                except Exception:
                    pass
            cursor.close()
            conn.close()

    def guardar_codigo_verificacion(self, email: str, codigo: str, expiracion) -> None:
        email_norm = (email or "").lower().strip()
        self.actualizar_por(
            "email = %s AND activo = TRUE",
            (email_norm,),
            {
                "codigo_verificacion": codigo,
                "codigo_verificacion_expira": expiracion,
            }
        )

    def guardar_codigo_recuperacion(self, email: str, codigo: str, expiracion) -> None:
        email_norm = (email or "").lower().strip()
        self.actualizar_por(
            "email = %s AND activo = TRUE",
            (email_norm,),
            {
                "codigo_recuperacion": codigo,
                "codigo_recuperacion_expira": expiracion,
            }
        )

    def cambiar_password(self, id_usuario: int, nueva_password: str) -> None:
        hash_pw = bcrypt.hashpw(nueva_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.actualizar(id_usuario, {"password_hash": hash_pw})


def asegurar_esquema_autenticacion() -> None:
    from ..connection import obtener_conexion_directa
    import mysql.connector

    try:
        conn = obtener_conexion_directa()
    except mysql.connector.Error:
        return

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW COLUMNS FROM usuario")
        columnas = {columna["Field"] for columna in cursor.fetchall()}

        cambios = {
            "nombre": "ALTER TABLE usuario ADD COLUMN nombre VARCHAR(100) NULL",
            "apellido": "ALTER TABLE usuario ADD COLUMN apellido VARCHAR(100) NULL",
            "rol": "ALTER TABLE usuario ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'lector'",
            "email_verificado": "ALTER TABLE usuario ADD COLUMN email_verificado BOOLEAN NOT NULL DEFAULT FALSE",
            "codigo_verificacion": "ALTER TABLE usuario ADD COLUMN codigo_verificacion VARCHAR(20) NULL",
            "codigo_verificacion_expira": "ALTER TABLE usuario ADD COLUMN codigo_verificacion_expira DATETIME NULL",
            "codigo_recuperacion": "ALTER TABLE usuario ADD COLUMN codigo_recuperacion VARCHAR(20) NULL",
            "codigo_recuperacion_expira": "ALTER TABLE usuario ADD COLUMN codigo_recuperacion_expira DATETIME NULL",
        }

        for nombre_columna, sentencia in cambios.items():
            if nombre_columna not in columnas:
                try:
                    cursor.execute(sentencia)
                except Exception:
                    pass

        cursor.execute("SELECT id_usuario FROM usuario WHERE rol = 'propietario' ORDER BY id_usuario LIMIT 1")
        propietario = cursor.fetchone()
        if propietario is None:
            cursor.execute("SELECT id_usuario FROM usuario ORDER BY id_usuario LIMIT 1")
            primer_usuario = cursor.fetchone()
            if primer_usuario:
                cursor.execute(
                    "UPDATE usuario SET rol = 'propietario' WHERE id_usuario = %s",
                    (primer_usuario["id_usuario"],),
                )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


asegurar_esquema_autenticacion()