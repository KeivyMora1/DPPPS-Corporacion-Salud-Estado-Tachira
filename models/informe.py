# ============================================================
# models/informe.py
# DAOs para las tablas 'periodo', 'informe_consolidado'
# e 'informe_detalle'.
# Maneja todas las consultas relacionadas con la consolidación
# y el historial de informes generados.
# ============================================================

from db.connection import get_connection


# ============================================================
# PeriodoDAO — gestión de períodos de consolidación
# ============================================================

class PeriodoDAO:

    def obtener_todos(self):
        """Retorna todos los períodos ordenados por fecha descendente."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*,
                   u.nombre_completo AS usuario_cierre_nombre
            FROM periodo p
            LEFT JOIN usuario u ON p.id_usuario_cierre = u.id_usuario
            ORDER BY p.fecha_inicio DESC
        """)
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_periodo):
        """Retorna un período por su ID."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, u.nombre_completo AS usuario_cierre_nombre
            FROM periodo p
            LEFT JOIN usuario u ON p.id_usuario_cierre = u.id_usuario
            WHERE p.id_periodo = %s
        """, (id_periodo,))
        periodo = cursor.fetchone()
        cursor.close()
        conn.close()
        return periodo

    def crear(self, tipo, anio, mes_inicio, mes_fin, fecha_inicio, fecha_fin):
        """Crea un nuevo período. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO periodo (tipo, anio, mes_inicio, mes_fin, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (tipo, anio, mes_inicio, mes_fin, fecha_inicio, fecha_fin))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id

    def cerrar(self, id_periodo, id_usuario_cierre):
        """Marca el período como cerrado."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE periodo
            SET estado = 'cerrado',
                id_usuario_cierre = %s,
                fecha_cierre = NOW()
            WHERE id_periodo = %s
        """, (id_usuario_cierre, id_periodo))
        conn.commit()
        cursor.close()
        conn.close()

    def reabrir(self, id_periodo, motivo):
        """Reabre un período cerrado, registrando el motivo."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE periodo
            SET estado = 'abierto',
                id_usuario_cierre = NULL,
                fecha_cierre = NULL,
                motivo_reapertura = %s
            WHERE id_periodo = %s
        """, (motivo, id_periodo))
        conn.commit()
        cursor.close()
        conn.close()

    def eliminar(self, id_periodo):
        """Elimina un período (solo si no tiene informes asociados)."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM periodo WHERE id_periodo = %s", (id_periodo,))
        conn.commit()
        cursor.close()
        conn.close()


# ============================================================
# InformeDAO — gestión de informes consolidados
# ============================================================

class InformeDAO:

    def obtener_todos(self):
        """Retorna todos los informes generados, ordenados por fecha desc."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ic.*,
                   p.tipo  AS periodo_tipo,
                   p.anio  AS periodo_anio,
                   p.mes_inicio, p.mes_fin,
                   a.nombre AS asic_nombre,
                   u.nombre_completo AS generador_nombre
            FROM informe_consolidado ic
            JOIN periodo p ON ic.id_periodo = p.id_periodo
            LEFT JOIN asic a ON ic.id_asic = a.id_asic
            JOIN usuario u ON ic.id_usuario_generador = u.id_usuario
            ORDER BY ic.fecha_generacion DESC
        """)
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_informe):
        """Retorna la cabecera de un informe por su ID."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ic.*,
                   p.tipo AS periodo_tipo, p.anio AS periodo_anio,
                   p.fecha_inicio AS periodo_fecha_inicio,
                   p.fecha_fin   AS periodo_fecha_fin,
                   p.mes_inicio, p.mes_fin,
                   a.nombre AS asic_nombre,
                   u.nombre_completo AS generador_nombre
            FROM informe_consolidado ic
            JOIN periodo p ON ic.id_periodo = p.id_periodo
            LEFT JOIN asic a ON ic.id_asic = a.id_asic
            JOIN usuario u ON ic.id_usuario_generador = u.id_usuario
            WHERE ic.id_informe = %s
        """, (id_informe,))
        informe = cursor.fetchone()
        cursor.close()
        conn.close()
        return informe

    def obtener_detalle(self, id_informe):
        """
        Retorna las actividades incluidas en un informe,
        con todos los campos necesarios para exportación/PDF.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.id_actividad, a.fecha_inicio, a.fecha_fin,
                   a.lugar, a.descripcion, a.participantes,
                   asic.nombre  AS asic_nombre,
                   ta.nombre    AS tipo_nombre
            FROM informe_detalle id2
            JOIN actividad a    ON id2.id_actividad = a.id_actividad
            JOIN asic           ON a.id_asic = asic.id_asic
            JOIN tipo_actividad ta ON a.id_tipo = ta.id_tipo
            WHERE id2.id_informe = %s
            ORDER BY asic.nombre, a.fecha_inicio
        """, (id_informe,))
        detalle = cursor.fetchall()
        cursor.close()
        conn.close()
        return detalle

    def crear(self, id_periodo, id_asic, titulo, total_actividades,
              total_participantes, observaciones, id_usuario_generador):
        """Inserta la cabecera de un informe. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO informe_consolidado
                (id_periodo, id_asic, titulo, total_actividades,
                 total_participantes, observaciones, id_usuario_generador)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_periodo, id_asic, titulo, total_actividades,
              total_participantes, observaciones, id_usuario_generador))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id

    def insertar_detalle(self, id_informe, ids_actividades):
        """Inserta en bloque los registros de informe_detalle."""
        if not ids_actividades:
            return
        conn = get_connection()
        cursor = conn.cursor()
        valores = [(id_informe, id_act) for id_act in ids_actividades]
        cursor.executemany(
            "INSERT INTO informe_detalle (id_informe, id_actividad) VALUES (%s, %s)",
            valores
        )
        conn.commit()
        cursor.close()
        conn.close()

    def eliminar(self, id_informe):
        """Elimina el informe y sus detalles (CASCADE si está configurado, o manual)."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM informe_detalle WHERE id_informe = %s", (id_informe,))
        cursor.execute("DELETE FROM informe_consolidado WHERE id_informe = %s", (id_informe,))
        conn.commit()
        cursor.close()
        conn.close()

    def obtener_resumen_por_asic(self, id_informe):
        """
        Retorna un resumen agrupado por ASIC para un informe dado.
        Útil para mostrar la tabla de resumen en el PDF.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT asic.nombre AS asic_nombre,
                   COUNT(a.id_actividad)  AS total_actividades,
                   SUM(a.participantes)   AS total_participantes
            FROM informe_detalle id2
            JOIN actividad a ON id2.id_actividad = a.id_actividad
            JOIN asic       ON a.id_asic = asic.id_asic
            WHERE id2.id_informe = %s
            GROUP BY asic.id_asic, asic.nombre
            ORDER BY asic.nombre
        """, (id_informe,))
        resumen = cursor.fetchall()
        cursor.close()
        conn.close()
        return resumen
