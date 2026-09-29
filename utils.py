from db import get_connection


def centrar_ventana(ventana, ancho: int, alto: int):
    """Centra una ventana Tkinter en la pantalla."""
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla  = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla  // 2) - (alto  // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
