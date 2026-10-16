import os
import re
import unicodedata
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from constants import TIPOS_ACTIVIDAD_PREDETERMINADOS
from utils import obtener_ruta_recurso


class InformeWordService:
    @property
    def PLANTILLA_INFORME_DOCX(self):
        return obtener_ruta_recurso("assets", "templates", "plantilla_reporte.docx")

    def generar_docx(self, datos: dict, ruta_salida: str) -> str:
        if not ruta_salida.lower().endswith(".docx"):
            ruta_salida = f"{ruta_salida}.docx"

        os.makedirs(os.path.dirname(ruta_salida) if os.path.dirname(ruta_salida) else ".", exist_ok=True)

        template_path = self.PLANTILLA_INFORME_DOCX
        if os.path.exists(template_path):
            with zipfile.ZipFile(template_path, "r") as src, zipfile.ZipFile(ruta_salida, "w", compression=zipfile.ZIP_DEFLATED) as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "word/document.xml":
                        data = self._word_template_con_fecha_actual(data)
                        data = self._word_template_con_datos(data, datos)
                    dst.writestr(info, data)
            return ruta_salida

        document_xml = self._word_document_xml(datos)
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
        core = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{titulo}</dc:title>
  <dc:creator>DPPPS</dc:creator>
  <cp:lastModifiedBy>DPPPS</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{fecha}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{fecha}</dcterms:modified>
