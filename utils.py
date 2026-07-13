# ============================================================
# utils.py
# Funciones de soporte reutilizables del sistema DPPPS.
#
# Contiene:
#   - Helpers para consultas rápidas a la BD (_query, _scalar)
#   - Función para centrar ventanas Tkinter
# ============================================================

from db import get_connection


def query(sql: str, params: tuple = ()) -> list:
    """
    Ejecuta una consulta SELECT y devuelve una lista de dicts.

    Ejemplo:
        rows = query("SELECT * FROM asic WHERE activo = TRUE")
        for r in rows:
            print(r["nombre"])
    """
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def scalar(sql: str, params: tuple = (), default=0):
    """
    Ejecuta una consulta escalar y devuelve el primer valor de la primera fila.

    Ejemplo:
        total = scalar("SELECT COUNT(*) FROM actividad WHERE eliminado = FALSE")
    """
    rows = query(sql, params)
    if rows:
        return list(rows[0].values())[0] or default
    return default


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
