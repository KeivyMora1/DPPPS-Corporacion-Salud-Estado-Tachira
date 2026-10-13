from datetime import date

from constants import (
    ACTIVIDAD_ESTABLECIMIENTO_OPCIONES,
    ASIC_PREDETERMINADOS,
    MUNICIPIOS_TACHIRA,
    TIPOS_ACTIVIDAD_PREDETERMINADOS,
)
from ..daos import ActividadDAO, AsicDAO, ParroquiaDAO, TipoActividadDAO
from .auth_service import AuthController


class ActividadController:
    """
    Controlador que maneja las actividades de salud.
    Valida las reglas de negocio antes de llamar al DAO correspondiente.
    """
    def __init__(self):
        self.actividad_dao = ActividadDAO()
        self.asic_dao = AsicDAO()
        self.parroquia_dao = ParroquiaDAO()
        self.tipo_dao = TipoActividadDAO()
        self.auth = AuthController()
    def listar_actividades(self, filtros=None):
        """Retorna la lista de actividades registradas, aplicando filtros si los hay."""
        return self.actividad_dao.obtener_todas(filtros)
    def listar_asics(self):
        """Retorna solo los ASIC permitidos por la plantilla del sistema."""
        asics_predeterminados = ASIC_PREDETERMINADOS

        def normalizar(nombre):
            return " ".join((nombre or "").strip().lower().split())

        if self.auth.puede_escribir():
            try:
                existentes = self.asic_dao.obtener_todos()
                nombres_existentes = {normalizar(a["nombre"]) for a in existentes}
                nombres_permitidos = {normalizar(nombre) for _, nombre in asics_predeterminados}

                for asic in existentes:
                    if normalizar(asic["nombre"]) not in nombres_permitidos:
                        self.asic_dao.desactivar(asic["id_asic"])

                for codigo, nombre in asics_predeterminados:
                    if normalizar(nombre) not in nombres_existentes:
                        self.asic_dao.crear(codigo, nombre, "", "")
            except Exception:
                pass

        asics = self.asic_dao.obtener_todos()
        nombres_permitidos = {normalizar(nombre) for _, nombre in asics_predeterminados}
        return [a for a in asics if normalizar(a["nombre"]) in nombres_permitidos]

    def listar_ubicaciones_asic(self):
        return self.parroquia_dao.obtener_todas()
    def listar_tipos_actividad(self):
        """Asegura los tipos iniciales y retorna todo el catálogo disponible."""
        tipos = self.tipo_dao.obtener_todos()
        if not tipos and self.auth.puede_escribir():
            for _, nombre in TIPOS_ACTIVIDAD_PREDETERMINADOS:
                self.tipo_dao.crear(nombre=nombre)
            tipos = self.tipo_dao.obtener_todos()
        return tipos

    def usuario_es_propietario(self):
        usuario = self.auth.obtener_usuario_actual()
        return bool(usuario and usuario.get("rol") == "propietario")

    def crear_tipo_actividad(self, nombre):
        if not self.usuario_es_propietario():
            return False, "Solo el usuario propietario puede gestionar tipos de actividad."

        nombre = (nombre or "").strip()
        if not nombre:
            return False, "El nombre del tipo de actividad es obligatorio."
        if len(nombre) > 150:
            return False, "El nombre del tipo de actividad no puede superar 150 caracteres."

        clave = " ".join(nombre.casefold().split())
        if any(
            " ".join((tipo["nombre"] or "").strip().casefold().split()) == clave
            for tipo in self.tipo_dao.obtener_todos()
        ):
            return False, "Ya existe un tipo de actividad con ese nombre."

        self.tipo_dao.crear(nombre=nombre)
        return True, "Tipo de actividad agregado exitosamente."

    def actualizar_tipo_actividad(self, id_tipo, nombre):
        if not self.usuario_es_propietario():
            return False, "Solo el usuario propietario puede gestionar tipos de actividad."

        nombre = (nombre or "").strip()
        if not nombre:
            return False, "El nombre del tipo de actividad es obligatorio."
        if len(nombre) > 150:
            return False, "El nombre del tipo de actividad no puede superar 150 caracteres."

        try:
            id_tipo = int(id_tipo)
        except (TypeError, ValueError):
            return False, "El tipo de actividad seleccionado no es válido."

        tipos = self.tipo_dao.obtener_todos()
        tipo_actual = next((tipo for tipo in tipos if tipo["id_tipo"] == id_tipo), None)
        if tipo_actual is None:
            return False, "El tipo de actividad seleccionado ya no existe."

        clave = " ".join(nombre.casefold().split())
        if any(
            tipo["id_tipo"] != id_tipo
            and " ".join((tipo["nombre"] or "").strip().casefold().split()) == clave
            for tipo in tipos
        ):
            return False, "Ya existe un tipo de actividad con ese nombre."

        self.tipo_dao.actualizar(id_tipo, nombre=nombre)
        return True, "Tipo de actividad actualizado exitosamente."
    def guardar_actividad(self, id_asic, id_tipo, fecha=None, estado=None, municipio=None, parroquia=None,
                           establecimiento_salud=None, nombre_establecimiento=None, comites_salud=None,
                           tema="", medicos=0, promotores_salud=0, voceros_comite_salud=0,
                           vocero_consejo_direccion=0, coordinador_docencia=0, autoridades_presentes=0,
                           otros_actores=0, personas_comunidad=0, estudiantes_aspirantes=0,
                           participantes=0, id_actividad=None, **kwargs):
        """Registra o actualiza una actividad con una sola fecha."""
        if fecha is None or not str(fecha).strip():
            return False, "La fecha es obligatoria."

        if not id_asic:
            return False, "Debes seleccionar un ASIC."
        if not id_tipo:
            return False, "Debes seleccionar un tipo de actividad."

        for campo, valor in [
            ("Estado", estado), ("Municipio", municipio), ("Parroquia", parroquia),
            ("Establecimiento de Salud", establecimiento_salud),
            ("Nombre del Establecimiento", nombre_establecimiento),
        ]:
            if valor is None or not str(valor).strip():
                return False, f"El campo {campo} es obligatorio."
        limites_texto = [
            ("Estado", estado, 100), ("Municipio", municipio, 100),
            ("Parroquia", parroquia, 100), ("Establecimiento de Salud", establecimiento_salud, 150),
            ("Nombre del Establecimiento", nombre_establecimiento, 200),
        ]
        for campo, valor, maximo in limites_texto:
            texto = str(valor).strip()
            if len(texto) > maximo or any(ord(caracter) < 32 for caracter in texto):
                return False, f"El campo {campo} no puede superar {maximo} caracteres ni contener controles."
        if estado != "Táchira":
            return False, "Debes seleccionar un estado válido."
        if municipio not in MUNICIPIOS_TACHIRA:
            return False, "Debes seleccionar un municipio válido."
        ubicaciones_asic = self.parroquia_dao.listar_por_asic(id_asic)
        if not any(
            ubicacion["municipio"] == municipio
            and ubicacion["parroquia"] == parroquia
            for ubicacion in ubicaciones_asic
        ):
            return False, "La parroquia debe corresponder al municipio seleccionado."
        if establecimiento_salud not in ACTIVIDAD_ESTABLECIMIENTO_OPCIONES:
            return False, "Debes seleccionar un establecimiento de salud válido."

        comites_texto = str(comites_salud).strip() if comites_salud is not None else ""
        if not comites_texto:
            return False, "El campo Comités de Salud es obligatorio."
        if not comites_texto.isdigit() or len(comites_texto) > 2:
            return False, "Comités de Salud debe contener solo números y tener máximo 2 dígitos."
        comites_valor = int(comites_texto)

        tema_texto = str(tema or "").strip()
        if not tema_texto:
            return False, "El tema tratado de la actividad es obligatorio."
        if len(tema_texto) > 150:
            return False, "El tema tratado no puede superar los 150 caracteres."

        if participantes is None or not str(participantes).strip():
            return False, "El total de asistencia es obligatorio."

        try:
            if isinstance(participantes, bool) or (
                isinstance(participantes, float) and not participantes.is_integer()
            ) or (isinstance(participantes, str) and not participantes.strip().isdigit()):
                raise ValueError()
            cant_participantes = int(participantes)
            if not 0 <= cant_participantes <= 899991:
                return False, "La cantidad de participantes debe estar entre 0 y 899991."
        except (ValueError, TypeError):
            return False, "La cantidad de participantes debe ser un numero entero valido."

        for campo, valor in [
            ("Médicos", medicos), ("Promotores en Salud", promotores_salud),
            ("Voceros Comité Salud", voceros_comite_salud),
            ("Vocero Consejo Dir. ASIC", vocero_consejo_direccion),
            ("Coordinador Docencia ASIC", coordinador_docencia),
            ("Autoridades Presentes", autoridades_presentes),
            ("Otros Actores", otros_actores),
            ("Personas Comunidad", personas_comunidad),
            ("Estudiantes Aspirantes", estudiantes_aspirantes)
        ]:
            if valor is None or not str(valor).strip():
                return False, f"El campo {campo} es obligatorio."
            try:
                if isinstance(valor, bool) or (
                    isinstance(valor, float) and not valor.is_integer()
                ) or (isinstance(valor, str) and not valor.strip().isdigit()):
                    raise ValueError()
                v = int(valor)
                if not 0 <= v <= 99999:
                    return False, f"El campo {campo} debe estar entre 0 y 99999."
            except (ValueError, TypeError):
                return False, f"El campo {campo} debe ser un numero entero valido."

        total_categorias = sum(int(valor) for valor in (
            medicos, promotores_salud, voceros_comite_salud, vocero_consejo_direccion,
            coordinador_docencia, autoridades_presentes, otros_actores,
            personas_comunidad, estudiantes_aspirantes,
        ))
        if total_categorias != cant_participantes:
            return False, "El total de asistencia debe coincidir con la suma de las categorías."

        try:
            fecha_obj = ActividadDAO._parse_fecha(fecha)
            fecha_bd = fecha_obj.strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            return False, "El formato de la fecha es inválido."
        if fecha_obj > date.today():
            return False, "La fecha de la actividad no puede ser futura."

        es_duplicado = self.actividad_dao.verificar_duplicado(
            id_asic=id_asic,
            id_tipo=id_tipo,
            fecha=fecha_bd,
            tema=tema_texto,
            excluir_id=id_actividad,
        )
        if es_duplicado:
            return False, "Ya existe una actividad registrada para este ASIC, tipo, fecha y tema similares."

        usuario = self.auth.obtener_usuario_actual()
        if not usuario:
            return False, "No hay una sesion de usuario activa."
        if not self.auth.usuario_puede_escribir(usuario):
            return False, self.auth.mensaje_sin_permiso()
        id_usuario = usuario["id_usuario"]

        argumentos_actividad = dict(
            id_asic=id_asic,
            id_tipo=id_tipo,
            id_usuario_registro=id_usuario,
            fecha=fecha_bd,
            estado=str(estado).strip(),
            municipio=str(municipio).strip(),
            parroquia=str(parroquia).strip(),
            establecimiento_salud=str(establecimiento_salud).strip(),
            nombre_establecimiento=str(nombre_establecimiento).strip(),
            comites_salud=comites_valor,
            tema=tema_texto,
            medicos=int(medicos) if medicos else 0,
            promotores_salud=int(promotores_salud) if promotores_salud else 0,
            voceros_comite_salud=int(voceros_comite_salud) if voceros_comite_salud else 0,
            vocero_consejo_direccion=int(vocero_consejo_direccion) if vocero_consejo_direccion else 0,
            coordinador_docencia=int(coordinador_docencia) if coordinador_docencia else 0,
            autoridades_presentes=int(autoridades_presentes) if autoridades_presentes else 0,
            otros_actores=int(otros_actores) if otros_actores else 0,
            personas_comunidad=int(personas_comunidad) if personas_comunidad else 0,
            estudiantes_aspirantes=int(estudiantes_aspirantes) if estudiantes_aspirantes else 0,
            participantes=cant_participantes,
            total_participantes=cant_participantes,
        )

        if id_actividad is None:
            self.actividad_dao.crear(**argumentos_actividad)
            return True, "Actividad registrada exitosamente."

        argumentos_actualizar = {k: v for k, v in argumentos_actividad.items() if k != "id_usuario_registro"}
        argumentos_actualizar["id_actividad"] = id_actividad
        self.actividad_dao.actualizar(**argumentos_actualizar)
        return True, "Actividad actualizada exitosamente."

    def eliminar_actividad(self, id_actividad):
        """Elimina de forma lógica una actividad."""
        usuario = self.auth.obtener_usuario_actual()
        if not self.auth.usuario_puede_escribir(usuario):
            return False, self.auth.mensaje_sin_permiso()
        self.actividad_dao.eliminar(id_actividad)
        return True, "Actividad eliminada correctamente."
