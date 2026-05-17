# ============================================================
# controllers/catalogo_controller.py
# Controlador para los catálogos del sistema:
#   - ASIC (Áreas de Salud Integral Comunitaria)
#   - Tipos de Actividad
#
# Se encarga de validar los datos antes de guardarlos
# y de llamar a los DAOs correspondientes.
# ============================================================

from models.asic import AsicDAO
from models.tipo_actividad import TipoActividadDAO


class CatalogoController:
    """
    Maneja la lógica de negocio para los catálogos.
    Las vistas llaman a este controlador, no directamente a los DAOs.
    """

    def __init__(self):
        self.asic_dao = AsicDAO()
        self.tipo_dao = TipoActividadDAO()

    # ==================== ASIC ====================

    def listar_asic(self):
        """Retorna todos los ASIC activos."""
        return self.asic_dao.obtener_todos()

    def guardar_asic(self, codigo, nombre, municipio="", parroquia="", id_asic=None):
        """
        Crea o actualiza un ASIC según si id_asic viene con valor o no.
        Retorna: (True, "mensaje ok") o (False, "mensaje error")
        """
        codigo = codigo.strip().upper()
        nombre = nombre.strip()

        if not codigo:
            return False, "El codigo del ASIC es obligatorio."
        if not nombre:
            return False, "El nombre del ASIC es obligatorio."

        # Verificar código duplicado
        existente = self.asic_dao.obtener_por_codigo(codigo)
        if existente and existente["id_asic"] != id_asic:
            return False, f"Ya existe un ASIC con el codigo '{codigo}'."

        if id_asic is None:
            self.asic_dao.crear(codigo, nombre, municipio.strip(), parroquia.strip())
            return True, f"ASIC '{nombre}' creado correctamente."
        else:
            self.asic_dao.actualizar(id_asic, codigo, nombre, municipio.strip(), parroquia.strip())
            return True, f"ASIC '{nombre}' actualizado correctamente."

    def eliminar_asic(self, id_asic):
        """Desactiva un ASIC. Retorna (True, mensaje) o (False, error)."""
        asic = self.asic_dao.obtener_por_id(id_asic)
        if not asic:
            return False, "No se encontro el ASIC."
        self.asic_dao.desactivar(id_asic)
        return True, f"ASIC '{asic['nombre']}' eliminado correctamente."

    # ==================== TIPOS DE ACTIVIDAD ====================

    def listar_tipos(self):
        """Retorna todos los tipos de actividad activos."""
        return self.tipo_dao.obtener_todos()

    def guardar_tipo(self, codigo, nombre, descripcion="", id_tipo=None):
        """
        Crea o actualiza un tipo de actividad.
        Retorna: (True, "mensaje ok") o (False, "mensaje error")
        """
        codigo = codigo.strip().upper()
        nombre = nombre.strip()

        if not codigo:
            return False, "El codigo del tipo es obligatorio."
        if not nombre:
            return False, "El nombre del tipo es obligatorio."

        # Verificar código duplicado
        existente = self.tipo_dao.obtener_por_codigo(codigo)
        if existente and existente["id_tipo"] != id_tipo:
            return False, f"Ya existe un tipo con el codigo '{codigo}'."

        if id_tipo is None:
            self.tipo_dao.crear(codigo, nombre, descripcion.strip())
            return True, f"Tipo '{nombre}' creado correctamente."
        else:
            self.tipo_dao.actualizar(id_tipo, codigo, nombre, descripcion.strip())
            return True, f"Tipo '{nombre}' actualizado correctamente."

    def eliminar_tipo(self, id_tipo):
        """Desactiva un tipo de actividad. Retorna (True, mensaje) o (False, error)."""
        tipo = self.tipo_dao.obtener_por_id(id_tipo)
        if not tipo:
            return False, "No se encontro el tipo de actividad."
        self.tipo_dao.desactivar(id_tipo)
        return True, f"Tipo '{tipo['nombre']}' eliminado correctamente."
