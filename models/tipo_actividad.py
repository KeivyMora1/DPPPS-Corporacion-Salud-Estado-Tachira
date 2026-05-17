# ============================================================
# models/tipo_actividad.py
# DAO para la tabla 'tipo_actividad'.
# Catálogo de tipos de actividad del sistema.
# ============================================================

from db.connection import get_connection


class TipoActividadDAO:

    def obtener_todos(self):
        """Retorna todos los tipos de actividad activos."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_actividad WHERE activo = TRUE ORDER BY nombre")
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_tipo):
        """Busca un tipo por su ID. Retorna dict o None."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_actividad WHERE id_tipo = %s", (id_tipo,))
        tipo = cursor.fetchone()
        cursor.close()
        conn.close()
        return tipo

    def obtener_por_codigo(self, codigo):
        """Busca un tipo por su código único. Útil para validar duplicados."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_actividad WHERE codigo = %s", (codigo,))
        tipo = cursor.fetchone()
        cursor.close()
        conn.close()
        return tipo

    def crear(self, codigo, nombre, descripcion=""):
        """Inserta un nuevo tipo de actividad. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tipo_actividad (codigo, nombre, descripcion) VALUES (%s, %s, %s)",
            (codigo, nombre, descripcion)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id

    def actualizar(self, id_tipo, codigo, nombre, descripcion=""):
        """Actualiza un tipo de actividad existente."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tipo_actividad SET codigo=%s, nombre=%s, descripcion=%s WHERE id_tipo=%s",
            (codigo, nombre, descripcion, id_tipo)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def desactivar(self, id_tipo):
        """Soft delete: marca el tipo como inactivo."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tipo_actividad SET activo = FALSE WHERE id_tipo = %s", (id_tipo,))
        conn.commit()
        cursor.close()
        conn.close()
