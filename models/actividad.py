# ============================================================
# models/actividad.py
# DAO para la tabla 'actividad'.
# Maneja las consultas SQL para registrar, editar, listar
# y eliminar actividades del sistema.
# ============================================================

from db.connection import get_connection


class ActividadDAO:

    def obtener_todas(self, filtros=None):
        """
        Retorna todas las actividades activas (no eliminadas).
        Puede recibir filtros como dict: {id_asic, id_tipo, fecha_desde, fecha_hasta}
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Consulta base
        sql = """
            SELECT a.id_actividad, a.id_asic, a.id_tipo, a.id_usuario_registro,
                   a.fecha_inicio, a.fecha_fin, a.lugar, a.descripcion, a.participantes,
                   a.created_at,
                   asic.nombre AS asic_nombre,
                   ta.nombre AS tipo_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM actividad a
            JOIN asic ON a.id_asic = asic.id_asic
            JOIN tipo_actividad ta ON a.id_tipo = ta.id_tipo
            JOIN usuario u ON a.id_usuario_registro = u.id_usuario
            WHERE a.eliminado = FALSE
        """
        
        params = []

        # Agregar filtros dinámicos si se especifican
        if filtros:
            if filtros.get("id_asic"):
                sql += " AND a.id_asic = %s"
                params.append(filtros["id_asic"])
            
            if filtros.get("id_tipo"):
                sql += " AND a.id_tipo = %s"
                params.append(filtros["id_tipo"])
            
            if filtros.get("fecha_desde"):
                sql += " AND a.fecha_inicio >= %s"
                params.append(filtros["fecha_desde"])
            
            if filtros.get("fecha_hasta"):
                sql += " AND a.fecha_fin <= %s"
                params.append(filtros["fecha_hasta"])

        # Ordenar por fecha de inicio descendente (más recientes primero)
        sql += " ORDER BY a.fecha_inicio DESC, a.id_actividad DESC"

        cursor.execute(sql, tuple(params))
        lista = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_actividad):
        """
        Retorna los detalles de una actividad específica por su ID.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT a.*,
                   asic.nombre AS asic_nombre,
                   ta.nombre AS tipo_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM actividad a
            JOIN asic ON a.id_asic = asic.id_asic
            JOIN tipo_actividad ta ON a.id_tipo = ta.id_tipo
            JOIN usuario u ON a.id_usuario_registro = u.id_usuario
            WHERE a.id_actividad = %s AND a.eliminado = FALSE
        """
        cursor.execute(sql, (id_actividad,))
        actividad = cursor.fetchone()

        cursor.close()
        conn.close()
        return actividad

    def crear(self, id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin, lugar, descripcion, participantes):
        """
        Inserta una nueva actividad en la base de datos.
        Retorna el ID de la actividad creada.
        """
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO actividad (id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin, lugar, descripcion, participantes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin, lugar, descripcion, participantes)
        
        cursor.execute(sql, valores)
        conn.commit()
        nuevo_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return nuevo_id

    def actualizar(self, id_actividad, id_asic, id_tipo, fecha_inicio, fecha_fin, lugar, descripcion, participantes):
        """
        Actualiza los datos de una actividad existente.
        """
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE actividad 
            SET id_asic = %s, id_tipo = %s, fecha_inicio = %s, fecha_fin = %s, 
                lugar = %s, descripcion = %s, participantes = %s 
            WHERE id_actividad = %s
        """
        valores = (id_asic, id_tipo, fecha_inicio, fecha_fin, lugar, descripcion, participantes, id_actividad)
        
        cursor.execute(sql, valores)
        conn.commit()

        cursor.close()
        conn.close()

    def eliminar(self, id_actividad):
        """
        Realiza un borrado lógico (soft delete) marcando el registro como eliminado.
        """
        conn = get_connection()
        cursor = conn.cursor()

        sql = "UPDATE actividad SET eliminado = TRUE WHERE id_actividad = %s"
        cursor.execute(sql, (id_actividad,))
        conn.commit()

        cursor.close()
        conn.close()

    def verificar_duplicado(self, id_asic, id_tipo, fecha_inicio, descripcion, excluir_id=None):
        """
        Comprueba si ya existe una actividad con el mismo ASIC, Tipo, Fecha de inicio
        y una descripción similar (primeros 100 caracteres normalizados sin espacios).
        Retorna True si es duplicado, False en caso contrario.
        """
        # Normalizar descripción a evaluar: minúsculas, sin espacios duplicados ni bordes, máx 100 caracteres.
        desc_normalizada = " ".join(descripcion.lower().strip().split())[:100]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscamos actividades activas en el mismo ASIC, tipo y fecha
        sql = """
            SELECT id_actividad, descripcion 
            FROM actividad 
            WHERE id_asic = %s AND id_tipo = %s AND fecha_inicio = %s AND eliminado = FALSE
        """
        params = [id_asic, id_tipo, fecha_inicio]

        # Si estamos editando, excluimos la actividad actual de la búsqueda
        if excluir_id is not None:
            sql += " AND id_actividad != %s"
            params.append(excluir_id)

        cursor.execute(sql, tuple(params))
        resultados = cursor.fetchall()

        cursor.close()
        conn.close()

        # Comparamos las descripciones normalizadas en Python (fácil de entender y explicar)
        for registro in resultados:
            reg_desc_normalizada = " ".join(registro["descripcion"].lower().strip().split())[:100]
            if reg_desc_normalizada == desc_normalizada:
                return True # ¡Duplicado detectado!

        return False
