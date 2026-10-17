import os

from constants import ALLOWED_EXTENSIONS, EMAIL_REGEX, MAX_FILE_SIZE_MB

def validar_correo(correo):
    correo = (correo or "").strip()
    if len(correo) > 120:
        return False
    if not EMAIL_REGEX.fullmatch(correo):
        return False
    parte_local = correo.split("@", 1)[0]
    return (
        not parte_local.startswith(".")
        and not parte_local.endswith(".")
        and ".." not in parte_local
    )

def validar_archivo_excel(ruta_archivo):
    if not ruta_archivo or not os.path.isfile(ruta_archivo):
        raise ValueError("Selecciona un archivo Excel existente.")
    if os.path.splitext(ruta_archivo)[1].lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("El archivo debe tener formato .xlsx.")
    if os.path.getsize(ruta_archivo) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"El archivo no puede superar {MAX_FILE_SIZE_MB} MB.")
