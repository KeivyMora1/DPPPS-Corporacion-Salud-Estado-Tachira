# ============================================================
# db.py
# Archivo único de base de datos y lógica del sistema DPPPS.
#
# Contiene (en orden):
#   1. Configuración general (antes en config/settings.py)
#   2. Conexión a la BD (antes en db/connection.py)
#   3. DAOs — consultas SQL (antes en models/)
#   4. Controladores — lógica y validación (antes en controllers/)
#   5. Servicios — Excel, PDF, Consolidación (antes en services/)
#   6. Setup inicial de BD (antes en db/setup.py)
#
# Para configurar la BD por primera vez ejecuta:
#   python db.py
# ============================================================
# ============================================================
# SECCIÓN 1 — CONFIGURACIÓN GENERAL
# (antes en config/settings.py)
# ============================================================
# Modo de conexión: "local" usa localhost, "lan" usa una IP de red
MODO = "local"
# Parámetros de conexión para cada modo
DATABASE = {
    "local": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",          # Cambia esto si tu MariaDB/MySQL tiene contraseña
        "database": "dppps_informes"
    },
    "lan": {
        "host": "192.168.1.100", # Cambia esto por la IP del servidor en la red
        "port": 3306,
        "user": "dppps_app",
        "password": "contraseña_segura",
        "database": "dppps_informes"
    }
}
# Carpetas donde se guardan los archivos subidos y los reportes generados
UPLOADS_DIR = "uploads/"
EXPORTS_DIR = "exports/"
# Ruta de la plantilla Excel para importación de actividades
TEMPLATE_PATH = "assets/templates/plantilla_importacion.xlsx"
# Tipos de archivo permitidos para evidencias
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf", ".docx"]
# Tamaño máximo de archivo en MB
MAX_FILE_SIZE_MB = 10
# Título de la aplicación (se muestra en la barra de la ventana)
APP_TITLE = "DPPPS — Sistema de Consolidación de Informes"
APP_VERSION = "1.0.0"
# ============================================================
# SECCIÓN 2 — CONEXIÓN A LA BASE DE DATOS
# (antes en db/connection.py)
# ============================================================
import mysql.connector
def get_connection():
    """
    Crea y devuelve una conexión a la base de datos.
    Usa el modo definido en MODO (local o lan).
    Ejemplo de uso:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario")
        conn.close()
    """
    params = DATABASE[MODO]
    try:
        conn = mysql.connector.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"]
        )
        return conn
    except mysql.connector.Error as error:
        print(f"[ERROR] No se pudo conectar a la base de datos: {error}")
        raise
# ============================================================
# SECCIÓN 3 — DAOs (Data Access Objects)
# Cada clase maneja las consultas SQL de una tabla.
# (antes en models/)
# ============================================================
import bcrypt
from datetime import date, datetime
class UsuarioDAO:
    """
    Maneja todas las operaciones de la tabla 'usuario'.
    Cada método realiza una operación específica en la base de datos.
    """
    def obtener_por_username(self, username):
        """Busca un usuario por su nombre de usuario. Retorna dict o None."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuario WHERE username = %s AND activo = TRUE",
            (username,)
        )
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return usuario
    def verificar_password(self, password_plano, password_hash):
        """Verifica si una contraseña en texto plano coincide con el hash guardado."""
        return bcrypt.checkpw(
            password_plano.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    def obtener_todos(self):
        """Retorna una lista con todos los usuarios activos del sistema."""
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
        """Crea un nuevo usuario. La contraseña se cifra automáticamente con bcrypt."""
        hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO usuario (username, password_hash, nombre_completo, email)
               VALUES (%s, %s, %s, %s)""",
            (username, hash_pw, nombre_completo, email)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id
    def cambiar_password(self, id_usuario, nueva_password):
        """Cambia la contraseña de un usuario existente."""
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
        """Desactiva un usuario (no lo borra, solo lo marca como inactivo)."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET activo = FALSE WHERE id_usuario = %s",
            (id_usuario,)
        )
        conn.commit()
        cursor.close()
        conn.close()
class ActividadDAO:
    """Maneja las consultas SQL para registrar, editar, listar y eliminar actividades."""
    def obtener_todas(self, filtros=None):
        """
        Retorna todas las actividades activas.
        filtros: dict con claves opcionales {id_asic, id_tipo, fecha_desde, fecha_hasta}
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT a.id_actividad, a.id_asic, a.id_tipo, a.id_usuario_registro,
                   a.fecha_inicio, a.fecha_fin,
                   a.estado, a.municipio, a.parroquia, a.establecimiento_salud,
                   a.nombre_establecimiento, a.comites_salud, a.lugar,
                   a.descripcion,
                   a.medicos, a.promotores_salud, a.voceros_comite_salud,
                   a.vocero_consejo_direccion, a.coordinador_docencia,
                   a.autoridades_presentes, a.otros_actores,
                   a.personas_comunidad, a.estudiantes_aspirantes, a.participantes,
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
        sql += " ORDER BY a.fecha_inicio DESC, a.id_actividad DESC"
        cursor.execute(sql, tuple(params))
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista
    def obtener_por_id(self, id_actividad):
        """Retorna los detalles de una actividad específica por su ID."""
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
    def crear(self, id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin,
               estado, municipio, parroquia, establecimiento_salud, nombre_establecimiento,
               comites_salud, lugar, descripcion,
               medicos, promotores_salud, voceros_comite_salud, vocero_consejo_direccion,
               coordinador_docencia, autoridades_presentes, otros_actores,
               personas_comunidad, estudiantes_aspirantes, participantes):
        """Inserta una nueva actividad. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO actividad (id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin,
                                   estado, municipio, parroquia, establecimiento_salud,
                                   nombre_establecimiento, comites_salud, lugar, descripcion,
                                   medicos, promotores_salud, voceros_comite_salud,
                                   vocero_consejo_direccion, coordinador_docencia,
                                   autoridades_presentes, otros_actores,
                                   personas_comunidad, estudiantes_aspirantes, participantes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin,
                             estado, municipio, parroquia, establecimiento_salud, nombre_establecimiento,
                             comites_salud, lugar, descripcion,
                             medicos, promotores_salud, voceros_comite_salud, vocero_consejo_direccion,
                             coordinador_docencia, autoridades_presentes, otros_actores,
                             personas_comunidad, estudiantes_aspirantes, participantes))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id
    def actualizar(self, id_actividad, id_asic, id_tipo, fecha_inicio, fecha_fin,
                     estado, municipio, parroquia, establecimiento_salud,
                     nombre_establecimiento, comites_salud, lugar, descripcion,
                     medicos, promotores_salud, voceros_comite_salud,
                     vocero_consejo_direccion, coordinador_docencia,
                     autoridades_presentes, otros_actores,
                     personas_comunidad, estudiantes_aspirantes, participantes):
        """Actualiza los datos de una actividad existente."""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE actividad
            SET id_asic = %s, id_tipo = %s, fecha_inicio = %s, fecha_fin = %s,
                estado = %s, municipio = %s, parroquia = %s, establecimiento_salud = %s,
                nombre_establecimiento = %s, comites_salud = %s, lugar = %s, descripcion = %s,
                medicos = %s, promotores_salud = %s, voceros_comite_salud = %s,
                vocero_consejo_direccion = %s, coordinador_docencia = %s,
                autoridades_presentes = %s, otros_actores = %s,
                personas_comunidad = %s, estudiantes_aspirantes = %s, participantes = %s
            WHERE id_actividad = %s
        """
        cursor.execute(sql, (id_asic, id_tipo, fecha_inicio, fecha_fin,
                             estado, municipio, parroquia, establecimiento_salud,
                             nombre_establecimiento, comites_salud, lugar, descripcion,
                             medicos, promotores_salud, voceros_comite_salud,
                             vocero_consejo_direccion, coordinador_docencia,
                             autoridades_presentes, otros_actores,
                             personas_comunidad, estudiantes_aspirantes, participantes,
                             id_actividad))
        conn.commit()
        cursor.close()
        conn.close()
    def eliminar(self, id_actividad):
        """Borrado lógico (soft delete): marca el registro como eliminado."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE actividad SET eliminado = TRUE WHERE id_actividad = %s", (id_actividad,))
        conn.commit()
        cursor.close()
        conn.close()
    def verificar_duplicado(self, id_asic, id_tipo, fecha_inicio, descripcion, excluir_id=None):
        """
        Comprueba si ya existe una actividad con el mismo ASIC, Tipo, Fecha de inicio
        y descripción similar. Retorna True si es duplicado.
        """
        desc_normalizada = " ".join(descripcion.lower().strip().split())[:100]
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT id_actividad, descripcion
            FROM actividad
            WHERE id_asic = %s AND id_tipo = %s AND fecha_inicio = %s AND eliminado = FALSE
        """
        params = [id_asic, id_tipo, fecha_inicio]
        if excluir_id is not None:
            sql += " AND id_actividad != %s"
            params.append(excluir_id)
        cursor.execute(sql, tuple(params))
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        for registro in resultados:
            reg_desc = " ".join(registro["descripcion"].lower().strip().split())[:100]
            if reg_desc == desc_normalizada:
                return True
        return False
