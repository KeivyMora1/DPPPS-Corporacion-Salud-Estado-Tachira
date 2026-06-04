# ============================================================
# controllers/actividad_controller.py
# Controlador para gestionar la lógica de las actividades.
# Valida los datos recibidos de la vista antes de guardarlos.
# ============================================================

from datetime import datetime, date
from models.actividad import ActividadDAO
from models.asic import AsicDAO
from models.tipo_actividad import TipoActividadDAO
from controllers.auth_controller import AuthController


class ActividadController:
    """
    Controlador que maneja las actividades de salud.
    Valida las reglas de negocio antes de llamar al DAO correspondiente.
    """

    def __init__(self):
        self.actividad_dao = ActividadDAO()
        self.asic_dao = AsicDAO()
        self.tipo_dao = TipoActividadDAO()
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

    def guardar_actividad(self, id_asic, id_tipo, fecha_inicio, fecha_fin, lugar, descripcion, participantes, id_actividad=None):
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
            self.actividad_dao.crear(
                id_asic=id_asic,
                id_tipo=id_tipo,
                id_usuario_registro=id_usuario,
                fecha_inicio=fecha_inicio_bd,
                fecha_fin=fecha_fin_bd,
                lugar=lugar,
                descripcion=descripcion,
                participantes=cant_participantes
            )
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
