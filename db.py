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
# Ruta de la plantilla Excel para importación de vocerías CS
VOCERIA_TEMPLATE_PATH = "assets/templates/FORMATO DE DATA COMITES 2026.xlsx"
# Tipos de archivo permitidos para evidencias
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf", ".docx"]
# Tamaño máximo de archivo en MB
MAX_FILE_SIZE_MB = 10
# Catálogo base de ASIC permitidos por el sistema
ASIC_PREDETERMINADOS = [
    ("ASIC-01", "Andrés Bello"),
    ("ASIC-02", "Antonio Rómulo Costa"),
    ("ASIC-03", "Ayacucho"),
    ("ASIC-04", "Bolívar"),
    ("ASIC-05", "Capacho Independencia"),
    ("ASIC-06", "Capacho Libertad"),
    ("ASIC-07", "Cárdenas"),
    ("ASIC-08", "Córdoba"),
    ("ASIC-09", "Dr. Hugo Murzi"),
    ("ASIC-10", "Dr. Jacinto Convit"),
    ("ASIC-11", "Dr. José María Vargas"),
    ("ASIC-12", "Fernández Feo"),
    ("ASIC-13", "García de Hevia"),
    ("ASIC-14", "Guásimos"),
    ("ASIC-15", "Jáuregui"),
    ("ASIC-16", "Junín"),
    ("ASIC-17", "Libertador"),
    ("ASIC-18", "Michelena"),
    ("ASIC-19", "Panamericano"),
    ("ASIC-20", "Sabaneta"),
    ("ASIC-21", "Samuel Darío Maldonado"),
    ("ASIC-22", "Sucre"),
    ("ASIC-23", "Torbes"),
    ("ASIC-24", "Ureña"),
    ("ASIC-25", "Uribante"),
]

VOCERIA_ESTADO_OPCIONES = ["Táchira"]

MUNICIPIOS_TACHIRA = [
    "Andrés Bello",
    "Antonio Rómulo Costa",
    "Ayacucho",
    "Bolívar",
    "Cárdenas",
    "Córdoba",
    "Fernández Feo",
    "Francisco de Miranda",
    "García de Hevia",
    "Guásimos",
    "Independencia",
    "Jáuregui",
    "José María Vargas",
    "Junín",
    "Libertad",
    "Libertador",
    "Lobatera",
    "Michelena",
    "Panamericano",
    "Pedro María Ureña",
    "Rafael Urdaneta",
    "Samuel Darío Maldonado",
    "San Cristóbal",
    "San Judas Tadeo",
    "Seboruco",
    "Simón Rodríguez",
    "Sucre",
    "Torbes",
    "Uribante",
]

VOCERIA_MUNICIPIO_OPCIONES = MUNICIPIOS_TACHIRA
VOCERIA_ASIC_OPCIONES = [nombre for _, nombre in ASIC_PREDETERMINADOS]