class AsicDAO:
    """Maneja todas las consultas relacionadas con la tabla 'asic'."""
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
        """Soft delete: marca el ASIC como inactivo."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE asic SET activo = FALSE WHERE id_asic = %s", (id_asic,))
        conn.commit()
        cursor.close()
        conn.close()
class TipoActividadDAO:
    """Maneja todas las consultas relacionadas con la tabla 'tipo_actividad'."""
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
        """Busca un tipo por su código único."""
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
class EvidenciaDAO:
    """Maneja la inserción, consulta y eliminación de evidencias en la base de datos."""
    def obtener_por_actividad(self, id_actividad):
        """Retorna la lista de todas las evidencias de una actividad."""
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
        """Retorna la información de una evidencia específica."""
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
        """Inserta una nueva referencia de evidencia. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO evidencia (id_actividad, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (id_actividad, nombre_archivo, ruta_archivo, tipo_archivo, tamano_bytes))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id
    def eliminar(self, id_evidencia):
        """
        Elimina el registro de una evidencia de la BD.
        Nota: no elimina el archivo físico del disco, eso lo hace ActividadController.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evidencia WHERE id_evidencia = %s", (id_evidencia,))
        conn.commit()
        cursor.close()
        conn.close()
class PeriodoDAO:
    """Gestión de períodos de consolidación."""
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
class InformeDAO:
    """Gestión de informes consolidados."""
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
        """Retorna las actividades incluidas en un informe para exportación/PDF."""
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
        """Elimina el informe y sus detalles."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM informe_detalle WHERE id_informe = %s", (id_informe,))
        cursor.execute("DELETE FROM informe_consolidado WHERE id_informe = %s", (id_informe,))
        conn.commit()
        cursor.close()
        conn.close()
    def obtener_resumen_por_asic(self, id_informe):
        """Retorna un resumen agrupado por ASIC para un informe dado."""
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
# ============================================================
# SECCIÓN 4 — CONTROLADORES
# Lógica de negocio y validaciones.
# (antes en controllers/)
# ============================================================
import os
import shutil
import time
import mimetypes
# Variable global que guarda los datos del usuario logueado
# Cuando es None, no hay nadie logueado
sesion_actual = None
class AuthController:
    """Maneja el login y logout del sistema."""
    def __init__(self):
        self.usuario_dao = UsuarioDAO()
    def login(self, username, password):
        """
        Intenta iniciar sesión con el username y password dados.
        Retorna:
            True  → login exitoso, sesion_actual queda guardada
            False → credenciales incorrectas o usuario inactivo
        """
        global sesion_actual
        usuario = self.usuario_dao.obtener_por_username(username)
        if usuario is None:
            return False
        password_correcta = self.usuario_dao.verificar_password(
            password,
            usuario["password_hash"]
        )
        if not password_correcta:
            return False
        # Login exitoso: guardamos la sesión
        sesion_actual = {
            "id_usuario": usuario["id_usuario"],
            "username": usuario["username"],
            "nombre_completo": usuario["nombre_completo"],
            "email": usuario["email"]
        }
        return True
    def logout(self):
        """Cierra la sesión actual."""
        global sesion_actual
        sesion_actual = None
    def obtener_usuario_actual(self):
        """Retorna los datos del usuario logueado, o None si no hay sesión."""
        return sesion_actual
    def hay_sesion_activa(self):
        """Retorna True si hay un usuario logueado."""
        return sesion_actual is not None
