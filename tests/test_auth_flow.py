import re
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

from db import AuthController, PDFService, TIPOS_ACTIVIDAD_PREDETERMINADOS


def test_generar_codigo_verificacion_es_numero_de_6_digitos():
    controller = AuthController()
    codigo = controller._generar_codigo()

    assert codigo.isdigit()
    assert len(codigo) == 6


def test_registrar_usuario_envia_codigo_y_marca_cuenta_no_verificada(monkeypatch):
    controller = AuthController()
    captured = {}

    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_por_email",
        lambda email: None,
    )
    monkeypatch.setattr(
        controller.usuario_dao,
        "crear",
        lambda **kwargs: 7,
    )

    def fake_enviar(email, codigo, tipo):
        captured["email"] = email
        captured["codigo"] = codigo
        captured["tipo"] = tipo
        return True

    monkeypatch.setattr(controller, "_enviar_codigo_por_email", fake_enviar)

    resultado = controller.registrar_usuario("Ana", "García", "ana@test.com", "Pass123!")

    assert resultado["success"] is True
    assert captured["email"] == "ana@test.com"
    assert captured["tipo"] == "verificacion"
    assert len(captured["codigo"]) == 6
    assert captured["codigo"].isdigit()


def test_login_rechaza_usuario_no_verificado(monkeypatch):
    controller = AuthController()

    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_por_email",
        lambda email: {
            "id_usuario": 1,
            "email": "ana@test.com",
            "password_hash": "$2b$12$abc",
            "nombre_completo": "Ana García",
            "email_verificado": False,
            "activo": True,
        },
    )

    monkeypatch.setattr(
        controller.usuario_dao,
        "verificar_password",
        lambda password_plano, password_hash: True,
    )

    assert controller.login("ana@test.com", "Pass123!") is False


def test_generar_word_crea_archivo_docx_con_contenido(tmp_path):
    datos = {
        "titulo": "Informe de prueba",
        "fecha_inicio": "2026-09-01",
        "fecha_fin": "2026-09-30",
        "total_actividades": 2,
        "total_participantes": 18,
        "resumen_por_asic": [
            {"nombre": "ASIC-01", "total_actividades": 1, "total_participantes": 8},
            {"nombre": "ASIC-02", "total_actividades": 1, "total_participantes": 10},
        ],
        "resumen_por_tipo": [
            {"nombre": "Salud toca tu puerta", "total_actividades": 2, "total_participantes": 18},
        ],
        "actividades": [
            {
                "asic_nombre": "ASIC-01",
                "tipo_nombre": "Salud toca tu puerta",
                "fecha_inicio": "2026-09-05",
                "fecha_fin": "2026-09-05",
                "participantes": 8,
                "descripcion": "Visita domiciliaria y charlas educativas.",
            }
        ],
        "observaciones": "Se adjunta el consolidado del mes.",
    }

    ruta = tmp_path / "informe_prueba.docx"
    resultado = PDFService().generar_word(datos, str(ruta))

    assert resultado == str(ruta)
    assert ruta.exists()
    assert zipfile.is_zipfile(ruta)

    with zipfile.ZipFile(ruta) as archivo:
        assert "word/document.xml" in archivo.namelist()
        contenido = archivo.read("word/document.xml").decode("utf-8", errors="ignore")
        assert "DPPPS N°___" in contenido
        assert "DPPPS N° 058" not in contenido
        assert "Oficio de entrega de informe de FEBRERO 2026" in contenido or "FEBRERO" in contenido


def test_generar_word_actualiza_fecha_de_cabecera_con_la_fecha_actual(tmp_path):
    datos = {
        "titulo": "Informe de prueba",
        "fecha_inicio": "2026-09-01",
        "fecha_fin": "2026-09-30",
        "total_actividades": 2,
        "total_participantes": 18,
        "resumen_por_tipo": [
            {"nombre": "Salud toca tu puerta", "total_actividades": 2, "total_participantes": 18},
        ],
    }

    ruta = tmp_path / "informe_fecha.docx"
    PDFService().generar_word(datos, str(ruta))

    with zipfile.ZipFile(ruta) as archivo:
        contenido = archivo.read("word/document.xml").decode("utf-8", errors="ignore")

    ahora = __import__("datetime").datetime.now()
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ]
    fecha_esperada = f"{ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"

    assert "San Cristóbal" in contenido
    assert f"San Cristóbal, {fecha_esperada}" in contenido
    assert "6 de Marzo de 2026" not in contenido


