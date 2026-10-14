import os
import sys


def obtener_ruta_recurso(*partes_ruta: str) -> str:
    """Devuelve la ruta absoluta a un recurso, compatible con PyInstaller (_MEIPASS) y entorno de desarrollo."""
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base_dir, *partes_ruta))


def set_favicon(ventana):
    """Establece el favicon común para cualquier ventana de la app."""
    logo_path = obtener_ruta_recurso("assets", "images", "logo2.ico")
    if not os.path.exists(logo_path):
        return

    try:
        ventana.iconbitmap(logo_path)
    except Exception:
        try:
            from PIL import Image, ImageTk
            img = Image.open(logo_path.replace(".ico", ".png"))
            photo = ImageTk.PhotoImage(img)
            ventana.iconphoto(True, photo)
            ventana._favicon = photo
        except Exception:
            pass


def centrar_ventana(ventana, ancho: int, alto: int):
    """Centra una ventana Tkinter en la pantalla."""
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla  = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla  // 2) - (alto  // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
