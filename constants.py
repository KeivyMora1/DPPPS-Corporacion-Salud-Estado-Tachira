import re
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

MODO = "local"
DATABASE = {
    "local": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "dppps_informes",
    },
    "lan": {
        "host": "192.168.1.100",
        "port": 3306,
        "user": "dppps_app",
        "password": "contraseña_segura",
        "database": "dppps_informes",
    },
}

def _obtener_ruta_base_recursos():
    import sys
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return base_dir

_BASE_RES = _obtener_ruta_base_recursos()
TEMPLATE_PATH = os.path.normpath(os.path.join(_BASE_RES, "assets", "templates", "plantilla_importacion_actividad.xlsx"))
VOCERIA_TEMPLATE_PATH = os.path.normpath(os.path.join(_BASE_RES, "assets", "templates", "plantilla_importacion_voceria.xlsx"))

APP_TITLE = "DPPPS — Sistema de Consolidación de Informes"
APP_VERSION = "1.0.0"

USUARIO_PROPIETARIO_PREDETERMINADO = "admin"
PASSWORD_PROPIETARIO_PREDETERMINADO = "12345678"
EMAIL_PROPIETARIO_PREDETERMINADO = os.getenv("OWNER_EMAIL", "").strip()

MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = [".xlsx"]
EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
)

ASIC_PREDETERMINADOS = [
    ("ASIC-01", "Andrés Bello"),
    ("ASIC-02", "Antonio Rómulo Costa"),
    ("ASIC-03", "Ayacucho"),
    ("ASIC-04", "Bolívar"),
    ("ASIC-05", "Independencia"),
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
    ("ASIC-16", "Junin · Rafael Urdaneta"),
    ("ASIC-17", "Libertador"),
    ("ASIC-18", "Michelena"),
    ("ASIC-19", "Panamericano · San Judas Tadeo"),
    ("ASIC-20", "Sabaneta"),
    ("ASIC-21", "Samuel Darío Maldonado"),
    ("ASIC-22", "Sucre"),
    ("ASIC-23", "San Josecito"),
    ("ASIC-24", "Ureña"),
    ("ASIC-25", "Uribante"),
]

VOCERIA_CENTRO_DISPENSADOR_OPCIONES = [
    "Consultorio Popular TIPO I",
    "Consultorio Popular TIPO II",
    "Consultorio Popular TIPO III",
    "Clinica Popular TIPO I",
    "Clinica Popular TIPO II",
    "CDI",
    "SRI",
    "CAT",
    "Hospitales TIPO I",
    "Hospitales TIPO II",
    "Hospitales TIPO III",
    "Hospitales TIPO IV",
]
ACTIVIDAD_ESTABLECIMIENTO_OPCIONES = VOCERIA_CENTRO_DISPENSADOR_OPCIONES

# Catálogo geográfico de respaldo/legado.
# La fuente de verdad activa reside en las tablas 'municipio' y 'parroquia' de la base de datos.
PARROQUIAS_POR_MUNICIPIO_TACHIRA = {
    "Andrés Bello": ["Cordero"],
    "Antonio Rómulo Costa": ["Virgen del Carmen"],
    "Ayacucho": ["San Juan de Colón", "Rivas Berti", "San Pedro del Río"],
    "Bolívar": [
        "San Antonio del Táchira",
        "Palotal",
        "Juan Vicente Gómez",
        "Isaías Medina Angarita",
    ],
    "Cárdenas": ["Táriba", "Amenodoro Rangel Lamús", "La Florida"],
    "Córdoba": ["Santa Ana del Táchira"],
    "Fernández Feo": ["San Rafael del Piñal", "Alberto Adriani", "Santo Domingo"],
    "Francisco de Miranda": ["San José de Bolívar"],
    "García de Hevia": ["La Fría", "Boca de Grita", "José Antonio Páez"],
    "Guásimos": ["Palmira"],
    "Independencia": ["Capacho Nuevo", "Juan Germán Roscio", "Román Cárdenas"],
    "Jáuregui": [
        "La Grita",
        "Emilio Constantino Guerrero",
        "Monseñor Miguel Antonio Salas",
    ],
    "José María Vargas": ["El Cobre"],
    "Junín": ["Rubio", "Bramón", "La Petrólea", "Quinimarí"],
    "Libertad": ["Capacho Viejo", "Cipriano Castro", "Manuel Felipe Rugeles"],
    "Libertador": ["Abejales", "Doradas", "Emeterio Ochoa", "San Joaquín de Navay"],
    "Lobatera": ["Lobatera", "Constitución"],
    "Michelena": ["Michelena"],
    "Panamericano": ["San Pablo", "La Palmita"],
    "Pedro María Ureña": ["Ureña", "Nueva Arcadia"],
    "Rafael Urdaneta": ["Delicias"],
    "Samuel Darío Maldonado": ["La Tendida", "Boconó", "Hernández"],
    "San Cristóbal": [
        "La Concordia",
        "Pedro María Morantes",
        "San Juan Bautista",
        "San Sebastián",
        "Francisco Romero Lobo",
    ],
    "San Judas Tadeo": ["San Judas Tadeo"],
    "Seboruco": ["Seboruco"],
    "Simón Rodríguez": ["San Simón"],
    "Sucre": ["Sucre", "Eleazar López Contreras", "San Pablo"],
    "Torbes": ["San Josecito"],
    "Uribante": ["Pregonero", "Cárdenas", "Juan Pablo Peñaloza", "Potosí"],
}