</cp:coreProperties>'''.format(
            titulo=escape(datos.get("titulo", "Informe Consolidado").strip() or "Informe Consolidado"),
            fecha=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>DPPPS</Application>
</Properties>'''

        with zipfile.ZipFile(ruta_salida, "w", compression=zipfile.ZIP_DEFLATED) as archivo:
            archivo.writestr("[Content_Types].xml", content_types)
            archivo.writestr("_rels/.rels", rels)
            archivo.writestr("docProps/core.xml", core)
            archivo.writestr("docProps/app.xml", app)
            archivo.writestr("word/document.xml", document_xml)
            archivo.writestr("word/styles.xml", self._word_styles_xml())

        return ruta_salida

    @staticmethod
    def _normalizar_texto(valor: str) -> str:
        if not valor:
            return ""
        valor = unicodedata.normalize("NFKD", valor)
        valor = valor.encode("ascii", "ignore").decode("ascii")
        valor = valor.lower().strip()
        valor = re.sub(r"[^a-z0-9]+", " ", valor)
        return " ".join(valor.split())

    @staticmethod
    def _texto_parrafo(parrafo, ns: dict) -> str:
        return "".join((n.text or "") for n in parrafo.findall(".//w:t", ns))

    @staticmethod
    def _poner_texto_en_parrafo(parrafo, texto: str, ns: dict):
        nodos = parrafo.findall(".//w:t", ns)
        if not nodos:
            run = ET.SubElement(parrafo, f"{{{ns['w']}}}r")
            texto_node = ET.SubElement(run, f"{{{ns['w']}}}t")
            texto_node.text = str(texto)
            return
        for idx, nodo in enumerate(nodos):
            nodo.text = str(texto) if idx == 0 else ""

    def _word_template_con_fecha_actual(self, xml_bytes: bytes) -> bytes:
        root = ET.fromstring(xml_bytes)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        ]
        ahora = datetime.now()
        fecha_hoy = f"{ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"

        for parrafo in root.findall(".//w:p", ns):
            textos = [n for n in parrafo.findall(".//w:t", ns)]
            contenido = "".join((n.text or "") for n in textos)
            if "San Cristóbal, 6 de Marzo de 2026" not in contenido and "6 de Marzo de 2026" not in contenido:
                continue

            nuevo_contenido = contenido.replace("San Cristóbal, 6 de Marzo de 2026", f"San Cristóbal, {fecha_hoy}")
            nuevo_contenido = nuevo_contenido.replace("6 de Marzo de 2026", fecha_hoy)

            for nodo in textos:
                nodo.text = ""
            if textos:
                textos[0].text = nuevo_contenido
            break

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _word_template_con_datos(self, xml_bytes: bytes, datos: dict) -> bytes:
        root = ET.fromstring(xml_bytes)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        resumen_tipo = datos.get("resumen_por_tipo", []) or []
        tipo_lookup = {}
        for fila in resumen_tipo:
            nombre = str(fila.get("nombre") or "").strip()
            if not nombre:
                continue
            tipo_lookup[self._normalizar_texto(nombre)] = {
                "total_actividades": int(fila.get("total_actividades", 0) or 0),
                "total_participantes": int(fila.get("total_participantes", 0) or 0),
            }

        for _, nombre in TIPOS_ACTIVIDAD_PREDETERMINADOS:
            tipo_lookup.setdefault(self._normalizar_texto(nombre), {
                "total_actividades": 0,
                "total_participantes": 0,
            })

        vocerias = datos.get("vocerias", []) or []
        llave_actualizacion = self._normalizar_texto("Actualización de los comités de salud")
        tipo_lookup.setdefault(llave_actualizacion, {"total_actividades": 0, "total_participantes": 0})
        tipo_lookup[llave_actualizacion]["total_actividades"] = len(vocerias) or tipo_lookup[llave_actualizacion].get("total_actividades", 0)

        def get_valor(nombre: str, campo: str) -> int:
            clave = self._normalizar_texto(nombre)
            datos_tipo = tipo_lookup.get(clave, {"total_actividades": 0, "total_participantes": 0})
            return int(datos_tipo.get(campo, 0) or 0)

        def asignar_valores_fila(indice_fila: int, valores):
            filas = root.findall(".//w:tr", ns)
            if indice_fila >= len(filas):
                return
            celdas = filas[indice_fila].findall("./w:tc", ns)
            if len(celdas) < 2:
                return
            nodos = celdas[1].findall(".//w:t", ns)
            if not nodos:
                return
            nodos_numericos = [n for n in nodos if (n.text or "").strip().isdigit()]
            for nodo, valor in zip(nodos_numericos, valores):
                nodo.text = str(valor)
            for nodo in nodos_numericos[len(valores):]:
                nodo.text = "0"

        filas = root.findall(".//w:tr", ns)
        if len(filas) > 1:
            celdas = filas[1].findall("./w:tc", ns)
            if len(celdas) > 1:
                texto_eliminar = "Seguimiento a los Comités de Salud mediante las vocerías en salud comunal"
                parrafos_etiqueta = celdas[0].findall("./w:p", ns)
                indice_actualizacion = next(
                    (
                        indice for indice, parrafo in enumerate(parrafos_etiqueta)
                        if "Actualización de los comités de salud" in "".join(
                            (n.text or "") for n in parrafo.findall(".//w:t", ns)
                        )
                    ),
                    None,
                )
                if indice_actualizacion is not None:
                    for parrafo in parrafos_etiqueta[:indice_actualizacion]:
                        celdas[0].remove(parrafo)

                parrafos_valor = celdas[1].findall("./w:p", ns)
                indice_ultimo_numero = next(
                    (
                        indice for indice in range(len(parrafos_valor) - 1, -1, -1)
                        if any(
                            (n.text or "").strip().isdigit()
                            for n in parrafos_valor[indice].findall(".//w:t", ns)
                        )
                    ),
                    None,
                )
                if indice_ultimo_numero is not None:
                    for parrafo in parrafos_valor[:indice_ultimo_numero]:
                        celdas[1].remove(parrafo)

        salud = (get_valor("Salud toca tu puerta", "total_actividades"), get_valor("Salud toca tu puerta", "total_participantes"))
        sesiones = (get_valor("Sesiones educativas", "total_actividades"), get_valor("Sesiones educativas", "total_participantes"))
        comites_escuela = (get_valor("Los Comités de Salud van a la escuela", "total_actividades"), get_valor("Los Comités de Salud van a la escuela", "total_participantes"))
        promocion = (get_valor("Actividades de Promoción y Prevención Social", "total_actividades"), get_valor("Actividades de Promoción y Prevención Social", "total_participantes"))
        jornadas = (get_valor("Participación Activa en Jornadas", "total_actividades"), get_valor("Participación Activa en Jornadas", "total_participantes"))
        inmunizaciones = (get_valor("Participación Activa en Inmunizaciones", "total_actividades"), get_valor("Participación Activa en Inmunizaciones", "total_participantes"))
        entrevista = (get_valor("Entrevista servicio social", "total_actividades"), get_valor("Entrevista servicio social", "total_participantes"))
        actividades_asic = (
            int(datos.get("total_actividades", 0) or 0),
            int(datos.get("total_participantes", 0) or 0),
        )

        asignar_valores_fila(1, [
            get_valor("Actualización de los comités de salud", "total_actividades"),
        ])
        asignar_valores_fila(2, [salud[0], salud[1]])
        asignar_valores_fila(3, [sesiones[0], sesiones[1], comites_escuela[0], comites_escuela[1]])
        asignar_valores_fila(4, [promocion[0], promocion[1], jornadas[0], jornadas[1], inmunizaciones[0], inmunizaciones[1]])
        asignar_valores_fila(5, [entrevista[0], entrevista[1], actividades_asic[0]])

        tipos_fijos = {
            self._normalizar_texto(nombre)
            for _, nombre in TIPOS_ACTIVIDAD_PREDETERMINADOS
        }
        tipos_fijos.add(llave_actualizacion)
        tipos_incluidos = set(tipos_fijos)
        tabla_resumen = root.find(".//w:tbl", ns)
        fila_base = root.findall(".//w:tbl/w:tr", ns)[2]

        for fila in resumen_tipo:
            nombre = str(fila.get("nombre") or "").strip()
            clave = self._normalizar_texto(nombre)
            if not nombre or clave in tipos_incluidos:
                continue

            fila_personalizada = deepcopy(fila_base)
            celdas = fila_personalizada.findall("./w:tc", ns)
            parrafo_nombre = next(
                (
                    parrafo for parrafo in celdas[0].findall("./w:p", ns)
                    if "salud toca tu puerta" in self._normalizar_texto(
                        self._texto_parrafo(parrafo, ns)
                    )
                ),
                None,
            )
            if parrafo_nombre is not None:
                self._poner_texto_en_parrafo(parrafo_nombre, nombre, ns)

            nodos_numericos = [
                nodo for nodo in celdas[1].findall(".//w:t", ns)
                if (nodo.text or "").strip().isdigit()
            ]
            valores = [
                int(fila.get("total_actividades", 0) or 0),
                int(fila.get("total_participantes", 0) or 0),
            ]
            for nodo, valor in zip(nodos_numericos, valores):
                nodo.text = str(valor)

            tabla_resumen.append(fila_personalizada)
            tipos_incluidos.add(clave)

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _word_document_xml(self, datos: dict) -> str:
        def p(texto: str, negrita: bool = False) -> str:
            texto_escapado = escape(texto)
            estilo = '<w:pPr><w:rPr><w:b/></w:rPr></w:pPr>' if negrita else ''
            return f'<w:p>{estilo}<w:r><w:t xml:space="preserve">{texto_escapado}</w:t></w:r></w:p>'

        lineas = [
            p("DPPPS N°___", True),
            p(datos.get("titulo", "Informe Consolidado"), True),
            p(self._subtitulo_periodo(datos) or "Período no definido"),
            p(f"ASIC: {datos.get('asic_nombre') or 'Todos los ASIC'}"),
            p(f"Total de actividades: {datos.get('total_actividades', 0)}"),
            p(f"Total de participantes: {datos.get('total_participantes', 0)}"),
        ]

        if datos.get("resumen_por_asic"):
            lineas.append(p("Resumen por ASIC:", True))
            for fila in datos["resumen_por_asic"]:
                nombre = fila.get("nombre") or fila.get("asic_nombre", "")
                lineas.append(
                    p(f"- {nombre}: {fila.get('total_actividades', 0)} actividades / {fila.get('total_participantes', 0)} participantes")
                )

        if datos.get("resumen_por_tipo"):
            lineas.append(p("Resumen por tipo de actividad:", True))
            for fila in datos["resumen_por_tipo"]:
                nombre = fila.get("nombre") or ""
                lineas.append(
                    p(f"- {nombre}: {fila.get('total_actividades', 0)} actividades / {fila.get('total_participantes', 0)} participantes")
                )

        if datos.get("actividades"):
            lineas.append(p("Detalle de actividades:", True))
            for i, act in enumerate(datos["actividades"], start=1):
                fecha_ini = act.get("fecha") or ""
                fecha_fin = act.get("fecha_fin") or fecha_ini
                tema = str(act.get("tema") or "").strip()
                lineas.append(
                    p(
                        f"{i}. {act.get('asic_nombre', '')} - {act.get('tipo_nombre', '')} - "
                        f"{fecha_ini} a {fecha_fin} - "
                        f"Participantes: {act.get('participantes', 0)} - "
                        f"Tema: {tema}"
                    )
                )

        obs = (datos.get("observaciones") or "").strip()
        if obs:
            lineas.append(p("Observaciones:", True))
            lineas.append(p(obs))

        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
            'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
            'xmlns:o="urn:schemas-microsoft-com:office:office" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
            'xmlns:v="urn:schemas-microsoft-com:vml" '
            'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
            'xmlns:w10="urn:schemas-microsoft-com:office:word" '
            'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
            'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
            'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
            'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
            'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
            'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
            'mc:Ignorable="w14 w15 wp14">'
            '<w:body>' + ''.join(lineas) + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'
        )

    def _word_styles_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:qFormat/></w:style>
</w:styles>'''