def test_generar_word_inyecta_totales_reales_en_la_plantilla(tmp_path):
    datos = {
        "titulo": "Informe de prueba",
        "fecha_inicio": "2026-09-01",
        "fecha_fin": "2026-09-30",
        "total_actividades": 2,
        "total_participantes": 18,
        "resumen_por_tipo": [
            {"nombre": "Salud toca tu puerta", "total_actividades": 2, "total_participantes": 18},
        ],
    }

    ruta = tmp_path / "informe_totales.docx"
    resultado = PDFService().generar_word(datos, str(ruta))

    assert resultado == str(ruta)
    with zipfile.ZipFile(ruta) as archivo:
        contenido = archivo.read("word/document.xml")
        xml = ET.fromstring(contenido)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        textos = [n.text or "" for n in xml.findall(".//w:t", ns)]

        def normalizar(valor):
            valor = unicodedata.normalize("NFKD", valor)
            valor = valor.encode("ascii", "ignore").decode("ascii")
            valor = valor.lower().strip()
            valor = re.sub(r"[^a-z0-9]+", " ", valor)
            return " ".join(valor.split())

        parrafos = ["".join((n.text or "") for n in p.findall(".//w:t", ns)) for p in xml.findall(".//w:p", ns)]
        encontrados = []
        for idx, texto in enumerate(parrafos):
            if normalizar(texto) == "salud toca tu puerta":
                for j in range(idx + 1, min(len(parrafos), idx + 20)):
                    siguiente = parrafos[j]
                    if normalizar(siguiente) in {"participantes", "particiantes"}:
                        for k in range(j + 1, min(len(parrafos), j + 12)):
                            bloque = parrafos[k]
                            if re.search(r"\d+", bloque):
                                encontrados.append(re.search(r"\d+", bloque).group(0))
                                break
                        break
                break

        assert encontrados[:1] == ["2"], encontrados[:6]
        texto_plano = contenido.decode("utf-8", errors="ignore")
        assert "Total de actividades:" not in texto_plano
        assert "Total de participantes:" not in texto_plano


def test_generar_word_conecta_todos_los_tipos_de_actividad_en_la_plantilla(tmp_path):
    datos = {
        "titulo": "Informe de prueba",
        "fecha_inicio": "2026-09-01",
        "fecha_fin": "2026-09-30",
        "total_actividades": 0,
        "total_participantes": 0,
        "resumen_por_tipo": [
            {"nombre": nombre, "total_actividades": indice + 1, "total_participantes": (indice + 1) * 10}
            for indice, (_, nombre) in enumerate(TIPOS_ACTIVIDAD_PREDETERMINADOS)
        ],
    }

    ruta = tmp_path / "informe_todos_tipos.docx"
    resultado = PDFService().generar_word(datos, str(ruta))

    assert resultado == str(ruta)
    with zipfile.ZipFile(ruta) as archivo:
        contenido = archivo.read("word/document.xml")
        xml = ET.fromstring(contenido)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        textos = [n.text or "" for n in xml.findall(".//w:t", ns)]

        def normalizar(valor):
            valor = unicodedata.normalize("NFKD", valor)
            valor = valor.encode("ascii", "ignore").decode("ascii")
            valor = valor.lower().strip()
            valor = re.sub(r"[^a-z0-9]+", " ", valor)
            return " ".join(valor.split())

        filas = []
        for fila in xml.findall(".//w:tr", ns):
            celdas = fila.findall("./w:tc", ns)
            if len(celdas) < 2:
                continue
            texto_celda_1 = "".join((n.text or "") for n in celdas[0].findall(".//w:t", ns))
            texto_celda_2 = "".join((n.text or "") for n in celdas[1].findall(".//w:t", ns))
            filas.append((texto_celda_1, texto_celda_2))

        for indice, (_, nombre) in enumerate(TIPOS_ACTIVIDAD_PREDETERMINADOS):
            alias = normalizar(nombre)
            encontro = False
            for texto_celda_1, texto_celda_2 in filas:
                if alias not in normalizar(texto_celda_1):
                    continue
                numeros = re.findall(r"\d+", texto_celda_2)
                if not numeros:
                    continue
                nombres_en_celda = [normalizar(item) for item in texto_celda_1.split()[:10] if item.strip()]
                # El orden real del patrón en la fila es el de los títulos que aparecen en la celda.
                if alias not in nombres_en_celda:
                    nombres_en_celda = [normalizar(item) for item in re.split(r"(?=[A-Z])", texto_celda_1) if item.strip()]
                posicion = nombres_en_celda.index(alias) if alias in nombres_en_celda else 0
                valor = numeros[min(posicion, len(numeros) - 1)]
                assert valor == str(indice + 1), (nombre, texto_celda_1, texto_celda_2, numeros)
                encontro = True
                break
            assert encontro is True, f"No se encontró el reemplazo para: {nombre}"
