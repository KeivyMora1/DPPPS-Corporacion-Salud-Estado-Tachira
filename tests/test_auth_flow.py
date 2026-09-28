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
        assert "Oficio de entrega de informe de FEBRERO 2026" not in contenido
        assert "San Cristóbal" in contenido


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
        parrafos = ["".join((n.text or "") for n in p.findall(".//w:t", ns)) for p in xml.findall(".//w:p", ns)]
        texto_plano = "\n".join(parrafos)

        assert "Salud toca tu puerta" in texto_plano
        assert "Participantes" in texto_plano
        assert "2" in texto_plano
        assert "18" in texto_plano
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
        contenido = archivo.read("word/document.xml").decode("utf-8", errors="ignore")

        def normalizar(valor):
            valor = unicodedata.normalize("NFKD", valor)
            valor = valor.encode("ascii", "ignore").decode("ascii")
            valor = valor.lower().strip()
            valor = re.sub(r"[^a-z0-9]+", " ", valor)
            return " ".join(valor.split())

        contenido_normalizado = normalizar(contenido)
        stopwords = {"a", "de", "la", "las", "los", "del", "el", "en", "y", "por", "con"}
        for indice, (_, nombre) in enumerate(TIPOS_ACTIVIDAD_PREDETERMINADOS):
            tokens = [token for token in normalizar(nombre).split() if token not in stopwords]
            assert tokens
            assert all(token in contenido_normalizado for token in tokens)
            assert str(indice + 1) in contenido