class ActividadController:
    """
    Controlador que maneja las actividades de salud.
    Valida las reglas de negocio antes de llamar al DAO correspondiente.
    """
    def __init__(self):
        self.actividad_dao = ActividadDAO()
        self.asic_dao = AsicDAO()
        self.tipo_dao = TipoActividadDAO()
        self.evidencia_dao = EvidenciaDAO()
        self.auth = AuthController()
    def listar_actividades(self, filtros=None):
        """Retorna la lista de actividades registradas, aplicando filtros si los hay."""
        return self.actividad_dao.obtener_todas(filtros)
    def listar_asics(self):
        """Retorna la lista de todos los ASIC activos."""
        return self.asic_dao.obtener_todos()
    def listar_tipos_actividad(self):
        """Retorna la lista de todos los tipos de actividad activos."""
        tipos_predeterminados = [
            ("TIPO-PRED-1", "Seguimiento a los Comités de Salud mediante las vocerías en salud comunal."),
            ("TIPO-PRED-2", "Actualización de los comités de salud."),
            ("TIPO-PRED-3", "Salud toca tu puerta"),
            ("TIPO-PRED-4", "Sesiones educativas"),
            ("TIPO-PRED-5", "*Los Comités de Salud van a la escuela\"."),
            ("TIPO-PRED-6", "Actividades de Promoción y Prevención Social"),
            ("TIPO-PRED-7", "Participación Activa en Jornadas."),
            ("TIPO-PRED-8", "Participación Activa en Inmunizaciones"),
            ("TIPO-PRED-9", "Entrevista servicio social.")
        ]
        try:
            existentes = self.tipo_dao.obtener_todos()
            nombres_existentes = {t["nombre"] for t in existentes}
            for codigo, nombre in tipos_predeterminados:
                if nombre not in nombres_existentes:
                    self.tipo_dao.crear(codigo, nombre, f"Tipo de actividad predeterminado: {nombre}")
        except Exception:
            pass
        return self.tipo_dao.obtener_todos()
    def guardar_actividad(self, id_asic, id_tipo, fecha_inicio, fecha_fin,
                               estado, municipio, parroquia, establecimiento_salud,
                               nombre_establecimiento, comites_salud, lugar, descripcion,
                               medicos, promotores_salud, voceros_comite_salud,
                               vocero_consejo_direccion, coordinador_docencia,
                               autoridades_presentes, otros_actores,
                               personas_comunidad, estudiantes_aspirantes, participantes,
                               id_actividad=None,
                               evidencias_temporales=None):
            """
            Registra una nueva actividad o actualiza una existente.
            Valida que los datos cumplan con las reglas de negocio.
            Retorna: (True, "mensaje exito") o (False, "mensaje error")
            """
            # 1. Validar ASIC y tipo
            if not id_asic:
                return False, "Debes seleccionar un ASIC."
            if not id_tipo:
                return False, "Debes seleccionar un tipo de actividad."
            # 2. Validar descripción (tema tratado)
            descripcion = descripcion.strip() if descripcion else ""
            if not descripcion:
                return False, "La descripcion de la actividad (Tema Tratado) es obligatoria."
            # 3. Validar lugar
            lugar = lugar.strip() if lugar else ""
            # 4. Validar participantes (total asistencia)
            try:
                cant_participantes = int(participantes)
                if cant_participantes < 0:
                    return False, "La cantidad de participantes no puede ser menor a 0."
            except (ValueError, TypeError):
                return False, "La cantidad de participantes debe ser un numero entero valido."
            # 5. Validar campos numéricos de participantes por categoría
            for campo, valor in [
                ("medicos", medicos), ("promotores_salud", promotores_salud),
                ("voceros_comite_salud", voceros_comite_salud),
                ("vocero_consejo_direccion", vocero_consejo_direccion),
                ("coordinador_docencia", coordinador_docencia),
                ("autoridades_presentes", autoridades_presentes),
                ("otros_actores", otros_actores),
                ("personas_comunidad", personas_comunidad),
                ("estudiantes_aspirantes", estudiantes_aspirantes)
            ]:
                try:
                    v = int(valor) if valor is not None else 0
                    if v < 0:
                        return False, f"El campo {campo} no puede ser menor a 0."
                except (ValueError, TypeError):
                    return False, f"El campo {campo} debe ser un numero entero valido."
            # 6. Convertir y validar fechas
            f_ini = None
            f_fin = None
            if isinstance(fecha_inicio, str):
                try:
                    if "/" in fecha_inicio:
                        f_ini = datetime.strptime(fecha_inicio, "%d/%m/%Y").date()
                    else:
                        f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                except ValueError:
                    return False, "El formato de la fecha de inicio es invalido."
            elif isinstance(fecha_inicio, (datetime, date)):
                f_ini = fecha_inicio if isinstance(fecha_inicio, date) else fecha_inicio.date()
            else:
                return False, "Fecha de inicio invalida."
            if isinstance(fecha_fin, str):
                try:
                    if "/" in fecha_fin:
                        f_fin = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    else:
                        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                except ValueError:
                    return False, "El formato de la fecha de fin es invalido."
            elif isinstance(fecha_fin, (datetime, date)):
                f_fin = fecha_fin if isinstance(fecha_fin, date) else fecha_fin.date()
            else:
                return False, "Fecha de fin invalida."
            if f_ini > f_fin:
                return False, "La fecha de inicio no puede ser posterior a la fecha de fin."
            fecha_inicio_bd = f_ini.strftime("%Y-%m-%d")
            fecha_fin_bd    = f_fin.strftime("%Y-%m-%d")
            # 7. Validar duplicidad
            es_duplicado = self.actividad_dao.verificar_duplicado(
                id_asic=id_asic,
                id_tipo=id_tipo,
                fecha_inicio=fecha_inicio_bd,
                descripcion=descripcion,
                excluir_id=id_actividad
            )
            if es_duplicado:
                return False, "Ya existe una actividad registrada para este ASIC, tipo, fecha de inicio y descripcion similar."
            # 8. Obtener usuario actual
            usuario = self.auth.obtener_usuario_actual()
            if not usuario:
                return False, "No hay una sesion de usuario activa."
            id_usuario = usuario["id_usuario"]
            # 9. Guardar en base de datos
            if id_actividad is None:
                nuevo_id = self.actividad_dao.crear(
                    id_asic=id_asic,
                    id_tipo=id_tipo,
                    id_usuario_registro=id_usuario,
                    fecha_inicio=fecha_inicio_bd,
                    fecha_fin=fecha_fin_bd,
                    estado=estado or "",
                    municipio=municipio or "",
                    parroquia=parroquia or "",
                    establecimiento_salud=establecimiento_salud or "",
                    nombre_establecimiento=nombre_establecimiento or "",
                    comites_salud=comites_salud or "",
                    lugar=lugar,
                    descripcion=descripcion,
                    medicos=int(medicos) if medicos else 0,
                    promotores_salud=int(promotores_salud) if promotores_salud else 0,
                    voceros_comite_salud=int(voceros_comite_salud) if voceros_comite_salud else 0,
                    vocero_consejo_direccion=int(vocero_consejo_direccion) if vocero_consejo_direccion else 0,
                    coordinador_docencia=int(coordinador_docencia) if coordinador_docencia else 0,
                    autoridades_presentes=int(autoridades_presentes) if autoridades_presentes else 0,
                    otros_actores=int(otros_actores) if otros_actores else 0,
                    personas_comunidad=int(personas_comunidad) if personas_comunidad else 0,
                    estudiantes_aspirantes=int(estudiantes_aspirantes) if estudiantes_aspirantes else 0,
                    participantes=cant_participantes
                )
                errores_adjuntos = []
                if evidencias_temporales:
                    for ruta in evidencias_temporales:
                        ok_ev, msg_ev = self.procesar_y_guardar_evidencia(nuevo_id, ruta)
                        if not ok_ev:
                            errores_adjuntos.append(f"{os.path.basename(ruta)} ({msg_ev})")
                if errores_adjuntos:
                    errores_str = ", ".join(errores_adjuntos)
                    return True, f"Actividad registrada, pero no se pudieron subir algunos archivos: {errores_str}"
                return True, "Actividad registrada exitosamente."
            else:
                self.actividad_dao.actualizar(
                    id_actividad=id_actividad,
                    id_asic=id_asic,
                    id_tipo=id_tipo,
                    fecha_inicio=fecha_inicio_bd,
                    fecha_fin=fecha_fin_bd,
                    estado=estado or "",
                    municipio=municipio or "",
                    parroquia=parroquia or "",
                    establecimiento_salud=establecimiento_salud or "",
                    nombre_establecimiento=nombre_establecimiento or "",
                    comites_salud=comites_salud or "",
                    lugar=lugar,
                    descripcion=descripcion,
                    medicos=int(medicos) if medicos else 0,
                    promotores_salud=int(promotores_salud) if promotores_salud else 0,
                    voceros_comite_salud=int(voceros_comite_salud) if voceros_comite_salud else 0,
                    vocero_consejo_direccion=int(vocero_consejo_direccion) if vocero_consejo_direccion else 0,
                    coordinador_docencia=int(coordinador_docencia) if coordinador_docencia else 0,
                    autoridades_presentes=int(autoridades_presentes) if autoridades_presentes else 0,
                    otros_actores=int(otros_actores) if otros_actores else 0,
                    personas_comunidad=int(personas_comunidad) if personas_comunidad else 0,
                    estudiantes_aspirantes=int(estudiantes_aspirantes) if estudiantes_aspirantes else 0,
                    participantes=cant_participantes
                )
                return True, "Actividad actualizada exitosamente."
            _ = None
    def eliminar_actividad(self, id_actividad):
        """Elimina de forma lógica una actividad."""
        self.actividad_dao.eliminar(id_actividad)
        return True, "Actividad eliminada correctamente."
    # ── Gestión de Evidencias ──────────────────────────────────────────
    def listar_evidencias_de_actividad(self, id_actividad):
        """Retorna la lista de archivos adjuntos de una actividad."""
        return self.evidencia_dao.obtener_por_actividad(id_actividad)
    def procesar_y_guardar_evidencia(self, id_actividad, ruta_origen):
        """
        Valida y copia físicamente una evidencia a la carpeta 'uploads'
        e inserta la referencia en la base de datos.
        """
        if not os.path.exists(ruta_origen):
            return False, "El archivo de origen no existe."
        _, ext = os.path.splitext(ruta_origen)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Extension no permitida ({ext}). Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        tamano_bytes = os.path.getsize(ruta_origen)
        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if tamano_bytes > max_bytes:
            return False, f"El archivo supera el tamano maximo de {MAX_FILE_SIZE_MB} MB."
        if not os.path.exists(UPLOADS_DIR):
            os.makedirs(UPLOADS_DIR)
        nombre_original = os.path.basename(ruta_origen)
        nombre_limpio = "".join(c for c in nombre_original if c.isalnum() or c in (".", "-", "_")).strip()
        timestamp = int(time.time())
        nombre_destino = f"actividad_{id_actividad}_{timestamp}_{nombre_limpio}"
        ruta_destino = os.path.join(UPLOADS_DIR, nombre_destino).replace("\\", "/")
        try:
            shutil.copy2(ruta_origen, ruta_destino)
            tipo_archivo, _ = mimetypes.guess_type(ruta_origen)
            if not tipo_archivo:
                tipo_archivo = "application/octet-stream"
            self.evidencia_dao.crear(
                id_actividad=id_actividad,
                nombre_archivo=nombre_original,
                ruta_archivo=ruta_destino,
                tipo_archivo=tipo_archivo,
                tamano_bytes=tamano_bytes
            )
            return True, "Archivo adjuntado correctamente."
        except Exception as e:
            if os.path.exists(ruta_destino):
                try:
                    os.remove(ruta_destino)
                except:
                    pass
            return False, f"Error al guardar el archivo: {str(e)}"
    def eliminar_evidencia(self, id_evidencia):
        """Elimina el registro de evidencia de la BD y borra el archivo físico."""
        evidencia = self.evidencia_dao.obtener_por_id(id_evidencia)
        if not evidencia:
            return False, "Evidencia no encontrada."
        try:
            self.evidencia_dao.eliminar(id_evidencia)
            ruta_archivo = evidencia["ruta_archivo"]
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            return True, "Evidencia eliminada correctamente."
        except Exception as e:
            return False, f"Error al eliminar la evidencia: {str(e)}"