def build_voceria_template(output_path=None):
    """Genera la plantilla Excel para vocerías CS con listas desplegables para Estado, Municipio y ASIC.

    El formato replica exactamente el archivo de referencia 'FORMATO DE DATA COMITES 2026 N.xlsx':
    - Fila 1: título fusionado A1:R1 con fondo rojo C00000 y texto blanco, altura 36.75
    - Fila 2: encabezados con fondo rojo C00000, texto blanco, bordes thin, wrap habilitado, altura 69.75
    - Filas 3+: datos con numeración correlativa en columna A, altura 25.5
    - Listas desplegables en columnas B (Estado), C (Municipio) y E (ASIC)
    """
    if output_path is None:
        output_path = VOCERIA_TEMPLATE_PATH

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "hoja1"

    # ── Colores y estilos del archivo de referencia ──────────────────────────
    RED_FILL    = "C00000"   # Rojo oscuro idéntico al original (FFC00000)
    WHITE_FONT  = "FFFFFFFF" # Blanco puro
    thin_side   = Side(border_style="thin", color="000000")
    thin_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    title_fill  = PatternFill("solid", fgColor=RED_FILL)
    title_font  = Font(bold=True, color=WHITE_FONT, size=12, name="Calibri")
    title_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    header_fill  = PatternFill("solid", fgColor=RED_FILL)
    header_font  = Font(bold=True, color=WHITE_FONT, size=12, name="Calibri")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # ── Fila 1: Título fusionado A1:R1 ───────────────────────────────────────
    ws.merge_cells("A1:R1")
    ws["A1"] = "DATAS DE LOS VOCEROS Y VOCERAS DE LOS COMITES DE SALUD  2026"
    ws["A1"].fill      = title_fill
    ws["A1"].font      = title_font
    ws["A1"].alignment = title_align
    ws.row_dimensions[1].height = 36.75

    # ── Fila 2: Encabezados de columnas (idénticos al original) ──────────────
    headers = [
        "Nro",
        "ESTADO",
        "MUNICIPIO",
        "PARROQUIA",
        "ASIC",
        "NOMBRE DEL COMITÉ",
        "INDIQUE QUE CENTRO DISPENSADOR DE SALUD ES  ( SRI, HOSPITAL, CAT, CDI, CLINICA POPULAR, CONSULTORIO MEDICO POPULAR, AMBULATORIO U OTRO )",
        "NOMBRE DEL CENTRO DISPENSADOR DE SALUD",
        "NOMBRES Y APELLIDO  ",
        "C.I:",
        "TELÉFONO",
        "VOCERIA",
        "FECHA DE NACIMIENTO",
        "EDAD",
        "SEXO",
        "PROFESION/OFICIO",
        "CORREO",
        "FECHAS DE ELECCION",
    ]

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col_idx, value=header)
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = header_align
        cell.border    = thin_border
    ws.row_dimensions[2].height = 69.75

    # ── Filas de datos vacías (3 en adelante) con altura y numeración ─────────
    data_align = Alignment(horizontal="center", vertical="center")
    data_font  = Font(size=11, name="Calibri")
    for row_idx in range(3, 33):
        ws.row_dimensions[row_idx].height = 25.5
        # Columna A: número de fila correlativo (igual que el original)
        cell_a = ws.cell(row=row_idx, column=1, value=row_idx - 2)
        cell_a.alignment = data_align
        cell_a.font      = data_font
        # Celdas restantes con alineación centrada
        for col_idx in range(2, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.alignment = data_align
            cell.font      = data_font

    # ── Anchos de columna exactos del archivo de referencia ───────────────────
    col_widths = {
        "A": 8.28515625,
        "B": 14.5703125,
        "C": 14.0,
        "D": 16.85546875,
        "E": 15.7109375,
        "F": 26.85546875,
        "G": 45.42578125,
        "H": 25.7109375,
        "I": 26.7109375,
        "J": 17.0,
        "K": 17.5703125,
        "L": 18.140625,
        "M": 20.7109375,
        "N": 20.7109375,
        "O": 8.0,
        "P": 22.85546875,
        "Q": 20.42578125,
        "R": 23.7109375,
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    # ── Listas desplegables en B (Estado), C (Municipio), E (ASIC) ───────────
    estado_options    = ",".join(VOCERIA_ESTADO_OPCIONES)
    municipio_options = ",".join(VOCERIA_MUNICIPIO_OPCIONES)
    asic_options      = ",".join(VOCERIA_ASIC_OPCIONES)

    dv_estado = DataValidation(type="list", formula1=f'"{estado_options}"', allow_blank=True)
    dv_estado.promptTitle = "Estado"
    dv_estado.prompt = "Seleccione una opción válida."
    dv_estado.add("B3:B1000")
    ws.add_data_validation(dv_estado)

    dv_municipio = DataValidation(type="list", formula1=f'"{municipio_options}"', allow_blank=True)
    dv_municipio.promptTitle = "Municipio"
    dv_municipio.prompt = "Seleccione un municipio válido."
    dv_municipio.add("C3:C1000")
    ws.add_data_validation(dv_municipio)

    dv_asic = DataValidation(type="list", formula1=f'"{asic_options}"', allow_blank=True)
    dv_asic.promptTitle = "ASIC"
    dv_asic.prompt = "Seleccione un ASIC válido."
    dv_asic.add("E3:E1000")
    ws.add_data_validation(dv_asic)

    wb.save(output_path)
    return output_path


# Catálogo base de tipos de actividad permitidos por el sistema
TIPOS_ACTIVIDAD_PREDETERMINADOS = [
    ("TIPO-01", "Salud toca tu puerta"),
    ("TIPO-02", "Sesiones educativas"),
    ("TIPO-03", "Los Comités de Salud van a la escuela"),
    ("TIPO-04", "Actividades de Promoción y Prevención Social"),
    ("TIPO-05", "Participación Activa en Jornadas"),
    ("TIPO-06", "Participación Activa en Inmunizaciones"),
    ("TIPO-07", "Entrevista servicio social"),
]
# Título de la aplicación (se muestra en la barra de la ventana)
APP_TITLE = "DPPPS — Sistema de Consolidación de Informes"
APP_VERSION = "1.0.0"
# ============================================================
# SECCIÓN 2 — CONEXIÓN A LA BASE DE DATOS
# (antes en db/connection.py)
# ============================================================
import mysql.connector
import random
import smtplib
import os
import re
import unicodedata
import zipfile
from copy import deepcopy
from email.message import EmailMessage
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

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
from datetime import date, datetime, timedelta
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

    def obtener_por_email(self, email):
        """Busca un usuario por correo. Retorna dict o None."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuario WHERE email = %s AND activo = TRUE",
            (email.lower().strip(),)
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

    def crear_usuario(self, nombre, apellido, email, password, codigo_verificacion="", codigo_verificacion_expira=None):
        """Crea un usuario nuevo para el flujo de registro con correo verificado."""
        hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        username = email.lower().strip()
        nombre_completo = f"{nombre.strip()} {apellido.strip()}".strip()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO usuario (
                username, password_hash, nombre_completo, email, nombre, apellido,
                email_verificado, codigo_verificacion, codigo_verificacion_expira, activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, FALSE, %s, %s, TRUE)
            """,
            (username, hash_pw, nombre_completo, email.lower().strip(), nombre.strip(), apellido.strip(), codigo_verificacion, codigo_verificacion_expira)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id

    def guardar_codigo_verificacion(self, email, codigo, expiracion):
        """Guarda el código de verificación en el usuario."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET codigo_verificacion = %s, codigo_verificacion_expira = %s WHERE email = %s AND activo = TRUE",
            (codigo, expiracion, email.lower().strip())
        )
        conn.commit()
        cursor.close()
        conn.close()

    def guardar_codigo_recuperacion(self, email, codigo, expiracion):
        """Guarda el código de recuperación de contraseña."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET codigo_recuperacion = %s, codigo_recuperacion_expira = %s WHERE email = %s AND activo = TRUE",
            (codigo, expiracion, email.lower().strip())
        )
        conn.commit()
        cursor.close()
        conn.close()

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


def asegurar_esquema_autenticacion():
    """Asegura que la tabla usuario tenga las columnas necesarias para registro por correo."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SHOW COLUMNS FROM usuario")
    columnas = {columna["Field"] for columna in cursor.fetchall()}
    cambios = {
        "nombre": "ALTER TABLE usuario ADD COLUMN nombre VARCHAR(100) NULL",
        "apellido": "ALTER TABLE usuario ADD COLUMN apellido VARCHAR(100) NULL",
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
    conn.commit()
    cursor.close()
    conn.close()


asegurar_esquema_autenticacion()
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
                   a.nombre_establecimiento, a.comites_salud,
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
               comites_salud, descripcion,
               medicos, promotores_salud, voceros_comite_salud, vocero_consejo_direccion,
               coordinador_docencia, autoridades_presentes, otros_actores,
               personas_comunidad, estudiantes_aspirantes, participantes):
        """Inserta una nueva actividad. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO actividad (id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin,
                                   estado, municipio, parroquia, establecimiento_salud,
                                   nombre_establecimiento, comites_salud, descripcion,
                                   medicos, promotores_salud, voceros_comite_salud,
                                   vocero_consejo_direccion, coordinador_docencia,
                                   autoridades_presentes, otros_actores,
                                   personas_comunidad, estudiantes_aspirantes, participantes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (id_asic, id_tipo, id_usuario_registro, fecha_inicio, fecha_fin,
                             estado, municipio, parroquia, establecimiento_salud, nombre_establecimiento,
                             comites_salud, descripcion,
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
                     nombre_establecimiento, comites_salud, descripcion,
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
                nombre_establecimiento = %s, comites_salud = %s, descripcion = %s,
                medicos = %s, promotores_salud = %s, voceros_comite_salud = %s,
                vocero_consejo_direccion = %s, coordinador_docencia = %s,
                autoridades_presentes = %s, otros_actores = %s,
                personas_comunidad = %s, estudiantes_aspirantes = %s, participantes = %s
            WHERE id_actividad = %s
        """
        cursor.execute(sql, (id_asic, id_tipo, fecha_inicio, fecha_fin,
                             estado, municipio, parroquia, establecimiento_salud,
                             nombre_establecimiento, comites_salud, descripcion,
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
    def crear(self, codigo, nombre):
        """Inserta un nuevo tipo de actividad. Retorna el ID generado."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tipo_actividad (codigo, nombre) VALUES (%s, %s)",
            (codigo, nombre)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id
    def actualizar(self, id_tipo, codigo, nombre):
        """Actualiza un tipo de actividad existente."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tipo_actividad SET codigo=%s, nombre=%s WHERE id_tipo=%s",
            (codigo, nombre, id_tipo)
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

class VoceriaDAO:
    """Maneja las consultas SQL para vocerías CS (cabecera)."""
    def obtener_todas(self, filtros=None):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT v.id_voceria, v.id_asic, v.id_tipo, v.id_usuario_registro,
                   v.fecha, v.estado, v.municipio, v.parroquia,
                   v.created_at,
                   a.nombre AS asic_nombre,
                   tv.nombre AS tipo_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM voceria v
            JOIN asic a ON v.id_asic = a.id_asic
            JOIN tipo_voceria tv ON v.id_tipo = tv.id_tipo
            JOIN usuario u ON v.id_usuario_registro = u.id_usuario
            WHERE v.eliminado = FALSE
        """
        params = []
        if filtros:
            if filtros.get("id_asic"):
                sql += " AND v.id_asic = %s"
                params.append(filtros["id_asic"])
            if filtros.get("id_tipo"):
                sql += " AND v.id_tipo = %s"
                params.append(filtros["id_tipo"])
            if filtros.get("fecha_desde"):
                sql += " AND v.fecha >= %s"
                params.append(filtros["fecha_desde"])
            if filtros.get("fecha_hasta"):
                sql += " AND v.fecha <= %s"
                params.append(filtros["fecha_hasta"])
        sql += " ORDER BY v.fecha DESC, v.id_voceria DESC"
        cursor.execute(sql, tuple(params))
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_voceria):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT v.id_voceria, v.id_asic, v.id_tipo, v.id_usuario_registro,
                   v.fecha, v.estado, v.municipio, v.parroquia,
                   v.created_at,
                   a.nombre AS asic_nombre,
                   tv.nombre AS tipo_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM voceria v
            JOIN asic a ON v.id_asic = a.id_asic
            JOIN tipo_voceria tv ON v.id_tipo = tv.id_tipo
            JOIN usuario u ON v.id_usuario_registro = u.id_usuario
            WHERE v.id_voceria = %s AND v.eliminado = FALSE
        """
        cursor.execute(sql, (id_voceria,))
        voc = cursor.fetchone()
        cursor.close()
        conn.close()
        return voc

    def obtener_con_items(self, id_voceria):
        """Obtiene la vocería con todos sus items (voceros)."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # Cabecera
        sql = """
            SELECT v.id_voceria, v.id_asic, v.id_tipo, v.id_usuario_registro,
                   v.fecha, v.estado, v.municipio, v.parroquia,
                   v.created_at,
                   a.nombre AS asic_nombre,
                   tv.nombre AS tipo_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM voceria v
            JOIN asic a ON v.id_asic = a.id_asic
            JOIN tipo_voceria tv ON v.id_tipo = tv.id_tipo
            JOIN usuario u ON v.id_usuario_registro = u.id_usuario
            WHERE v.id_voceria = %s AND v.eliminado = FALSE
        """
        cursor.execute(sql, (id_voceria,))
        voc = cursor.fetchone()
        if not voc:
            cursor.close()
            conn.close()
            return None
        # Items
        sql_items = """
            SELECT vi.*, tv.nombre AS tipo_voceria_nombre
            FROM voceria_item vi
            JOIN tipo_voceria tv ON vi.id_tipo_voceria = tv.id_tipo
            WHERE vi.id_voceria = %s AND vi.eliminado = FALSE
            ORDER BY vi.id_item
        """
        cursor.execute(sql_items, (id_voceria,))
        items = cursor.fetchall()
        voc["items"] = items
        cursor.close()
        conn.close()
        return voc

    def crear(self, id_asic, id_tipo, id_usuario_registro, fecha, estado, municipio, parroquia,
              items):
        """
        Crea vocería cabecera + items en una transacción.
        items: lista de dicts con los campos de voceria_item
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Crear cabecera
            sql = """
                INSERT INTO voceria (id_asic, id_tipo, id_usuario_registro, fecha, estado, municipio, parroquia)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (id_asic, id_tipo, id_usuario_registro, fecha, estado, municipio, parroquia))
            id_voceria = cursor.lastrowid

            # 2. Crear items
            if items:
                sql_item = """
                    INSERT INTO voceria_item (id_voceria, id_tipo_voceria, nombre_comite, centro_dispensador,
                                             nombre_centro, nombres, ci, telefono, fecha_nacimiento, edad,
                                             sexo, profesion, correo, fechas_eleccion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                for item in items:
                    cursor.execute(sql_item, (
                        id_voceria,
                        item.get("id_tipo_voceria"),
                        item.get("nombre_comite"),
                        item.get("centro_dispensador"),
                        item.get("nombre_centro"),
                        item.get("nombres"),
                        item.get("ci"),
                        item.get("telefono"),
                        item.get("fecha_nacimiento"),
                        item.get("edad"),
                        item.get("sexo"),
                        item.get("profesion"),
                        item.get("correo"),
                        item.get("fechas_eleccion")
                    ))

            conn.commit()
            return id_voceria
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, id_voceria, id_asic, id_tipo, fecha, estado, municipio, parroquia,
                   items):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Actualizar cabecera
            sql = """
                UPDATE voceria
                SET id_asic = %s, id_tipo = %s, fecha = %s, estado = %s, municipio = %s, parroquia = %s
                WHERE id_voceria = %s
            """
            cursor.execute(sql, (id_asic, id_tipo, fecha, estado, municipio, parroquia,
                                 id_voceria))

            # 2. Soft delete items existentes
            cursor.execute("UPDATE voceria_item SET eliminado = TRUE WHERE id_voceria = %s", (id_voceria,))

            # 3. Crear nuevos items
            if items:
                sql_item = """
                    INSERT INTO voceria_item (id_voceria, id_tipo_voceria, nombre_comite, centro_dispensador,
                                             nombre_centro, nombres, ci, telefono, fecha_nacimiento, edad,
                                             sexo, profesion, correo, fechas_eleccion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                for item in items:
                    cursor.execute(sql_item, (
                        id_voceria,
                        item.get("id_tipo_voceria"),
                        item.get("nombre_comite"),
                        item.get("centro_dispensador"),
                        item.get("nombre_centro"),
                        item.get("nombres"),
                        item.get("ci"),
                        item.get("telefono"),
                        item.get("fecha_nacimiento"),
                        item.get("edad"),
                        item.get("sexo"),
                        item.get("profesion"),
                        item.get("correo"),
                        item.get("fechas_eleccion")
                    ))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, id_voceria):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE voceria SET eliminado = TRUE WHERE id_voceria = %s", (id_voceria,))
            cursor.execute("UPDATE voceria_item SET eliminado = TRUE WHERE id_voceria = %s", (id_voceria,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()


class TipoVoceriaDAO:
    """Maneja el catálogo de tipos de vocería."""
    def obtener_todos(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_voceria WHERE activo = TRUE ORDER BY nombre")
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_tipo):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_voceria WHERE id_tipo = %s", (id_tipo,))
        tipo = cursor.fetchone()
        cursor.close()
        conn.close()
        return tipo

    def obtener_por_codigo(self, codigo):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_voceria WHERE codigo = %s", (codigo,))
        tipo = cursor.fetchone()
        cursor.close()
        conn.close()
        return tipo

    def crear(self, codigo, nombre):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tipo_voceria (codigo, nombre) VALUES (%s, %s)", (codigo, nombre))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id

    def actualizar(self, id_tipo, codigo, nombre):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tipo_voceria SET codigo=%s, nombre=%s WHERE id_tipo=%s", (codigo, nombre, id_tipo))
        conn.commit()
        cursor.close()
        conn.close()

    def desactivar(self, id_tipo):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tipo_voceria SET activo = FALSE WHERE id_tipo = %s", (id_tipo,))
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

    @staticmethod
    def _generar_codigo(longitud=6):
        return str(random.randint(10 ** (longitud - 1), (10 ** longitud) - 1))

    def _enviar_codigo_por_email(self, email, codigo, tipo):
        """Envía un código por correo usando SMTP. Si no hay configuración no falla el flujo."""
        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "587"))
        usuario = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        if not host or not usuario or not password:
            return False

        asunto = "Código de verificación" if tipo == "verificacion" else "Código para recuperar tu contraseña"
        cuerpo = (
            f"Tu código es: {codigo}\n\n"
            f"Este código vence en 10 minutos."
        )

        try:
            msg = EmailMessage()
            msg["From"] = usuario
            msg["To"] = email
            msg["Subject"] = asunto
            msg.set_content(cuerpo, charset="utf-8")

            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(usuario, password)
                server.send_message(msg)
            return True
        except Exception as exc:
            print(f"[WARN] No se pudo enviar el correo: {exc}")
            return False

    def registrar_usuario(self, nombre, apellido, email, password):
        """Crea un usuario nuevo y exige validación por correo."""
        email = (email or "").strip().lower()
        nombre = (nombre or "").strip()
        apellido = (apellido or "").strip()
        if not nombre or not apellido or not email or not password:
            return {"success": False, "message": "Completa todos los campos."}
        if "@" not in email or "." not in email.split("@")[-1]:
            return {"success": False, "message": "Ingresa un correo válido."}
        if len(password) < 6:
            return {"success": False, "message": "La contraseña debe tener al menos 6 caracteres."}
        if self.usuario_dao.obtener_por_email(email):
            return {"success": False, "message": "Este correo ya está registrado."}

        codigo = self._generar_codigo()
        expiracion = datetime.now() + timedelta(minutes=10)
        try:
            self.usuario_dao.crear_usuario(nombre, apellido, email, password, codigo, expiracion)
            enviado = self._enviar_codigo_por_email(email, codigo, "verificacion")
            respuesta = {
                "success": True,
                "message": "Cuenta creada. Revisa tu correo para verificarla.",
            }
            if not enviado:
                respuesta["message"] = (
                    "Cuenta creada. No se pudo enviar el correo en este momento. "
                    "Intenta nuevamente más tarde."
                )
            return respuesta
        except Exception as exc:
            print(f"[ERROR] Error al registrar usuario: {exc}")
            return {"success": False, "message": "No se pudo crear la cuenta."}

    def verificar_email(self, email, codigo):
        """Valida el código de verificación enviado al correo."""
        email = (email or "").strip().lower()
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return False
        if usuario.get("codigo_verificacion") != str(codigo).strip():
            return False
        if usuario.get("codigo_verificacion_expira") is None:
            return False
        if datetime.now() > usuario["codigo_verificacion_expira"]:
            return False
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET email_verificado = TRUE, codigo_verificacion = NULL, codigo_verificacion_expira = NULL WHERE id_usuario = %s",
            (usuario["id_usuario"],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def login(self, credential, password):
        """
        Intenta iniciar sesión con correo o username y password.
        Requiere que el correo haya sido verificado.
        """
        global sesion_actual
        email = credential.strip().lower() if isinstance(credential, str) else ""
        usuario = self.usuario_dao.obtener_por_email(email) if "@" in email else self.usuario_dao.obtener_por_username(email)
        if usuario is None:
            return False
        if usuario.get("email_verificado") in (False, 0, None):
            return False
        password_correcta = self.usuario_dao.verificar_password(
            password,
            usuario["password_hash"]
        )
        if not password_correcta:
            return False
        sesion_actual = {
            "id_usuario": usuario["id_usuario"],
            "username": usuario.get("username") or usuario.get("email"),
            "nombre_completo": usuario.get("nombre_completo") or f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip(),
            "email": usuario.get("email")
        }
        return True

    def solicitar_recuperacion(self, email):
        """Genera y envía un código para recuperar la contraseña."""
        email = (email or "").strip().lower()
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return {"success": False, "message": "No existe una cuenta con ese correo."}
        codigo = self._generar_codigo()
        expiracion = datetime.now() + timedelta(minutes=10)
        self.usuario_dao.guardar_codigo_recuperacion(email, codigo, expiracion)
        enviado = self._enviar_codigo_por_email(email, codigo, "recuperacion")
        respuesta = {"success": True, "message": "Se envió un código a tu correo."}
        if not enviado:
            respuesta["message"] = (
                "No se pudo enviar el correo en este momento. Intenta nuevamente más tarde."
            )
        return respuesta

    def cambiar_password_con_codigo(self, email, codigo, nueva_password):
        """Recupera contraseña usando el código enviado al correo."""
        email = (email or "").strip().lower()
        if len(nueva_password) < 6:
            return {"success": False, "message": "La contraseña debe tener al menos 6 caracteres."}
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return {"success": False, "message": "No existe una cuenta con ese correo."}
        if usuario.get("codigo_recuperacion") != str(codigo).strip():
            return {"success": False, "message": "Código incorrecto."}
        if usuario.get("codigo_recuperacion_expira") is None or datetime.now() > usuario["codigo_recuperacion_expira"]:
            return {"success": False, "message": "El código ha expirado."}
        self.usuario_dao.cambiar_password(usuario["id_usuario"], nueva_password)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET codigo_recuperacion = NULL, codigo_recuperacion_expira = NULL WHERE id_usuario = %s",
            (usuario["id_usuario"],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True, "message": "Contraseña actualizada correctamente."}

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
        """Retorna solo los ASIC permitidos por la plantilla del sistema."""
        asics_predeterminados = ASIC_PREDETERMINADOS

        def normalizar(nombre):
            return " ".join((nombre or "").strip().lower().split())

        try:
            existentes = self.asic_dao.obtener_todos()
            nombres_existentes = {normalizar(a["nombre"]) for a in existentes}
            nombres_permitidos = {normalizar(nombre) for _, nombre in asics_predeterminados}

            for asic in existentes:
                if normalizar(asic["nombre"]) not in nombres_permitidos:
                    self.asic_dao.desactivar(asic["id_asic"])

            for codigo, nombre in asics_predeterminados:
                if normalizar(nombre) not in nombres_existentes:
                    self.asic_dao.crear(codigo, nombre, "", "")
        except Exception:
            pass

        asics = self.asic_dao.obtener_todos()
        nombres_permitidos = {normalizar(nombre) for _, nombre in asics_predeterminados}
        return [a for a in asics if normalizar(a["nombre"]) in nombres_permitidos]
    def listar_tipos_actividad(self):
        """Retorna solo los tipos de actividad permitidos por la plantilla del sistema."""
        tipos_predeterminados = TIPOS_ACTIVIDAD_PREDETERMINADOS

        def normalizar(nombre):
            return " ".join((nombre or "").strip().lower().split())

        try:
            existentes = self.tipo_dao.obtener_todos()
            nombres_existentes = {normalizar(t["nombre"]) for t in existentes}
            nombres_permitidos = {normalizar(nombre) for _, nombre in tipos_predeterminados}

            for tipo in existentes:
                if normalizar(tipo["nombre"]) not in nombres_permitidos:
                    self.tipo_dao.desactivar(tipo["id_tipo"])

            for codigo, nombre in tipos_predeterminados:
                if normalizar(nombre) not in nombres_existentes:
                    self.tipo_dao.crear(codigo, nombre, f"Tipo de actividad predeterminado: {nombre}")
        except Exception:
            pass

        tipos = self.tipo_dao.obtener_todos()
        nombres_permitidos = {normalizar(nombre) for _, nombre in tipos_predeterminados}
        return [t for t in tipos if normalizar(t["nombre"]) in nombres_permitidos]
    def guardar_actividad(self, id_asic, id_tipo, fecha_inicio, fecha_fin,
                           estado, municipio, parroquia, establecimiento_salud,
                           nombre_establecimiento, comites_salud, descripcion,
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
        # 3. Validar participantes (total asistencia)
        try:
            cant_participantes = int(participantes)
            if cant_participantes < 0:
                return False, "La cantidad de participantes no puede ser menor a 0."
        except (ValueError, TypeError):
            return False, "La cantidad de participantes debe ser un numero entero valido."
        # 4. Validar campos numéricos de participantes por categoría
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
        # 5. Convertir y validar fechas
        f_ini = None
        f_fin = None
        if isinstance(fecha_inicio, str):
            try:
                if "/" in fecha_inicio:
                    f_ini = datetime.strptime(fecha_inicio, "%d/%m/%Y").date()
                else:
                    f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            except ValueError:
                return False, "El formato de la fecha es inválido."
        elif isinstance(fecha_inicio, (datetime, date)):
            f_ini = fecha_inicio if isinstance(fecha_inicio, date) else fecha_inicio.date()
        else:
            return False, "La fecha es inválida."
        if isinstance(fecha_fin, str):
            try:
                if "/" in fecha_fin:
                    f_fin = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                else:
                    f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            except ValueError:
                return False, "El formato de la fecha es inválido."
        elif isinstance(fecha_fin, (datetime, date)):
            f_fin = fecha_fin if isinstance(fecha_fin, date) else fecha_fin.date()
        else:
            return False, "La fecha es inválida."
        if f_ini > f_fin:
            return False, "La fecha no puede ser posterior a la fecha final."
        fecha_inicio_bd = f_ini.strftime("%Y-%m-%d")
        fecha_fin_bd    = f_fin.strftime("%Y-%m-%d")
        # 6. Validar duplicidad
        es_duplicado = self.actividad_dao.verificar_duplicado(
            id_asic=id_asic,
            id_tipo=id_tipo,
            fecha_inicio=fecha_inicio_bd,
            descripcion=descripcion,
            excluir_id=id_actividad
        )
        if es_duplicado:
            return False, "Ya existe una actividad registrada para este ASIC, tipo, fecha y descripción similar."
        # 7. Obtener usuario actual
        usuario = self.auth.obtener_usuario_actual()
        if not usuario:
            return False, "No hay una sesion de usuario activa."
        id_usuario = usuario["id_usuario"]
        # 8. Guardar en base de datos
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
    def guardar_tipo(self, codigo, nombre, id_tipo=None):
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
            self.tipo_dao.crear(codigo, nombre)
            return True, f"Tipo '{nombre}' creado correctamente."
        else:
            self.tipo_dao.actualizar(id_tipo, codigo, nombre)
            return True, f"Tipo '{nombre}' actualizado correctamente."
    def eliminar_tipo(self, id_tipo):
        """Desactiva un tipo de actividad. Retorna (True, mensaje) o (False, error)."""
        tipo = self.tipo_dao.obtener_por_id(id_tipo)
        if not tipo:
            return False, "No se encontro el tipo de actividad."
        self.tipo_dao.desactivar(id_tipo)
        return True, f"Tipo '{tipo['nombre']}' eliminado correctamente."


class VoceriaController:
    """Maneja la lógica de negocio para vocerías CS."""
    def __init__(self):
        self.voceria_dao = VoceriaDAO()
        self.tipo_voceria_dao = TipoVoceriaDAO()
        self.asic_dao = AsicDAO()
        self.auth = AuthController()

    def listar_vocerias(self, filtros=None):
        return self.voceria_dao.obtener_todas(filtros)

    def listar_asics(self):
        asics = self.asic_dao.obtener_todos()
        return asics

    def listar_tipos_voceria(self):
        tipos = self.tipo_voceria_dao.obtener_todos()
        return tipos

    def obtener_voceria_completa(self, id_voceria):
        """Obtiene vocería con todos sus items (voceros)."""
        return self.voceria_dao.obtener_con_items(id_voceria)

    def guardar_voceria(self, id_asic, id_tipo=None, fecha=None, estado=None, municipio=None, parroquia=None,
                         items=None, id_voceria=None):
        """
        Guarda vocería con sus items (voceros).
        items: lista de dicts con los campos de cada vocero
        """
        if items is None:
            items = []

        if not id_asic:
            return False, "Debes seleccionar un ASIC."
        if not fecha or str(fecha).strip() in ("", "AAAA-MM-DD"):
            return False, "La fecha es obligatoria."
        if not estado or not str(estado).strip():
            return False, "El estado es obligatorio."
        if not municipio or not str(municipio).strip():
            return False, "El municipio es obligatorio."
        if not parroquia or not str(parroquia).strip() or str(parroquia).strip() == "Parroquia":
            return False, "La parroquia es obligatoria."
        if not items:
            return False, "Debe agregar al menos 1 vocería."

        tipos_voceria = self.tipo_voceria_dao.obtener_todos()
        if not id_tipo and tipos_voceria:
            id_tipo = tipos_voceria[0]["id_tipo"]
        if not id_tipo:
            return False, "Debes seleccionar un tipo de vocería."

        # Validar TODOS los campos en cada item
        for idx, item in enumerate(items, start=1):
            if not item.get("nombre_comite") or not str(item.get("nombre_comite")).strip():
                return False, f"Vocería #{idx}: Nombre del Comité es obligatorio."
            if not item.get("centro_dispensador") or not str(item.get("centro_dispensador")).strip():
                return False, f"Vocería #{idx}: Centro dispensador es obligatorio."
            if not item.get("nombre_centro") or not str(item.get("nombre_centro")).strip():
                return False, f"Vocería #{idx}: Nombre del Centro es obligatorio."
            if not item.get("nombres") or not str(item.get("nombres")).strip():
                return False, f"Vocería #{idx}: Nombres y Apellidos son obligatorios."
            if not item.get("ci") or not str(item.get("ci")).strip():
                return False, f"Vocería #{idx}: C.I. es obligatoria."
            if not item.get("telefono") or not str(item.get("telefono")).strip():
                return False, f"Vocería #{idx}: Teléfono es obligatorio."
            if not item.get("fecha_nacimiento") or not str(item.get("fecha_nacimiento")).strip() or str(item.get("fecha_nacimiento")).strip() == "AAAA-MM-DD":
                return False, f"Vocería #{idx}: Fecha de Nacimiento es obligatoria."
            if not item.get("edad") or not str(item.get("edad")).strip() or str(item.get("edad")).strip() == "Edad":
                return False, f"Vocería #{idx}: Edad es obligatoria."
            if not item.get("id_tipo_voceria"):
                return False, f"Vocería #{idx}: Debe seleccionar una vocería."
            if not item.get("sexo") or not str(item.get("sexo")).strip():
                return False, f"Vocería #{idx}: Sexo es obligatorio."
            if not item.get("profesion") or not str(item.get("profesion")).strip():
                return False, f"Vocería #{idx}: Profesión/Oficio es obligatoria."
            if not item.get("correo") or not str(item.get("correo")).strip():
                return False, f"Vocería #{idx}: Correo electrónico es obligatorio."
            if "@" not in str(item.get("correo")):
                return False, f"Vocería #{idx}: Correo electrónico no válido (debe incluir '@')."
            if not item.get("fechas_eleccion") or not str(item.get("fechas_eleccion")).strip() or str(item.get("fechas_eleccion")).strip() == "AAAA-MM-DD":
                return False, f"Vocería #{idx}: Fechas de Elección es obligatoria."

        id_usuario = self.auth.obtener_usuario_actual()
        id_usuario_registro = id_usuario["id_usuario"] if id_usuario else 1

        try:
            if id_voceria is None:
                self.voceria_dao.crear(id_asic, id_tipo, id_usuario_registro, fecha, estado, municipio, parroquia,
                                       items)
                return True, "Vocería registrada correctamente."
            else:
                self.voceria_dao.actualizar(id_voceria, id_asic, id_tipo, fecha, estado, municipio, parroquia,
                                           items)
                return True, "Vocería actualizada correctamente."
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"

    def eliminar_voceria(self, id_voceria):
        voc = self.voceria_dao.obtener_por_id(id_voceria)
        if not voc:
            return False, "No se encontró la vocería."
        self.voceria_dao.eliminar(id_voceria)
        return True, "Vocería eliminada correctamente."


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
        self._voceria_dao = VoceriaDAO()
    def generar_previo(self, fecha_inicio, fecha_fin, id_asic=None) -> dict:
        """
        Calcula el resumen SIN guardar en BD.
        id_asic puede ser None (todos), un entero (un ASIC) o una lista de enteros (varios ASIC).
        Retorna un dict listo para mostrar en la UI y luego pasarlo a guardar().
        """
        actividades = self._obtener_actividades(fecha_inicio, fecha_fin, id_asic)
        total_act  = len(actividades)
        total_part = sum(a["participantes"] for a in actividades)
        resumen_tipo = self._agrupar(actividades, "tipo_nombre")
        resumen_asic = self._agrupar(actividades, "asic_nombre")
        
        # Obtener vocerías CS con los mismos filtros
        vocerias = self._obtener_vocerias(fecha_inicio, fecha_fin, id_asic)

        # Nombre(s) de ASIC para mostrar en la UI
        asic_nombre = None
        if id_asic:
            ids = id_asic if isinstance(id_asic, list) else [id_asic]
            nombres = []
            for aid in ids:
                asic = self._asic_dao.obtener_por_id(aid)
                if asic:
                    nombres.append(asic["nombre"])
            asic_nombre = ", ".join(nombres) if nombres else str(ids)

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
            "vocerias":            vocerias,
        }
    def _obtener_actividades(self, fecha_inicio, fecha_fin, id_asic) -> list:
        """Usa ActividadDAO con filtros de fecha y ASIC.
        id_asic puede ser None, un entero o una lista de enteros.
        """
        filtros_base = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        if not id_asic:
            # Sin filtro de ASIC → traer todo
            return self._actividad_dao.obtener_todas(filtros_base)

        ids = id_asic if isinstance(id_asic, list) else [id_asic]
        if len(ids) == 1:
            filtros = dict(filtros_base)
            filtros["id_asic"] = ids[0]
            return self._actividad_dao.obtener_todas(filtros)

        # Varios ASIC: consultar uno por uno y combinar sin duplicados
        vistas: dict = {}  # id_actividad → registro
        for aid in ids:
            filtros = dict(filtros_base)
            filtros["id_asic"] = aid
            for act in self._actividad_dao.obtener_todas(filtros):
                vistas[act["id_actividad"]] = act
        return sorted(vistas.values(), key=lambda a: (str(a.get("fecha_inicio", "")), a["id_actividad"]), reverse=True)
    def _obtener_vocerias(self, fecha_inicio, fecha_fin, id_asic) -> list:
        """Obtiene vocerías CS con filtros de fecha y ASIC.
        id_asic puede ser None, un entero o una lista de enteros.
        """
        filtros_base = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        if not id_asic:
            return self._voceria_dao.obtener_todas(filtros_base)

        ids = id_asic if isinstance(id_asic, list) else [id_asic]
        if len(ids) == 1:
            filtros = dict(filtros_base)
            filtros["id_asic"] = ids[0]
            return self._voceria_dao.obtener_todas(filtros)

        # Varios ASIC: consultar uno por uno y combinar sin duplicados
        vistas: dict = {}  # id_voceria → registro
        for aid in ids:
            filtros = dict(filtros_base)
            filtros["id_asic"] = aid
            for voc in self._voceria_dao.obtener_todas(filtros):
                vistas[voc["id_voceria"]] = voc
        return sorted(vistas.values(), key=lambda v: (str(v.get("fecha", "")), v["id_voceria"]), reverse=True)

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
# NOTA: "participantes" puede venir como columna única, como "total_asistencia",
# o sumarse desde PARTICIPANTES_CATEGORIAS.
COLUMNAS_REQUERIDAS = [
    "asic", "tipo_actividad", "fecha_inicio", "descripcion",
    "participantes",
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
        # "participantes" puede ser columna única, "total_asistencia" o varias categorías.
        faltantes = []
        for col in COLUMNAS_REQUERIDAS:
            if col in idx:
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
    TEMPLATE_WORD_OFICIO = os.path.join("assets", "templates", "Oficio de entrega de informe de FEBRERO 2026.docx")

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
    def generar_word(self, datos: dict, ruta_salida: str) -> str:
        """Genera el documento Word exportado usando la plantilla oficial del oficio."""
        if not ruta_salida.lower().endswith(".docx"):
            ruta_salida = f"{ruta_salida}.docx"

        os.makedirs(os.path.dirname(ruta_salida) if os.path.dirname(ruta_salida) else ".", exist_ok=True)

        template_path = os.path.join(os.path.dirname(__file__), self.TEMPLATE_WORD_OFICIO)
        if os.path.exists(template_path):
            with zipfile.ZipFile(template_path, "r") as src, zipfile.ZipFile(ruta_salida, "w", compression=zipfile.ZIP_DEFLATED) as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "word/document.xml":
                        data = self._word_template_con_fecha_actual(data)
                        data = self._word_template_con_datos(data, datos)
                    dst.writestr(info, data)
            return ruta_salida

        document_xml = self._word_document_xml(datos)
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
        core = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{titulo}</dc:title>
  <dc:creator>DPPPS</dc:creator>
  <cp:lastModifiedBy>DPPPS</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{fecha}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{fecha}</dcterms:modified>
</cp:coreProperties>'''.format(
            titulo=escape(datos.get("titulo", "Informe Consolidado").strip() or "Informe Consolidado"),
            fecha=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>DPPPS</Application>
</Properties>'''

        with zipfile.ZipFile(ruta_salida, "w", compression=zipfile.ZIP_DEFLATED) as archivo:
            archivo.writestr("[Content_Types].xml", content_types)
            archivo.writestr("_rels/.rels", rels)
            archivo.writestr("docProps/core.xml", core)
            archivo.writestr("docProps/app.xml", app)
            archivo.writestr("word/document.xml", document_xml)
            archivo.writestr("word/styles.xml", self._word_styles_xml())

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

    @staticmethod
    def _normalizar_texto(valor: str) -> str:
        if not valor:
            return ""
        valor = unicodedata.normalize("NFKD", valor)
        valor = valor.encode("ascii", "ignore").decode("ascii")
        valor = valor.lower().strip()
        valor = re.sub(r"[^a-z0-9]+", " ", valor)
        return " ".join(valor.split())

    @staticmethod
    def _texto_parrafo(parrafo, ns: dict) -> str:
        return "".join((n.text or "") for n in parrafo.findall(".//w:t", ns))

    @staticmethod
    def _poner_texto_en_parrafo(parrafo, texto: str, ns: dict):
        nodos = parrafo.findall(".//w:t", ns)
        if not nodos:
            run = ET.SubElement(parrafo, f"{{{ns['w']}}}r")
            texto_node = ET.SubElement(run, f"{{{ns['w']}}}t")
            texto_node.text = str(texto)
            return
        for idx, nodo in enumerate(nodos):
            nodo.text = str(texto) if idx == 0 else ""

    def _word_template_con_fecha_actual(self, xml_bytes: bytes) -> bytes:
        """Actualiza la fecha visible en la cabecera del oficio con la fecha local actual del dispositivo."""
        root = ET.fromstring(xml_bytes)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        ]
        ahora = datetime.now()
        fecha_hoy = f"{ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"

        for parrafo in root.findall(".//w:p", ns):
            textos = [n for n in parrafo.findall(".//w:t", ns)]
            contenido = "".join((n.text or "") for n in textos)
            if "San Cristóbal, 6 de Marzo de 2026" not in contenido and "6 de Marzo de 2026" not in contenido:
                continue

            nuevo_contenido = contenido.replace("San Cristóbal, 6 de Marzo de 2026", f"San Cristóbal, {fecha_hoy}")
            nuevo_contenido = nuevo_contenido.replace("6 de Marzo de 2026", fecha_hoy)

            for nodo in textos:
                nodo.text = ""
            if textos:
                textos[0].text = nuevo_contenido
            break

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _word_template_con_datos(self, xml_bytes: bytes, datos: dict) -> bytes:
        """Reemplaza los conteos reales en cada tipo de actividad de la plantilla del oficio.

        La tabla tiene 2 celdas por fila:
        - Celda 1: párrafos con el nombre de la actividad, luego 'Participantes', etc.
        - Celda 2: párrafos con números alineados a las líneas de la celda 1.
        Se preserva un párrafo por línea para que los números queden frente a su texto.
        """
        root = ET.fromstring(xml_bytes)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        w_ns = ns["w"]

        resumen_tipo = datos.get("resumen_por_tipo", []) or []
        tipo_map = {}
        for fila in resumen_tipo:
            nombre = str(fila.get("nombre") or "").strip()
            if not nombre:
                continue
            tipo_map[self._normalizar_texto(nombre)] = {
                "total_actividades":   int(fila.get("total_actividades",  0) or 0),
                "total_participantes": int(fila.get("total_participantes", 0) or 0),
            }

        # Agregar conteo de vocerías a "Actualización de los comités de salud"
        vocerias = datos.get("vocerias", []) or []
        vocerias_count = len(vocerias)
        if vocerias_count > 0:
            # Buscar la clave normalizada que coincida con esta actividad
            target_norm = self._normalizar_texto("Actualización de los comités de salud")
            if target_norm not in tipo_map:
                tipo_map[target_norm] = {"total_actividades": 0, "total_participantes": 0}
            tipo_map[target_norm]["total_actividades"] += vocerias_count

        nombre_aliases = []
        for _, nombre in TIPOS_ACTIVIDAD_PREDETERMINADOS:
            if nombre:
                nombre_aliases.append(nombre)
        # Asegurar que "Actualización de los comités de salud" esté en los aliases
        # para que la plantilla lo reconozca aunque no haya actividades de ese tipo
        nombre_aliases.append("Actualización de los comités de salud")
        for fila in resumen_tipo:
            nombre = str(fila.get("nombre") or "").strip()
            if nombre and nombre not in nombre_aliases:
                nombre_aliases.append(nombre)

        for fila_elem in root.findall(".//w:tr", ns):
            celdas = fila_elem.findall("./w:tc", ns)
            if len(celdas) < 2:
                continue

            cel1_elem = celdas[0]
            cel2_elem = celdas[1]

            # Analizar cada párrafo de la celda 1 para determinar qué valor
            # va en el párrafo correspondiente de la celda 2.
            parrafos_cel1 = cel1_elem.findall("w:p", ns)
            if not parrafos_cel1:
                continue

            # Primero verificamos si esta fila contiene algún tipo reconocible
            texto_total_cel1 = "".join(
                (n.text or "") for n in cel1_elem.findall(".//w:t", ns)
            )
            contiene_tipo = any(
                self._normalizar_texto(alias) in self._normalizar_texto(texto_total_cel1)
                for alias in nombre_aliases
                if self._normalizar_texto(alias)
            )
            if not contiene_tipo:
                continue

            # Si la fila contiene 'Entrevista servicio social', asegurar que la línea siguiente sea 'Participantes'
            if "entrevista servicio social" in self._normalizar_texto(texto_total_cel1):
                tiene_part = any(
                    self._normalizar_texto("".join((n.text or "") for n in p.findall(".//w:t", ns))) in ("participantes", "particiantes")
                    for p in parrafos_cel1
                )
                if not tiene_part:
                    for pi, p in enumerate(parrafos_cel1):
                        txt_p = self._normalizar_texto("".join((n.text or "") for n in p.findall(".//w:t", ns)))
                        if "entrevista servicio social" in txt_p:
                            for p_sig in parrafos_cel1[pi+1:]:
                                txt_sig = "".join((n.text or "") for n in p_sig.findall(".//w:t", ns)).strip()
                                if txt_sig:
                                    t_nodes = p_sig.findall(".//w:t", ns)
                                    for tidx, tn in enumerate(t_nodes):
                                        tn.text = "Participantes" if tidx == 0 else ""
                                    break

            # Extraer estilo de un párrafo con número en cel2 para reutilizarlo
            rpr_xml_orig = None
            ppr_xml_orig = None
            for p_ref in cel2_elem.findall("w:p", ns):
                t_nodes = p_ref.findall(".//w:t", ns)
                texto_p = "".join((n.text or "") for n in t_nodes).strip()
                if texto_p:  # párrafo que tiene contenido → tomar su estilo
                    rpr_e = p_ref.find(".//w:rPr", ns)
                    ppr_e = p_ref.find("w:pPr",  ns)
                    if rpr_e is not None:
                        rpr_xml_orig = ET.tostring(rpr_e, encoding="unicode")
                    if ppr_e is not None:
                        ppr_xml_orig = ET.tostring(ppr_e, encoding="unicode")
                    break

            # Preservar tcPr (propiedades de celda) antes de limpiar
            tcpr_elem = cel2_elem.find("w:tcPr", ns)
            tcpr_xml = ET.tostring(tcpr_elem, encoding="unicode") if tcpr_elem is not None else None

            # Limpiar celda 2
            for child in list(cel2_elem):
                cel2_elem.remove(child)

            # Restaurar tcPr
            if tcpr_xml:
                try:
                    cel2_elem.append(ET.fromstring(tcpr_xml))
                except Exception:
                    pass

            # Reconstruir celda 2: un párrafo por cada párrafo de celda 1
            ultimo_tipo_norm = None
            for p1 in parrafos_cel1:
                texto_p1 = "".join((n.text or "") for n in p1.findall(".//w:t", ns)).strip()
                linea_norm = self._normalizar_texto(texto_p1)

                # Determinar qué número poner en este párrafo
                valor: str | None = None

                if not texto_p1:
                    # Párrafo vacío → dejar vacío en cel2 (preserva espaciado)
                    valor = None
                elif linea_norm in ("participantes", "particiantes", "participantes "):
                    # Línea "Participantes" → conteo de participantes del tipo previo
                    if ultimo_tipo_norm is not None:
                        valor = str(tipo_map.get(ultimo_tipo_norm, {}).get("total_participantes", 0))
                    else:
                        valor = "0"
                else:
                    # Buscar si esta línea contiene algún tipo de actividad
                    for alias in nombre_aliases:
                        alias_norm = self._normalizar_texto(alias)
                        if alias_norm and alias_norm in linea_norm:
                            valor = str(tipo_map.get(alias_norm, {}).get("total_actividades", 0))
                            ultimo_tipo_norm = alias_norm
                            break
                    if valor is None and texto_p1:
                        valor = "0"

                # Crear el párrafo en cel2
                nuevo_p = ET.SubElement(cel2_elem, f"{{{w_ns}}}p")
                if ppr_xml_orig:
                    try:
                        nuevo_p.insert(0, ET.fromstring(ppr_xml_orig))
                    except Exception:
                        pass
                if valor is not None:
                    nuevo_r = ET.SubElement(nuevo_p, f"{{{w_ns}}}r")
                    if rpr_xml_orig:
                        try:
                            nuevo_r.insert(0, ET.fromstring(rpr_xml_orig))
                        except Exception:
                            pass
                    nuevo_t = ET.SubElement(nuevo_r, f"{{{w_ns}}}t")
                    nuevo_t.text = valor

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _word_document_xml(self, datos: dict) -> str:
        def p(texto: str, negrita: bool = False) -> str:
            texto_escapado = escape(texto)
            estilo = '<w:pPr><w:rPr><w:b/></w:rPr></w:pPr>' if negrita else ''
            return f'<w:p>{estilo}<w:r><w:t xml:space="preserve">{texto_escapado}</w:t></w:r></w:p>'

        lineas = [
            p("DPPPS N°___", True),
            p(datos.get("titulo", "Informe Consolidado"), True),
            p(self._subtitulo_periodo(datos) or "Período no definido"),
            p(f"ASIC: {datos.get('asic_nombre') or 'Todos los ASIC'}"),
            p(f"Total de actividades: {datos.get('total_actividades', 0)}"),
            p(f"Total de participantes: {datos.get('total_participantes', 0)}"),
        ]

        if datos.get("resumen_por_asic"):
            lineas.append(p("Resumen por ASIC:", True))
            for fila in datos["resumen_por_asic"]:
                nombre = fila.get("nombre") or fila.get("asic_nombre", "")
                lineas.append(
                    p(f"- {nombre}: {fila.get('total_actividades', 0)} actividades / {fila.get('total_participantes', 0)} participantes")
                )

        if datos.get("resumen_por_tipo"):
            lineas.append(p("Resumen por tipo de actividad:", True))
            for fila in datos["resumen_por_tipo"]:
                nombre = fila.get("nombre") or ""
                lineas.append(
                    p(f"- {nombre}: {fila.get('total_actividades', 0)} actividades / {fila.get('total_participantes', 0)} participantes")
                )

        if datos.get("actividades"):
            lineas.append(p("Detalle de actividades:", True))
            for i, act in enumerate(datos["actividades"], start=1):
                lineas.append(
                    p(
                        f"{i}. {act.get('asic_nombre', '')} - {act.get('tipo_nombre', '')} - "
                        f"{act.get('fecha_inicio', '')} a {act.get('fecha_fin', '')} - "
                        f"Participantes: {act.get('participantes', 0)} - "
                        f"Descripción: {act.get('descripcion', '')}"
                    )
                )

        obs = (datos.get("observaciones") or "").strip()
        if obs:
            lineas.append(p("Observaciones:", True))
            lineas.append(p(obs))

        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
            'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
            'xmlns:o="urn:schemas-microsoft-com:office:office" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
            'xmlns:v="urn:schemas-microsoft-com:vml" '
            'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
            'xmlns:w10="urn:schemas-microsoft-com:office:word" '
            'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
            'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
            'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
            'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
            'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
            'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
            'mc:Ignorable="w14 w15 wp14">'
            '<w:body>' + ''.join(lineas) + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'
        )

    def _word_styles_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:qFormat/></w:style>
</w:styles>'''

    # ── Bloques PDF ────────────────────────────────────────────────────
    def _encabezado(self, datos: dict, estilos: dict) -> list:
        titulo      = datos.get("titulo", "Informe Consolidado de Actividades")
        subtitulo   = self._subtitulo_periodo(datos)
        asic_nombre = datos.get("asic_nombre") or datos.get("cabecera", {}).get("asic_nombre", "")
        alcance     = f"ASIC: {asic_nombre}" if asic_nombre else "Todos los ASIC"
        return [
            Paragraph("CORPORACIÓN DE SALUD DEL ESTADO TÁCHIRA", estilos["institucion"]),
            Paragraph("División para la Promoción de la Participación Popular en Salud (DPPPS)", estilos["dependencia"]),
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
               ["#", "ASIC", "Tipo", "Fecha Inicio", "Fecha Fin", "Participantes", "Descripción"]]
        filas = [cab]
        for i, act in enumerate(actividades, start=1):
            filas.append([
                Paragraph(str(i),                          estilos["td_centro"]),
                Paragraph(act.get("asic_nombre", ""),      estilos["td_pequeño"]),
                Paragraph(act.get("tipo_nombre", ""),      estilos["td_pequeño"]),
                Paragraph(str(act.get("fecha_inicio", "")), estilos["td_centro"]),
                Paragraph(str(act.get("fecha_fin",   "")), estilos["td_centro"]),
                Paragraph(str(act.get("participantes", 0)), estilos["td_centro"]),
                Paragraph(act.get("descripcion", "")[:120], estilos["td_pequeño"]),
            ])
        tabla = Table(filas, colWidths=["4%","13%","12%","9%","9%","8%","45%"], repeatRows=1)
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
                     "Participantes", "Descripción"]
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
                act.get("participantes", 0),
                act.get("descripcion", ""),
            ]
            for col, val in enumerate(valores, 1):
                c = ws.cell(fila_idx, col, val)
                c.border = border
                c.alignment = Alignment(vertical="top", wrap_text=(col == 7))
                if i % 2 == 0:
                    c.fill = r_fill
        anchos = [5, 25, 22, 13, 13, 13, 60]
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
