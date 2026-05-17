# ============================================================
# models/asic.py
# DAO para la tabla 'asic'.
# Maneja todas las consultas relacionadas con las
# Áreas de Salud Integral Comunitaria (ASIC).
# ============================================================

from db.connection import get_connection


class AsicDAO:

    def obtener_todos(self):
        """Retorna lista de todos los ASIC activos."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asic WHERE activo = TRUE ORDER BY nombre")
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_asic):
        """Busca un ASIC por su ID. Retorna dict o None."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asic WHERE id_asic = %s", (id_asic,))
        asic = cursor.fetchone()
        cursor.close()
        conn.close()
        return asic

    def obtener_por_codigo(self, codigo):
        """Busca un ASIC por su código único. Útil para validar duplicados."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asic WHERE codigo = %s", (codigo,))
        asic = cursor.fetchone()
        cursor.close()
        conn.close()
        return asic

    def crear(self, codigo, nombre, municipio="", parroquia=""):
        """Inserta un nuevo ASIC. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO asic (codigo, nombre, municipio, parroquia) VALUES (%s, %s, %s, %s)",
            (codigo, nombre, municipio, parroquia)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id

    def actualizar(self, id_asic, codigo, nombre, municipio="", parroquia=""):
        """Actualiza los datos de un ASIC existente."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE asic SET codigo=%s, nombre=%s, municipio=%s, parroquia=%s WHERE id_asic=%s",
            (codigo, nombre, municipio, parroquia, id_asic)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def desactivar(self, id_asic):
        """Soft delete: marca el ASIC como inactivo en vez de borrarlo."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE asic SET activo = FALSE WHERE id_asic = %s", (id_asic,))
        conn.commit()
        cursor.close()
        conn.close()
