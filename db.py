from datetime import date, datetime, timedelta
MODO = "local"
DATABASE = {
    "local": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "dppps_informes"
    },
    "lan": {
        "host": "192.168.1.100",
        "port": 3306,
        "user": "dppps_app",
        "password": "contraseña_segura",
        "database": "dppps_informes"
    }
}

TEMPLATE_PATH = "assets/templates/plantilla_importacion_actividad.xlsx"
VOCERIA_TEMPLATE_PATH = "assets/templates/plantilla_importacion_voceria.xlsx"

MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = [".xlsx"]
VOCERIA_CENTRO_DISPENSADOR_OPCIONES = [
    "Consultorio Popular TIPO I", "Consultorio Popular TIPO II",
    "Consultorio Popular TIPO III", "Clinica Popular TIPO I",
    "Clinica Popular TIPO II", "CDI", "SRI", "CAT",
    "Hospitales TIPO I", "Hospitales TIPO II", "Hospitales TIPO III",
    "Hospitales TIPO IV",
]
ACTIVIDAD_ESTABLECIMIENTO_OPCIONES = VOCERIA_CENTRO_DISPENSADOR_OPCIONES


def validar_correo(correo):
    correo = (correo or "").strip()
    if len(correo) > 120:
        return False
    if not re.fullmatch(
        r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+",
        correo,
    ):
        return False
    parte_local = correo.split("@", 1)[0]
    return not parte_local.startswith(".") and not parte_local.endswith(".") and ".." not in parte_local


def validar_archivo_excel(ruta_archivo):
    if not ruta_archivo or not os.path.isfile(ruta_archivo):
        raise ValueError("Selecciona un archivo Excel existente.")
    if os.path.splitext(ruta_archivo)[1].lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("El archivo debe tener formato .xlsx.")
    if os.path.getsize(ruta_archivo) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"El archivo no puede superar {MAX_FILE_SIZE_MB} MB.")

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
VOCERIA_TIPO_OPCIONES = [
    "V. CONTRALORÍA",
    "V. DEL ADULTO MAYOR",
    "V. DE ENFERMEDADES CRÓNICAS TRASMISIBLES Y NO TRASMISIBLES",
    "V. DE PERSONAS CON DISCAPACIDAD, ENCAMADOS Y CUIDADORES EN SALUD",
    "V. DE SALUD Y VIDA",
    "V. DE NIÑOS, NIÑAS Y ADOLESCENTES",
    "V. DE LA JUVENTUD EN SALUD",
    "V. DE EDUCACIÓN POPULAR EN SALUD INTERCULTURAL Y ANCESTRAL",
    "V. DE INMUNIZACIONES",
    "V. DE PROYECTOS EN SALUD",
]
VOCERIA_SEXO_OPCIONES = ["M", "F"]


