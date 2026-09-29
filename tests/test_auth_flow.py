import re
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

import mysql.connector

from db import AuthController, PDFService, TIPOS_ACTIVIDAD_PREDETERMINADOS, ActividadController
import db as db_module


def test_asegurar_esquema_autenticacion_no_falla_si_la_bd_aun_no_existe(monkeypatch):
    def fake_get_connection():
        raise mysql.connector.Error(1049, "Unknown database 'dppps_informes'")

    monkeypatch.setattr(db_module, "get_connection", fake_get_connection)

    assert db_module.asegurar_esquema_autenticacion() is None


def test_schema_cumple_requerimientos_de_base_solicitada():
    schema = open("schema.sql", encoding="utf-8").read()

    assert "CREATE TABLE IF NOT EXISTS asic" in schema
    assert "id_asic INT AUTO_INCREMENT PRIMARY KEY" in schema
    assert "nombre VARCHAR(150) NOT NULL" in schema
    assert "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP" in schema
    assert "codigo VARCHAR(20)" not in schema
    assert "fecha_inicio" not in schema
    assert "fecha_fin" not in schema
    assert "CREATE TABLE IF NOT EXISTS evidencia" not in schema
    assert "CREATE TABLE IF NOT EXISTS voceria_item" not in schema


def test_catalogos_no_usan_columna_activo(monkeypatch):
    consultas = []

    class CursorFalso:
        def execute(self, sql, params=()):
            consultas.append(sql.lower())
            return None

        def fetchall(self):
            return []

        def close(self):
            pass

    class ConexionFalsa:
        def cursor(self, dictionary=True):
            return CursorFalso()

        def close(self):
            pass

    monkeypatch.setattr(db_module, "get_connection", lambda: ConexionFalsa())

    db_module.AsicDAO().obtener_todos()
    db_module.TipoActividadDAO().obtener_todos()
    db_module.TipoVoceriaDAO().obtener_todos()

    assert all("activo" not in sql for sql in consultas)


def test_actividad_dao_no_usa_fechas_anteriores_ni_descripcion_obsoleta(monkeypatch):
    sentencias = []

    class CursorFalso:
        lastrowid = 1

        def execute(self, sql, params=()):
            sentencias.append(sql.lower())
            return None

        def fetchall(self):
            return []

        def fetchone(self):
            return None

        def close(self):
            pass

    class ConexionFalsa:
        def cursor(self, dictionary=True):
            return CursorFalso()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(db_module, "get_connection", lambda: ConexionFalsa())

    dao = db_module.ActividadDAO()
    dao.obtener_todas()
    dao.crear(1, 1, 1, fecha="2026-09-05", tema="Prueba")
    dao.actualizar(1, 1, 1, fecha="2026-09-05", tema="Prueba")

    assert all(
        "fecha_inicio" not in sql and "fecha_fin" not in sql and "descripcion" not in sql and "a.descripcion" not in sql and "descripcion = %s" not in sql
        for sql in sentencias
    )


def test_actividad_dao_usa_nombres_de_bd_sin_aliases_de_interfaz():
    assert not hasattr(db_module.ActividadDAO, "_normalizar_actividad")
    aliases = getattr(db_module, "HEADER_ALIASES", {})
    assert "descripcion" not in aliases
    assert "fecha_inicio" not in aliases
    assert "fecha_fin" not in aliases
    assert aliases.get("tema") == "tema"
    assert aliases.get("fecha") == "fecha"


def test_generar_codigo_verificacion_es_numero_de_6_digitos():
    controller = AuthController()
    codigo = controller._generar_codigo()

    assert codigo.isdigit()
    assert len(codigo) == 6


def test_guardar_actividad_acepta_fecha_unica(monkeypatch):
    controller = ActividadController()

    monkeypatch.setattr(controller.auth, "obtener_usuario_actual", lambda: {"id_usuario": 1})
    monkeypatch.setattr(controller.actividad_dao, "verificar_duplicado", lambda **kwargs: False)

    creados = {}

    def fake_crear(**kwargs):
        creados.update(kwargs)
        return 99

    monkeypatch.setattr(controller.actividad_dao, "crear", fake_crear)

    resultado = controller.guardar_actividad(
        id_asic=1,
        id_tipo=1,
        fecha="2026-09-05",
        estado="Táchira",
        municipio="San Cristóbal",
        parroquia="San José",
        establecimiento_salud="Hospital",
        nombre_establecimiento="Hospital Central",
        comites_salud=1,
        tema="Tema de prueba",
        medicos=0,
        promotores_salud=2,
        voceros_comite_salud=1,
        vocero_consejo_direccion=0,
        coordinador_docencia=0,
        autoridades_presentes=0,
        otros_actores=0,
        personas_comunidad=5,
        estudiantes_aspirantes=0,
        participantes=8,
    )

    assert resultado[0] is True
    assert creados["fecha"] == "2026-09-05"
    assert creados["tema"] == "Tema de prueba"


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


def test_registrar_usuario_guarda_username_en_db(monkeypatch):
    controller = AuthController()
    captured = {}

    monkeypatch.setattr(controller.usuario_dao, "obtener_por_email", lambda email: None)
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_username", lambda username: None)

    def fake_crear(**kwargs):
        captured.update(kwargs)
        return 9

    monkeypatch.setattr(controller.usuario_dao, "crear", fake_crear)
    monkeypatch.setattr(controller, "_enviar_codigo_por_email", lambda *args, **kwargs: True)

    resultado = controller.registrar_usuario("Ana", "García", "ana@test.com", "Pass123!", username="ana_user")

    assert resultado["success"] is True
    assert captured["username"] == "ana_user"


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
        assert "Seguimiento a los Comités de Salud mediante las vocerías en salud comunal" not in texto_plano

        filas = xml.findall(".//w:tr", ns)
        valores_fila_establecimientos = [
            n.text for n in filas[5].findall("./w:tc", ns)[1].findall(".//w:t", ns)
            if (n.text or "").strip().isdigit()
        ]
        assert valores_fila_establecimientos[-1] == "2"

        fila_actualizacion = filas[1]
        celda_etiqueta = fila_actualizacion.findall("./w:tc", ns)[0]
        celda_total = fila_actualizacion.findall("./w:tc", ns)[1]
        assert "Actualización de los comités de salud" in "".join(
            n.text or "" for n in celda_etiqueta.findall("./w:p[1]//w:t", ns)
        )
        assert "0" in "".join(n.text or "" for n in celda_total.findall("./w:p[1]//w:t", ns))


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
