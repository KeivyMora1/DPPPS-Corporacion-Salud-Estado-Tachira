import os
import zipfile
from datetime import date, timedelta
from typing import Dict, List
from xml.etree import ElementTree as ET

from ...daos import ActividadDAO, AsicDAO
from utils import obtener_ruta_recurso


MESES_ESPANOL = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]


class ReporteSemanalService:
    """Servicio para la consolidación y generación del reporte semanal en Word."""

    @property
    def PLANTILLA_DOCX(self) -> str:
        return obtener_ruta_recurso("assets", "templates", "plantilla_reporte_semanal.docx")

    @classmethod
    def obtener_semana_de_fecha(cls, d: date) -> Dict:
        """
        Dada una fecha cualquiera, calcula la semana laboral completa de 7 días
        (de Lunes a Domingo) y su número de semana correspondiente dentro del mes.
        """
        lunes = d - timedelta(days=d.weekday())
        domingo = lunes + timedelta(days=6)

        # Usamos el jueves como día central para determinar el mes y año representativo
        jueves = lunes + timedelta(days=3)
        numero_semana = (jueves.day - 1) // 7 + 1

        etiqueta = f"Semana {numero_semana} ({lunes.strftime('%d/%m')} al {domingo.strftime('%d/%m')})"

        return {
            "numero": numero_semana,
            "fecha_inicio": lunes,
            "fecha_fin": domingo,
            "etiqueta": etiqueta,
            "mes_nombre": MESES_ESPANOL[jueves.month - 1],
            "year": jueves.year,
            "month": jueves.month,
        }

    def obtener_ranking_semanal(self, fecha_inicio: date, fecha_fin: date) -> List[Dict]:
        """
        Calcula la cantidad de actividades por cada ASIC en el rango de fechas especificado.
        Retorna la lista de ASICs ordenada descendentemente por cantidad de actividades.
        """
        todos_asics = AsicDAO().obtener_todos()


        filtros = {
            "fecha_desde": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_hasta": fecha_fin.strftime("%Y-%m-%d"),
        }
        actividades = ActividadDAO().obtener_todas(filtros)

        conteo_por_asic = {}
        for act in actividades:
            id_asic = act.get("id_asic")
            conteo_por_asic[id_asic] = conteo_por_asic.get(id_asic, 0) + 1

        ranking = []
        for asic in todos_asics:
            aid = asic["id_asic"]
            ranking.append({
                "id_asic": aid,
                "nombre": asic["nombre"],
                "total_actividades": conteo_por_asic.get(aid, 0),
            })

        # Ordenar descendente por total_actividades, y en caso de empate alfabéticamente por nombre
        ranking.sort(key=lambda x: (-x["total_actividades"], x["nombre"]))
        return ranking

    def generar_docx(self, mes_nombre: str, numero_semana: int, ranking: list, ruta_salida: str) -> str:
        """
        Genera el documento Word del reporte semanal basado en la plantilla plantilla_reporte_semanal.docx.
        Modifica el encabezado 'MES (SEMANA 1)' por f'{mes_nombre.upper()} (SEMANA {numero_semana})'
        y llena la tabla con los ASICs ordenados por actividades.
        """
        if not ruta_salida.lower().endswith(".docx"):
            ruta_salida = f"{ruta_salida}.docx"

        os.makedirs(os.path.dirname(ruta_salida) if os.path.dirname(ruta_salida) else ".", exist_ok=True)

        template_path = self.PLANTILLA_DOCX
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"No se encontró la plantilla semanal en: {template_path}")

        with zipfile.ZipFile(template_path, "r") as src, zipfile.ZipFile(ruta_salida, "w", compression=zipfile.ZIP_DEFLATED) as dst:
            for info in src.infolist():
                data = src.read(info.filename)
                if info.filename == "word/document.xml":
                    data = self._procesar_xml_semanal(data, mes_nombre, numero_semana, ranking)
                dst.writestr(info, data)

        return ruta_salida

    def _procesar_xml_semanal(self, xml_bytes: bytes, mes_nombre: str, numero_semana: int, ranking: list) -> bytes:
        root = ET.fromstring(xml_bytes)
        ns_w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        ns = {"w": ns_w}

        texto_reemplazo_encabezado = f"{mes_nombre.upper()} (SEMANA {numero_semana})"

        # Reemplazar el título de la columna 2 en el encabezado
        for p in root.findall(".//w:p", ns):
            textos = p.findall(".//w:t", ns)
            full_t = "".join(t.text or "" for t in textos)
            if "MES (SEMANA 1)" in full_t:
                for t in textos:
                    if "MES (SEMANA 1)" in (t.text or ""):
                        t.text = t.text.replace("MES (SEMANA 1)", texto_reemplazo_encabezado)

        # Rellenar la tabla
        tbl = root.find(".//w:tbl", ns)
        if tbl is not None:
            rows = tbl.findall(".//w:tr", ns)
            # Fila 0 es vacía, Fila 1 es encabezado, Filas 2..26 son las 25 filas de datos
            for idx, item in enumerate(ranking):
                fila_idx = idx + 2
                if fila_idx >= len(rows):
                    break
                celdas = rows[fila_idx].findall("./w:tc", ns)
                if len(celdas) >= 2:
                    # Columna 1 (índice 0): Nombre del ASIC
                    self._asignar_texto_celda(celdas[0], item["nombre"], ns)
                    # Columna 2 (índice 1): Cantidad de actividades
                    self._asignar_texto_celda(celdas[1], str(item["total_actividades"]), ns)

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _asignar_texto_celda(celda, texto: str, ns: dict):
        p = celda.find("./w:p", ns)
        if p is None:
            p = ET.SubElement(celda, f"{{{ns['w']}}}p")
        # Limpiar nodos de texto existentes si los hay
        nodos_t = p.findall(".//w:t", ns)
        if nodos_t:
            for idx, n in enumerate(nodos_t):
                n.text = texto if idx == 0 else ""
        else:
            run = ET.SubElement(p, f"{{{ns['w']}}}r")
            t = ET.SubElement(run, f"{{{ns['w']}}}t")
            t.text = str(texto)


__all__ = ["ReporteSemanalService", "MESES_ESPANOL"]