MUNICIPIOS_TACHIRA = list(PARROQUIAS_POR_MUNICIPIO_TACHIRA)

ASIC_POR_MUNICIPIO = {
    "Andrés Bello": ["Andrés Bello"],
    "Antonio Rómulo Costa": ["Antonio Rómulo Costa"],
    "Ayacucho": ["Ayacucho"],
    "Bolívar": ["Bolívar"],
    "Cárdenas": ["Cárdenas"],
    "Córdoba": ["Córdoba"],
    "Fernández Feo": ["Fernández Feo"],
    "Francisco de Miranda": [],
    "García de Hevia": ["García de Hevia"],
    "Guásimos": ["Guásimos"],
    "Independencia": ["Independencia"],
    "Jáuregui": ["Jáuregui"],
    "José María Vargas": [],
    "Junín": ["Junin · Rafael Urdaneta"],
    "Libertad": ["Capacho Libertad"],
    "Libertador": ["Libertador"],
    "Lobatera": ["Michelena"],
    "Michelena": ["Michelena"],
    "Panamericano": ["Panamericano · San Judas Tadeo"],
    "Pedro María Ureña": ["Ureña"],
    "Rafael Urdaneta": ["Junin · Rafael Urdaneta"],
    "Samuel Darío Maldonado": ["Samuel Darío Maldonado"],
    "San Cristóbal": [
        "Dr. Hugo Murzi",
        "Dr. Jacinto Convit",
        "Dr. José María Vargas",
        "Sabaneta",
    ],
    "San Judas Tadeo": ["Panamericano · San Judas Tadeo"],
    "Seboruco": ["Antonio Rómulo Costa"],
    "Simón Rodríguez": [],
    "Sucre": ["Sucre"],
    "Torbes": ["San Josecito"],
    "Uribante": ["Uribante"],
}

UBICACIONES_ASIC_PREDETERMINADAS = [
    (asic, municipio, parroquia)
    for _, asic in ASIC_PREDETERMINADOS
    for municipio, parroquias in PARROQUIAS_POR_MUNICIPIO_TACHIRA.items()
    for parroquia in parroquias
]

VOCERIA_MUNICIPIO_OPCIONES = MUNICIPIOS_TACHIRA
VOCERIA_ASIC_OPCIONES = [nombre for _, nombre in ASIC_PREDETERMINADOS]

VOCERIA_ESTADO_OPCIONES = ["Táchira"]

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

TIPOS_ACTIVIDAD_PREDETERMINADOS = [
    ("TIPO-01", "Salud toca tu puerta"),
    ("TIPO-02", "Sesiones educativas"),
    ("TIPO-03", "Los Comités de Salud van a la escuela"),
    ("TIPO-04", "Actividades de Promoción y Prevención Social"),
    ("TIPO-05", "Participación Activa en Jornadas"),
    ("TIPO-06", "Participación Activa en Inmunizaciones"),
    ("TIPO-07", "Entrevista servicio social"),
]

THEME = {
    "bg_base": "#20053D",
    "bg_sidebar": "#26405E",
    "bg_header": "#1a2f45",
    "bg_hover": "#2f4d6a",
    "bg_active": "#345572",
    "bg_surface": "#26405E",
    "bg_card": "#26405E",
    "border": "#345572",
    "accent": "#613BE3",
    "accent_dim": "#4e2fb8",
    "success": "#317E87",
    "success_dim": "#266470",
    "amber": "#d4a843",
    "rose": "#c45050",
    "text_primary": "#CBE1DB",
    "text_muted": "#8faab0",
    "text_dim": "#5a7a85",
    "red": "#c45050",
    "red_hover": "#a83838",
    "red_bg": "#30152a",
    "red_fg": "#e88080",
}
