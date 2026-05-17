# ============================================================
# config/settings.py
# Configuración general del sistema DPPPS
# Aquí se definen los parámetros de conexión a la base de datos
# y otras configuraciones globales de la aplicación.
# ============================================================

# Modo de conexión: "local" usa localhost, "lan" usa una IP de red
MODO = "local"

# Parámetros de conexión para cada modo
DATABASE = {
    "local": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "admin",          # Cambia esto si tu MariaDB/MySQL tiene contraseña
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
