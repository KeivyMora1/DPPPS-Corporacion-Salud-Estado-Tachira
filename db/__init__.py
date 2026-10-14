"""
Paquete db - Capa de acceso a datos del sistema DPPPS.

Este paquete proporciona acceso a datos y servicios para el sistema DPPPS.
Mantiene compatibilidad total con el código existente.

Estructura:
- db.connection: Pool de conexiones y context managers
- db.base_dao: Clase base genérica para DAOs
- db.daos: Implementaciones de Data Access Objects por entidad
- db.services: Lógica de negocio (auth, actividades, vocerías, reportes)
- db.validators: Validaciones centralizadas
- db.utils: Utilidades de conexión
"""

# ─── Exports explícitos de la nueva estructura ───
from .connection import (
    obtener_pool,
    reiniciar_pool,
    conexion,
    transaccion,
    obtener_conexion_directa,
    ejecutar_consulta,
)

from .base_dao import (
    BaseDAO,
    BaseDAOSinId,
)

from .daos import (
    UsuarioDAO,
    ActividadDAO,
    AsicDAO,
    TipoActividadDAO,
    TipoVoceriaDAO,
    MunicipioDAO,
    ParroquiaDAO,
    ComiteDAO,
    VoceriaDAO,
)

from .daos.usuario_dao import asegurar_esquema_autenticacion

from .utils import get_connection
from .validators import validar_archivo_excel, validar_correo
from .services import (
    AuthController,
    ActividadController,
    VoceriaController,
    ConsolidacionService,
    ExcelService,
    ExcelServiceVoceria,
    InformeWordService,
    ReporteSemanalService,
    build_voceria_template,
)
from .services.auth_service import sesion_actual
from .services.reportes import (
    COLUMNAS_REQUERIDAS,
    HEADER_ALIASES,
    PARTICIPANTES_CATEGORIAS,
)

# Re-exportar constantes históricas para compatibilidad con tests y módulos existentes
from constants import (
    MODO,
    DATABASE,
    TEMPLATE_PATH,
    VOCERIA_TEMPLATE_PATH,
    MAX_FILE_SIZE_MB,
    ALLOWED_EXTENSIONS,
    VOCERIA_CENTRO_DISPENSADOR_OPCIONES,
    ACTIVIDAD_ESTABLECIMIENTO_OPCIONES,
    EMAIL_REGEX,
    ASIC_PREDETERMINADOS,
    VOCERIA_ESTADO_OPCIONES,
    PARROQUIAS_POR_MUNICIPIO_TACHIRA,
    MUNICIPIOS_TACHIRA,
    ASIC_POR_MUNICIPIO,
    UBICACIONES_ASIC_PREDETERMINADAS,
    VOCERIA_MUNICIPIO_OPCIONES,
    VOCERIA_ASIC_OPCIONES,
    VOCERIA_TIPO_OPCIONES,
    VOCERIA_SEXO_OPCIONES,
    TIPOS_ACTIVIDAD_PREDETERMINADOS,
    APP_TITLE,
    APP_VERSION,
)

__all__ = [
    # Connection pool
    "obtener_pool",
    "reiniciar_pool",
    "conexion",
    "transaccion",
    "obtener_conexion_directa",
    "ejecutar_consulta",
    # Base DAO
    "BaseDAO",
    "BaseDAOSinId",
    # DAOs
    "UsuarioDAO",
    "ActividadDAO",
    "AsicDAO",
    "TipoActividadDAO",
    "TipoVoceriaDAO",
    "MunicipioDAO",
    "ParroquiaDAO",
    "ComiteDAO",
    "VoceriaDAO",
    # Schema setup
    "asegurar_esquema_autenticacion",
    # Utilities and validation
    "get_connection",
    "validar_archivo_excel",
    "validar_correo",
    # Services
    "AuthController",
    "ActividadController",
    "VoceriaController",
    "ConsolidacionService",
    "ExcelService",
    "ExcelServiceVoceria",
    "InformeWordService",
    "ReporteSemanalService",
    "build_voceria_template",
    "sesion_actual",
    # Excel import metadata
    "COLUMNAS_REQUERIDAS",
    "HEADER_ALIASES",
    "PARTICIPANTES_CATEGORIAS",
    # Constantes re-exportadas
    "MODO",
    "DATABASE",
    "TEMPLATE_PATH",
    "VOCERIA_TEMPLATE_PATH",
    "MAX_FILE_SIZE_MB",
    "ALLOWED_EXTENSIONS",
    "VOCERIA_CENTRO_DISPENSADOR_OPCIONES",
    "ACTIVIDAD_ESTABLECIMIENTO_OPCIONES",
    "EMAIL_REGEX",
    "ASIC_PREDETERMINADOS",
    "VOCERIA_ESTADO_OPCIONES",
    "PARROQUIAS_POR_MUNICIPIO_TACHIRA",
    "MUNICIPIOS_TACHIRA",
    "ASIC_POR_MUNICIPIO",
    "UBICACIONES_ASIC_PREDETERMINADAS",
    "VOCERIA_MUNICIPIO_OPCIONES",
    "VOCERIA_ASIC_OPCIONES",
    "VOCERIA_TIPO_OPCIONES",
    "VOCERIA_SEXO_OPCIONES",
    "TIPOS_ACTIVIDAD_PREDETERMINADOS",
    "APP_TITLE",
    "APP_VERSION",
]