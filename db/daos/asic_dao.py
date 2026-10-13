"""
DAO para la tabla asic.
Migración a BaseDAO manteniendo API idéntica al legacy.
"""

from typing import Optional, Dict, Any, List

from ..base_dao import BaseDAO


class AsicDAO(BaseDAO):
    TABLA = "asic"
    CAMPOS = ["nombre"]
    CAMPO_ID = "id_asic"

    def obtener_todos(self) -> List[Dict[str, Any]]:
        return super().obtener_todos(orden_por="nombre")

    def obtener_por_id(self, id_asic: int) -> Optional[Dict[str, Any]]:
        return super().obtener_por_id(id_asic)

    def crear(self, codigo: Optional[str] = None, nombre: Optional[str] = None,
              municipio: str = "", parroquia: str = "") -> int:
        nombre_final = (nombre or codigo or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del ASIC es obligatorio.")

        return super().crear({"nombre": nombre_final})

    def actualizar(self, id_asic: int, codigo: Optional[str] = None,
                   nombre: Optional[str] = None, municipio: str = "",
                   parroquia: str = "") -> bool:
        nombre_final = (nombre or codigo or "").strip()
        if not nombre_final:
            raise ValueError("El nombre del ASIC es obligatorio.")

        return super().actualizar(id_asic, {"nombre": nombre_final})

    def desactivar(self, id_asic: int) -> bool:
        return self.eliminar(id_asic, borrado_fisico=True)