class CatalogoController:
    """Maneja la lógica de negocio para los catálogos (ASIC y Tipos de Actividad)."""
    def __init__(self):
        self.asic_dao = AsicDAO()
        self.tipo_dao = TipoActividadDAO()
    # ── ASIC ──────────────────────────────────────────────────────────
    def listar_asic(self):
        """Retorna todos los ASIC activos."""
        return self.asic_dao.obtener_todos()
    def guardar_asic(self, codigo, nombre, municipio="", parroquia="", id_asic=None):
        """
        Crea o actualiza un ASIC.
        Retorna: (True, "mensaje ok") o (False, "mensaje error")
        """
        codigo = codigo.strip().upper()
        nombre = nombre.strip()
        if not codigo:
            return False, "El codigo del ASIC es obligatorio."
        if not nombre:
            return False, "El nombre del ASIC es obligatorio."
        existente = self.asic_dao.obtener_por_codigo(codigo)
        if existente and existente["id_asic"] != id_asic:
            return False, f"Ya existe un ASIC con el codigo '{codigo}'."
        if id_asic is None:
            self.asic_dao.crear(codigo, nombre, municipio.strip(), parroquia.strip())
            return True, f"ASIC '{nombre}' creado correctamente."
        else:
            self.asic_dao.actualizar(id_asic, codigo, nombre, municipio.strip(), parroquia.strip())
            return True, f"ASIC '{nombre}' actualizado correctamente."
    def eliminar_asic(self, id_asic):
        """Desactiva un ASIC. Retorna (True, mensaje) o (False, error)."""
        asic = self.asic_dao.obtener_por_id(id_asic)
        if not asic:
            return False, "No se encontro el ASIC."
        self.asic_dao.desactivar(id_asic)
        return True, f"ASIC '{asic['nombre']}' eliminado correctamente."
    # ── Tipos de Actividad ────────────────────────────────────────────
    def listar_tipos(self):
        """Retorna todos los tipos de actividad activos."""
        return self.tipo_dao.obtener_todos()
    def guardar_tipo(self, codigo, nombre, descripcion="", id_tipo=None):
        """
        Crea o actualiza un tipo de actividad.
        Retorna: (True, "mensaje ok") o (False, "mensaje error")
        """
        codigo = codigo.strip().upper()
        nombre = nombre.strip()
        if not codigo:
            return False, "El codigo del tipo es obligatorio."
        if not nombre:
            return False, "El nombre del tipo es obligatorio."
        existente = self.tipo_dao.obtener_por_codigo(codigo)
        if existente and existente["id_tipo"] != id_tipo:
            return False, f"Ya existe un tipo con el codigo '{codigo}'."
        if id_tipo is None:
            self.tipo_dao.crear(codigo, nombre, descripcion.strip())
            return True, f"Tipo '{nombre}' creado correctamente."
        else:
            self.tipo_dao.actualizar(id_tipo, codigo, nombre, descripcion.strip())
            return True, f"Tipo '{nombre}' actualizado correctamente."
    def eliminar_tipo(self, id_tipo):
        """Desactiva un tipo de actividad. Retorna (True, mensaje) o (False, error)."""
        tipo = self.tipo_dao.obtener_por_id(id_tipo)
        if not tipo:
            return False, "No se encontro el tipo de actividad."
        self.tipo_dao.desactivar(id_tipo)
        return True, f"Tipo '{tipo['nombre']}' eliminado correctamente."
# ============================================================
# SECCIÓN 5 — SERVICIOS
# Lógica de negocio compleja: Excel, PDF, Consolidación.
# (antes en services/)
# ============================================================
import openpyxl
import re
import unicodedata
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)
# Paleta de colores para PDF
_AZUL_OSCURO = colors.HexColor("#0f3460")
_AZUL_MEDIO  = colors.HexColor("#16213e")
_ROJO_ACENTO = colors.HexColor("#e94560")
_VERDE       = colors.HexColor("#05c46b")
_GRIS_CLARO  = colors.HexColor("#f4f6f8")
_GRIS_BORDE  = colors.HexColor("#cccccc")
_BLANCO      = colors.white
_NEGRO       = colors.black
class ConsolidacionService:
    """
    Genera y persiste informes consolidados de actividades
    para un período y (opcionalmente) un ASIC concreto.
    """
    def __init__(self, id_usuario: int):
        """id_usuario: ID del usuario que genera el informe."""
        self.id_usuario = id_usuario
        self._actividad_dao = ActividadDAO()
        self._asic_dao = AsicDAO()
        self._informe_dao = InformeDAO()
        self._periodo_dao = PeriodoDAO()
    def generar_previo(self, fecha_inicio, fecha_fin, id_asic=None) -> dict:
        """
        Calcula el resumen SIN guardar en BD.
        Retorna un dict listo para mostrar en la UI y luego pasarlo a guardar().
        """
        actividades = self._obtener_actividades(fecha_inicio, fecha_fin, id_asic)
        total_act  = len(actividades)
        total_part = sum(a["participantes"] for a in actividades)
        resumen_tipo = self._agrupar(actividades, "tipo_nombre")
        resumen_asic = self._agrupar(actividades, "asic_nombre")
        asic_nombre = None
        if id_asic:
            asic = self._asic_dao.obtener_por_id(id_asic)
            asic_nombre = asic["nombre"] if asic else str(id_asic)
        return {
            "actividades":         actividades,
            "resumen_por_tipo":    resumen_tipo,
            "resumen_por_asic":    resumen_asic,
            "total_actividades":   total_act,
            "total_participantes": total_part,
            "fecha_inicio":        fecha_inicio,
            "fecha_fin":           fecha_fin,
            "id_asic":             id_asic,
            "asic_nombre":         asic_nombre,
        }
    def guardar(self, previo: dict, id_periodo: int, titulo: str, observaciones: str = "") -> int:
        """
        Persiste el informe en BD a partir de los datos del previo.
        Retorna el id_informe generado.
        """
        actividades    = previo["actividades"]
        id_asic        = previo["id_asic"]
        total_act      = previo["total_actividades"]
        total_part     = previo["total_participantes"]
        id_informe = self._informe_dao.crear(
            id_periodo=id_periodo,
            id_asic=id_asic,
            titulo=titulo,
            total_actividades=total_act,
            total_participantes=total_part,
            observaciones=observaciones,
            id_usuario_generador=self.id_usuario,
        )
        ids_actividades = [a["id_actividad"] for a in actividades]
        self._informe_dao.insertar_detalle(id_informe, ids_actividades)
        return id_informe
    def listar_informes(self) -> list:
        """Retorna todos los informes generados (para el historial)."""
        return self._informe_dao.obtener_todos()
    def obtener_informe_completo(self, id_informe: int) -> dict:
        """Retorna la cabecera + detalle + resúmenes de un informe guardado."""
        cabecera     = self._informe_dao.obtener_por_id(id_informe)
        detalle      = self._informe_dao.obtener_detalle(id_informe)
        resumen_asic = self._informe_dao.obtener_resumen_por_asic(id_informe)
        resumen_tipo = self._agrupar(detalle, "tipo_nombre")
        return {
            "cabecera":           cabecera,
            "actividades":        detalle,
            "resumen_por_asic":   resumen_asic,
            "resumen_por_tipo":   resumen_tipo,
            "total_actividades":  cabecera["total_actividades"],
            "total_participantes":cabecera["total_participantes"],
        }
    def listar_periodos(self) -> list:
        """Retorna todos los períodos registrados."""
        return self._periodo_dao.obtener_todos()
    def crear_periodo(self, tipo: str, anio: int, mes_inicio: int,
                      mes_fin: int, fecha_inicio, fecha_fin) -> int:
        """Crea un nuevo período de consolidación."""
        return self._periodo_dao.crear(tipo, anio, mes_inicio, mes_fin,
                                       fecha_inicio, fecha_fin)
    def eliminar_informe(self, id_informe: int):
        """Elimina un informe y su detalle de la BD."""
        self._informe_dao.eliminar(id_informe)
    def _obtener_actividades(self, fecha_inicio, fecha_fin, id_asic) -> list:
        """Usa ActividadDAO con filtros de fecha y ASIC."""
        filtros = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        if id_asic:
            filtros["id_asic"] = id_asic
        return self._actividad_dao.obtener_todas(filtros)
    @staticmethod
    def _agrupar(actividades: list, campo_grupo: str) -> list:
        """Agrupa actividades por un campo y calcula totales."""
        grupos: dict = {}
        for act in actividades:
            clave = act.get(campo_grupo) or "Sin clasificar"
            if clave not in grupos:
                grupos[clave] = {"nombre": clave, "total_actividades": 0, "total_participantes": 0}
            grupos[clave]["total_actividades"]  += 1
            grupos[clave]["total_participantes"] += act.get("participantes", 0)
        return sorted(grupos.values(), key=lambda x: x["nombre"])
