# ============================================================
# models/evidencia.py
# DAO para la tabla 'evidencia'.
# Maneja la inserción, consulta y eliminación de referencias
# de archivos adjuntos (evidencias) en la base de datos.
# ============================================================

from db.connection import get_connection


class EvidenciaDAO:

    def obtener_por_actividad(self, id_actividad):
        """
        Retorna la lista de todas las evidencias asociadas a una actividad.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT id_evidencia, id_actividad, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes, created_at
            FROM evidencia
            WHERE id_actividad = %s
            ORDER BY id_evidencia ASC
        """
        cursor.execute(sql, (id_actividad,))
        lista = cursor.fetchall()

        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_evidencia):
        """
        Retorna la información de una evidencia específica por su ID.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT id_evidencia, id_actividad, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes, created_at
            FROM evidencia
            WHERE id_evidencia = %s
        """
        cursor.execute(sql, (id_evidencia,))
        evidencia = cursor.fetchone()

        cursor.close()
        conn.close()
        return evidencia

    def crear(self, id_actividad, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes):
        """
        Inserta una nueva referencia de evidencia en la base de datos.
        Retorna el ID autogenerado.
        """
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO evidencia (id_actividad, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (id_actividad, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes)
        
        cursor.execute(sql, valores)
        conn.commit()
        nuevo_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return nuevo_id

    def eliminar(self, id_evidencia):
        """
        Elimina el registro de una evidencia de la base de datos.
        Nota: Este método no elimina el archivo físico del disco, eso lo hace el controlador.
        """
        conn = get_connection()
        cursor = conn.cursor()

        sql = "DELETE FROM evidencia WHERE id_evidencia = %s"
        cursor.execute(sql, (id_evidencia,))
        conn.commit()

        cursor.close()
        conn.close()
