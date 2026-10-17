from .connection import obtener_conexion_directa

def get_connection():
    """Obtiene una conexión directa del pool; el caller debe cerrarla."""
    return obtener_conexion_directa()
