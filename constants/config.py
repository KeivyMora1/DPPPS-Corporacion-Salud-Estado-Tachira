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

APP_TITLE = "DPPPS — Sistema de Consolidación de Informes"
APP_VERSION = "1.0.0"