# Columnas requeridas en el Excel de importación
# NOTA: Usamos detección flexible — "lugar" puede venir como columna única
# O componerse desde LOCATION_FIELDS; "participantes" puede venir como columna
# única, como "total_asistencia", o sumarse desde PARTICIPANTES_CATEGORIAS.
COLUMNAS_REQUERIDAS = [
    "asic", "tipo_actividad", "fecha_inicio", "descripcion",
    "lugar", "participantes",
]
HEADER_ALIASES = {
    # Fecha
    "fecha": "fecha_inicio",
    "fecha inicio": "fecha_inicio",
    "fecha inicio yyyy mm dd": "fecha_inicio",
    "fecha fin": "fecha_fin",
    # Ubicación
    "estado": "estado",
    "municipio": "municipio",
    "parroquia": "parroquia",
    "asic": "asic",
    "establecimiento de salud": "establecimiento_salud",
    "establecimiento de salud cdi sri hospital cat clinica popular": "establecimiento_salud",
    "nombre del establecimiento de salud": "nombre_establecimiento_salud",
    "comites de salud": "comites_de_salud",
    "comités de salud": "comites_de_salud",
    "ubicación": "ubicacion",
    "ubicacion": "ubicacion",
    # Tipo de actividad
    "actividad desarrollada": "tipo_actividad",
    "actividad": "tipo_actividad",
    "tipo de actividad": "tipo_actividad",
    "tipo actividad": "tipo_actividad",
    "tipo de actividad nombre exacto": "tipo_actividad",
    "asic nombre exacto": "asic",
    # Descripción / tema
    "tema tratado": "descripcion",
    "descripcion": "descripcion",
    "descripcion numero": "descripcion",
    # Participantes y totales
    "participantes": "participantes",
    "participantes numero": "participantes",
    "medicos": "medicos",
    "promotores en salud": "promotores_en_salud",
    "voceros de comité de salud": "voceros_de_comite_de_salud",
    "voceros de comite de salud": "voceros_de_comite_de_salud",
    "vocero del consejo de direccion del asic": "vocero_del_consejo_de_direccion_del_asic",
    "coordinador de docencia e investigacion del asic": "coordinador_de_docencia_e_investigacion_del_asic",
    "autoridades presentes": "autoridades_presentes",
    "otros actores involucrados": "otros_actores_involucrados",
    "cantidad de personas de la comunidad": "cantidad_personas_comunidad",
    "cantidad de personas de la comunidad estudiantes ninos y adultos": "cantidad_personas_comunidad",
    "estudiantes aspirantes para la salud involucrados en la actividad": "estudiantes_aspirantes",
    "total de asistencia": "total_asistencia",
}
PARTICIPANTES_CATEGORIAS = [
    "medicos", "promotores_en_salud", "voceros_de_comite_de_salud",
    "vocero_del_consejo_de_direccion_del_asic", "coordinador_de_docencia_e_investigacion_del_asic",
    "autoridades_presentes", "otros_actores_involucrados", "cantidad_personas_comunidad",
    "estudiantes_aspirantes",
]
LOCATION_FIELDS = [
    "estado", "municipio", "parroquia", "establecimiento_salud",
    "nombre_establecimiento_salud", "comites_de_salud",
]
class ExcelService:
    """
    Servicio encargado de leer un archivo Excel y convertir sus filas
    en registros de actividad, con validación detallada por fila.
    """
    def __init__(self, id_usuario_registro: int):
        """id_usuario_registro: ID del usuario que realiza la importación."""
        self.id_usuario_registro = id_usuario_registro
        self._actividad_dao = ActividadDAO()
        self._asic_dao = AsicDAO()
        self._tipo_dao = TipoActividadDAO()
        self._cache_asic: dict = {}
        self._cache_tipo: dict = {}
    def previsualizar(self, ruta_archivo: str) -> dict:
        """
        Lee el Excel y valida cada fila SIN insertar en BD.
        Retorna: {columnas, filas_validas, filas_error, total_filas}
        """
        wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
        ws = wb.active
        # Detecta si es la plantilla nueva (fila 3 con encabezados) o vieja (fila 1 con encabezados).
        raw_header_row = next(ws.iter_rows(min_row=3, max_row=3, values_only=True))
        cabecera_raw = [str(c).strip() if c is not None else "" for c in raw_header_row]
        cabecera_normalizada = [self._normalizar_encabezado(c) for c in cabecera_raw]
        idx = {cab: i for i, cab in enumerate(cabecera_normalizada) if cab}
        data_start = 4
        # Si faltan columnas en fila 3 (ej. "FECHA" está en celda fusionada A2:A3),
        # complementa con encabezados de la fila 2 (solo para columnas vacías en fila 3).
        raw_row2 = next(ws.iter_rows(min_row=2, max_row=2, values_only=True))
        for i, val in enumerate(raw_row2):
            if i < len(cabecera_raw) and not cabecera_raw[i] and val is not None:
                normalizado = self._normalizar_encabezado(str(val))
                if normalizado:
                    idx[normalizado] = i
                    cabecera_raw[i] = str(val).strip()
        if not any(col in idx for col in COLUMNAS_REQUERIDAS):
            raw_header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            cabecera_raw = [str(c).strip() if c is not None else "" for c in raw_header_row]
            cabecera_normalizada = [self._normalizar_encabezado(c) for c in cabecera_raw]
            idx = {cab: i for i, cab in enumerate(cabecera_normalizada) if cab}
            data_start = 2
        # Chequea que existan las columnas mínimas necesarias para la importación.
        # "lugar" puede ser una columna única o componerse desde LOCATION_FIELDS.
        # "participantes" puede ser columna única, "total_asistencia" o varias categorías.
        faltantes = []
        for col in COLUMNAS_REQUERIDAS:
            if col in idx:
                continue
            if col == "lugar" and any(cf in idx for cf in LOCATION_FIELDS):
                continue
            if col == "participantes" and ("total_asistencia" in idx or any(cf in idx for cf in PARTICIPANTES_CATEGORIAS)):
                continue
            faltantes.append(col)
        if faltantes:
            raise ValueError(
                f"El archivo no tiene las columnas requeridas: {', '.join(faltantes)}.\n"
                f"Columnas detectadas: {', '.join(cabecera_raw)}"
            )
        filas_validas = []
        filas_error   = []
        for numero_fila, fila in enumerate(ws.iter_rows(min_row=4, values_only=True), start=4):
            if all(v is None or str(v).strip() == "" for v in fila):
                continue
            datos_crudos = {col: fila[idx[col]] if col in idx and idx[col] < len(fila) else None for col in COLUMNAS_REQUERIDAS}
            errores = []
            asic_nombre  = str(datos_crudos["asic"]).strip()          if datos_crudos["asic"]          else ""
            tipo_nombre  = str(datos_crudos["tipo_actividad"]).strip() if datos_crudos["tipo_actividad"] else ""
            lugar        = self._combinar_ubicacion(fila, idx) or (str(datos_crudos.get("lugar")).strip() if datos_crudos.get("lugar") else "")
            descripcion  = str(datos_crudos["descripcion"]).strip()    if datos_crudos["descripcion"]    else ""
            try:
                participantes = self._calcular_total_asistencia(fila, idx, datos_crudos)
                if participantes is None or participantes < 0:
                    raise ValueError()
            except (TypeError, ValueError):
                participantes = None
                errores.append("'TOTAL DE ASISTENCIA' no es un número entero válido.")
            fecha_inicio = self._parsear_fecha(datos_crudos["fecha_inicio"])
            if fecha_inicio is None:
                errores.append("'FECHA' no tiene formato de fecha válido (YYYY-MM-DD o DD/MM/YYYY).")
            if not asic_nombre:
                errores.append("El campo 'ASIC' está vacío.")
            if not tipo_nombre:
                errores.append("El campo 'ACTIVIDAD DESARROLLADA' está vacío.")
            if not lugar:
                errores.append("Los campos de ubicación no están completos.")
            if not descripcion:
                errores.append("El campo 'TEMA TRATADO' está vacío.")
            id_asic = None
            id_tipo = None
            if asic_nombre:
                id_asic = self._resolver_asic(asic_nombre)
                if id_asic is None:
                    errores.append(f"ASIC no encontrado en BD: «{asic_nombre}».")
            if tipo_nombre:
                id_tipo = self._resolver_tipo(tipo_nombre)
                if id_tipo is None:
                    errores.append(f"Tipo de actividad no encontrado en BD: «{tipo_nombre}».")
            if id_asic and id_tipo and fecha_inicio and descripcion and not errores:
                es_duplicado = self._actividad_dao.verificar_duplicado(
                    id_asic, id_tipo, fecha_inicio, descripcion
                )
                if es_duplicado:
                    errores.append("Duplicado: ya existe una actividad con el mismo ASIC, tipo, fecha e inicio de descripción.")
            fila_procesada = {
                "numero_fila": numero_fila,
                "id_asic": id_asic,
                "id_tipo": id_tipo,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_inicio,
                "estado": self._obtener_valor_columna(fila, idx, "estado"),
                "municipio": self._obtener_valor_columna(fila, idx, "municipio"),
                "parroquia": self._obtener_valor_columna(fila, idx, "parroquia"),
                "establecimiento_salud": self._obtener_valor_columna(fila, idx, "establecimiento_salud"),
                "nombre_establecimiento": self._obtener_valor_columna(fila, idx, "nombre_establecimiento_salud"),
                "comites_salud": self._obtener_valor_columna(fila, idx, "comites_de_salud"),
                "lugar": lugar,
                "descripcion": descripcion,
                "medicos": self._parse_int(self._obtener_valor_columna(fila, idx, "medicos")),
                "promotores_salud": self._parse_int(self._obtener_valor_columna(fila, idx, "promotores_en_salud")),
                "voceros_comite_salud": self._parse_int(self._obtener_valor_columna(fila, idx, "voceros_de_comite_de_salud")),
                "vocero_consejo_direccion": self._parse_int(self._obtener_valor_columna(fila, idx, "vocero_del_consejo_de_direccion_del_asic")),
                "coordinador_docencia": self._parse_int(self._obtener_valor_columna(fila, idx, "coordinador_de_docencia_e_investigacion_del_asic")),
                "autoridades_presentes": self._parse_int(self._obtener_valor_columna(fila, idx, "autoridades_presentes")),
                "otros_actores": self._parse_int(self._obtener_valor_columna(fila, idx, "otros_actores_involucrados")),
                "personas_comunidad": self._parse_int(self._obtener_valor_columna(fila, idx, "cantidad_personas_comunidad")),
                "estudiantes_aspirantes": self._parse_int(self._obtener_valor_columna(fila, idx, "estudiantes_aspirantes")),
                "participantes": participantes,
                "datos_crudos": datos_crudos,
            }
            if errores:
                filas_error.append({**fila_procesada, "errores": errores})
            else:
                filas_validas.append(fila_procesada)
        return {
            "columnas": cabecera_raw,
            "filas_validas": filas_validas,
            "filas_error": filas_error,
            "total_filas": len(filas_validas) + len(filas_error),
        }
    def importar(self, filas_validas: list) -> dict:
        """
        Inserta en BD todas las filas ya validadas.
        Retorna: {insertadas, errores_al_insertar}
        """
        insertadas = 0
        errores_al_insertar = []
        for fila in filas_validas:
            try:
                self._actividad_dao.crear(
                    id_asic=fila["id_asic"],
                    id_tipo=fila["id_tipo"],
                    id_usuario_registro=self.id_usuario_registro,
                    fecha_inicio=fila["fecha_inicio"],
                    fecha_fin=fila["fecha_fin"],
                    estado=fila.get("estado") or "",
                    municipio=fila.get("municipio") or "",
                    parroquia=fila.get("parroquia") or "",
                    establecimiento_salud=fila.get("establecimiento_salud") or "",
                    nombre_establecimiento=fila.get("nombre_establecimiento") or "",
                    comites_salud=fila.get("comites_salud") or "",
                    lugar=fila["lugar"],
                    descripcion=fila["descripcion"],
                    medicos=fila.get("medicos") or 0,
                    promotores_salud=fila.get("promotores_salud") or 0,
                    voceros_comite_salud=fila.get("voceros_comite_salud") or 0,
                    vocero_consejo_direccion=fila.get("vocero_consejo_direccion") or 0,
                    coordinador_docencia=fila.get("coordinador_docencia") or 0,
                    autoridades_presentes=fila.get("autoridades_presentes") or 0,
                    otros_actores=fila.get("otros_actores") or 0,
                    personas_comunidad=fila.get("personas_comunidad") or 0,
                    estudiantes_aspirantes=fila.get("estudiantes_aspirantes") or 0,
                    participantes=fila["participantes"],
                )
                insertadas += 1
            except Exception as exc:
                errores_al_insertar.append({
                    "numero_fila": fila["numero_fila"],
                    "error": str(exc),
                })
        return {"insertadas": insertadas, "errores_al_insertar": errores_al_insertar}
    def _normalizar_encabezado(self, texto):
        if texto is None:
            return ""
        valor = str(texto).strip().lower()
        valor = unicodedata.normalize("NFKD", valor)
        valor = "".join(ch for ch in valor if not unicodedata.combining(ch))
        valor = re.sub(r"[^a-z0-9]+", " ", valor)
        valor = " ".join(valor.split())
        return HEADER_ALIASES.get(valor, valor)
    def _obtener_valor_columna(self, fila, idx, campo):
        if campo not in idx or idx[campo] >= len(fila):
            return None
        return fila[idx[campo]]
    def _combinar_ubicacion(self, fila, idx):
        valores = []
        for campo in LOCATION_FIELDS:
            valor = self._obtener_valor_columna(fila, idx, campo)
            if valor is not None and str(valor).strip() != "":
                valores.append(str(valor).strip())
        return " / ".join(valores).strip()
    def _parse_int(self, valor):
        if valor is None:
            return None
        if isinstance(valor, bool):
            return None
        if isinstance(valor, (int, float)) and float(valor).is_integer():
            return int(valor)
        try:
            texto = str(valor).strip()
            if texto == "":
                return None
            return int(texto)
        except (TypeError, ValueError):
            return None
    def _calcular_total_asistencia(self, fila, idx, datos_crudos):
        total = self._obtener_valor_columna(fila, idx, "total_asistencia")
        total_num = self._parse_int(total)
        if total_num is not None:
            return total_num
        suma = 0
        encontrado = False
        for campo in PARTICIPANTES_CATEGORIAS:
            valor = self._obtener_valor_columna(fila, idx, campo)
            if valor is None or str(valor).strip() == "":
                continue
            encontrado = True
            valor_num = self._parse_int(valor)
            if valor_num is None:
                return None
            suma += valor_num
        if encontrado:
            return suma
        return self._parse_int(datos_crudos.get("participantes"))
    def _parsear_fecha(self, valor):
        """Acepta objetos date/datetime o strings YYYY-MM-DD / DD/MM/YYYY."""
        if valor is None:
            return None
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        texto = str(valor).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(texto, fmt).date()
            except ValueError:
                pass
        return None
    def _resolver_asic(self, nombre: str):
        """Busca el id_asic por nombre (case-insensitive). Usa caché."""
        key = nombre.lower().strip()
        if key in self._cache_asic:
            return self._cache_asic[key]
        for asic in self._asic_dao.obtener_todos():
            if asic["nombre"].lower().strip() == key:
                self._cache_asic[key] = asic["id_asic"]
                return asic["id_asic"]
        self._cache_asic[key] = None
        return None
    def _resolver_tipo(self, nombre: str):
        """Busca el id_tipo por nombre (case-insensitive). Usa caché."""
        key = nombre.lower().strip()
        if key in self._cache_tipo:
            return self._cache_tipo[key]
        for tipo in self._tipo_dao.obtener_todos():
            if tipo["nombre"].lower().strip() == key:
                self._cache_tipo[key] = tipo["id_tipo"]
                return tipo["id_tipo"]
        self._cache_tipo[key] = None
        return None
