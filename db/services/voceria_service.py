import re
from datetime import date, datetime, timedelta

from constants import (
    MUNICIPIOS_TACHIRA,
    VOCERIA_CENTRO_DISPENSADOR_OPCIONES,
    VOCERIA_ESTADO_OPCIONES,
)
from ..daos import AsicDAO, MunicipioDAO, ParroquiaDAO, TipoVoceriaDAO, VoceriaDAO
from ..validators import validar_correo
from .auth_service import AuthController

class VoceriaController:
    """Maneja la lógica de negocio para vocerías CS."""
    def __init__(self):
        self.voceria_dao = VoceriaDAO()
        self.tipo_voceria_dao = TipoVoceriaDAO()
        self.asic_dao = AsicDAO()
        self.municipio_dao = MunicipioDAO()
        self.parroquia_dao = ParroquiaDAO()
        self.auth = AuthController()

    def _parsear_fecha(self, valor):
        """Acepta objetos date/datetime o strings YYYY-MM-DD / DD/MM/YYYY."""
        if valor is None:
            return None
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        texto = str(valor).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(texto, fmt).date()
            except ValueError:
                pass
        return None

    def listar_vocerias(self, filtros=None):
        return self.voceria_dao.obtener_todas(filtros)

    def listar_asics(self):
        asics = self.asic_dao.obtener_todos()
        return asics

    def listar_ubicaciones_asic(self):
        return self.parroquia_dao.obtener_todas()

    def listar_tipos_voceria(self):
        tipos = self.tipo_voceria_dao.obtener_todos()
        return tipos

    def listar_municipios(self):
        """Retorna todos los municipios desde la base de datos."""
        return self.municipio_dao.obtener_todos()

    def listar_parroquias(self, id_o_nombre_municipio=None):
        """Retorna las parroquias desde la base de datos, opcionalmente filtradas por municipio."""
        if id_o_nombre_municipio:
            return self.parroquia_dao.listar_por_municipio(id_o_nombre_municipio)
        return self.parroquia_dao.listar_por_asic()

    def listar_ubicaciones_asic(self):
        return self.parroquia_dao.obtener_todas()

    def obtener_voceria_completa(self, id_voceria):
        """Obtiene vocería con todos sus items (voceros)."""
        return self.voceria_dao.obtener_con_items(id_voceria)

    def guardar_voceria(self, id_asic, id_tipo=None, estado=None, municipio=None, parroquia=None,
                         centro_dispensador=None, nombre_centro=None, nombre_comite=None, items=None, id_voceria=None,
                         connection=None):
        """
        Guarda vocería con sus items (voceros).
        items: lista de dicts con los campos de cada vocero
        centro_dispensador, nombre_centro, nombre_comite: campos generales que aplican a toda la vocería
        """
        if items is None:
            items = []

        estado = str(estado or "").strip()
        municipio = str(municipio or "").strip()
        parroquia = str(parroquia or "").strip()
        centro_dispensador = str(centro_dispensador or "").strip()
        nombre_centro = str(nombre_centro or "").strip()
        nombre_comite = str(nombre_comite or "").strip()

        if not id_asic:
            return False, "Debes seleccionar un ASIC."
        campos_generales = [
            ("Estado", estado, 100), ("Municipio", municipio, 100),
            ("Parroquia", parroquia, 100), ("Centro dispensador", centro_dispensador, 100),
            ("Nombre del centro", nombre_centro, 200), ("Nombre del comité", nombre_comite, 200),
        ]
        for etiqueta, valor, maximo in campos_generales:
            texto = str(valor or "").strip()
            if not texto or texto == "Parroquia":
                return False, f"{etiqueta} es obligatorio."
            if len(texto) > maximo or any(ord(caracter) < 32 for caracter in texto):
                return False, f"{etiqueta} no puede superar {maximo} caracteres ni contener controles."
        if estado not in VOCERIA_ESTADO_OPCIONES:
            return False, "Debes seleccionar un estado válido."
        _municipio_dao = getattr(self, "municipio_dao", None)
        if _municipio_dao is not None:
            municipios_validos = {m["nombre"] for m in _municipio_dao.obtener_todos()}
        else:
            municipios_validos = set(MUNICIPIOS_TACHIRA)
        if municipio not in municipios_validos:
            return False, "Debes seleccionar un municipio válido."
        ubicaciones_asic = self.parroquia_dao.listar_por_asic(id_asic)
        if not any(
            ubicacion["municipio"] == municipio
            and ubicacion["parroquia"] == parroquia
            for ubicacion in ubicaciones_asic
        ):
            return False, "La parroquia debe corresponder al municipio seleccionado."
        if centro_dispensador not in VOCERIA_CENTRO_DISPENSADOR_OPCIONES:
            return False, "Debes seleccionar un centro dispensador válido."
        if not items:
            return False, "Debe agregar al menos 7 vocerías (máx. 10)."
        if len(items) < 7:
            return False, f"Debe agregar al menos 7 vocerías (actual: {len(items)})."
        if len(items) > 10:
            return False, f"Máximo 10 vocerías permitidas (actual: {len(items)})."

        tipos_voceria = self.tipo_voceria_dao.obtener_todos()
        tipos_validos = {int(tipo["id_tipo"]) for tipo in tipos_voceria}
        if not id_tipo and tipos_voceria:
            id_tipo = tipos_voceria[0]["id_tipo"]
        try:
            id_tipo = int(id_tipo)
        except (TypeError, ValueError):
            return False, "Debes seleccionar un tipo de vocería."
        if id_tipo not in tipos_validos:
            return False, "Debes seleccionar un tipo de vocería válido."

        # Validar TODOS los campos en cada item (sin centro_dispensador, nombre_centro, nombre_comite que ahora son generales)
        for idx, item in enumerate(items, start=1):
            nombres = str(item.get("nombres") or "").strip()
            if not nombres:
                return False, f"Vocería #{idx}: Nombres y Apellidos son obligatorios."
            if not 5 <= len(nombres) <= 40:
                return False, f"Vocería #{idx}: Nombres y Apellidos debe tener entre 5 y 40 caracteres."
            if any(caracter.isdigit() or ord(caracter) < 32 for caracter in nombres):
                return False, f"Vocería #{idx}: Nombres y Apellidos no puede contener números ni controles."
            if not item.get("ci") or not str(item.get("ci")).strip():
                return False, f"Vocería #{idx}: C.I. es obligatoria."
            ci = str(item.get("ci")).strip()
            ci_digitos = ci.replace(",", "")
            formato_ci_valido = bool(re.fullmatch(r"(?:\d{7,8}|\d{1,2}(?:,\d{3}){2})", ci))
            if not formato_ci_valido or not 7 <= len(ci_digitos) <= 8:
                return False, f"Vocería #{idx}: La C.I. debe tener entre 7 y 8 dígitos."
            telefono = str(item.get("telefono") or "").strip()
            if not telefono:
                return False, f"Vocería #{idx}: Teléfono es obligatorio."
            if not telefono.isdigit() or not 11 <= len(telefono) <= 12:
                return False, f"Vocería #{idx}: El teléfono debe tener entre 11 y 12 dígitos."
            fecha_nacimiento = self._parsear_fecha(item.get("fecha_nacimiento"))
            if not fecha_nacimiento:
                return False, f"Vocería #{idx}: Fecha de Nacimiento es obligatoria."
            hoy = date.today()
            edad_por_fecha = hoy.year - fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
            )
            if not 18 <= edad_por_fecha <= 99:
                return False, f"Vocería #{idx}: La persona debe tener entre 18 y 99 años según su fecha de nacimiento."
            edad = str(item.get("edad") or "").strip()
            if not edad:
                return False, f"Vocería #{idx}: Edad es obligatoria."
            if not edad.isdigit() or len(edad) > 2 or not 18 <= int(edad) <= 99:
                return False, f"Vocería #{idx}: La edad debe estar entre 18 y 99 años."
            if int(edad) != edad_por_fecha:
                return False, f"Vocería #{idx}: La edad no coincide con la fecha de nacimiento."
            try:
                id_tipo_item = int(item.get("id_tipo_voceria"))
            except (TypeError, ValueError):
                id_tipo_item = None
            if id_tipo_item not in tipos_validos:
                return False, f"Vocería #{idx}: Debe seleccionar una vocería."
            if item.get("sexo") not in ("M", "F"):
                return False, f"Vocería #{idx}: Debe seleccionar un sexo válido."
            profesion = str(item.get("profesion") or "").strip()
            if not profesion:
                return False, f"Vocería #{idx}: Profesión/Oficio es obligatoria."
            if not 3 <= len(profesion) <= 40:
                return False, f"Vocería #{idx}: Profesión/Oficio debe tener entre 3 y 40 caracteres."
            correo = str(item.get("correo") or "").strip()
            if not correo:
                return False, f"Vocería #{idx}: Correo electrónico es obligatorio."
            if not validar_correo(correo):
                return False, f"Vocería #{idx}: Correo electrónico no válido."
            if not item.get("fechas_eleccion") or not str(item.get("fechas_eleccion")).strip() or str(item.get("fechas_eleccion")).strip() == "AAAA-MM-DD":
                return False, f"Vocería #{idx}: Fechas de Elección es obligatoria."
            fecha_eleccion = self._parsear_fecha(item.get("fechas_eleccion"))
            if not fecha_eleccion:
                return False, f"Vocería #{idx}: La fecha de elección no es válida."
            if fecha_eleccion > date.today():
                return False, f"Vocería #{idx}: La fecha de elección no puede ser futura."
            hace_dos_anos = date.today() - timedelta(days=730)
            if fecha_eleccion < hace_dos_anos:
                return False, f"Vocería #{idx}: La fecha de elección ({item.get('fechas_eleccion')}) tiene más de 2 años de antigüedad."

        id_usuario = self.auth.obtener_usuario_actual()
        if not id_usuario:
            return False, "No hay una sesion de usuario activa."
        if not self.auth.usuario_puede_escribir(id_usuario):
            return False, self.auth.mensaje_sin_permiso()
        id_usuario_registro = id_usuario["id_usuario"]

        try:
            if id_voceria is None:
                self.voceria_dao.crear(id_asic, id_tipo, id_usuario_registro, estado, municipio, parroquia,
                                       centro_dispensador, nombre_centro, nombre_comite, items, connection=connection)
                return True, "Vocería registrada correctamente."
            else:
                self.voceria_dao.actualizar(id_voceria, id_asic, id_tipo, estado, municipio, parroquia,
                                            centro_dispensador, nombre_centro, nombre_comite, items)
                return True, "Vocería actualizada correctamente."
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"

    def eliminar_voceria(self, id_comite):
        """Elimina un comité y sus vocerías asociadas (soft delete)."""
        usuario = self.auth.obtener_usuario_actual()
        if not self.auth.usuario_puede_escribir(usuario):
            return False, self.auth.mensaje_sin_permiso()
        self.voceria_dao.eliminar(id_comite)
        return True, "Vocería eliminada correctamente."
