"""
DAOs para tablas de catálogo: TipoActividad, TipoVoceria, Parroquia.
Migración a BaseDAO manteniendo API idéntica al legacy.
"""

from typing import Optional, Dict, Any, List

from ..base_dao import BaseDAO
from ..connection import ejecutar_consulta
from constants import (
    MUNICIPIOS_TACHIRA,
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


class MunicipioDAO(BaseDAO):
    """Data Access Object para municipios."""
    
    TABLA = "municipio"
    CAMPOS = ["nombre"]
    CAMPO_ID = "id_municipio"
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los municipios ordenados alfabéticamente."""
        try:
            return super().obtener_todos(orden_por="nombre")
        except Exception:
            return [{"id_municipio": i, "nombre": m} for i, m in enumerate(MUNICIPIOS_TACHIRA, 1)]
    
    def obtener_por_id(self, id_municipio: int) -> Optional[Dict[str, Any]]:
        """Obtiene un municipio por su ID."""
        return super().obtener_por_id(id_municipio)
    
    def obtener_por_nombre(self, nombre: str) -> Optional[Dict[str, Any]]:
        """Busca un municipio por su nombre exacto."""
        nombre_limpio = (nombre or "").strip()
        if not nombre_limpio:
            return None
        try:
            return self.obtener_uno("nombre = %s", (nombre_limpio,))
        except Exception:
            if nombre_limpio in MUNICIPIOS_TACHIRA:
                return {"id_municipio": MUNICIPIOS_TACHIRA.index(nombre_limpio) + 1, "nombre": nombre_limpio}
            return None
    
    def crear(self, nombre: str) -> int:
        """Crea un nuevo municipio."""
        nombre_final = (nombre or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del municipio es obligatorio.")
        return super().crear({"nombre": nombre_final})
    
    def actualizar(self, id_municipio: int, nombre: str) -> bool:
        """Actualiza el nombre de un municipio existente."""
        nombre_final = (nombre or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del municipio es obligatorio.")
        return super().actualizar(id_municipio, {"nombre": nombre_final})


class ParroquiaDAO(BaseDAO):
    """Data Access Object para parroquias y ubicaciones geográficas."""
    
    TABLA = "parroquia"
    CAMPOS = ["id_municipio", "nombre"]
    CAMPO_ID = "id_parroquia"
    
    def obtener_todas(self) -> List[Dict[str, Any]]:
        """
        Retorna todas las ubicaciones (asic, municipio, parroquia).
        Consulta la BD con JOIN entre parroquia y municipio.
        """
        try:
            sql = """
                SELECT p.id_parroquia, p.id_municipio, p.nombre AS parroquia, m.nombre AS municipio
                FROM parroquia p
                JOIN municipio m ON m.id_municipio = p.id_municipio
                ORDER BY m.nombre, p.nombre
            """
            filas = ejecutar_consulta(sql, obtener_todos=True) or []
            if filas:
                from .asic_dao import AsicDAO
                asics = AsicDAO().obtener_todos() or []
                if not asics:
                    from constants import ASIC_PREDETERMINADOS
                    asics = [{"nombre": nom} for _, nom in ASIC_PREDETERMINADOS]
                
                resultado = []
                for a in asics:
                    for f in filas:
                        resultado.append({
                            "id_parroquia": f["id_parroquia"],
                            "id_municipio": f["id_municipio"],
                            "asic_nombre": a["nombre"],
                            "municipio": f["municipio"],
                            "parroquia": f["parroquia"],
                        })
                return resultado
        except Exception:
            pass
        
        return [
            {"asic_nombre": asic, "municipio": municipio, "parroquia": parroquia}
            for asic, municipio, parroquia in UBICACIONES_ASIC_PREDETERMINADAS
        ]
    
    def listar_por_asic(self, id_asic: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retorna la geografía estatal completa (municipios y parroquias de Táchira)
        consultada desde las tablas municipio y parroquia de la base de datos.
        """
        try:
            sql = """
                SELECT p.id_parroquia, p.id_municipio, p.nombre AS parroquia, m.nombre AS municipio
                FROM parroquia p
                JOIN municipio m ON m.id_municipio = p.id_municipio
                ORDER BY m.nombre, p.nombre
            """
            filas = ejecutar_consulta(sql, obtener_todos=True) or []
            if filas:
                return [
                    {
                        "id_parroquia": f["id_parroquia"],
                        "id_municipio": f["id_municipio"],
                        "municipio": f["municipio"],
                        "parroquia": f["parroquia"],
                    }
                    for f in filas
                ]
        except Exception:
            pass
        
        return [
            {"municipio": municipio, "parroquia": parroquia}
            for municipio, parroquias in PARROQUIAS_POR_MUNICIPIO_TACHIRA.items()
            for parroquia in parroquias
        ]
    
    def listar_por_municipio(self, id_o_nombre: Any) -> List[Dict[str, Any]]:
        """Retorna las parroquias pertenecientes a un municipio (por ID o por nombre)."""
        try:
            if isinstance(id_o_nombre, int) or (isinstance(id_o_nombre, str) and id_o_nombre.isdigit()):
                sql = """
                    SELECT p.id_parroquia, p.id_municipio, p.nombre AS parroquia, m.nombre AS municipio
                    FROM parroquia p
                    JOIN municipio m ON m.id_municipio = p.id_municipio
                    WHERE p.id_municipio = %s
                    ORDER BY p.nombre
                """
                return ejecutar_consulta(sql, (int(id_o_nombre),), obtener_todos=True) or []
            else:
                sql = """
                    SELECT p.id_parroquia, p.id_municipio, p.nombre AS parroquia, m.nombre AS municipio
                    FROM parroquia p
                    JOIN municipio m ON m.id_municipio = p.id_municipio
                    WHERE m.nombre = %s
                    ORDER BY p.nombre
                """
                return ejecutar_consulta(sql, (str(id_o_nombre).strip(),), obtener_todos=True) or []
        except Exception:
            pass
        
        nombre_mun = str(id_o_nombre).strip()
        parrs = PARROQUIAS_POR_MUNICIPIO_TACHIRA.get(nombre_mun, [])
        return [{"municipio": nombre_mun, "parroquia": p} for p in parrs]
    
    def crear(self, id_municipio: int, nombre: str) -> int:
        """Crea una nueva parroquia asociada a un municipio."""
        nombre_final = (nombre or "").strip()
        if not nombre_final:
            raise ValueError("El nombre de la parroquia es obligatorio.")
        return super().crear({"id_municipio": id_municipio, "nombre": nombre_final})
    
    def actualizar(self, id_parroquia: int, id_municipio: Optional[int] = None,
                   nombre: Optional[str] = None) -> bool:
        """Actualiza una parroquia existente."""
        datos = {}
        if id_municipio is not None:
            datos["id_municipio"] = id_municipio
        if nombre is not None:
            nombre_final = nombre.strip()
            if not nombre_final:
                raise ValueError("El nombre de la parroquia no puede estar vacío.")
            datos["nombre"] = nombre_final
        if not datos:
            return False
        return super().actualizar(id_parroquia, datos)