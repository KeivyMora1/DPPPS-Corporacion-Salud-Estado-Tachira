"""
DAOs para tablas de catálogo: TipoActividad, TipoVoceria, Parroquia.
Migración a BaseDAO manteniendo API idéntica al legacy.
"""

from typing import Optional, Dict, Any, List

from ..base_dao import BaseDAO
from constants import (
    PARROQUIAS_POR_MUNICIPIO_TACHIRA,
    UBICACIONES_ASIC_PREDETERMINADAS,
)


class TipoActividadDAO(BaseDAO):
    """Data Access Object para tipos de actividad."""
    
    TABLA = "tipo_actividad"
    CAMPOS = ["nombre"]
    CAMPO_ID = "id_tipo"
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de actividad ordenados por nombre."""
        return super().obtener_todos(orden_por="nombre")
    
    def obtener_por_id(self, id_tipo: int) -> Optional[Dict[str, Any]]:
        """Obtiene un tipo por su ID."""
        return super().obtener_por_id(id_tipo)
    
    def crear(self, codigo: Optional[str] = None, nombre: Optional[str] = None) -> int:
        """Crea un nuevo tipo de actividad."""
        nombre_final = (nombre or codigo or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del tipo de actividad es obligatorio.")
        return super().crear({"nombre": nombre_final})
    
    def actualizar(self, id_tipo: int, codigo: Optional[str] = None, 
                   nombre: Optional[str] = None) -> bool:
        """Actualiza un tipo de actividad existente."""
        nombre_final = (nombre or codigo or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del tipo de actividad es obligatorio.")
        return super().actualizar(id_tipo, {"nombre": nombre_final})


class TipoVoceriaDAO(BaseDAO):
    """Data Access Object para tipos de vocería."""
    
    TABLA = "tipo_voceria"
    CAMPOS = ["nombre"]
    CAMPO_ID = "id_tipo"
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de vocería ordenados por nombre."""
        return super().obtener_todos(orden_por="nombre")
    
    def obtener_por_id(self, id_tipo: int) -> Optional[Dict[str, Any]]:
        """Obtiene un tipo por su ID."""
        return super().obtener_por_id(id_tipo)
    
    def crear(self, codigo: Optional[str] = None, nombre: Optional[str] = None) -> int:
        """Crea un nuevo tipo de vocería."""
        nombre_final = (nombre or codigo or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del tipo de vocería es obligatorio.")
        return super().crear({"nombre": nombre_final})
    
    def actualizar(self, id_tipo: int, codigo: Optional[str] = None, 
                   nombre: Optional[str] = None) -> bool:
        """Actualiza un tipo de vocería existente."""
        nombre_final = (nombre or codigo or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del tipo de vocería es obligatorio.")
        return super().actualizar(id_tipo, {"nombre": nombre_final})


class ParroquiaDAO:
    """
    DAO para parroquias/ubicaciones.
    No usa BaseDAO porque no hay tabla 'parroquia' en BD - usa constantes.
    """
    
    def obtener_todas(self) -> List[Dict[str, str]]:
        """Retorna todas las ubicaciones ASIC predeterminadas."""
        return [
            {"asic_nombre": asic, "municipio": municipio, "parroquia": parroquia}
            for asic, municipio, parroquia in UBICACIONES_ASIC_PREDETERMINADAS
        ]
    
    def listar_por_asic(self, id_asic: int) -> List[Dict[str, str]]:
        """
        Retorna la geografía estatal completa (municipios y parroquias de Táchira),
        independiente del ASIC seleccionado (legacy behavior).
        """
        return [
            {"municipio": municipio, "parroquia": parroquia}
            for municipio, parroquias in PARROQUIAS_POR_MUNICIPIO_TACHIRA.items()
            for parroquia in parroquias
        ]