import re
import unicodedata
import zipfile
from xml.etree import ElementTree as ET
from datetime import date, timedelta

import mysql.connector

from db import AuthController, PDFService, TIPOS_ACTIVIDAD_PREDETERMINADOS, ActividadController, ExcelServiceVoceria, VoceriaController
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
    tema = "T" * 150

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
        tema=tema,
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
    assert creados["tema"] == tema


def _datos_actividad_validos(**cambios):
    datos = {
        "id_asic": 1,
        "id_tipo": 1,
        "fecha": "2000-01-01",
        "estado": "Táchira",
        "municipio": "San Cristóbal",
        "parroquia": "San José",
        "establecimiento_salud": "CDI",
        "nombre_establecimiento": "Centro de Salud",
        "comites_salud": "0",
        "tema": "Tema de prueba",
        "medicos": "0",
        "promotores_salud": "0",
        "voceros_comite_salud": "0",
        "vocero_consejo_direccion": "0",
        "coordinador_docencia": "0",
        "autoridades_presentes": "0",
        "otros_actores": "0",
        "personas_comunidad": "0",
        "estudiantes_aspirantes": "0",
        "participantes": "0",
    }
    datos.update(cambios)
    return datos


def _datos_voceria_validos(**cambios):
    datos = {
        "nombres": "Ana Pérez",
        "ci": "12345678",
        "telefono": "04141234567",
        "fecha_nacimiento": "2000-01-01",
        "edad": "26",
        "id_tipo_voceria": 1,
        "sexo": "F",
        "profesion": "Enfermera",
        "correo": "ana.perez@test.com",
        "fechas_eleccion": (date.today() - timedelta(days=1)).isoformat(),
    }
    datos.update(cambios)
    return datos


def _controlador_voceria_preparado(monkeypatch):
    controller = VoceriaController()
    monkeypatch.setattr(controller.tipo_voceria_dao, "obtener_todos", lambda: [{"id_tipo": 1}])
    monkeypatch.setattr(controller.auth, "obtener_usuario_actual", lambda: {"id_usuario": 1})
    monkeypatch.setattr(controller.voceria_dao, "crear", lambda *args, **kwargs: 1)
    return controller


def _guardar_voceria_con_item(monkeypatch, **cambios):
    controller = _controlador_voceria_preparado(monkeypatch)
    items = [_datos_voceria_validos(**cambios)] + [_datos_voceria_validos() for _ in range(6)]
    return controller.guardar_voceria(
        id_asic=1,
        id_tipo=1,
        estado="Táchira",
        municipio="San Cristóbal",
        parroquia="San José",
        centro_dispensador="CDI",
        nombre_centro="Centro de Salud",
        nombre_comite="Comité Central",
        items=items,
    )


def test_voceria_rechaza_campos_fuera_de_los_nuevos_limites(monkeypatch):
    casos = [
        ({"telefono": "1" * 13}, "teléfono"),
        ({"telefono": "1" * 10}, "11 y 12 dígitos"),
        ({"ci": "123456"}, "C.I."),
        ({"edad": "100"}, "edad"),
        ({"nombres": "Juan"}, "Nombres"),
        ({"profesion": "A" * 41}, "Profesión"),
        ({"correo": "a@b.co"}, "Correo"),
    ]

    for cambios, campo in casos:
        resultado = _guardar_voceria_con_item(monkeypatch, **cambios)
        assert resultado[0] is False
        assert campo in resultado[1]


def test_voceria_rechaza_fechas_de_nacimiento_y_eleccion_invalidas(monkeypatch):
    limite = date.today().replace(year=date.today().year - 18)

    resultado_nacimiento = _guardar_voceria_con_item(
        monkeypatch,
        fecha_nacimiento=limite.isoformat(),
        edad="18",
    )
    assert resultado_nacimiento[0] is True

    resultado_mayor_99 = _guardar_voceria_con_item(
        monkeypatch,
        fecha_nacimiento="1920-01-01",
        edad="99",
    )
    assert resultado_mayor_99[0] is False
    assert "18 y 99 años" in resultado_mayor_99[1]

    resultado_eleccion = _guardar_voceria_con_item(
        monkeypatch,
        fechas_eleccion=(date.today() + timedelta(days=1)).isoformat(),
    )
    assert resultado_eleccion == (
        False,
        "Vocería #1: La fecha de elección no puede ser futura.",
    )


def test_excel_voceria_aplica_los_nuevos_limites():
    servicio = ExcelServiceVoceria(id_usuario_registro=1)
    fila = {
        campo: valor
        for campo, valor in {
            "nombres": "Juan",
            "ci": "123456",
            "telefono": "1" * 10,
            "fecha_nacimiento": "1920-09-30",
            "edad": "100",
            "voceria": "Vocería 1",
            "sexo": "F",
            "profesion": "A" * 41,
            "correo": "a@b.co",
            "fechas_eleccion": (date.today() + timedelta(days=1)).isoformat(),
            "estado": "Táchira",
            "municipio": "San Cristóbal",
            "parroquia": "San José",
            "asic": "Andrés Bello",
            "nombre_comite": "Comité Central",
            "centro_dispensador": "CDI",
            "nombre_centro": "Centro de Salud",
        }.items()
    }

    errores = servicio._validar_fila(fila, 3)

    assert any("11 y 12 dígitos" in error for error in errores)
    assert any("C.I." in error and "7 y 8 dígitos" in error for error in errores)
    assert any("2 dígitos" in error for error in errores)
    assert any("18 y 99" in error for error in errores)
    assert any("futura" in error for error in errores)
    assert any("5 y 40" in error for error in errores)
    assert any("11 caracteres" in error for error in errores)


