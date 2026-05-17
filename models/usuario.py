# ============================================================
# models/usuario.py
# DAO (Data Access Object) de la tabla 'usuario'.
# Contiene todas las consultas SQL relacionadas con usuarios.
# ============================================================

import bcrypt
from db.connection import get_connection


class UsuarioDAO:
    """
    Clase que maneja todas las operaciones de la tabla 'usuario'.
    Cada método realiza una operación específica en la base de datos.
    """

    def obtener_por_username(self, username):
        """
        Busca un usuario por su nombre de usuario.
        Retorna un diccionario con los datos del usuario, o None si no existe.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)  # dictionary=True para obtener dicts en vez de tuplas

        cursor.execute(
            "SELECT * FROM usuario WHERE username = %s AND activo = TRUE",
            (username,)
        )
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()
        return usuario

    def verificar_password(self, password_plano, password_hash):
        """
        Verifica si una contraseña en texto plano coincide con el hash guardado.
        Retorna True si coincide, False si no.
        """
        return bcrypt.checkpw(
            password_plano.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    def obtener_todos(self):
        """
        Retorna una lista con todos los usuarios activos del sistema.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_usuario, username, nombre_completo, email, activo, created_at "
            "FROM usuario ORDER BY nombre_completo"
        )
        usuarios = cursor.fetchall()

        cursor.close()
        conn.close()
        return usuarios

    def crear(self, username, password, nombre_completo, email=""):
        """
        Crea un nuevo usuario en la base de datos.
        La contraseña se cifra automáticamente con bcrypt.
        """
        # Ciframos la contraseña antes de guardarla
        hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO usuario (username, password_hash, nombre_completo, email)
               VALUES (%s, %s, %s, %s)""",
            (username, hash_pw, nombre_completo, email)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid  # ID del usuario recién creado

        cursor.close()
        conn.close()
        return nuevo_id

    def cambiar_password(self, id_usuario, nueva_password):
        """
        Cambia la contraseña de un usuario existente.
        """
        hash_pw = bcrypt.hashpw(nueva_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE usuario SET password_hash = %s WHERE id_usuario = %s",
            (hash_pw, id_usuario)
        )
        conn.commit()

        cursor.close()
        conn.close()

    def desactivar(self, id_usuario):
        """
        Desactiva un usuario (no lo borra, solo lo marca como inactivo).
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE usuario SET activo = FALSE WHERE id_usuario = %s",
            (id_usuario,)
        )
        conn.commit()

        cursor.close()
        conn.close()