def build_voceria_template(output_path=None):
    """Genera la plantilla Excel para vocerías CS con listas desplegables."""
    if output_path is None:
        output_path = VOCERIA_TEMPLATE_PATH

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.utils import get_column_letter
    from openpyxl.workbook.defined_name import DefinedName

    wb = Workbook()
    ws = wb.active
    ws.title = "hoja1"

    RED_FILL = "C00000"
    WHITE_FONT = "FFFFFFFF"
    thin_side = Side(border_style="thin", color="000000")
    thin_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    title_fill = PatternFill("solid", fgColor=RED_FILL)
    title_font = Font(bold=True, color=WHITE_FONT, size=12, name="Calibri")
    title_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    header_fill = PatternFill("solid", fgColor=RED_FILL)
    header_font = Font(bold=True, color=WHITE_FONT, size=12, name="Calibri")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.merge_cells("A1:R1")
    ws["A1"] = "DATAS DE LOS VOCEROS Y VOCERAS DE LOS COMITES DE SALUD  2026"
    ws["A1"].fill = title_fill
    ws["A1"].font = title_font
    ws["A1"].alignment = title_align
    ws.row_dimensions[1].height = 36.75

    headers = [
        "Nro", "ESTADO", "MUNICIPIO", "PARROQUIA", "ASIC",
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
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align
        cell.border = thin_border
    ws.row_dimensions[2].height = 69.75

    data_align = Alignment(horizontal="center", vertical="center")
    data_font = Font(size=11, name="Calibri")
    for row_idx in range(3, 13):
        ws.row_dimensions[row_idx].height = 25.5
        cell_a = ws.cell(row=row_idx, column=1, value=row_idx - 2)
        cell_a.alignment = data_align
        cell_a.font = data_font
        for col_idx in range(2, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.alignment = data_align
            cell.font = data_font
            if col_idx == 11:
                cell.number_format = "@"
        for col_idx in (13, 18):
            ws.cell(row=row_idx, column=col_idx).number_format = "yyyy-mm-dd"

    for row_idx in range(3, 1001):
        ws.cell(row=row_idx, column=10).number_format = r"##\,###\,##0"
        celda_edad = ws.cell(row=row_idx, column=14)
        celda_edad.value = f'=IF(M{row_idx}="","",DATEDIF(M{row_idx},TODAY(),"Y"))'
        celda_edad.number_format = "0"

    col_widths = {
        "A": 8.28515625, "B": 14.5703125, "C": 14.0, "D": 16.85546875,
        "E": 15.7109375, "F": 26.85546875, "G": 45.42578125,
        "H": 25.7109375, "I": 26.7109375, "J": 17.0,
        "K": 17.5703125, "L": 18.140625, "M": 20.7109375,
        "N": 20.7109375, "O": 8.0, "P": 22.85546875,
        "Q": 20.42578125, "R": 23.7109375,
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    ws_listas = wb.create_sheet("_listas")

    def agregar_lista(nombre, columna, opciones, rango, titulo):
        for fila, opcion in enumerate(opciones, start=1):
            ws_listas.cell(row=fila, column=columna, value=opcion)

        letra_columna = get_column_letter(columna)
        referencia = f"'_listas'!${letra_columna}$1:${letra_columna}${len(opciones)}"
        wb.defined_names.add(DefinedName(nombre, attr_text=referencia))

        validacion = DataValidation(type="list", formula1=nombre, allow_blank=True)
        validacion.promptTitle = titulo
        validacion.prompt = "Seleccione una opción válida."
        validacion.add(rango)
        ws.add_data_validation(validacion)

    agregar_lista("ListaEstados", 1, VOCERIA_ESTADO_OPCIONES, "B3:B1000", "Estado")
    agregar_lista("ListaMunicipios", 2, VOCERIA_MUNICIPIO_OPCIONES, "C3:C1000", "Municipio")
    agregar_lista("ListaAsic", 3, VOCERIA_ASIC_OPCIONES, "E3:E1000", "ASIC")
    agregar_lista("ListaCentros", 4, VOCERIA_CENTRO_DISPENSADOR_OPCIONES, "G3:G1000", "Centro dispensador")
    agregar_lista("ListaVocerias", 5, VOCERIA_TIPO_OPCIONES, "L3:L1000", "Vocería")
    agregar_lista("ListaSexo", 6, VOCERIA_SEXO_OPCIONES, "O3:O1000", "Sexo")
    ws_listas.sheet_state = "hidden"

    dv_fecha = DataValidation(
        type="date",
        operator="between",
        formula1="DATE(1900,1,1)",
        formula2="DATE(9999,12,31)",
        allow_blank=True,
    )
    dv_fecha.promptTitle = "Fecha"
    dv_fecha.prompt = "Ingrese una fecha válida. Se mostrará como AAAA-MM-DD."
    dv_fecha.errorTitle = "Fecha no válida"
    dv_fecha.error = "Ingrese un valor de fecha válido."
    dv_fecha.showErrorMessage = True
    dv_fecha.add("M3:M1000")
    dv_fecha.add("R3:R1000")
    ws.add_data_validation(dv_fecha)

    dv_edad = DataValidation(
        type="whole",
        operator="between",
        formula1="18",
        formula2="99",
        allow_blank=True,
    )
    dv_edad.promptTitle = "Edad"
    dv_edad.prompt = "Ingrese una edad entera entre 18 y 99 años."
    dv_edad.errorTitle = "Edad no válida"
    dv_edad.error = "La edad debe ser un número entero entre 18 y 99."
    dv_edad.showErrorMessage = True
    dv_edad.add("N3:N1000")
    ws.add_data_validation(dv_edad)

    dv_ci = DataValidation(
        type="whole",
        operator="between",
        formula1="1000000",
        formula2="99999999",
        allow_blank=True,
    )
    dv_ci.promptTitle = "C.I."
    dv_ci.prompt = "Ingrese entre 7 y 8 dígitos. Se mostrarán comas cada tres dígitos."
    dv_ci.errorTitle = "C.I. no válida"
    dv_ci.error = "La C.I. debe ser un número entero de 7 u 8 dígitos."
    dv_ci.showErrorMessage = True
    dv_ci.add("J3:J1000")
    ws.add_data_validation(dv_ci)

    wb.save(output_path)
    return output_path


TIPOS_ACTIVIDAD_PREDETERMINADOS = [
    ("TIPO-01", "Salud toca tu puerta"),
    ("TIPO-02", "Sesiones educativas"),
    ("TIPO-03", "Los Comités de Salud van a la escuela"),
    ("TIPO-04", "Actividades de Promoción y Prevención Social"),
    ("TIPO-05", "Participación Activa en Jornadas"),
    ("TIPO-06", "Participación Activa en Inmunizaciones"),
    ("TIPO-07", "Entrevista servicio social"),
]
APP_TITLE = "DPPPS — Sistema de Consolidación de Informes"
APP_VERSION = "1.0.0"
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
    """Crea y devuelve una conexión a la base de datos usando el modo actual."""
    params = DATABASE[MODO]
    try:
        conn = mysql.connector.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
            use_pure=True
        )
        return conn
    except mysql.connector.Error as error:
        print(f"[ERROR] No se pudo conectar a la base de datos: {error}")
        raise

import bcrypt
from datetime import date, datetime, timedelta, timezone

class UsuarioDAO:
    def obtener_por_username(self, username):
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

    def obtener_propietario(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuario WHERE rol = 'propietario' AND activo = TRUE ORDER BY id_usuario LIMIT 1"
        )
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return usuario

    def verificar_password(self, password_plano, password_hash):
        return bcrypt.checkpw(
            password_plano.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    def obtener_todos(self):
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

    def crear(self, username=None, password=None, nombre_completo=None, email="", **kwargs):
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

        conn = get_connection()
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

            if nombre or apellido or codigo_verificacion or codigo_verificacion_expira is not None:
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
            conn.commit()
            return cursor.lastrowid
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

    def crear_usuario(self, nombre, apellido, email, password, codigo_verificacion="", codigo_verificacion_expira=None):
        return self.crear(
            username=email.lower().strip(),
            password=password,
            nombre_completo=f"{nombre.strip()} {apellido.strip()}".strip(),
            email=email.lower().strip(),
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            codigo_verificacion=codigo_verificacion,
            codigo_verificacion_expira=codigo_verificacion_expira,
        )

    def guardar_codigo_verificacion(self, email, codigo, expiracion):
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
    try:
        conn = get_connection()
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

class ActividadDAO:
    @staticmethod
    def _parse_fecha(fecha=None):
        if fecha is None:
            raise ValueError("Debe proporcionarse una fecha válida")
        if isinstance(fecha, str):
            fecha = fecha.strip()
            for formato in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(fecha, formato).date()
                except ValueError:
                    continue
            raise ValueError(f"Fecha inválida: {fecha}")
        if isinstance(fecha, (datetime, date)):
            return fecha.date() if isinstance(fecha, datetime) else fecha
        raise ValueError("Debe proporcionarse una fecha válida")

    def obtener_todas(self, filtros=None):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT a.id_actividad, a.id_asic, a.id_tipo, a.id_usuario_registro,
                   a.fecha,
                   a.estado, a.municipio, a.parroquia, a.establecimiento_salud,
                   a.nombre_establecimiento, a.comites_salud,
                   a.tema AS tema,
                   a.cant_medicos,
                   a.cant_promotores_salud,
                   a.cant_voceros_comite_salud,
                   a.cant_vocero_consejo_direccion,
                   a.cant_coordinador_docencia,
                   a.cant_autoridades,
                   a.cant_otros_actores,
                   a.cant_personas_comunidad,
                   a.cant_estudiantes_aspirantes,
                   a.total_participantes,
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
                sql += " AND a.fecha >= %s"
                params.append(filtros["fecha_desde"])
            if filtros.get("fecha_hasta"):
                sql += " AND a.fecha <= %s"
                params.append(filtros["fecha_hasta"])
        sql += " ORDER BY a.fecha DESC, a.id_actividad DESC"
        cursor.execute(sql, tuple(params))
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    def obtener_por_id(self, id_actividad):
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

    def crear(self, id_asic, id_tipo, id_usuario_registro, fecha=None,
               estado="", municipio="", parroquia="", establecimiento_salud="", nombre_establecimiento="",
               comites_salud="", tema="",
               medicos=0, promotores_salud=0, voceros_comite_salud=0, vocero_consejo_direccion=0,
             coordinador_docencia=0, autoridades_presentes=0, otros_actores=0,
             personas_comunidad=0, estudiantes_aspirantes=0, participantes=0, total_participantes=None,
             connection=None):
        fecha_bd = self._parse_fecha(fecha).strftime("%Y-%m-%d")
        owns_connection = connection is None
        conn = connection or get_connection()
        cursor = conn.cursor()
        tema_texto = str(tema).strip() if tema is not None else ""
        sql = """
            INSERT INTO actividad (
                id_asic, id_tipo, id_usuario_registro,
                fecha,
                estado, municipio, parroquia, establecimiento_salud,
                nombre_establecimiento, comites_salud,
                tema,
                cant_medicos, cant_promotores_salud, cant_voceros_comite_salud,
                cant_vocero_consejo_direccion, cant_coordinador_docencia,
                cant_autoridades, cant_otros_actores,
                cant_personas_comunidad, cant_estudiantes_aspirantes,
                total_participantes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql, (
                id_asic, id_tipo, id_usuario_registro,
                fecha_bd,
                estado, municipio, parroquia, establecimiento_salud,
                nombre_establecimiento, comites_salud,
                tema_texto,
                medicos, promotores_salud, voceros_comite_salud,
                vocero_consejo_direccion, coordinador_docencia,
                autoridades_presentes, otros_actores,
                personas_comunidad, estudiantes_aspirantes,
                total_participantes if total_participantes is not None else participantes,
            ))
            nuevo_id = cursor.lastrowid
            if owns_connection:
                conn.commit()
            return nuevo_id
        except Exception:
            if owns_connection:
                conn.rollback()
            raise
        finally:
            cursor.close()
            if owns_connection:
                conn.close()

    def actualizar(self, id_actividad, id_asic, id_tipo, fecha=None,
                  estado="", municipio="", parroquia="", establecimiento_salud="",
                  nombre_establecimiento="", comites_salud="", tema="",
                  medicos=0, promotores_salud=0, voceros_comite_salud=0, vocero_consejo_direccion=0,
                  coordinador_docencia=0, autoridades_presentes=0, otros_actores=0,
                  personas_comunidad=0, estudiantes_aspirantes=0, participantes=0, total_participantes=None):
        fecha_bd = self._parse_fecha(fecha).strftime("%Y-%m-%d")
        conn = get_connection()
        cursor = conn.cursor()
        tema_texto = str(tema).strip() if tema is not None else ""
        sql = """
            UPDATE actividad
            SET id_asic = %s, id_tipo = %s, fecha = %s,
                estado = %s, municipio = %s, parroquia = %s, establecimiento_salud = %s,
                nombre_establecimiento = %s, comites_salud = %s,
                tema = %s,
                cant_medicos = %s, cant_promotores_salud = %s, cant_voceros_comite_salud = %s,
                cant_vocero_consejo_direccion = %s, cant_coordinador_docencia = %s,
                cant_autoridades = %s, cant_otros_actores = %s,
                cant_personas_comunidad = %s, cant_estudiantes_aspirantes = %s,
                total_participantes = %s
            WHERE id_actividad = %s
        """
        cursor.execute(sql, (
            id_asic, id_tipo, fecha_bd,
            estado, municipio, parroquia, establecimiento_salud,
            nombre_establecimiento, comites_salud,
            tema_texto,
            medicos, promotores_salud, voceros_comite_salud,
            vocero_consejo_direccion, coordinador_docencia,
            autoridades_presentes, otros_actores,
            personas_comunidad, estudiantes_aspirantes,
            total_participantes if total_participantes is not None else participantes,
            id_actividad,
        ))
        conn.commit()
        cursor.close()
        conn.close()

    def eliminar(self, id_actividad):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE actividad SET eliminado = TRUE WHERE id_actividad = %s", (id_actividad,))
        conn.commit()
        cursor.close()
        conn.close()
        conn.close()

    def verificar_duplicado(self, id_asic, id_tipo, fecha, tema=None, excluir_id=None):
        """Comprueba si ya existe una actividad con el mismo ASIC, tipo, fecha y tema."""
        tema_normalizado = str(tema).strip() if tema is not None else ""
        desc_normalizada = " ".join(tema_normalizado.lower().split())[:100]
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT id_actividad, tema
            FROM actividad
            WHERE id_asic = %s AND id_tipo = %s AND fecha = %s AND eliminado = FALSE
        """
        params = [id_asic, id_tipo, fecha]
        if excluir_id is not None:
            sql += " AND id_actividad != %s"
            params.append(excluir_id)
        cursor.execute(sql, tuple(params))
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        for registro in resultados:
            reg_desc = " ".join((registro.get("tema") or "").lower().strip().split())[:100]
            if reg_desc == desc_normalizada:
                return True
        return False

class AsicDAO:
    def obtener_todos(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asic ORDER BY nombre")
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista
    def obtener_por_id(self, id_asic):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asic WHERE id_asic = %s", (id_asic,))
        asic = cursor.fetchone()
        cursor.close()
        conn.close()
        return asic
    def obtener_por_codigo(self, codigo):
        codigo = (codigo or "").strip()
        if not codigo:
            return None
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        conn.close()
        cursor.execute("INSERT INTO asic (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id
    def actualizar(self, id_asic, codigo=None, nombre=None, municipio="", parroquia=""):
        nombre = (nombre or codigo or "").strip()
        if not nombre:
            raise ValueError("El nombre del ASIC es obligatorio.")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE asic SET nombre=%s WHERE id_asic=%s", (nombre, id_asic))
        conn.commit()
        cursor.close()
        conn.close()
    def desactivar(self, id_asic):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM asic WHERE id_asic = %s", (id_asic,))
        conn.commit()
        cursor.close()
        conn.close()

class TipoActividadDAO:
    def obtener_todos(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_actividad ORDER BY nombre")
        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista
    def obtener_por_id(self, id_tipo):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_actividad WHERE id_tipo = %s", (id_tipo,))
        tipo = cursor.fetchone()
        cursor.close()
        conn.close()
        return tipo
    def obtener_por_codigo(self, codigo):
        codigo = (codigo or "").strip()
        if not codigo:
            return None
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_actividad WHERE nombre = %s ORDER BY nombre LIMIT 1", (codigo,))
        tipo = cursor.fetchone()
        cursor.close()
        conn.close()
        return tipo
    def crear(self, codigo=None, nombre=None):
        nombre = (nombre or codigo or "").strip()
        if not nombre:
            raise ValueError("El nombre del tipo de actividad es obligatorio.")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tipo_actividad (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id
    def actualizar(self, id_tipo, codigo=None, nombre=None):
        nombre = (nombre or codigo or "").strip()
        if not nombre:
            raise ValueError("El nombre del tipo de actividad es obligatorio.")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tipo_actividad SET nombre=%s WHERE id_tipo=%s", (nombre, id_tipo))
        conn.commit()
        cursor.close()
        conn.close()


class ComiteDAO:
    def obtener_todos(self, filtros=None):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT c.*, a.nombre AS asic_nombre, u.nombre_completo AS usuario_nombre
            FROM comite c
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
            WHERE c.eliminado = FALSE
        """
        params = []
        if filtros:
            if filtros.get("id_asic"):
                sql += " AND c.id_asic = %s"
                params.append(filtros["id_asic"])
        sql += " ORDER BY c.created_at DESC, c.id_comite DESC"
        cursor.execute(sql, tuple(params))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items

    def obtener_por_id(self, id_comite):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comite WHERE id_comite = %s AND eliminado = FALSE", (id_comite,))
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        return item

    def crear(self, id_asic, id_usuario_registro, estado="", municipio="", parroquia="", centro_dispensador="", nombre_centro="", nombre_comite="", connection=None):
        owns_connection = connection is None
        conn = connection or get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO comite (id_asic, id_usuario_registro, estado, municipio, parroquia, centro_dispensador, nombre_centro, nombre_comite)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (id_asic, id_usuario_registro, estado, municipio, parroquia, centro_dispensador, nombre_centro, nombre_comite)
            )
            nuevo_id = cursor.lastrowid
            if owns_connection:
                conn.commit()
            return nuevo_id
        except Exception:
            if owns_connection:
                conn.rollback()
            raise
        finally:
            cursor.close()
            if owns_connection:
                conn.close()

    def actualizar(self, id_comite, id_asic, id_usuario_registro, estado="", municipio="", parroquia="", centro_dispensador="", nombre_centro="", nombre_comite=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE comite
            SET id_asic = %s, id_usuario_registro = %s, estado = %s, municipio = %s, parroquia = %s,
                centro_dispensador = %s, nombre_centro = %s, nombre_comite = %s
            WHERE id_comite = %s
            """,
            (id_asic, id_usuario_registro, estado, municipio, parroquia, centro_dispensador, nombre_centro, nombre_comite, id_comite)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def eliminar(self, id_comite):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE comite SET eliminado = TRUE WHERE id_comite = %s", (id_comite,))
        conn.commit()
        cursor.close()
        conn.close()
        return True


class VoceriaDAO:
    def obtener_todas(self, filtros=None):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT c.id_comite AS id_voceria,
                   c.created_at AS fecha_registro,
                   COUNT(v.id_voceria) AS cantidad_vocerias,
                   c.estado,
                   c.municipio,
                   c.parroquia,
                   c.nombre_comite,
                   c.nombre_centro,
                   c.centro_dispensador,
                   a.nombre AS asic_nombre,
                   u.nombre_completo AS usuario_nombre
            FROM comite c
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
            LEFT JOIN voceria v ON v.id_comite = c.id_comite AND v.eliminado = FALSE
            WHERE c.eliminado = FALSE
        """
        params = []
        if filtros:
            if filtros.get("id_asic"):
                sql += " AND c.id_asic = %s"
                params.append(filtros["id_asic"])
            if filtros.get("id_tipo"):
                sql += " AND EXISTS (SELECT 1 FROM voceria v2 WHERE v2.id_comite = c.id_comite AND v2.id_tipo_voceria = %s AND v2.eliminado = FALSE)"
                params.append(filtros["id_tipo"])
            if filtros.get("nombre_comite"):
                sql += " AND c.nombre_comite LIKE %s"
                params.append(f"%{filtros['nombre_comite']}%")
            if filtros.get("fecha_desde"):
                sql += " AND DATE(c.created_at) >= %s"
                params.append(filtros["fecha_desde"])
            if filtros.get("fecha_hasta"):
                sql += " AND DATE(c.created_at) <= %s"
                params.append(filtros["fecha_hasta"])
        sql += " GROUP BY c.id_comite ORDER BY c.created_at DESC, c.id_comite DESC"
        cursor.execute(sql, tuple(params))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items

    def obtener_por_id(self, id_voceria):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT v.*, c.*, tv.nombre AS tipo_nombre, a.nombre AS asic_nombre, u.nombre_completo AS usuario_nombre
            FROM voceria v
            JOIN comite c ON v.id_comite = c.id_comite
            JOIN tipo_voceria tv ON v.id_tipo_voceria = tv.id_tipo
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
            WHERE v.id_voceria = %s AND v.eliminado = FALSE AND c.eliminado = FALSE
        """
        cursor.execute(sql, (id_voceria,))
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        return item

    def obtener_con_items(self, id_comite):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, a.nombre AS asic_nombre, u.nombre_completo AS usuario_nombre
            FROM comite c
            JOIN asic a ON c.id_asic = a.id_asic
            JOIN usuario u ON c.id_usuario_registro = u.id_usuario
            WHERE c.id_comite = %s AND c.eliminado = FALSE
        """, (id_comite,))
        comite = cursor.fetchone()
        if not comite:
            cursor.close()
            conn.close()
            return None
        
        cursor.execute("""
            SELECT v.*, tv.nombre AS tipo_voceria_nombre
            FROM voceria v
            JOIN tipo_voceria tv ON v.id_tipo_voceria = tv.id_tipo
            WHERE v.id_comite = %s AND v.eliminado = FALSE
        """, (id_comite,))
        voceros = cursor.fetchall()
        cursor.close()
        conn.close()
        
        comite["items"] = voceros
        comite["id_voceria"] = comite["id_comite"]
        tipos_unicos = list(dict.fromkeys(v.get("tipo_voceria_nombre", "") for v in voceros if v.get("tipo_voceria_nombre")))
        comite["tipo_nombre"] = ", ".join(tipos_unicos) if tipos_unicos else ""
        return comite

    def crear(self, id_asic, id_tipo, id_usuario_registro, estado, municipio, parroquia,
              centro_dispensador, nombre_centro, nombre_comite, items, connection=None):
        comite_dao = ComiteDAO()
        owns_connection = connection is None
        conn = connection or get_connection()
        cursor = conn.cursor()
        try:
            id_comite = comite_dao.crear(
                id_asic=id_asic,
                id_usuario_registro=id_usuario_registro,
                estado=estado or "",
                municipio=municipio or "",
                parroquia=parroquia or "",
                centro_dispensador=centro_dispensador or "",
                nombre_centro=nombre_centro or "",
                nombre_comite=nombre_comite or "",
                connection=conn,
            )
            if items:
                sql = """
                    INSERT INTO voceria (id_comite, id_tipo_voceria, nombres, ci, telefono, fecha_nacimiento, edad,
                                         sexo, profesion, correo, fechas_eleccion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                for item in items:
                    cursor.execute(sql, (
                        id_comite,
                        item.get("id_tipo_voceria") or id_tipo,
                        item.get("nombres"),
                        item.get("ci"),
                        item.get("telefono"),
                        item.get("fecha_nacimiento"),
                        item.get("edad"),
                        item.get("sexo"),
                        item.get("profesion"),
                        item.get("correo"),
                        item.get("fechas_eleccion"),
                    ))
            if owns_connection:
                conn.commit()
            return id_comite
        except Exception:
            if owns_connection:
                conn.rollback()
            raise
        finally:
            cursor.close()
            if owns_connection:
                conn.close()

    def actualizar(self, id_voceria, id_asic, id_tipo, estado, municipio, parroquia,
                   centro_dispensador, nombre_centro, nombre_comite, items):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE comite
                SET id_asic = %s, estado = %s, municipio = %s, parroquia = %s,
                    centro_dispensador = %s, nombre_centro = %s, nombre_comite = %s
                WHERE id_comite = %s
                """,
                (id_asic, estado, municipio, parroquia, centro_dispensador, nombre_centro, nombre_comite, id_voceria)
            )
            cursor.execute("UPDATE voceria SET eliminado = TRUE WHERE id_comite = %s", (id_voceria,))
            if items:
                sql = """
                    INSERT INTO voceria (id_comite, id_tipo_voceria, nombres, ci, telefono, fecha_nacimiento, edad,
                                         sexo, profesion, correo, fechas_eleccion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                for item in items:
                    cursor.execute(sql, (
                        id_voceria,
                        item.get("id_tipo_voceria") or id_tipo,
                        item.get("nombres"),
                        item.get("ci"),
                        item.get("telefono"),
                        item.get("fecha_nacimiento"),
                        item.get("edad"),
                        item.get("sexo"),
                        item.get("profesion"),
                        item.get("correo"),
                        item.get("fechas_eleccion"),
                    ))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, id_voceria):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE comite SET eliminado = TRUE WHERE id_comite = %s", (id_voceria,))
            cursor.execute("UPDATE voceria SET eliminado = TRUE WHERE id_comite = %s", (id_voceria,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()


class TipoVoceriaDAO:
    def obtener_todos(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_voceria ORDER BY nombre")
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
        codigo = (codigo or "").strip()
        if not codigo:
            return None
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipo_voceria WHERE nombre = %s ORDER BY nombre LIMIT 1", (codigo,))
        tipo = cursor.fetchone()
        cursor.close()
        conn.close()
        return tipo

    def crear(self, codigo=None, nombre=None):
        nombre = (nombre or codigo or "").strip()
        if not nombre:
            raise ValueError("El nombre del tipo de vocería es obligatorio.")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tipo_voceria (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return nuevo_id

    def actualizar(self, id_tipo, codigo=None, nombre=None):
        nombre = (nombre or codigo or "").strip()
        if not nombre:
            raise ValueError("El nombre del tipo de vocería es obligatorio.")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tipo_voceria SET nombre=%s WHERE id_tipo=%s", (nombre, id_tipo))
        conn.commit()
        cursor.close()
        conn.close()

    def desactivar(self, id_tipo):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tipo_voceria WHERE id_tipo = %s", (id_tipo,))
        conn.commit()
        cursor.close()
        conn.close()

import os
import shutil
import time
import mimetypes

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

    def registrar_usuario(self, nombre, apellido, email, password, username=None,
                          cuenta_administrador=False, password_propietario=None):
        """Crea un usuario nuevo y exige validación por correo."""
        email = (email or "").strip().lower()
        nombre = (nombre or "").strip()
        apellido = (apellido or "").strip()
        username = (username or email).strip()

        if not nombre or not apellido or not email or not password or not username:
            return {"success": False, "message": "Completa todos los campos."}
        if not validar_correo(email) or len(email) > 60:
            return {"success": False, "message": "Ingresa un correo válido."}
        if not 3 <= len(username) <= 50:
            return {"success": False, "message": "El nombre de usuario debe tener entre 3 y 50 caracteres."}
        if any(caracter.isspace() for caracter in username):
            return {"success": False, "message": "El nombre de usuario no puede contener espacios."}
        if len(nombre) < 2 or len(nombre) > 60 or any(caracter.isdigit() for caracter in nombre):
            return {"success": False, "message": "El nombre debe tener entre 2 y 60 caracteres y no contener números."}
        if len(apellido) < 2 or len(apellido) > 60 or any(caracter.isdigit() for caracter in apellido):
            return {"success": False, "message": "El apellido debe tener entre 2 y 60 caracteres y no contener números."}
        if len(f"{nombre} {apellido}") > 120:
            return {"success": False, "message": "El nombre completo no puede superar 120 caracteres."}
        if len(password) < 8:
            return {"success": False, "message": "La contraseña debe tener al menos 8 caracteres."}
        if len(password) > 60:
            return {"success": False, "message": "La contraseña no puede superar 60 caracteres."}
        if len(password.encode("utf-8")) > 72:
            return {"success": False, "message": "La contraseña no puede superar 72 bytes."}
        propietario = self.usuario_dao.obtener_propietario()
        if cuenta_administrador and propietario:
            if not password_propietario or not self.usuario_dao.verificar_password(
                password_propietario, propietario["password_hash"]
            ):
                return {"success": False, "message": "La contraseña del usuario propietario es incorrecta."}
        if self.usuario_dao.obtener_por_email(email):
            return {"success": False, "message": "Este correo ya está registrado."}
        if self.usuario_dao.obtener_por_username(username):
            return {"success": False, "message": "Este nombre de usuario ya está en uso."}

        codigo = self._generar_codigo()
        expiracion = datetime.now() + timedelta(minutes=10)
        try:
            self.usuario_dao.crear(
                username=username,
                password=password,
                nombre_completo=f"{nombre.strip()} {apellido.strip()}".strip(),
                email=email.lower().strip(),
                nombre=nombre.strip(),
                apellido=apellido.strip(),
                codigo_verificacion=codigo,
                codigo_verificacion_expira=expiracion,
                rol="administrador" if cuenta_administrador and propietario else "lector",
                administrador_autorizado=bool(cuenta_administrador and propietario),
            )
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
        codigo_str = str(codigo or "").strip()
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return False
        if len(codigo_str) != 6 or not codigo_str.isdigit():
            return False
        if usuario.get("codigo_verificacion") != codigo_str:
            return False
        expiracion = usuario.get("codigo_verificacion_expira")
        if expiracion is None:
            return False
        if isinstance(expiracion, str):
            try:
                expiracion = datetime.fromisoformat(expiracion.replace("Z", "+00:00"))
            except ValueError:
                return False
        if datetime.now() > expiracion:
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

    def reenviar_codigo_verificacion(self, email):
        """Genera y envía un nuevo código de verificación para una cuenta no verificada."""
        email = (email or "").strip().lower()
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return {"success": False, "message": "No existe una cuenta con ese correo."}

        codigo = self._generar_codigo()
        expiracion = datetime.now() + timedelta(minutes=10)
        self.usuario_dao.guardar_codigo_verificacion(email, codigo, expiracion)
        enviado = self._enviar_codigo_por_email(email, codigo, "verificacion")
        respuesta = {"success": True, "message": "Se envió un nuevo código a tu correo."}
        if not enviado:
            respuesta["message"] = (
                "Se generó un nuevo código, pero no se pudo enviar el correo en este momento. "
                "Intenta nuevamente más tarde."
            )
        return respuesta

    def login(self, credential, password):
        """
        Intenta iniciar sesión con correo o username y password.
        Requiere que el correo haya sido verificado.
        """
        global sesion_actual
        if not isinstance(credential, str) or not isinstance(password, str):
            return False
        if len(credential.strip()) > 60 or len(password) > 60 or len(password.encode("utf-8")) > 72:
            return False
        email = credential.strip().lower()
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
            "email": usuario.get("email"),
            "rol": usuario.get("rol") or "lector",
        }
        return True

    def solicitar_recuperacion(self, email):
        """Genera y envía un código para recuperar la contraseña."""
        email = (email or "").strip().lower()
        if not validar_correo(email):
            return {"success": False, "message": "Ingresa un correo válido."}
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
        codigo = str(codigo or "").strip()
        nueva_password = nueva_password or ""
        if not validar_correo(email):
            return {"success": False, "message": "Ingresa un correo válido."}
        if len(codigo) != 6 or not codigo.isdigit():
            return {"success": False, "message": "El código debe tener exactamente 6 dígitos numéricos."}
        if len(nueva_password) < 8:
            return {"success": False, "message": "La contraseña debe tener al menos 8 caracteres."}
        if len(nueva_password.encode("utf-8")) > 72:
            return {"success": False, "message": "La contraseña no puede superar 72 bytes."}
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

    def puede_escribir(self):
        """Indica si la sesión activa puede modificar información del sistema."""
        return self.usuario_puede_escribir(sesion_actual)

    @staticmethod
    def usuario_puede_escribir(usuario):
        return bool(
            usuario
            and usuario.get("rol", "propietario") in ("propietario", "administrador")
        )

    @staticmethod
    def mensaje_sin_permiso():
        return "Tu rol de lector no permite crear, editar ni eliminar información."
class ActividadController:
    """
    Controlador que maneja las actividades de salud.
    Valida las reglas de negocio antes de llamar al DAO correspondiente.
    """
    def __init__(self):
        self.actividad_dao = ActividadDAO()
        self.asic_dao = AsicDAO()
        self.tipo_dao = TipoActividadDAO()
        self.auth = AuthController()
    def listar_actividades(self, filtros=None):
        """Retorna la lista de actividades registradas, aplicando filtros si los hay."""
        return self.actividad_dao.obtener_todas(filtros)
    def listar_asics(self):
        """Retorna solo los ASIC permitidos por la plantilla del sistema."""
        asics_predeterminados = ASIC_PREDETERMINADOS

        def normalizar(nombre):
            return " ".join((nombre or "").strip().lower().split())

        if self.auth.puede_escribir():
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
        """Asegura los tipos iniciales y retorna todo el catálogo disponible."""
        tipos = self.tipo_dao.obtener_todos()
        if not tipos and self.auth.puede_escribir():
            for _, nombre in TIPOS_ACTIVIDAD_PREDETERMINADOS:
                self.tipo_dao.crear(nombre=nombre)
            tipos = self.tipo_dao.obtener_todos()
        return tipos

    def usuario_es_propietario(self):
        usuario = self.auth.obtener_usuario_actual()
        return bool(usuario and usuario.get("rol") == "propietario")

    def crear_tipo_actividad(self, nombre):
        if not self.usuario_es_propietario():
            return False, "Solo el usuario propietario puede gestionar tipos de actividad."

        nombre = (nombre or "").strip()
        if not nombre:
            return False, "El nombre del tipo de actividad es obligatorio."
        if len(nombre) > 150:
            return False, "El nombre del tipo de actividad no puede superar 150 caracteres."

        clave = " ".join(nombre.casefold().split())
        if any(
            " ".join((tipo["nombre"] or "").strip().casefold().split()) == clave
            for tipo in self.tipo_dao.obtener_todos()
        ):
            return False, "Ya existe un tipo de actividad con ese nombre."

        self.tipo_dao.crear(nombre=nombre)
        return True, "Tipo de actividad agregado exitosamente."

    def actualizar_tipo_actividad(self, id_tipo, nombre):
        if not self.usuario_es_propietario():
            return False, "Solo el usuario propietario puede gestionar tipos de actividad."

        nombre = (nombre or "").strip()
        if not nombre:
            return False, "El nombre del tipo de actividad es obligatorio."
        if len(nombre) > 150:
            return False, "El nombre del tipo de actividad no puede superar 150 caracteres."

        try:
            id_tipo = int(id_tipo)
        except (TypeError, ValueError):
            return False, "El tipo de actividad seleccionado no es válido."

        tipos = self.tipo_dao.obtener_todos()
        tipo_actual = next((tipo for tipo in tipos if tipo["id_tipo"] == id_tipo), None)
        if tipo_actual is None:
            return False, "El tipo de actividad seleccionado ya no existe."

        clave = " ".join(nombre.casefold().split())
        if any(
            tipo["id_tipo"] != id_tipo
            and " ".join((tipo["nombre"] or "").strip().casefold().split()) == clave
            for tipo in tipos
        ):
            return False, "Ya existe un tipo de actividad con ese nombre."

        self.tipo_dao.actualizar(id_tipo, nombre=nombre)
        return True, "Tipo de actividad actualizado exitosamente."
    def guardar_actividad(self, id_asic, id_tipo, fecha=None, estado=None, municipio=None, parroquia=None,
                           establecimiento_salud=None, nombre_establecimiento=None, comites_salud=None,
                           tema="", medicos=0, promotores_salud=0, voceros_comite_salud=0,
                           vocero_consejo_direccion=0, coordinador_docencia=0, autoridades_presentes=0,
                           otros_actores=0, personas_comunidad=0, estudiantes_aspirantes=0,
                           participantes=0, id_actividad=None, **kwargs):
        """Registra o actualiza una actividad con una sola fecha."""
        if fecha is None or not str(fecha).strip():
            return False, "La fecha es obligatoria."

        if not id_asic:
            return False, "Debes seleccionar un ASIC."
        if not id_tipo:
            return False, "Debes seleccionar un tipo de actividad."

        for campo, valor in [
            ("Estado", estado), ("Municipio", municipio), ("Parroquia", parroquia),
            ("Establecimiento de Salud", establecimiento_salud),
            ("Nombre del Establecimiento", nombre_establecimiento),
        ]:
            if valor is None or not str(valor).strip():
                return False, f"El campo {campo} es obligatorio."
        limites_texto = [
            ("Estado", estado, 100), ("Municipio", municipio, 100),
            ("Parroquia", parroquia, 100), ("Establecimiento de Salud", establecimiento_salud, 150),
            ("Nombre del Establecimiento", nombre_establecimiento, 200),
        ]
        for campo, valor, maximo in limites_texto:
            texto = str(valor).strip()
            if len(texto) > maximo or any(ord(caracter) < 32 for caracter in texto):
                return False, f"El campo {campo} no puede superar {maximo} caracteres ni contener controles."
        if estado != "Táchira":
            return False, "Debes seleccionar un estado válido."
        if municipio not in MUNICIPIOS_TACHIRA:
            return False, "Debes seleccionar un municipio válido."
        if establecimiento_salud not in ACTIVIDAD_ESTABLECIMIENTO_OPCIONES:
            return False, "Debes seleccionar un establecimiento de salud válido."

        comites_texto = str(comites_salud).strip() if comites_salud is not None else ""
        if not comites_texto:
            return False, "El campo Comités de Salud es obligatorio."
        if not comites_texto.isdigit() or len(comites_texto) > 2:
            return False, "Comités de Salud debe contener solo números y tener máximo 2 dígitos."
        comites_valor = int(comites_texto)

        tema_texto = str(tema or "").strip()
        if not tema_texto:
            return False, "El tema tratado de la actividad es obligatorio."
        if len(tema_texto) > 150:
            return False, "El tema tratado no puede superar los 150 caracteres."

        if participantes is None or not str(participantes).strip():
            return False, "El total de asistencia es obligatorio."

        try:
            if isinstance(participantes, bool) or (
                isinstance(participantes, float) and not participantes.is_integer()
            ) or (isinstance(participantes, str) and not participantes.strip().isdigit()):
                raise ValueError()
            cant_participantes = int(participantes)
            if not 0 <= cant_participantes <= 899991:
                return False, "La cantidad de participantes debe estar entre 0 y 899991."
        except (ValueError, TypeError):
            return False, "La cantidad de participantes debe ser un numero entero valido."

        for campo, valor in [
            ("Médicos", medicos), ("Promotores en Salud", promotores_salud),
            ("Voceros Comité Salud", voceros_comite_salud),
            ("Vocero Consejo Dir. ASIC", vocero_consejo_direccion),
            ("Coordinador Docencia ASIC", coordinador_docencia),
            ("Autoridades Presentes", autoridades_presentes),
            ("Otros Actores", otros_actores),
            ("Personas Comunidad", personas_comunidad),
            ("Estudiantes Aspirantes", estudiantes_aspirantes)
        ]:
            if valor is None or not str(valor).strip():
                return False, f"El campo {campo} es obligatorio."
            try:
                if isinstance(valor, bool) or (
                    isinstance(valor, float) and not valor.is_integer()
                ) or (isinstance(valor, str) and not valor.strip().isdigit()):
                    raise ValueError()
                v = int(valor)
                if not 0 <= v <= 99999:
                    return False, f"El campo {campo} debe estar entre 0 y 99999."
            except (ValueError, TypeError):
                return False, f"El campo {campo} debe ser un numero entero valido."

        total_categorias = sum(int(valor) for valor in (
            medicos, promotores_salud, voceros_comite_salud, vocero_consejo_direccion,
            coordinador_docencia, autoridades_presentes, otros_actores,
            personas_comunidad, estudiantes_aspirantes,
        ))
        if total_categorias != cant_participantes:
            return False, "El total de asistencia debe coincidir con la suma de las categorías."

        try:
            fecha_obj = ActividadDAO._parse_fecha(fecha)
            fecha_bd = fecha_obj.strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            return False, "El formato de la fecha es inválido."
        if fecha_obj > date.today():
            return False, "La fecha de la actividad no puede ser futura."

        es_duplicado = self.actividad_dao.verificar_duplicado(
            id_asic=id_asic,
            id_tipo=id_tipo,
            fecha=fecha_bd,
            tema=tema_texto,
            excluir_id=id_actividad,
        )
        if es_duplicado:
            return False, "Ya existe una actividad registrada para este ASIC, tipo, fecha y tema similares."

        usuario = self.auth.obtener_usuario_actual()
        if not usuario:
            return False, "No hay una sesion de usuario activa."
        if not self.auth.usuario_puede_escribir(usuario):
            return False, self.auth.mensaje_sin_permiso()
        id_usuario = usuario["id_usuario"]

        argumentos_actividad = dict(
            id_asic=id_asic,
            id_tipo=id_tipo,
            id_usuario_registro=id_usuario,
            fecha=fecha_bd,
            estado=str(estado).strip(),
            municipio=str(municipio).strip(),
            parroquia=str(parroquia).strip(),
            establecimiento_salud=str(establecimiento_salud).strip(),
            nombre_establecimiento=str(nombre_establecimiento).strip(),
            comites_salud=comites_valor,
            tema=tema_texto,
            medicos=int(medicos) if medicos else 0,
            promotores_salud=int(promotores_salud) if promotores_salud else 0,
            voceros_comite_salud=int(voceros_comite_salud) if voceros_comite_salud else 0,
            vocero_consejo_direccion=int(vocero_consejo_direccion) if vocero_consejo_direccion else 0,
            coordinador_docencia=int(coordinador_docencia) if coordinador_docencia else 0,
            autoridades_presentes=int(autoridades_presentes) if autoridades_presentes else 0,
            otros_actores=int(otros_actores) if otros_actores else 0,
            personas_comunidad=int(personas_comunidad) if personas_comunidad else 0,
            estudiantes_aspirantes=int(estudiantes_aspirantes) if estudiantes_aspirantes else 0,
            participantes=cant_participantes,
            total_participantes=cant_participantes,
        )

        if id_actividad is None:
            self.actividad_dao.crear(**argumentos_actividad)
            return True, "Actividad registrada exitosamente."

        argumentos_actualizar = {k: v for k, v in argumentos_actividad.items() if k != "id_usuario_registro"}
        argumentos_actualizar["id_actividad"] = id_actividad
        self.actividad_dao.actualizar(**argumentos_actualizar)
        return True, "Actividad actualizada exitosamente."

    def eliminar_actividad(self, id_actividad):
        """Elimina de forma lógica una actividad."""
        usuario = self.auth.obtener_usuario_actual()
        if not self.auth.usuario_puede_escribir(usuario):
            return False, self.auth.mensaje_sin_permiso()
        self.actividad_dao.eliminar(id_actividad)
        return True, "Actividad eliminada correctamente."


class VoceriaController:
    """Maneja la lógica de negocio para vocerías CS."""
    def __init__(self):
        self.voceria_dao = VoceriaDAO()
        self.tipo_voceria_dao = TipoVoceriaDAO()
        self.asic_dao = AsicDAO()
        self.auth = AuthController()

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

    def guardar_voceria(self, id_asic, id_tipo=None, estado=None, municipio=None, parroquia=None,
                         centro_dispensador=None, nombre_centro=None, nombre_comite=None, items=None, id_voceria=None,
                         connection=None):
        """
        Guarda vocería con sus items (voceros).
        items: lista de dicts con los campos de cada vocero
        centro_dispensador, nombre_centro, nombre_comite: campos generales que aplican a toda la vocería
        """
        if items is None:
            items = []

        estado = str(estado or "").strip()
        municipio = str(municipio or "").strip()
        parroquia = str(parroquia or "").strip()
        centro_dispensador = str(centro_dispensador or "").strip()
        nombre_centro = str(nombre_centro or "").strip()
        nombre_comite = str(nombre_comite or "").strip()

        if not id_asic:
            return False, "Debes seleccionar un ASIC."
        campos_generales = [
            ("Estado", estado, 100), ("Municipio", municipio, 100),
            ("Parroquia", parroquia, 100), ("Centro dispensador", centro_dispensador, 100),
            ("Nombre del centro", nombre_centro, 200), ("Nombre del comité", nombre_comite, 200),
        ]
        for etiqueta, valor, maximo in campos_generales:
            texto = str(valor or "").strip()
            if not texto or texto == "Parroquia":
                return False, f"{etiqueta} es obligatorio."
            if len(texto) > maximo or any(ord(caracter) < 32 for caracter in texto):
                return False, f"{etiqueta} no puede superar {maximo} caracteres ni contener controles."
        if estado not in VOCERIA_ESTADO_OPCIONES:
            return False, "Debes seleccionar un estado válido."
        if municipio not in MUNICIPIOS_TACHIRA:
            return False, "Debes seleccionar un municipio válido."
        if centro_dispensador not in VOCERIA_CENTRO_DISPENSADOR_OPCIONES:
            return False, "Debes seleccionar un centro dispensador válido."
        if not items:
            return False, "Debe agregar al menos 7 vocerías (máx. 10)."
        if len(items) < 7:
            return False, f"Debe agregar al menos 7 vocerías (actual: {len(items)})."
        if len(items) > 10:
            return False, f"Máximo 10 vocerías permitidas (actual: {len(items)})."

        tipos_voceria = self.tipo_voceria_dao.obtener_todos()
        tipos_validos = {int(tipo["id_tipo"]) for tipo in tipos_voceria}
        if not id_tipo and tipos_voceria:
            id_tipo = tipos_voceria[0]["id_tipo"]
        try:
            id_tipo = int(id_tipo)
        except (TypeError, ValueError):
            return False, "Debes seleccionar un tipo de vocería."
        if id_tipo not in tipos_validos:
            return False, "Debes seleccionar un tipo de vocería válido."

        # Validar TODOS los campos en cada item (sin centro_dispensador, nombre_centro, nombre_comite que ahora son generales)
        for idx, item in enumerate(items, start=1):
            nombres = str(item.get("nombres") or "").strip()
            if not nombres:
                return False, f"Vocería #{idx}: Nombres y Apellidos son obligatorios."
            if not 5 <= len(nombres) <= 40:
                return False, f"Vocería #{idx}: Nombres y Apellidos debe tener entre 5 y 40 caracteres."
            if any(caracter.isdigit() or ord(caracter) < 32 for caracter in nombres):
                return False, f"Vocería #{idx}: Nombres y Apellidos no puede contener números ni controles."
            if not item.get("ci") or not str(item.get("ci")).strip():
                return False, f"Vocería #{idx}: C.I. es obligatoria."
            ci = str(item.get("ci")).strip()
            ci_digitos = ci.replace(",", "")
            formato_ci_valido = bool(re.fullmatch(r"(?:\d{7,8}|\d{1,2}(?:,\d{3}){2})", ci))
            if not formato_ci_valido or not 7 <= len(ci_digitos) <= 8:
                return False, f"Vocería #{idx}: La C.I. debe tener entre 7 y 8 dígitos."
            telefono = str(item.get("telefono") or "").strip()
            if not telefono:
                return False, f"Vocería #{idx}: Teléfono es obligatorio."
            if not telefono.isdigit() or not 11 <= len(telefono) <= 12:
                return False, f"Vocería #{idx}: El teléfono debe tener entre 11 y 12 dígitos."
            fecha_nacimiento = self._parsear_fecha(item.get("fecha_nacimiento"))
            if not fecha_nacimiento:
                return False, f"Vocería #{idx}: Fecha de Nacimiento es obligatoria."
            hoy = date.today()
            edad_por_fecha = hoy.year - fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
            )
            if not 18 <= edad_por_fecha <= 99:
                return False, f"Vocería #{idx}: La persona debe tener entre 18 y 99 años según su fecha de nacimiento."
            edad = str(item.get("edad") or "").strip()
            if not edad:
                return False, f"Vocería #{idx}: Edad es obligatoria."
            if not edad.isdigit() or len(edad) > 2 or not 18 <= int(edad) <= 99:
                return False, f"Vocería #{idx}: La edad debe estar entre 18 y 99 años."
            if int(edad) != edad_por_fecha:
                return False, f"Vocería #{idx}: La edad no coincide con la fecha de nacimiento."
            try:
                id_tipo_item = int(item.get("id_tipo_voceria"))
            except (TypeError, ValueError):
                id_tipo_item = None
            if id_tipo_item not in tipos_validos:
                return False, f"Vocería #{idx}: Debe seleccionar una vocería."
            if item.get("sexo") not in ("M", "F"):
                return False, f"Vocería #{idx}: Debe seleccionar un sexo válido."
            profesion = str(item.get("profesion") or "").strip()
            if not profesion:
                return False, f"Vocería #{idx}: Profesión/Oficio es obligatoria."
            if not 3 <= len(profesion) <= 40:
                return False, f"Vocería #{idx}: Profesión/Oficio debe tener entre 3 y 40 caracteres."
            correo = str(item.get("correo") or "").strip()
            if not correo:
                return False, f"Vocería #{idx}: Correo electrónico es obligatorio."
            if not validar_correo(correo):
                return False, f"Vocería #{idx}: Correo electrónico no válido."
            if not item.get("fechas_eleccion") or not str(item.get("fechas_eleccion")).strip() or str(item.get("fechas_eleccion")).strip() == "AAAA-MM-DD":
                return False, f"Vocería #{idx}: Fechas de Elección es obligatoria."
            fecha_eleccion = self._parsear_fecha(item.get("fechas_eleccion"))
            if not fecha_eleccion:
                return False, f"Vocería #{idx}: La fecha de elección no es válida."
            if fecha_eleccion > date.today():
                return False, f"Vocería #{idx}: La fecha de elección no puede ser futura."
            hace_dos_anos = date.today() - timedelta(days=730)
            if fecha_eleccion < hace_dos_anos:
                return False, f"Vocería #{idx}: La fecha de elección ({item.get('fechas_eleccion')}) tiene más de 2 años de antigüedad."

        id_usuario = self.auth.obtener_usuario_actual()
        if not id_usuario:
            return False, "No hay una sesion de usuario activa."
        if not self.auth.usuario_puede_escribir(id_usuario):
            return False, self.auth.mensaje_sin_permiso()
        id_usuario_registro = id_usuario["id_usuario"]

        try:
            if id_voceria is None:
                self.voceria_dao.crear(id_asic, id_tipo, id_usuario_registro, estado, municipio, parroquia,
                                       centro_dispensador, nombre_centro, nombre_comite, items, connection=connection)
                return True, "Vocería registrada correctamente."
            else:
                self.voceria_dao.actualizar(id_voceria, id_asic, id_tipo, estado, municipio, parroquia,
                                            centro_dispensador, nombre_centro, nombre_comite, items)
                return True, "Vocería actualizada correctamente."
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"

    def eliminar_voceria(self, id_comite):
        """Elimina un comité y sus vocerías asociadas (soft delete)."""
        usuario = self.auth.obtener_usuario_actual()
        if not self.auth.usuario_puede_escribir(usuario):
            return False, self.auth.mensaje_sin_permiso()
        self.voceria_dao.eliminar(id_comite)
        return True, "Vocería eliminada correctamente."


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

_AZUL_OSCURO = colors.HexColor("#0f3460")
_AZUL_MEDIO = colors.HexColor("#16213e")
_ROJO_ACENTO = colors.HexColor("#e94560")
_VERDE = colors.HexColor("#05c46b")
_GRIS_CLARO = colors.HexColor("#f4f6f8")
_GRIS_BORDE = colors.HexColor("#cccccc")
_BLANCO = colors.white
_NEGRO = colors.black


class ConsolidacionService:
    def __init__(self, id_usuario: int):
        self.id_usuario = id_usuario
        self._actividad_dao = ActividadDAO()
        self._asic_dao = AsicDAO()
        self._voceria_dao = VoceriaDAO()

    def generar_previo(self, fecha_inicio, fecha_fin, id_asic=None) -> dict:
        actividades = self._obtener_actividades(fecha_inicio, fecha_fin, id_asic)
        total_act = len(actividades)
        total_part = sum(a["total_participantes"] for a in actividades)
        resumen_tipo = self._agrupar(actividades, "tipo_nombre")
        resumen_asic = self._agrupar(actividades, "asic_nombre")

        vocerias = self._obtener_vocerias(fecha_inicio, fecha_fin, id_asic)

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
            "actividades": actividades,
            "resumen_por_tipo": resumen_tipo,
            "resumen_por_asic": resumen_asic,
            "total_actividades": total_act,
            "total_participantes": total_part,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "id_asic": id_asic,
            "asic_nombre": asic_nombre,
            "vocerias": vocerias,
        }

    def _obtener_actividades(self, fecha_inicio, fecha_fin, id_asic) -> list:
        filtros_base = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        if not id_asic:
            return self._actividad_dao.obtener_todas(filtros_base)

        ids = id_asic if isinstance(id_asic, list) else [id_asic]
        if len(ids) == 1:
            filtros = dict(filtros_base)
            filtros["id_asic"] = ids[0]
            return self._actividad_dao.obtener_todas(filtros)

        vistas = {}
        for aid in ids:
            filtros = dict(filtros_base)
            filtros["id_asic"] = aid
            for act in self._actividad_dao.obtener_todas(filtros):
                vistas[act["id_actividad"]] = act
        return sorted(vistas.values(), key=lambda a: (str(a.get("fecha", "")), a["id_actividad"]), reverse=True)

    def _obtener_vocerias(self, fecha_inicio, fecha_fin, id_asic) -> list:
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

        vistas = {}
        for aid in ids:
            filtros = dict(filtros_base)
            filtros["id_asic"] = aid
            for voc in self._voceria_dao.obtener_todas(filtros):
                vistas[voc["id_voceria"]] = voc
        return sorted(vistas.values(), key=lambda v: (str(v.get("fecha_registro", "")), v["id_voceria"]), reverse=True)

    @staticmethod
    def _agrupar(actividades: list, campo_grupo: str) -> list:
        grupos = {}
        for act in actividades:
            clave = act.get(campo_grupo) or "Sin clasificar"
            if clave not in grupos:
                grupos[clave] = {"nombre": clave, "total_actividades": 0, "total_participantes": 0}
            grupos[clave]["total_actividades"] += 1
            grupos[clave]["total_participantes"] += act.get("total_participantes", 0)
        return sorted(grupos.values(), key=lambda x: x["nombre"])
# Columnas requeridas en el Excel de importación
# El esquema final usa `fecha` y `tema`; se aceptan sinónimos heredados para compatibilidad.
COLUMNAS_REQUERIDAS = [
    "asic", "tipo_actividad", "fecha", "tema",
    "participantes",
]
HEADER_ALIASES = {
    # Fecha
    "fecha": "fecha",
    "fecha inicio": "fecha",
    "fecha inicio yyyy mm dd": "fecha",
    "fecha fin": "fecha",
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
    "cantidad de comites de salud": "comites_de_salud",
    "cantidad de comités de salud": "comites_de_salud",
    "cantidad de comites de salud 0 99": "comites_de_salud",
    "ubicación": "ubicacion",
    "ubicacion": "ubicacion",
    # Tipo de actividad
    "actividad desarrollada": "tipo_actividad",
    "actividad": "tipo_actividad",
    "tipo de actividad": "tipo_actividad",
    "tipo actividad": "tipo_actividad",
    "tipo de actividad nombre exacto": "tipo_actividad",
    "asic nombre exacto": "asic",
    # Tema
    "tema tratado": "tema",
    "tema": "tema",
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

    def _validar_campos_fila(self, fila, idx, fecha, tema, comites_salud, participantes):
        errores = []
        valores_obligatorios = {
            "ESTADO": self._obtener_valor_columna(fila, idx, "estado"),
            "MUNICIPIO": self._obtener_valor_columna(fila, idx, "municipio"),
            "PARROQUIA": self._obtener_valor_columna(fila, idx, "parroquia"),
            "ESTABLECIMIENTO DE SALUD": self._obtener_valor_columna(fila, idx, "establecimiento_salud"),
            "NOMBRE DEL ESTABLECIMIENTO": self._obtener_valor_columna(fila, idx, "nombre_establecimiento_salud"),
        }
        for campo, valor in valores_obligatorios.items():
            if valor is None or not str(valor).strip():
                errores.append(f"El campo '{campo}' está vacío.")
        limites_texto = {
            "ESTADO": (valores_obligatorios["ESTADO"], 100),
            "MUNICIPIO": (valores_obligatorios["MUNICIPIO"], 100),
            "PARROQUIA": (valores_obligatorios["PARROQUIA"], 100),
            "ESTABLECIMIENTO DE SALUD": (valores_obligatorios["ESTABLECIMIENTO DE SALUD"], 150),
            "NOMBRE DEL ESTABLECIMIENTO": (valores_obligatorios["NOMBRE DEL ESTABLECIMIENTO"], 200),
        }
        for campo, (valor, maximo) in limites_texto.items():
            texto = str(valor or "").strip()
            if len(texto) > maximo or any(ord(caracter) < 32 for caracter in texto):
                errores.append(f"'{campo}' supera {maximo} caracteres o contiene controles.")
        estado = str(valores_obligatorios["ESTADO"] or "").strip()
        municipio = str(valores_obligatorios["MUNICIPIO"] or "").strip()
        establecimiento = str(valores_obligatorios["ESTABLECIMIENTO DE SALUD"] or "").strip()
        if estado and estado != "Táchira":
            errores.append("'ESTADO' no es válido.")
        if municipio and municipio not in MUNICIPIOS_TACHIRA:
            errores.append("'MUNICIPIO' no es válido.")
        if establecimiento and establecimiento not in ACTIVIDAD_ESTABLECIMIENTO_OPCIONES:
            errores.append("'ESTABLECIMIENTO DE SALUD' no es válido.")

        if fecha is None:
            errores.append("'FECHA' no tiene formato de fecha válido (YYYY-MM-DD o DD/MM/YYYY).")
        elif fecha > date.today():
            errores.append("'FECHA' no puede ser futura.")

        if not tema:
            errores.append("El campo 'TEMA TRATADO' está vacío.")
        elif len(tema) > 150:
            errores.append("'TEMA TRATADO' no puede superar los 150 caracteres.")

        if comites_salud is None or not 0 <= comites_salud <= 99:
            errores.append(
                "'CANTIDAD DE COMITÉS DE SALUD' debe ser un número entero entre 0 y 99; "
                "ingrese la cantidad, no el nombre del comité."
            )

        participantes_por_categoria = []
        for campo in PARTICIPANTES_CATEGORIAS:
            valor = self._obtener_valor_columna(fila, idx, campo)
            if valor is None or not str(valor).strip():
                participantes_por_categoria.append(0)
                continue
            cantidad = self._parse_int(valor)
            if cantidad is None or not 0 <= cantidad <= 99999:
                errores.append(
                    f"'{campo.replace('_', ' ').upper()}' debe ser un número entero entre 0 y 99999."
                )
                participantes_por_categoria.append(0)
                continue
            participantes_por_categoria.append(cantidad)

        hay_desglose = any(
            valor is not None and str(valor).strip() != ""
            for campo in PARTICIPANTES_CATEGORIAS
            for valor in [self._obtener_valor_columna(fila, idx, campo)]
        )
        if hay_desglose and participantes is not None and sum(participantes_por_categoria) != participantes:
            errores.append("'TOTAL DE ASISTENCIA' debe coincidir con la suma de las categorías de participantes.")

        return errores

    def previsualizar(self, ruta_archivo: str) -> dict:
        """
        Lee el Excel y valida cada fila SIN insertar en BD.
        Retorna: {columnas, filas_validas, filas_error, total_filas}
        """
        validar_archivo_excel(ruta_archivo)
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
            tema = str(datos_crudos.get("tema") or "").strip()
            comites_salud = self._parse_int(self._obtener_valor_columna(fila, idx, "comites_de_salud"))
            try:
                participantes = self._calcular_total_asistencia(fila, idx, datos_crudos)
                if participantes is None or not 0 <= participantes <= 899991:
                    raise ValueError()
            except (TypeError, ValueError):
                participantes = None
                errores.append("'TOTAL DE ASISTENCIA' debe ser un entero entre 0 y 899991.")
            fecha_actividad = self._parsear_fecha(datos_crudos.get("fecha"))
            errores.extend(self._validar_campos_fila(
                fila, idx, fecha_actividad, tema, comites_salud, participantes,
            ))
            if not asic_nombre:
                errores.append("El campo 'ASIC' está vacío.")
            if not tipo_nombre:
                errores.append("El campo 'ACTIVIDAD DESARROLLADA' está vacío.")
            id_asic = None
            id_tipo = None
            if asic_nombre:
                id_asic = self._resolver_asic(asic_nombre)
                if id_asic is None:
                    errores.append(f"ASIC no encontrado en BD: «{asic_nombre}».")
            if tipo_nombre:
                id_tipo = self._resolver_tipo(tipo_nombre)
                if id_tipo is None:
                    errores.append(f"Tipo de actividad no encontrado en BD: «{tipo_nombre}»." )
            if id_asic and id_tipo and fecha_actividad and tema and not errores:
                es_duplicado = self._actividad_dao.verificar_duplicado(
                    id_asic, id_tipo, fecha_actividad, tema=tema
                )
                if es_duplicado:
                    errores.append("Duplicado: ya existe una actividad con el mismo ASIC, tipo, fecha y tema.")
            fila_procesada = {
                "numero_fila": numero_fila,
                "id_asic": id_asic,
                "id_tipo": id_tipo,
                "fecha": fecha_actividad,
                "estado": self._obtener_valor_columna(fila, idx, "estado"),
                "municipio": self._obtener_valor_columna(fila, idx, "municipio"),
                "parroquia": self._obtener_valor_columna(fila, idx, "parroquia"),
                "establecimiento_salud": self._obtener_valor_columna(fila, idx, "establecimiento_salud"),
                "nombre_establecimiento": self._obtener_valor_columna(fila, idx, "nombre_establecimiento_salud"),
                "comites_salud": comites_salud,
                "tema": tema,
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
        Inserta en BD todas las filas ya validadas dentro de una única transacción.
        Retorna: {insertadas, errores_al_insertar}
        """
        auth = AuthController()
        usuario = auth.obtener_usuario_actual()
        if not auth.usuario_puede_escribir(usuario):
            raise PermissionError(auth.mensaje_sin_permiso())
        if not filas_validas:
            return {"insertadas": 0, "errores_al_insertar": []}

        conn = get_connection()
        fila_actual = None
        try:
            for fila in filas_validas:
                fila_actual = fila
                self._actividad_dao.crear(
                    id_asic=fila["id_asic"],
                    id_tipo=fila["id_tipo"],
                    id_usuario_registro=self.id_usuario_registro,
                    fecha=fila.get("fecha"),
                    estado=fila.get("estado") or "",
                    municipio=fila.get("municipio") or "",
                    parroquia=fila.get("parroquia") or "",
                    establecimiento_salud=fila.get("establecimiento_salud") or "",
                    nombre_establecimiento=fila.get("nombre_establecimiento") or "",
                    comites_salud=fila.get("comites_salud"),
                    tema=fila.get("tema") or "",
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
                    connection=conn,
                )
            conn.commit()
            return {"insertadas": len(filas_validas), "errores_al_insertar": []}
        except Exception as exc:
            conn.rollback()
            return {
                "insertadas": 0,
                "errores_al_insertar": [{
                    "numero_fila": fila_actual.get("numero_fila") if fila_actual else "-",
                    "error": str(exc),
                }],
            }
        finally:
            conn.close()
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


class ExcelServiceVoceria:
    """
    Servicio encargado de leer un archivo Excel de vocerías y convertir sus filas
    en registros, con validación detallada por comité.
    """
    # Encabezados esperados en la plantilla (fila 2)
    VOCERIA_HEADERS = [
        "nro",
        "estado",
        "municipio",
        "parroquia",
        "asic",
        "nombre_comite",
        "centro_dispensador",
        "nombre_centro",
        "nombres",
        "ci",
        "telefono",
        "voceria",
        "fecha_nacimiento",
        "edad",
        "sexo",
        "profesion",
        "correo",
        "fechas_eleccion",
    ]

    HEADER_ALIASES_VOCERIA = {
        "nro": "nro",
        "n": "nro",
        "numero": "nro",
        "estado": "estado",
        "municipio": "municipio",
        "parroquia": "parroquia",
        "asic": "asic",
        "nombre del comite": "nombre_comite",
        "nombre del comité": "nombre_comite",
        "indique que centro dispensador de salud es sri hospital cat cdi clinica popular consultorio medico popular ambulatorio u otro": "centro_dispensador",
        "indique que centro dispensador de salud es": "centro_dispensador",
        "centro dispensador": "centro_dispensador",
        "nombre del centro dispensador de salud": "nombre_centro",
        "nombre del centro": "nombre_centro",
        "nombres y apellido": "nombres",
        "nombres": "nombres",
        "c i": "ci",
        "c.i.": "ci",
        "ci": "ci",
        "telefono": "telefono",
        "teléfono": "telefono",
        "voceria": "voceria",
        "vocería": "voceria",
        "fecha de nacimiento": "fecha_nacimiento",
        "edad": "edad",
        "sexo": "sexo",
        "profesion oficio": "profesion",
        "profesion/oficio": "profesion",
        "profesion": "profesion",
        "profesión": "profesion",
        "correo": "correo",
        "fechas de eleccion": "fechas_eleccion",
        "fechas de elección": "fechas_eleccion",
        "fecha de eleccion": "fechas_eleccion",
        "fecha de elección": "fechas_eleccion",
    }

    CAMPOS_OBLIGATORIOS = [
        "estado", "municipio", "parroquia", "asic", "nombre_comite",
        "centro_dispensador", "nombre_centro", "nombres", "ci",
        "telefono", "voceria", "fecha_nacimiento", "edad",
        "sexo", "profesion", "correo", "fechas_eleccion"
    ]

    def __init__(self, id_usuario_registro: int):
        self.id_usuario_registro = id_usuario_registro
        self._asic_dao = AsicDAO()
        self._tipo_voceria_dao = TipoVoceriaDAO()
        self._cache_asic: dict = {}
        self._cache_tipo_voceria: dict = {}

    def previsualizar(self, ruta_archivo: str) -> dict:
        """
        Lee el Excel y valida cada fila SIN insertar en BD.
        Agrupa por 'nombre_comite' y valida reglas de negocio.
        Retorna: {columnas, comites_validos, comites_error, total_filas, total_comites}
        """
        import openpyxl
        from datetime import date, datetime, timedelta

        validar_archivo_excel(ruta_archivo)
        wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
        ws = wb.active

        # Try row 2 first (standard template)
        raw_header_row = next(ws.iter_rows(min_row=2, max_row=2, values_only=True))
        cabecera_raw = [str(c).strip() if c is not None else "" for c in raw_header_row]
        cabecera_normalizada = [self._normalizar_encabezado(c) for c in cabecera_raw]
        idx = {cab: i for i, cab in enumerate(cabecera_normalizada) if cab}

        # Fallback: if row 2 doesn't have valid headers, try row 1
        # (handles cases where template was modified)
        claves_esperadas = {"estado", "municipio", "parroquia", "asic", "nombre_comite",
                           "centro_dispensador", "nombre_centro", "nombres", "ci",
                           "telefono", "voceria", "fecha_nacimiento", "edad",
                           "sexo", "profesion", "correo", "fechas_eleccion"}
        if not claves_esperadas.intersection(idx.keys()):
            raw_header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            cabecera_raw = [str(c).strip() if c is not None else "" for c in raw_header_row]
            cabecera_normalizada = [self._normalizar_encabezado(c) for c in cabecera_raw]
            idx = {cab: i for i, cab in enumerate(cabecera_normalizada) if cab}
            data_start = 2
        else:
            data_start = 3

        if not idx:
            raise ValueError("No se detectaron encabezados válidos en el archivo.")

        filas_por_comite: dict = {}
        errores_globales = []

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=data_start, values_only=True), start=data_start):
            if all(v is None or str(v).strip() == "" for v in fila):
                continue

            datos_crudos = self._extraer_datos_fila(fila, idx, cabecera_raw)
            errores_fila = self._validar_fila(datos_crudos, numero_fila)

            nombre_comite = (datos_crudos.get("nombre_comite") or "").strip()
            if not nombre_comite:
                errores_fila.append("El campo 'NOMBRE DEL COMITÉ' está vacío.")

            if errores_fila:
                errores_globales.append({
                    "numero_fila": numero_fila,
                    "nombre_comite": nombre_comite or "(sin comité)",
                    "errores": errores_fila,
                    "datos_crudos": datos_crudos
                })
            else:
                if nombre_comite not in filas_por_comite:
                    filas_por_comite[nombre_comite] = []
                filas_por_comite[nombre_comite].append({
                    "numero_fila": numero_fila,
                    "datos": datos_crudos
                })

        comites_validos = []
        comites_error = []

        for nombre_comite, filas in filas_por_comite.items():
            errores_comite = self._validar_comite(nombre_comite, filas)
            if errores_comite:
                for f in filas:
                    comites_error.append({
                        "numero_fila": f["numero_fila"],
                        "nombre_comite": nombre_comite,
                        "errores": errores_comite,
                        "datos_crudos": f["datos"]
                    })
            else:
                comites_validos.append({
                    "nombre_comite": nombre_comite,
                    "filas": filas
                })

        return {
            "columnas": cabecera_raw,
            "comites_validos": comites_validos,
            "comites_error": comites_error,
            "filas_error_sin_comite": errores_globales,
            "total_filas_procesadas": sum(len(c["filas"]) for c in comites_validos) + len(comites_error) + len(errores_globales),
            "total_comites_validos": len(comites_validos),
            "total_comites_error": len(set(c["nombre_comite"] for c in comites_error)),
        }

    def _normalizar_encabezado(self, texto):
        if texto is None:
            return ""
        valor = str(texto).strip().lower()
        import unicodedata
        valor = unicodedata.normalize("NFKD", valor)
        valor = "".join(ch for ch in valor if not unicodedata.combining(ch))
        import re
        valor = re.sub(r"[^a-z0-9]+", " ", valor)
        valor = " ".join(valor.split())
        return self.HEADER_ALIASES_VOCERIA.get(valor, valor)

    def _extraer_datos_fila(self, fila, idx, cabecera_raw):
        datos = {}
        for campo in self.VOCERIA_HEADERS:
            if campo in idx and idx[campo] < len(fila):
                valor = fila[idx[campo]]
                if campo == "telefono":
                    datos[campo] = self._normalizar_telefono_excel(valor)
                elif campo in ("fecha_nacimiento", "fechas_eleccion") and isinstance(valor, (date, datetime)):
                    datos[campo] = valor.strftime("%Y-%m-%d")
                elif campo == "ci" and isinstance(valor, (int, float)) and not isinstance(valor, bool):
                    datos[campo] = str(int(valor)) if float(valor).is_integer() else str(valor).strip()
                elif campo == "edad" and isinstance(valor, (int, float)) and not isinstance(valor, bool):
                    datos[campo] = str(int(valor)) if float(valor).is_integer() else str(valor).strip()
                else:
                    datos[campo] = str(valor).strip() if valor is not None else ""
            else:
                datos[campo] = ""

        if not datos.get("edad"):
            fecha_nacimiento = self._parsear_fecha(datos.get("fecha_nacimiento"))
            if fecha_nacimiento:
                hoy = date.today()
                edad = hoy.year - fecha_nacimiento.year - (
                    (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
                )
                datos["edad"] = str(edad)
        return datos

    def _normalizar_telefono_excel(self, valor):
        if valor is None:
            return ""

        es_numerico = isinstance(valor, (int, float)) and not isinstance(valor, bool)
        if isinstance(valor, float):
            if not valor.is_integer():
                return str(valor).strip()
            texto = str(int(valor))
        else:
            texto = str(valor).strip()

        if es_numerico and len(texto) == 10 and texto.startswith(("412", "414", "416", "424", "426")):
            texto = "0" + texto

        texto_digitos = texto[1:] if texto.startswith("+") else texto
        separadores = " ()-./"
        if all(caracter.isdigit() or caracter.isspace() or caracter in separadores for caracter in texto_digitos):
            return "".join(caracter for caracter in texto_digitos if caracter.isdigit())
        return texto

    def _validar_fila(self, datos, numero_fila):
        errores = []
        for campo in self.CAMPOS_OBLIGATORIOS:
            valor = (datos.get(campo) or "").strip()
            if not valor or valor.lower() in ("aaaa-mm-dd", "edad", "seleccionar...", "(sin opciones disponibles)"):
                nombre_campo = campo.replace("_", " ").upper()
                errores.append(f"Fila {numero_fila}: El campo '{nombre_campo}' es obligatorio.")
        correo = (datos.get("correo") or "").strip()
        if correo and not validar_correo(correo):
            errores.append(f"Fila {numero_fila}: Correo electrónico no válido.")

        nombres = (datos.get("nombres") or "").strip()
        if nombres and not 5 <= len(nombres) <= 40:
            errores.append(f"Fila {numero_fila}: Nombres y Apellidos debe tener entre 5 y 40 caracteres.")
        if nombres and any(caracter.isdigit() or ord(caracter) < 32 for caracter in nombres):
            errores.append(f"Fila {numero_fila}: Nombres y Apellidos no puede contener números ni controles.")

        ci = (datos.get("ci") or "").strip()
        ci_digitos = ci.replace(",", "")
        formato_ci_valido = bool(re.fullmatch(r"(?:\d{7,8}|\d{1,2}(?:,\d{3}){2})", ci))
        if ci and (not formato_ci_valido or not 7 <= len(ci_digitos) <= 8):
            errores.append(f"Fila {numero_fila}: La C.I. debe tener entre 7 y 8 dígitos.")

        profesion = (datos.get("profesion") or "").strip()
        if profesion and not 3 <= len(profesion) <= 40:
            errores.append(f"Fila {numero_fila}: Profesión/Oficio debe tener entre 3 y 40 caracteres.")

        telefono = (datos.get("telefono") or "").strip()
        if telefono and (not telefono.isdigit() or not 11 <= len(telefono) <= 12):
            errores.append(f"Fila {numero_fila}: El teléfono debe tener entre 11 y 12 dígitos.")

        edad = (datos.get("edad") or "").strip()
        if edad and (not edad.isdigit() or len(edad) > 2 or not 18 <= int(edad) <= 99):
            errores.append(f"Fila {numero_fila}: La edad debe estar entre 18 y 99 años.")

        sexo = (datos.get("sexo") or "").strip()
        if sexo and sexo not in ("M", "F"):
            errores.append(f"Fila {numero_fila}: Sexo debe ser M o F.")

        limites_generales = {
            "estado": 100, "municipio": 100, "parroquia": 100,
            "centro_dispensador": 100, "nombre_centro": 200, "nombre_comite": 200,
        }
        for campo, maximo in limites_generales.items():
            valor = (datos.get(campo) or "").strip()
            if valor and (len(valor) > maximo or any(ord(caracter) < 32 for caracter in valor)):
                errores.append(f"Fila {numero_fila}: '{campo.replace('_', ' ').upper()}' supera {maximo} caracteres o contiene controles.")

        estado = (datos.get("estado") or "").strip()
        if estado and estado not in VOCERIA_ESTADO_OPCIONES:
            errores.append(f"Fila {numero_fila}: Estado no válido.")
        municipio = (datos.get("municipio") or "").strip()
        if municipio and municipio not in MUNICIPIOS_TACHIRA:
            errores.append(f"Fila {numero_fila}: Municipio no válido.")
        centro_dispensador = (datos.get("centro_dispensador") or "").strip()
        if centro_dispensador and centro_dispensador not in VOCERIA_CENTRO_DISPENSADOR_OPCIONES:
            errores.append(f"Fila {numero_fila}: Centro dispensador no válido.")

        hoy = date.today()
        fecha_nacimiento = self._parsear_fecha(datos.get("fecha_nacimiento"))
        if datos.get("fecha_nacimiento") and not fecha_nacimiento:
            errores.append(f"Fila {numero_fila}: Fecha de Nacimiento no válida.")
        elif fecha_nacimiento:
            edad_por_fecha = hoy.year - fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
            )
            if not 18 <= edad_por_fecha <= 99:
                errores.append(f"Fila {numero_fila}: La persona debe tener entre 18 y 99 años según su Fecha de Nacimiento.")
            if edad.isdigit() and int(edad) != edad_por_fecha:
                errores.append(f"Fila {numero_fila}: La edad no coincide con la Fecha de Nacimiento.")

        fecha_eleccion = self._parsear_fecha(datos.get("fechas_eleccion"))
        if datos.get("fechas_eleccion") and not fecha_eleccion:
            errores.append(f"Fila {numero_fila}: Fecha de Elección no válida.")
        elif fecha_eleccion and fecha_eleccion > hoy:
            errores.append(f"Fila {numero_fila}: La Fecha de Elección no puede ser futura.")
        elif fecha_eleccion and fecha_eleccion < hoy - timedelta(days=730):
            errores.append(f"Fila {numero_fila}: La Fecha de Elección no puede tener más de 2 años.")
        return errores

    def _validar_comite(self, nombre_comite, filas):
        errores = []

        if len(filas) < 7:
            errores.append(f"El comité '{nombre_comite}' debe tener mínimo 7 vocerías (actual: {len(filas)}).")
        if len(filas) > 10:
            errores.append(f"El comité '{nombre_comite}' debe tener máximo 10 vocerías (actual: {len(filas)}).")

        vocerias_vistas = set()
        for f in filas:
            datos = f["datos"]
            voceria = (datos.get("voceria") or "").strip().lower()
            if voceria in vocerias_vistas:
                errores.append(f"Comité '{nombre_comite}': Vocería duplicada '{datos.get('voceria')}'.")
            vocerias_vistas.add(voceria)

            fecha_eleccion_str = (datos.get("fechas_eleccion") or "").strip()
            fecha_eleccion = self._parsear_fecha(fecha_eleccion_str)
            if fecha_eleccion:
                hace_dos_anos = date.today() - timedelta(days=730)
                if fecha_eleccion < hace_dos_anos:
                    errores.append(
                        f"Comité '{nombre_comite}', fila {f['numero_fila']}: "
                        f"La fecha de elección ({fecha_eleccion_str}) tiene más de 2 años de antigüedad."
                    )

        return errores

    def _parsear_fecha(self, valor):
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

    def importar(self, comites_validos: list) -> dict:
        """
        Inserta en BD todos los comités ya validados.
        Retorna: {comites_insertados, voceros_insertados, errores_al_insertar}
        """
        auth = AuthController()
        usuario = auth.obtener_usuario_actual()
        if not auth.usuario_puede_escribir(usuario):
            raise PermissionError(auth.mensaje_sin_permiso())
        from db import VoceriaController
        voceria_ctrl = VoceriaController()

        if not comites_validos:
            return {
                "comites_insertados": 0,
                "voceros_insertados": 0,
                "errores_al_insertar": [],
            }

        conn = get_connection()
        comite_actual = None
        comites_insertados = 0
        voceros_insertados = 0
        try:
            for comite in comites_validos:
                comite_actual = comite
                primera_fila = comite["filas"][0]["datos"]
                id_asic = self._resolver_asic(primera_fila.get("asic", ""))
                if not id_asic:
                    raise ValueError(f"ASIC no encontrado: {primera_fila.get('asic')}")

                id_tipo_voceria = self._resolver_tipo_voceria(primera_fila.get("voceria", ""))
                if not id_tipo_voceria:
                    tipos = self._tipo_voceria_dao.obtener_todos()
                    if tipos:
                        id_tipo_voceria = tipos[0]["id_tipo"]
                    else:
                        raise ValueError("No hay tipos de vocería configurados en el sistema.")

                items = []
                for f in comite["filas"]:
                    d = f["datos"]
                    item = {
                        "nombres": d.get("nombres", ""),
                        "ci": d.get("ci", ""),
                        "telefono": d.get("telefono", ""),
                        "fecha_nacimiento": d.get("fecha_nacimiento", ""),
                        "edad": d.get("edad", ""),
                        "id_tipo_voceria": self._resolver_tipo_voceria(d.get("voceria", "")) or id_tipo_voceria,
                        "sexo": d.get("sexo", ""),
                        "profesion": d.get("profesion", ""),
                        "correo": d.get("correo", ""),
                        "fechas_eleccion": d.get("fechas_eleccion", ""),
                    }
                    items.append(item)

                ok, msg = voceria_ctrl.guardar_voceria(
                    id_asic=id_asic,
                    id_tipo=id_tipo_voceria,
                    estado=primera_fila.get("estado", ""),
                    municipio=primera_fila.get("municipio", ""),
                    parroquia=primera_fila.get("parroquia", ""),
                    centro_dispensador=primera_fila.get("centro_dispensador", ""),
                    nombre_centro=primera_fila.get("nombre_centro", ""),
                    nombre_comite=primera_fila.get("nombre_comite", ""),
                    items=items,
                    connection=conn,
                )
                if not ok:
                    raise Exception(msg)
                comites_insertados += 1
                voceros_insertados += len(items)

            conn.commit()
            return {
                "comites_insertados": comites_insertados,
                "voceros_insertados": voceros_insertados,
                "errores_al_insertar": [],
            }
        except Exception as exc:
            conn.rollback()
            return {
                "comites_insertados": 0,
                "voceros_insertados": 0,
                "errores_al_insertar": [{
                    "nombre_comite": comite_actual.get("nombre_comite", "(desconocido)") if comite_actual else "(desconocido)",
                    "error": str(exc)
                }],
            }
        finally:
            conn.close()

    def _resolver_asic(self, nombre: str):
        key = nombre.lower().strip()
        if key in self._cache_asic:
            return self._cache_asic[key]
        for asic in self._asic_dao.obtener_todos():
            if asic["nombre"].lower().strip() == key:
                self._cache_asic[key] = asic["id_asic"]
                return asic["id_asic"]
        self._cache_asic[key] = None
        return None

    def _resolver_tipo_voceria(self, nombre: str):
        key = nombre.lower().strip()
        if key in self._cache_tipo_voceria:
            return self._cache_tipo_voceria[key]
        for tipo in self._tipo_voceria_dao.obtener_todos():
            if tipo["nombre"].lower().strip() == key:
                self._cache_tipo_voceria[key] = tipo["id_tipo"]
                return tipo["id_tipo"]
        self._cache_tipo_voceria[key] = None
        return None


class PDFService:
    """Genera el documento Word del informe consolidado usando plantilla oficial."""
    TEMPLATE_WORD_OFICIO = os.path.join("assets", "templates", "plantilla_reporte.docx")

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
            fecha=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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
        """Actualiza solo los valores dinámicos de la plantilla oficial sin alterar su estructura."""
        root = ET.fromstring(xml_bytes)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        resumen_tipo = datos.get("resumen_por_tipo", []) or []
        tipo_lookup = {}
        for fila in resumen_tipo:
            nombre = str(fila.get("nombre") or "").strip()
            if not nombre:
                continue
            tipo_lookup[self._normalizar_texto(nombre)] = {
                "total_actividades": int(fila.get("total_actividades", 0) or 0),
                "total_participantes": int(fila.get("total_participantes", 0) or 0),
            }

        for _, nombre in TIPOS_ACTIVIDAD_PREDETERMINADOS:
            tipo_lookup.setdefault(self._normalizar_texto(nombre), {
                "total_actividades": 0,
                "total_participantes": 0,
            })

        vocerias = datos.get("vocerias", []) or []
        llave_actualizacion = self._normalizar_texto("Actualización de los comités de salud")
        tipo_lookup.setdefault(llave_actualizacion, {"total_actividades": 0, "total_participantes": 0})
        tipo_lookup[llave_actualizacion]["total_actividades"] = len(vocerias) or tipo_lookup[llave_actualizacion].get("total_actividades", 0)

        def get_valor(nombre: str, campo: str) -> int:
            clave = self._normalizar_texto(nombre)
            datos_tipo = tipo_lookup.get(clave, {"total_actividades": 0, "total_participantes": 0})
            return int(datos_tipo.get(campo, 0) or 0)

        def asignar_valores_fila(indice_fila: int, valores):
            filas = root.findall(".//w:tr", ns)
            if indice_fila >= len(filas):
                return
            celdas = filas[indice_fila].findall("./w:tc", ns)
            if len(celdas) < 2:
                return
            nodos = celdas[1].findall(".//w:t", ns)
            if not nodos:
                return
            nodos_numericos = [n for n in nodos if (n.text or "").strip().isdigit()]
            for nodo, valor in zip(nodos_numericos, valores):
                nodo.text = str(valor)
            for nodo in nodos_numericos[len(valores):]:
                nodo.text = "0"

        filas = root.findall(".//w:tr", ns)
        if len(filas) > 1:
            celdas = filas[1].findall("./w:tc", ns)
            if len(celdas) > 1:
                texto_eliminar = "Seguimiento a los Comités de Salud mediante las vocerías en salud comunal"
                parrafos_etiqueta = celdas[0].findall("./w:p", ns)
                indice_actualizacion = next(
                    (
                        indice for indice, parrafo in enumerate(parrafos_etiqueta)
                        if "Actualización de los comités de salud" in "".join(
                            (n.text or "") for n in parrafo.findall(".//w:t", ns)
                        )
                    ),
                    None,
                )
                if indice_actualizacion is not None:
                    for parrafo in parrafos_etiqueta[:indice_actualizacion]:
                        celdas[0].remove(parrafo)

                parrafos_valor = celdas[1].findall("./w:p", ns)
                indice_ultimo_numero = next(
                    (
                        indice for indice in range(len(parrafos_valor) - 1, -1, -1)
                        if any(
                            (n.text or "").strip().isdigit()
                            for n in parrafos_valor[indice].findall(".//w:t", ns)
                        )
                    ),
                    None,
                )
                if indice_ultimo_numero is not None:
                    for parrafo in parrafos_valor[:indice_ultimo_numero]:
                        celdas[1].remove(parrafo)

        salud = (get_valor("Salud toca tu puerta", "total_actividades"), get_valor("Salud toca tu puerta", "total_participantes"))
        sesiones = (get_valor("Sesiones educativas", "total_actividades"), get_valor("Sesiones educativas", "total_participantes"))
        comites_escuela = (get_valor("Los Comités de Salud van a la escuela", "total_actividades"), get_valor("Los Comités de Salud van a la escuela", "total_participantes"))
        promocion = (get_valor("Actividades de Promoción y Prevención Social", "total_actividades"), get_valor("Actividades de Promoción y Prevención Social", "total_participantes"))
        jornadas = (get_valor("Participación Activa en Jornadas", "total_actividades"), get_valor("Participación Activa en Jornadas", "total_participantes"))
        inmunizaciones = (get_valor("Participación Activa en Inmunizaciones", "total_actividades"), get_valor("Participación Activa en Inmunizaciones", "total_participantes"))
        entrevista = (get_valor("Entrevista servicio social", "total_actividades"), get_valor("Entrevista servicio social", "total_participantes"))
        actividades_asic = (
            int(datos.get("total_actividades", 0) or 0),
            int(datos.get("total_participantes", 0) or 0),
        )

        asignar_valores_fila(1, [
            get_valor("Actualización de los comités de salud", "total_actividades"),
        ])
        asignar_valores_fila(2, [salud[0], salud[1]])
        asignar_valores_fila(3, [sesiones[0], sesiones[1], comites_escuela[0], comites_escuela[1]])
        asignar_valores_fila(4, [promocion[0], promocion[1], jornadas[0], jornadas[1], inmunizaciones[0], inmunizaciones[1]])
        asignar_valores_fila(5, [entrevista[0], entrevista[1], actividades_asic[0]])

        tipos_fijos = {
            self._normalizar_texto(nombre)
            for _, nombre in TIPOS_ACTIVIDAD_PREDETERMINADOS
        }
        tipos_fijos.add(llave_actualizacion)
        tipos_incluidos = set(tipos_fijos)
        tabla_resumen = root.find(".//w:tbl", ns)
        fila_base = root.findall(".//w:tbl/w:tr", ns)[2]

        for fila in resumen_tipo:
            nombre = str(fila.get("nombre") or "").strip()
            clave = self._normalizar_texto(nombre)
            if not nombre or clave in tipos_incluidos:
                continue

            fila_personalizada = deepcopy(fila_base)
            celdas = fila_personalizada.findall("./w:tc", ns)
            parrafo_nombre = next(
                (
                    parrafo for parrafo in celdas[0].findall("./w:p", ns)
                    if "salud toca tu puerta" in self._normalizar_texto(
                        self._texto_parrafo(parrafo, ns)
                    )
                ),
                None,
            )
            if parrafo_nombre is not None:
                self._poner_texto_en_parrafo(parrafo_nombre, nombre, ns)

            nodos_numericos = [
                nodo for nodo in celdas[1].findall(".//w:t", ns)
                if (nodo.text or "").strip().isdigit()
            ]
            valores = [
                int(fila.get("total_actividades", 0) or 0),
                int(fila.get("total_participantes", 0) or 0),
            ]
            for nodo, valor in zip(nodos_numericos, valores):
                nodo.text = str(valor)

            tabla_resumen.append(fila_personalizada)
            tipos_incluidos.add(clave)

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
                fecha_ini = act.get("fecha") or ""
                fecha_fin = act.get("fecha_fin") or fecha_ini
                tema = str(act.get("tema") or "").strip()
                lineas.append(
                    p(
                        f"{i}. {act.get('asic_nombre', '')} - {act.get('tipo_nombre', '')} - "
                        f"{fecha_ini} a {fecha_fin} - "
                        f"Participantes: {act.get('participantes', 0)} - "
                        f"Tema: {tema}"
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
            fecha_ini = act.get("fecha") or ""
            fecha_fin = act.get("fecha_fin") or fecha_ini
            tema = str(act.get("tema") or "").strip()
            filas.append([
                Paragraph(str(i),                          estilos["td_centro"]),
                Paragraph(act.get("asic_nombre", ""),      estilos["td_pequeño"]),
                Paragraph(act.get("tipo_nombre", ""),      estilos["td_pequeño"]),
                Paragraph(str(fecha_ini),                   estilos["td_centro"]),
                Paragraph(str(fecha_fin),                   estilos["td_centro"]),
                Paragraph(str(act.get("participantes", 0)), estilos["td_centro"]),
                Paragraph(tema[:120], estilos["td_pequeño"]),
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
if __name__ == "__main__":
    print("=== Setup inicial del Sistema DPPPS ===\n")
    try:
        _setup_crear_base_de_datos()
        _setup_ejecutar_schema()
        print("\n[LISTO] Setup completado exitosamente.")
        print("   Ya puedes ejecutar la aplicacion con: python main.py")
    except Exception as e:
        print(f"\n[ERROR] Error durante el setup: {e}")
        print("   Verifica que MariaDB/MySQL este corriendo y los datos en DATABASE sean correctos.")