def test_guardar_actividad_rechaza_fecha_futura():
    controller = ActividadController()
    fecha_futura = (date.today() + timedelta(days=1)).isoformat()

    resultado = controller.guardar_actividad(**_datos_actividad_validos(fecha=fecha_futura))

    assert resultado == (False, "La fecha de la actividad no puede ser futura.")


def test_guardar_actividad_rechaza_tema_mayor_a_150_caracteres():
    controller = ActividadController()

    resultado = controller.guardar_actividad(**_datos_actividad_validos(tema="x" * 151))

    assert resultado == (False, "El tema tratado no puede superar los 150 caracteres.")


def test_guardar_actividad_requiere_todos_los_campos():
    controller = ActividadController()
    campos_requeridos = [
        "id_asic", "id_tipo", "fecha", "estado", "municipio", "parroquia",
        "establecimiento_salud", "nombre_establecimiento", "comites_salud", "tema",
        "medicos", "promotores_salud", "voceros_comite_salud",
        "vocero_consejo_direccion", "coordinador_docencia", "autoridades_presentes",
        "otros_actores", "personas_comunidad", "estudiantes_aspirantes", "participantes",
    ]

    for campo in campos_requeridos:
        resultado = controller.guardar_actividad(**_datos_actividad_validos(**{campo: ""}))
        assert resultado[0] is False, f"El campo {campo} no debe aceptar un valor vacío."


def test_error_actividad_muestra_etiqueta_visible_del_campo():
    controller = ActividadController()

    resultado = controller.guardar_actividad(
        **_datos_actividad_validos(voceros_comite_salud="")
    )

    assert resultado == (False, "El campo Voceros Comité Salud es obligatorio.")


def test_guardar_actividad_valida_comites_salud():
    controller = ActividadController()

    for valor in ("abc", "100"):
        resultado = controller.guardar_actividad(**_datos_actividad_validos(comites_salud=valor))
        assert resultado == (
            False,
            "Comités de Salud debe contener solo números y tener máximo 2 dígitos.",
        )


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


def test_validar_datos_registro_rechaza_campos_incompletos_o_invalidos():
    from pantallas.login.controller import ControladorLogin

    assert ControladorLogin._validar_datos_registro("", "García", "ana", "ana@test.com", "Pass123!") == "Completa todos los campos."
    assert ControladorLogin._validar_datos_registro("Ana1", "García", "ana", "ana@test.com", "Pass123!") == "El nombre no puede contener números."
    assert ControladorLogin._validar_datos_registro("Ana", "Gar2cía", "ana", "ana@test.com", "Pass123!") == "El apellido no puede contener números."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "an", "ana@test.com", "Pass123!") == "El nombre de usuario debe tener al menos 3 caracteres."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana user", "ana@test.com", "Pass123!") == "El nombre de usuario no puede contener espacios."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana", "correo", "Pass123!") == "Ingresa un correo válido."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana", "ana@test.com", "123") == "La contraseña debe tener al menos 6 caracteres."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana", "ana@test.com", "Pass123!") is None


def test_verificar_email_rechaza_codigo_con_longitud_o_formato_incorrecto(monkeypatch):
    controller = AuthController()

    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_por_email",
        lambda email: {
            "id_usuario": 1,
            "email": "ana@test.com",
            "codigo_verificacion": "123456",
            "codigo_verificacion_expira": "2030-01-01 00:00:00",
        },
    )

    assert controller.verificar_email("ana@test.com", "12345") is False
    assert controller.verificar_email("ana@test.com", "abc123") is False
    assert controller.verificar_email("ana@test.com", "123456") is True


def test_reenviar_codigo_verificacion_actualiza_codigo_y_envia_email(monkeypatch):
    controller = AuthController()
    captured = {}

    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_por_email",
        lambda email: {"id_usuario": 1, "email": "ana@test.com", "email_verificado": False},
    )

    def fake_guardar(email, codigo, expiracion):
        captured["email"] = email
        captured["codigo"] = codigo
        captured["expiracion"] = expiracion

    monkeypatch.setattr(controller.usuario_dao, "guardar_codigo_verificacion", fake_guardar)
    monkeypatch.setattr(controller, "_enviar_codigo_por_email", lambda email, codigo, tipo: True)

    resultado = controller.reenviar_codigo_verificacion("ana@test.com")

    assert resultado["success"] is True
    assert captured["email"] == "ana@test.com"
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