class PDFService:
    """Genera el PDF y Excel del informe consolidado usando ReportLab y openpyxl."""
    def generar_pdf(self, datos: dict, ruta_salida: str) -> str:
        """
        Genera el PDF del informe y lo guarda en ruta_salida.
        datos: dict de ConsolidacionService.obtener_informe_completo() o generar_previo().
        Retorna ruta_salida.
        """
        os.makedirs(os.path.dirname(ruta_salida) if os.path.dirname(ruta_salida) else ".", exist_ok=True)
        doc = SimpleDocTemplate(
            ruta_salida,
            pagesize=landscape(A4),
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm,  bottomMargin=2*cm,
            title=datos.get("titulo", "Informe Consolidado"),
        )
        estilos  = self._estilos()
        historia = []
        historia += self._encabezado(datos, estilos)
        historia.append(Spacer(1, 0.4*cm))
        historia.append(HRFlowable(width="100%", thickness=2, color=_AZUL_OSCURO))
        historia.append(Spacer(1, 0.3*cm))
        historia += self._tarjetas_resumen(datos, estilos)
        historia.append(Spacer(1, 0.5*cm))
        if datos.get("resumen_por_asic"):
            historia += self._tabla_resumen_generica("Resumen por ASIC", datos["resumen_por_asic"], estilos, _AZUL_OSCURO)
            historia.append(Spacer(1, 0.5*cm))
        if datos.get("resumen_por_tipo"):
            historia += self._tabla_resumen_generica("Resumen por Tipo de Actividad", datos["resumen_por_tipo"], estilos, _AZUL_MEDIO)
            historia.append(Spacer(1, 0.5*cm))
        if datos.get("actividades"):
            historia.append(PageBreak())
            historia += self._tabla_detalle(datos["actividades"], estilos)
        obs = datos.get("observaciones", "")
        if obs and obs.strip():
            historia.append(Spacer(1, 0.5*cm))
            historia.append(Paragraph("Observaciones", estilos["subtitulo"]))
            historia.append(Paragraph(obs, estilos["normal"]))
        historia.append(Spacer(1, 0.5*cm))
        historia.append(HRFlowable(width="100%", thickness=1, color=_GRIS_BORDE))
        historia.append(Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} — "
            f"{APP_TITLE} v{APP_VERSION}",
            estilos["pie"],
        ))
        doc.build(historia)
        return ruta_salida
    def generar_excel(self, datos: dict, ruta_salida: str) -> str:
        """
        Genera un Excel con dos hojas: Resumen y Detalle de actividades.
        Retorna ruta_salida.
        """
        os.makedirs(os.path.dirname(ruta_salida) if os.path.dirname(ruta_salida) else ".", exist_ok=True)
        wb = openpyxl.Workbook()
        ws_res = wb.active
        ws_res.title = "Resumen"
        self._excel_hoja_resumen(ws_res, datos)
        ws_det = wb.create_sheet("Detalle de Actividades")
        self._excel_hoja_detalle(ws_det, datos)
        wb.save(ruta_salida)
        return ruta_salida
    # ── Bloques PDF ────────────────────────────────────────────────────
    def _encabezado(self, datos: dict, estilos: dict) -> list:
        titulo      = datos.get("titulo", "Informe Consolidado de Actividades")
        subtitulo   = self._subtitulo_periodo(datos)
        asic_nombre = datos.get("asic_nombre") or datos.get("cabecera", {}).get("asic_nombre", "")
        alcance     = f"ASIC: {asic_nombre}" if asic_nombre else "Todos los ASIC"
        return [
            Paragraph("CORPORACIÓN DE SALUD DEL ESTADO TÁCHIRA", estilos["institucion"]),
            Paragraph("Dirección de Programas y Proyectos de Promoción de Salud (DPPPS)", estilos["dependencia"]),
            Spacer(1, 0.2*cm),
            Paragraph(titulo, estilos["titulo"]),
            Paragraph(f"{subtitulo}  |  {alcance}", estilos["subtitulo_gris"]),
        ]
    def _tarjetas_resumen(self, datos: dict, estilos: dict) -> list:
        total_act  = datos.get("total_actividades",  0)
        total_part = datos.get("total_participantes", 0)
        tabla_data = [
            [Paragraph("TOTAL ACTIVIDADES", estilos["chip_label"]),
             Paragraph("TOTAL PARTICIPANTES", estilos["chip_label"])],
            [Paragraph(str(total_act),  estilos["chip_valor"]),
             Paragraph(str(total_part), estilos["chip_valor"])],
        ]
        tabla = Table(tabla_data, colWidths=["50%", "50%"])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), _AZUL_OSCURO),
            ("BACKGROUND", (1, 0), (1, -1), _ROJO_ACENTO),
            ("TEXTCOLOR",  (0, 0), (-1, -1), _BLANCO),
            ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        return [tabla]
    def _tabla_resumen_generica(self, titulo: str, resumen: list, estilos: dict, color_cabecera) -> list:
        elems = [Paragraph(titulo, estilos["subtitulo"])]
        cab = [Paragraph("Nombre", estilos["th"]),
               Paragraph("Actividades", estilos["th"]),
               Paragraph("Participantes", estilos["th"])]
        filas = [cab]
        for fila in resumen:
            nombre = fila.get("nombre") or fila.get("asic_nombre", "")
            filas.append([
                Paragraph(nombre, estilos["td"]),
                Paragraph(str(fila["total_actividades"]),  estilos["td_centro"]),
                Paragraph(str(fila["total_participantes"]), estilos["td_centro"]),
            ])
        tabla = Table(filas, colWidths=["60%", "20%", "20%"])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), color_cabecera),
            ("TEXTCOLOR",  (0, 0), (-1, 0), _BLANCO),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_BLANCO, _GRIS_CLARO]),
            ("GRID",       (0, 0), (-1, -1), 0.5, _GRIS_BORDE),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ]))
        elems.append(tabla)
        return elems
    def _tabla_detalle(self, actividades: list, estilos: dict) -> list:
        elems = [Paragraph("Detalle de Actividades", estilos["subtitulo"])]
        cab = [Paragraph(h, estilos["th"]) for h in
               ["#", "ASIC", "Tipo", "Fecha Inicio", "Fecha Fin", "Lugar", "Participantes", "Descripción"]]
        filas = [cab]
        for i, act in enumerate(actividades, start=1):
            filas.append([
                Paragraph(str(i),                          estilos["td_centro"]),
                Paragraph(act.get("asic_nombre", ""),      estilos["td_pequeño"]),
                Paragraph(act.get("tipo_nombre", ""),      estilos["td_pequeño"]),
                Paragraph(str(act.get("fecha_inicio", "")), estilos["td_centro"]),
                Paragraph(str(act.get("fecha_fin",   "")), estilos["td_centro"]),
                Paragraph(act.get("lugar", ""),            estilos["td_pequeño"]),
                Paragraph(str(act.get("participantes", 0)), estilos["td_centro"]),
                Paragraph(act.get("descripcion", "")[:120], estilos["td_pequeño"]),
            ])
        tabla = Table(filas, colWidths=["4%","13%","12%","9%","9%","13%","8%","32%"], repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _AZUL_OSCURO),
            ("TEXTCOLOR",  (0, 0), (-1, 0), _BLANCO),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 8),
            ("FONTSIZE",   (0, 1), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_BLANCO, _GRIS_CLARO]),
            ("GRID",       (0, 0), (-1, -1), 0.4, _GRIS_BORDE),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ]))
        elems.append(tabla)
        return elems
    # ── Hojas Excel ────────────────────────────────────────────────────
    def _excel_hoja_resumen(self, ws, datos: dict):
        """Hoja 1: encabezado + totales + resúmenes por ASIC y tipo."""
        h_fill = PatternFill("solid", fgColor="FF0F3460")
        h_font = Font(color="FFFFFFFF", bold=True, size=11)
        r_fill = PatternFill("solid", fgColor="FFF4F6F8")
        border = Border(
            left=Side(style="thin", color="FFCCCCCC"),
            right=Side(style="thin", color="FFCCCCCC"),
            top=Side(style="thin", color="FFCCCCCC"),
            bottom=Side(style="thin", color="FFCCCCCC"),
        )
        titulo = datos.get("titulo", "Informe Consolidado")
        ws.merge_cells("A1:F1")
        ws["A1"] = titulo
        ws["A1"].font = Font(bold=True, size=14, color="FF0F3460")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 30
        subtitulo = self._subtitulo_periodo(datos)
        ws.merge_cells("A2:F2")
        ws["A2"] = subtitulo
        ws["A2"].font = Font(size=10, color="FF888888", italic=True)
        ws["A2"].alignment = Alignment(horizontal="center")
        ws["A4"] = "Total Actividades"
        ws["B4"] = datos.get("total_actividades", 0)
        ws["D4"] = "Total Participantes"
        ws["E4"] = datos.get("total_participantes", 0)
        for cell in ["A4", "D4"]:
            ws[cell].font = Font(bold=True, color="FF0F3460")
        for cell in ["B4", "E4"]:
            ws[cell].font = Font(bold=True, size=14)
        fila = 6
        ws.cell(fila, 1, "RESUMEN POR ASIC").font = Font(bold=True, size=11, color="FF0F3460")
        fila += 1
        for col, cab in enumerate(["ASIC", "Actividades", "Participantes"], 1):
            c = ws.cell(fila, col, cab)
            c.fill = h_fill; c.font = h_font
            c.alignment = Alignment(horizontal="center")
            c.border = border
        fila += 1
        for i, row in enumerate(datos.get("resumen_por_asic", [])):
            nombre = row.get("nombre") or row.get("asic_nombre", "")
            for col, val in enumerate([nombre, row["total_actividades"], row["total_participantes"]], 1):
                c = ws.cell(fila, col, val)
                c.border = border
                if i % 2 == 0:
                    c.fill = r_fill
            fila += 1
        fila += 1
        ws.cell(fila, 1, "RESUMEN POR TIPO DE ACTIVIDAD").font = Font(bold=True, size=11, color="FF0F3460")
        fila += 1
        for col, cab in enumerate(["Tipo de Actividad", "Actividades", "Participantes"], 1):
            c = ws.cell(fila, col, cab)
            c.fill = h_fill; c.font = h_font
            c.alignment = Alignment(horizontal="center")
            c.border = border
        fila += 1
        for i, row in enumerate(datos.get("resumen_por_tipo", [])):
            for col, val in enumerate([row["nombre"], row["total_actividades"], row["total_participantes"]], 1):
                c = ws.cell(fila, col, val)
                c.border = border
                if i % 2 == 0:
                    c.fill = r_fill
            fila += 1
        for col, w in zip(["A", "B", "C", "D", "E", "F"], [45, 15, 15, 30, 15, 15]):
            ws.column_dimensions[col].width = w
    def _excel_hoja_detalle(self, ws, datos: dict):
        """Hoja 2: todas las actividades una por fila."""
        h_fill = PatternFill("solid", fgColor="FF0F3460")
        h_font = Font(color="FFFFFFFF", bold=True, size=10)
        r_fill = PatternFill("solid", fgColor="FFF4F6F8")
        border = Border(
            left=Side(style="thin", color="FFCCCCCC"),
            right=Side(style="thin", color="FFCCCCCC"),
            top=Side(style="thin", color="FFCCCCCC"),
            bottom=Side(style="thin", color="FFCCCCCC"),
        )
        cabeceras = ["#", "ASIC", "Tipo", "Fecha Inicio", "Fecha Fin",
                     "Lugar", "Participantes", "Descripción"]
        for col, cab in enumerate(cabeceras, 1):
            c = ws.cell(1, col, cab)
            c.fill = h_fill; c.font = h_font
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = border
        ws.row_dimensions[1].height = 22
        for i, act in enumerate(datos.get("actividades", []), start=1):
            fila_idx = i + 1
            valores = [
                i,
                act.get("asic_nombre", ""),
                act.get("tipo_nombre", ""),
                str(act.get("fecha_inicio", "")),
                str(act.get("fecha_fin", "")),
                act.get("lugar", ""),
                act.get("participantes", 0),
                act.get("descripcion", ""),
            ]
            for col, val in enumerate(valores, 1):
                c = ws.cell(fila_idx, col, val)
                c.border = border
                c.alignment = Alignment(vertical="top", wrap_text=(col == 8))
                if i % 2 == 0:
                    c.fill = r_fill
        anchos = [5, 25, 22, 13, 13, 25, 13, 60]
        for col_idx, w in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = w
    # ── Helpers ────────────────────────────────────────────────────────
    def _subtitulo_periodo(self, datos: dict) -> str:
        """Construye el texto del período a partir del dict de datos."""
        cabecera = datos.get("cabecera", {})
        tipo = cabecera.get("periodo_tipo") or datos.get("tipo_periodo", "")
        anio = cabecera.get("periodo_anio") or datos.get("anio_periodo", "")
        f_ini = cabecera.get("periodo_fecha_inicio") or datos.get("fecha_inicio", "")
        f_fin = cabecera.get("periodo_fecha_fin")    or datos.get("fecha_fin", "")
        if tipo and anio:
            return f"Período {tipo.capitalize()} {anio}"
        if f_ini and f_fin:
            return f"Del {f_ini} al {f_fin}"
        return ""
    @staticmethod
    def _estilos() -> dict:
        base = getSampleStyleSheet()
        return {
            "institucion":    ParagraphStyle("institucion",    parent=base["Normal"],  fontSize=10, textColor=_AZUL_OSCURO, fontName="Helvetica-Bold", alignment=TA_CENTER),
            "dependencia":    ParagraphStyle("dependencia",    parent=base["Normal"],  fontSize=8,  textColor=_AZUL_MEDIO, alignment=TA_CENTER),
            "titulo":         ParagraphStyle("titulo",         parent=base["Title"],   fontSize=14, textColor=_AZUL_OSCURO, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2),
            "subtitulo_gris": ParagraphStyle("subtitulo_gris", parent=base["Normal"],  fontSize=9,  textColor=colors.HexColor("#888888"), alignment=TA_CENTER),
            "subtitulo":      ParagraphStyle("subtitulo",      parent=base["Heading2"],fontSize=10, textColor=_AZUL_OSCURO, fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=4),
            "normal":         ParagraphStyle("normal",         parent=base["Normal"],  fontSize=9,  leading=13),
            "th":             ParagraphStyle("th",             parent=base["Normal"],  fontSize=8,  textColor=_BLANCO, fontName="Helvetica-Bold", alignment=TA_CENTER),
            "td":             ParagraphStyle("td",             parent=base["Normal"],  fontSize=8,  leading=11),
            "td_centro":      ParagraphStyle("td_centro",      parent=base["Normal"],  fontSize=8,  alignment=TA_CENTER, leading=11),
            "td_pequeño":     ParagraphStyle("td_pequeño",     parent=base["Normal"],  fontSize=7,  leading=10),
            "chip_label":     ParagraphStyle("chip_label",     parent=base["Normal"],  fontSize=8,  textColor=_BLANCO, fontName="Helvetica-Bold", alignment=TA_CENTER),
            "chip_valor":     ParagraphStyle("chip_valor",     parent=base["Normal"],  fontSize=22, textColor=_BLANCO, fontName="Helvetica-Bold", alignment=TA_CENTER),
            "pie":            ParagraphStyle("pie",            parent=base["Normal"],  fontSize=7,  textColor=colors.HexColor("#aaaaaa"), alignment=TA_RIGHT),
        }
