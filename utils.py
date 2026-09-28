# ============================================================
# utils.py
# Funciones de soporte reutilizables del sistema DPPPS.
#
# Contiene:
#   - Función para centrar ventanas Tkinter
# ============================================================

from db import get_connection


def centrar_ventana(ventana, ancho: int, alto: int):
    """
    Centra una ventana Tkinter en el monitor del usuario.

    Ejemplo:
        centrar_ventana(root, 420, 500)
    """
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla  = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla  // 2) - (alto  // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
