# ============================================================
# controllers/actividad_controller.py
# Controlador para gestionar la lógica de las actividades.
# Valida los datos recibidos de la vista antes de guardarlos.
# ============================================================

from datetime import datetime, date
import os
import shutil
import time
import mimetypes
from models.actividad import ActividadDAO
from models.asic import AsicDAO
from models.tipo_actividad import TipoActividadDAO
from models.evidencia import EvidenciaDAO
from controllers.auth_controller import AuthController
from config.settings import UPLOADS_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB


class ActividadController:
    """
    Controlador que maneja las actividades de salud.
    Valida las reglas de negocio antes de llamar al DAO correspondiente.
    """

    def __init__(self):
        self.actividad_dao = ActividadDAO()
        self.asic_dao = AsicDAO()
        self.tipo_dao = TipoActividadDAO()
        self.evidencia_dao = EvidenciaDAO()
        self.auth = AuthController()

    def listar_actividades(self, filtros=None):
        """Retorna la lista de actividades registradas, aplicando filtros si los hay."""
        return self.actividad_dao.obtener_todas(filtros)

    def listar_asics(self):
        """Retorna la lista de todos los ASIC activos."""
        return self.asic_dao.obtener_todos()

    def listar_tipos_actividad(self):
        """Retorna la lista de todos los tipos de actividad activos."""
        return self.tipo_dao.obtener_todos()

    def guardar_actividad(self, id_asic, id_tipo, fecha_inicio, fecha_fin, lugar, descripcion, participantes, id_actividad=None, evidencias_temporales=None):
        """
        Registra una nueva actividad o actualiza una existente.
        Valida que los datos cumplan con las reglas de negocio.
        
        Retorna: (True, "mensaje exito") o (False, "mensaje error")
        """
        # 1. Validar que se haya seleccionado un ASIC y un tipo de actividad
        if not id_asic:
            return False, "Debes seleccionar un ASIC."
        if not id_tipo:
            return False, "Debes seleccionar un tipo de actividad."

        # 2. Validar que la descripción no esté vacía
        descripcion = descripcion.strip() if descripcion else ""
        if not descripcion:
            return False, "La descripcion de la actividad es obligatoria."

        # 3. Validar el lugar
        lugar = lugar.strip() if lugar else ""

        # 4. Validar cantidad de participantes
        try:
            cant_participantes = int(participantes)
            if cant_participantes < 0:
                return False, "La cantidad de participantes no puede ser menor a 0."
        except (ValueError, TypeError):
            return False, "La cantidad de participantes debe ser un numero entero valido."

        # 5. Convertir y validar fechas
        f_ini = None
        f_fin = None

        # Convertir fecha_inicio
        if isinstance(fecha_inicio, str):
            try:
                # Si viene en formato DD/MM/AAAA (común en widgets visuales)
                if "/" in fecha_inicio:
                    f_ini = datetime.strptime(fecha_inicio, "%d/%m/%Y").date()
                else:
                    f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            except ValueError:
                return False, "El formato de la fecha de inicio es invalido."
        elif isinstance(fecha_inicio, (datetime, date)):
            f_ini = fecha_inicio
        else:
            return False, "Fecha de inicio invalida."

        # Convertir fecha_fin
        if isinstance(fecha_fin, str):
            try:
                if "/" in fecha_fin:
                    f_fin = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                else:
                    f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            except ValueError:
                return False, "El formato de la fecha de fin es invalido."
        elif isinstance(fecha_fin, (datetime, date)):
            f_fin = fecha_fin
        else:
            return False, "Fecha de fin invalida."

        # Validar que fecha_inicio <= fecha_fin
        if f_ini > f_fin:
            return False, "La fecha de inicio no puede ser posterior a la fecha de fin."

        # 6. Validar duplicidad
        # Formatear la fecha para la BD como 'AAAA-MM-DD'
        fecha_inicio_bd = f_ini.strftime("%Y-%m-%d")
        fecha_fin_bd = f_fin.strftime("%Y-%m-%d")

        es_duplicado = self.actividad_dao.verificar_duplicado(
            id_asic=id_asic,
            id_tipo=id_tipo,
            fecha_inicio=fecha_inicio_bd,
            descripcion=descripcion,
            excluir_id=id_actividad
        )

        if es_duplicado:
            return False, "Ya existe una actividad registrada para este ASIC, tipo, fecha de inicio y descripcion similar."

        # 7. Obtener usuario registrado actual
        usuario = self.auth.obtener_usuario_actual()
        if not usuario:
            return False, "No hay una sesion de usuario activa."
        id_usuario = usuario["id_usuario"]

        # 8. Guardar en base de datos
        if id_actividad is None:
            # Crear nueva actividad
            nuevo_id = self.actividad_dao.crear(
                id_asic=id_asic,
                id_tipo=id_tipo,
                id_usuario_registro=id_usuario,
                fecha_inicio=fecha_inicio_bd,
                fecha_fin=fecha_fin_bd,
                lugar=lugar,
                descripcion=descripcion,
                participantes=cant_participantes
            )
            
            # Guardar evidencias temporales si existen
            errores_adjuntos = []
            if evidencias_temporales:
                for ruta in evidencias_temporales:
                    ok_ev, msg_ev = self.procesar_y_guardar_evidencia(nuevo_id, ruta)
                    if not ok_ev:
                        errores_adjuntos.append(f"{os.path.basename(ruta)} ({msg_ev})")
            
            if errores_adjuntos:
                errores_str = ", ".join(errores_adjuntos)
                return True, f"Actividad registrada, pero no se pudieron subir algunos archivos: {errores_str}"
            
            return True, "Actividad registrada exitosamente."
        else:
            # Actualizar actividad existente
            self.actividad_dao.actualizar(
                id_actividad=id_actividad,
                id_asic=id_asic,
                id_tipo=id_tipo,
                fecha_inicio=fecha_inicio_bd,
                fecha_fin=fecha_fin_bd,
                lugar=lugar,
                descripcion=descripcion,
                participantes=cant_participantes
            )
            return True, "Actividad actualizada exitosamente."

    def eliminar_actividad(self, id_actividad):
        """Elimina de forma lógica una actividad."""
        self.actividad_dao.eliminar(id_actividad)
        return True, "Actividad eliminada correctamente."

    # ==================== GESTIÓN DE EVIDENCIAS ====================

    def listar_evidencias_de_actividad(self, id_actividad):
        """Retorna la lista de archivos adjuntos de una actividad."""
        return self.evidencia_dao.obtener_por_actividad(id_actividad)

    def procesar_y_guardar_evidencia(self, id_actividad, ruta_origen):
        """
        Valida y copia físicamente una evidencia a la carpeta 'uploads'
        e inserta la referencia en la base de datos.
        """
        # Validar existencia del archivo de origen
        if not os.path.exists(ruta_origen):
            return False, "El archivo de origen no existe."

        # Validar extensión
        _, ext = os.path.splitext(ruta_origen)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Extension no permitida ({ext}). Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"

        # Validar tamaño
        tamano_bytes = os.path.getsize(ruta_origen)
        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if tamano_bytes > max_bytes:
            return False, f"El archivo supera el tamano maximo de {MAX_FILE_SIZE_MB} MB."

        # Asegurar que el directorio de destino existe
        if not os.path.exists(UPLOADS_DIR):
            os.makedirs(UPLOADS_DIR)

        # Generar nombre de destino seguro sin colisiones
        nombre_original = os.path.basename(ruta_origen)
        # Limpiar caracteres raros del nombre
        nombre_limpio = "".join(c for c in nombre_original if c.isalnum() or c in (".", "-", "_")).strip()
        timestamp = int(time.time())
        # Nombre único
        nombre_destino = f"actividad_{id_actividad}_{timestamp}_{nombre_limpio}"
        ruta_destino = os.path.join(UPLOADS_DIR, nombre_destino).replace("\\", "/")

        try:
            # Copiar el archivo físicamente
            shutil.copy2(ruta_origen, ruta_destino)
            
            # Adivinar tipo mime
            tipo_archivo, _ = mimetypes.guess_type(ruta_origen)
            if not tipo_archivo:
                tipo_archivo = "application/octet-stream"

            # Insertar en BD
            self.evidencia_dao.crear(
                id_actividad=id_actividad,
                nombre_archivo=nombre_original,
                ruta_archivo=ruta_destino,
                tipo_archivo=tipo_archivo,
                tamano_bytes=tamano_bytes
            )
            return True, "Archivo adjuntado correctamente."
        except Exception as e:
            # En caso de error, intentar limpiar si se copió el archivo
            if os.path.exists(ruta_destino):
                try:
                    os.remove(ruta_destino)
                except:
                    pass
            return False, f"Error al guardar el archivo: {str(e)}"

    def eliminar_evidencia(self, id_evidencia):
        """Elimina el registro de evidencia de la BD y borra el archivo físico."""
        evidencia = self.evidencia_dao.obtener_por_id(id_evidencia)
        if not evidencia:
            return False, "Evidencia no encontrada."

        try:
            # 1. Eliminar de base de datos
            self.evidencia_dao.eliminar(id_evidencia)

            # 2. Intentar eliminar físicamente el archivo del disco
            ruta_archivo = evidencia["ruta_archivo"]
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            return True, "Evidencia eliminada correctamente."
        except Exception as e:
            return False, f"Error al eliminar la evidencia: {str(e)}"