# ============================================================
# SECCIÓN 6 — SETUP INICIAL DE LA BASE DE DATOS
# (antes en db/setup.py)
#
# Ejecuta este archivo directamente para configurar la BD:
#   python db.py
# ============================================================
def _setup_crear_base_de_datos():
    """Crea la base de datos si no existe."""
    params = DATABASE[MODO].copy()
    nombre_bd = params.pop("database")
    conn = mysql.connector.connect(**params)
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {nombre_bd} "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[OK] Base de datos '{nombre_bd}' lista.")
def _setup_ejecutar_schema():
    """Ejecuta el script schema.sql para crear todas las tablas."""
    import os as _os
    ruta_schema = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "schema.sql")
    with open(ruta_schema, "r", encoding="utf-8") as f:
        sql_completo = f.read()
    params = DATABASE[MODO]
    conn = mysql.connector.connect(**params)
    cursor = conn.cursor()
    sentencias = [s.strip() for s in sql_completo.split(";") if s.strip()]
    for sentencia in sentencias:
        try:
            cursor.execute(sentencia)
        except mysql.connector.Error as e:
            if e.errno not in (1050, 1060, 1061):
                print(f"[ADVERTENCIA] {e}")
    conn.commit()
    cursor.close()
    conn.close()
    print("[OK] Tablas creadas correctamente.")
def _setup_crear_usuario_admin():
    """Crea el usuario admin con contraseña cifrada si no existe."""
    params = DATABASE[MODO]
    print("\n--- Configuración del usuario administrador ---")
    password = input("Ingrese la contraseña para el usuario 'admin': ").strip()
    if not password:
        password = "admin123"
        print("[INFO] Se usó la contraseña por defecto: admin123")
    password_bytes = password.encode("utf-8")
    hash_password  = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
    conn   = mysql.connector.connect(**params)
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario FROM usuario WHERE username = 'admin'")
    existe = cursor.fetchone()
    if existe:
        cursor.execute(
            "UPDATE usuario SET password_hash = %s WHERE username = 'admin'",
            (hash_password,)
        )
        print("[OK] Contraseña del admin actualizada.")
    else:
        cursor.execute(
            """INSERT INTO usuario (username, password_hash, nombre_completo, email)
               VALUES (%s, %s, %s, %s)""",
            ("admin", hash_password, "Administrador del Sistema", "admin@dppps.gob.ve")
        )
        print("[OK] Usuario admin creado.")
    conn.commit()
    cursor.close()
    conn.close()
if __name__ == "__main__":
    print("=== Setup inicial del Sistema DPPPS ===\n")
    try:
        _setup_crear_base_de_datos()
        _setup_ejecutar_schema()
        _setup_crear_usuario_admin()
        print("\n[LISTO] Setup completado exitosamente.")
        print("   Ya puedes ejecutar la aplicacion con: python main.py")
    except Exception as e:
        print(f"\n[ERROR] Error durante el setup: {e}")
        print("   Verifica que MariaDB/MySQL este corriendo y los datos en DATABASE sean correctos.")
