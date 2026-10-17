import re
import unicodedata
import zipfile
from xml.etree import ElementTree as ET
from datetime import date, timedelta

import mysql.connector
import pytest

from db import AuthController, InformeWordService, ActividadController, ExcelServiceVoceria, VoceriaController
from constants import TIPOS_ACTIVIDAD_PREDETERMINADOS
import db as db_module


@pytest.fixture(autouse=True)
def usar_catalogo_de_ubicaciones_en_memoria(monkeypatch):
    monkeypatch.setattr(
        db_module.ParroquiaDAO,
        "listar_por_asic",
        lambda self, id_asic: [
            {"municipio": "San Cristóbal", "parroquia": "San Sebastián"}
        ],
    )


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
        rowcount = 1

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

    from contextlib import contextmanager
    @contextmanager
    def _tx_falsa():
        yield ConexionFalsa()

    monkeypatch.setattr(db_module, "get_connection", lambda: ConexionFalsa())
    monkeypatch.setattr("db.daos.actividad_dao.transaccion", _tx_falsa)
    monkeypatch.setattr("db.daos.actividad_dao.ejecutar_consulta", lambda sql, params=(), **kw: sentencias.append(sql.lower()) or [])

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


def test_login_rechaza_credenciales_fuera_de_limite(monkeypatch):
    controller = AuthController()
    consultas = []
    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_por_email",
        lambda valor: consultas.append(valor),
    )
    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_por_username",
        lambda valor: consultas.append(valor),
    )

    assert controller.login("u" * 61, "Password1") is False
    assert controller.login("usuario", "P" * 61) is False
    assert controller.login("usuario", "á" * 37) is False
    assert consultas == []


def test_registro_rechaza_campos_mayores_a_sus_limites():
    controller = AuthController()
    casos = [
        (("Ana", "García", "ana@example.com", "1234567", "usuario"), "al menos 8 caracteres"),
        (("A" * 61, "García", "ana@example.com", "Pass123!", "usuario"), "2 y 60"),
        (("Ana", "García", "ana@example.com", "Pass123!", "u" * 51), "3 y 50"),
        (("Ana", "García", "a" * 50 + "@example.com", "Pass123!", "usuario"), "correo válido"),
        (("Ana", "García", "ana@example.com", "P" * 61, "usuario"), "60 caracteres"),
    ]

    for datos, mensaje in casos:
        resultado = controller.registrar_usuario(*datos)
        assert resultado["success"] is False
        assert mensaje in resultado["message"]


def test_validacion_de_correo_y_codigo_de_recuperacion():
    assert db_module.validar_correo("a@b.co")
    assert not db_module.validar_correo("ana@@test.com")
    assert not db_module.validar_correo("ana..perez@test.com")

    resultado = AuthController().cambiar_password_con_codigo(
        "ana@test.com", "12x456", "Nueva123",
    )
    assert resultado == {
        "success": False,
        "message": "El código debe tener exactamente 6 dígitos numéricos.",
    }


def test_importadores_rechazan_archivos_no_xlsx(tmp_path):
    archivo = tmp_path / "libro.xls"
    archivo.write_bytes(b"contenido")

    try:
        db_module.validar_archivo_excel(str(archivo))
    except ValueError as exc:
        assert ".xlsx" in str(exc)
    else:
        raise AssertionError("El importador no debe aceptar archivos .xls.")


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
        parroquia="San Sebastián",
        establecimiento_salud="Hospitales TIPO I",
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
        "parroquia": "San Sebastián",
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
        parroquia="San Sebastián",
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
        ({"correo": "ana@@test.com"}, "Correo"),
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

    resultado_edad = _guardar_voceria_con_item(monkeypatch, edad="25")
    assert resultado_edad == (
        False,
        "Vocería #1: La edad no coincide con la fecha de nacimiento.",
    )

    resultado_sexo = _guardar_voceria_con_item(monkeypatch, sexo="X")
    assert resultado_sexo == (False, "Vocería #1: Debe seleccionar un sexo válido.")


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
            "correo": "ana@@test.com",
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
    assert any("Correo electrónico no válido" in error for error in errores)


def test_excel_actividad_rechaza_datos_que_el_formulario_no_acepta(tmp_path):
    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    headers = [
        "ASIC", "ACTIVIDAD DESARROLLADA", "FECHA", "TEMA TRATADO",
        "TOTAL DE ASISTENCIA", "ESTADO", "MUNICIPIO", "PARROQUIA",
        "ESTABLECIMIENTO DE SALUD", "NOMBRE DEL ESTABLECIMIENTO DE SALUD",
        "CANTIDAD DE COMITÉS DE SALUD", "MEDICOS",
    ]
    worksheet.append([])
    worksheet.append([])
    worksheet.append(headers)
    worksheet.append([
        "ASIC", "Actividad", (date.today() + timedelta(days=1)).isoformat(),
        "Tema", 2, "Táchira", "Municipio", "Parroquia", "CDI", "Centro",
        1, "no-numérico",
    ])
    worksheet.append([
        "ASIC", "Actividad", date.today().isoformat(), "T" * 151, 2,
        "", "San Cristóbal", "Parroquia", "CDI", "Centro", 1, 2,
    ])
    ruta = tmp_path / "actividades.xlsx"
    workbook.save(ruta)

    servicio = object.__new__(db_module.ExcelService)
    servicio._resolver_asic = lambda nombre: 1
    servicio._resolver_tipo = lambda nombre: 1
    servicio._actividad_dao = type(
        "ActividadDAOFalsa", (), {"verificar_duplicado": lambda *args, **kwargs: False}
    )()
    servicio._parroquia_dao = type(
        "ParroquiaDAOFalsa",
        (),
        {
            "listar_por_asic": lambda self, id_asic: [
                {"municipio": "San Cristóbal", "parroquia": "Parroquia"}
            ]
        },
    )()
    servicio._cache_ubicaciones = {}

    resultado = servicio.previsualizar(str(ruta))

    assert resultado["filas_validas"] == []
    errores_primera_fila = " ".join(resultado["filas_error"][0]["errores"])
    errores_segunda_fila = " ".join(resultado["filas_error"][1]["errores"])
    assert "no puede ser futura" in errores_primera_fila
    assert "MEDICOS" in errores_primera_fila
    assert "ESTADO" in errores_segunda_fila
    assert "150 caracteres" in errores_segunda_fila


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


def test_guardar_actividad_exige_total_coherente_y_catalogos_validos():
    controller = ActividadController()

    resultado_total = controller.guardar_actividad(
        **_datos_actividad_validos(participantes="1")
    )
    assert resultado_total == (
        False,
        "El total de asistencia debe coincidir con la suma de las categorías.",
    )

    resultado_municipio = controller.guardar_actividad(
        **_datos_actividad_validos(municipio="Municipio inventado")
    )
    assert resultado_municipio == (False, "Debes seleccionar un municipio válido.")


def test_importacion_actividades_revierte_todo_si_falla_una_fila(monkeypatch):
    class ConexionFalsa:
        def __init__(self):
            self.commits = 0
            self.rollbacks = 0
            self.cerrada = False

        def commit(self):
            self.commits += 1

        def rollback(self):
            self.rollbacks += 1

        def close(self):
            self.cerrada = True

    class AuthFalsa:
        def obtener_usuario_actual(self):
            return {"id_usuario": 1}

        def usuario_puede_escribir(self, usuario):
            return True

    class ActividadDAOFalsa:
        def __init__(self):
            self.filas = 0

        def crear(self, **kwargs):
            self.filas += 1
            if self.filas == 2:
                raise ValueError("Error simulado en la segunda fila")

    conexion = ConexionFalsa()
    servicio = object.__new__(db_module.ExcelService)
    servicio.id_usuario_registro = 1
    servicio._actividad_dao = ActividadDAOFalsa()
    monkeypatch.setattr(db_module, "AuthController", AuthFalsa)
    monkeypatch.setattr(db_module, "get_connection", lambda: conexion)

    resultado = servicio.importar([
        {"numero_fila": 4, "id_asic": 1, "id_tipo": 1, "fecha": date(2026, 9, 1), "comites_salud": 0, "participantes": 1},
        {"numero_fila": 5, "id_asic": 1, "id_tipo": 1, "fecha": date(2026, 9, 2), "comites_salud": 0, "participantes": 1},
    ])

    assert resultado["insertadas"] == 0
    assert resultado["errores_al_insertar"][0]["numero_fila"] == 5
    assert conexion.commits == 0
    assert conexion.rollbacks == 1
    assert conexion.cerrada


def test_importacion_vocerias_revierte_todo_si_falla_un_comite(monkeypatch):
    class ConexionFalsa:
        def __init__(self):
            self.commits = 0
            self.rollbacks = 0
            self.cerrada = False

        def commit(self):
            self.commits += 1

        def rollback(self):
            self.rollbacks += 1

        def close(self):
            self.cerrada = True

    class AuthFalsa:
        def obtener_usuario_actual(self):
            return {"id_usuario": 1}

        def usuario_puede_escribir(self, usuario):
            return True

    class VoceriaControllerFalso:
        def __init__(self):
            self.comites = 0

        def guardar_voceria(self, **kwargs):
            self.comites += 1
            if self.comites == 2:
                return False, "Error simulado en el segundo comité"
            return True, "Guardado"

    conexion = ConexionFalsa()
    controlador = VoceriaControllerFalso()
    servicio = object.__new__(ExcelServiceVoceria)
    servicio.id_usuario_registro = 1
    servicio._tipo_voceria_dao = object()
    monkeypatch.setattr(servicio, "_resolver_asic", lambda nombre: 1)
    monkeypatch.setattr(servicio, "_resolver_tipo_voceria", lambda nombre: 1)
    monkeypatch.setattr(db_module, "AuthController", AuthFalsa)
    monkeypatch.setattr(db_module, "VoceriaController", lambda: controlador)
    monkeypatch.setattr(db_module, "get_connection", lambda: conexion)
    comites = [
        {"nombre_comite": nombre, "filas": [{"datos": {"asic": "ASIC", "voceria": "Vocería", "nombre_comite": nombre}}]}
        for nombre in ("Comité 1", "Comité 2")
    ]

    resultado = servicio.importar(comites)

    assert resultado["comites_insertados"] == 0
    assert resultado["voceros_insertados"] == 0
    assert resultado["errores_al_insertar"][0]["nombre_comite"] == "Comité 2"
    assert conexion.commits == 0
    assert conexion.rollbacks == 1
    assert conexion.cerrada


def test_registrar_usuario_envia_codigo_y_marca_cuenta_no_verificada(monkeypatch):
    controller = AuthController()
    captured = {}

    monkeypatch.setattr(controller.usuario_dao, "obtener_propietario", lambda: None)
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

    monkeypatch.setattr(controller.usuario_dao, "obtener_propietario", lambda: None)
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_email", lambda email: None)
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_username", lambda username: None)

    def fake_crear(**kwargs):
        captured.update(kwargs)
        return 9

    monkeypatch.setattr(controller.usuario_dao, "crear", fake_crear)
    monkeypatch.setattr(controller, "_enviar_codigo_por_email", lambda *args, **kwargs: True)

    resultado = controller.registrar_usuario("Ana", "García", "ana@test.com", "Pass123!", username="Juanito")

    assert resultado["success"] is True
    assert captured["username"] == "Juanito"


def test_modelo_principal_muestra_username_y_rol_formateados():
    from pantallas.principal import ModeloPrincipal

    modelo = ModeloPrincipal.__new__(ModeloPrincipal)
    modelo.usuario = {"username": "juanito", "rol": "administrador"}

    assert modelo.get_username() == "Juanito"
    assert modelo.get_rol() == "Administrador"


def test_registrar_administrador_requiere_password_del_propietario(monkeypatch):
    controller = AuthController()
    propietario = {"password_hash": "hash-propietario"}
    creado = []

    monkeypatch.setattr(controller.usuario_dao, "obtener_propietario", lambda: propietario)
    monkeypatch.setattr(controller.usuario_dao, "verificar_password", lambda password, hashed: False)
    monkeypatch.setattr(controller.usuario_dao, "crear", lambda **kwargs: creado.append(kwargs))

    resultado = controller.registrar_usuario(
        "Ana", "García", "ana@test.com", "Pass123!",
        cuenta_administrador=True,
        password_propietario="incorrecta",
    )

    assert resultado == {
        "success": False,
        "message": "La contraseña del usuario propietario es incorrecta.",
    }
    assert creado == []


def test_registrar_administrador_guarda_rol_solo_con_password_valida(monkeypatch):
    controller = AuthController()
    capturado = {}

    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_propietario",
        lambda: {"password_hash": "hash-propietario"},
    )
    monkeypatch.setattr(controller.usuario_dao, "verificar_password", lambda password, hashed: True)
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_email", lambda email: None)
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_username", lambda username: None)
    monkeypatch.setattr(controller.usuario_dao, "crear", lambda **kwargs: capturado.update(kwargs) or 10)
    monkeypatch.setattr(controller, "_enviar_codigo_por_email", lambda *args: True)

    resultado = controller.registrar_usuario(
        "Ana", "García", "ana@test.com", "Pass123!",
        cuenta_administrador=True,
        password_propietario="valida",
    )

    assert resultado["success"] is True
    assert capturado["rol"] == "administrador"
    assert capturado["administrador_autorizado"] is True


def test_crear_cuenta_solo_permite_al_propietario_y_no_envia_codigo_al_crear(monkeypatch):
    from db.services import auth_service

    controller = AuthController()
    creado = {}
    monkeypatch.setattr(
        auth_service,
        "sesion_actual",
        {"id_usuario": 1, "rol": "propietario"},
    )
    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_propietario",
        lambda: {"password_hash": "hash-propietario"},
    )
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_email", lambda email: None)
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_username", lambda username: None)
    monkeypatch.setattr(
        controller.usuario_dao,
        "crear",
        lambda **kwargs: creado.update(kwargs) or 12,
    )
    monkeypatch.setattr(
        controller,
        "_enviar_codigo_por_email",
        lambda *args: pytest.fail("El correo debe enviarse en el primer inicio de sesión."),
    )

    resultado = controller.crear_cuenta(
        "Ana", "García", "ana@test.com", "Pass123!",
        username="ana", cuenta_administrador=True,
    )

    assert resultado["success"] is True
    assert "Cuenta creada." in resultado["message"]
    assert "primera vez" in resultado["message"]
    assert creado["username"] == "ana"
    assert creado["rol"] == "administrador"


def test_crear_cuenta_rechaza_sesion_no_propietaria(monkeypatch):
    from db.services import auth_service

    controller = AuthController()
    monkeypatch.setattr(
        auth_service,
        "sesion_actual",
        {"id_usuario": 2, "rol": "administrador"},
    )
    monkeypatch.setattr(
        controller.usuario_dao,
        "crear",
        lambda **kwargs: pytest.fail("No debe crear cuentas desde otra sesión."),
    )

    resultado = controller.crear_cuenta(
        "Ana", "García", "ana@test.com", "Pass123!", username="ana",
    )

    assert resultado["success"] is False
    assert "Solo el usuario propietario" in resultado["message"]


def test_listar_cuentas_requiere_sesion_de_propietario(monkeypatch):
    from db.services import auth_service

    controller = AuthController()
    monkeypatch.setattr(
        auth_service,
        "sesion_actual",
        {"id_usuario": 2, "rol": "administrador"},
    )
    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_cuentas",
        lambda: pytest.fail("Una sesión no propietaria no debe listar cuentas."),
    )

    with pytest.raises(PermissionError):
        controller.listar_cuentas()


def test_opcion_cuentas_esta_despues_de_tipos_de_actividad():
    from pantallas.principal import VistaPrincipal

    claves_menu = [clave for clave, _texto in VistaPrincipal.MENU_ITEMS]

    assert claves_menu.index("cuentas") == claves_menu.index("tipos_actividad") + 1


def test_login_no_verificado_solo_envia_codigo_con_password_correcta(monkeypatch):
    controller = AuthController()
    usuario = {
        "id_usuario": 1,
        "username": "ana",
        "email": "ana@test.com",
        "password_hash": "hash",
        "email_verificado": False,
    }
    monkeypatch.setattr(controller.usuario_dao, "obtener_por_username", lambda username: usuario)
    monkeypatch.setattr(
        controller.usuario_dao,
        "verificar_password",
        lambda password, password_hash: password == "Pass123!",
    )

    assert controller.autenticar_pendiente_verificacion("ana", "incorrecta") is None
    assert controller.autenticar_pendiente_verificacion("ana", "Pass123!") == usuario


def test_usuario_dao_asigna_propietario_al_primer_registro(monkeypatch):
    consultas = []

    class CursorFalso:
        lastrowid = 12

        def __init__(self):
            self.resultado_pendiente = False

        def execute(self, sql, params=()):
            consultas.append((sql.lower(), params))
            self.resultado_pendiente = sql.lstrip().lower().startswith("select")

        def fetchone(self):
            sql = consultas[-1][0]
            self.resultado_pendiente = False
            return (1,) if "get_lock" in sql else (0,)

        def close(self):
            assert not self.resultado_pendiente

    class ConexionFalsa:
        def cursor(self):
            return CursorFalso()

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(db_module, "get_connection", lambda: ConexionFalsa())

    usuario_id = db_module.UsuarioDAO().crear(
        username="primero",
        password="Pass123!",
        nombre_completo="Primer Usuario",
        email="primero@test.com",
    )

    insercion = next(params for sql, params in consultas if "insert into usuario" in sql)
    assert usuario_id == 12
    assert insercion[-1] == "propietario"
    assert any("release_lock" in sql for sql, _ in consultas)


def test_obtener_propietario_no_duplica_limit_en_consulta(monkeypatch):
    import db.base_dao as base_dao

    consulta = {}

    def capturar_consulta(sql, parametros=(), **kwargs):
        consulta["sql"] = sql
        consulta["parametros"] = parametros
        return None

    monkeypatch.setattr(base_dao, "ejecutar_consulta", capturar_consulta)

    db_module.UsuarioDAO().obtener_propietario()

    assert consulta["sql"] == (
        "SELECT * FROM usuario WHERE rol = %s AND activo = TRUE "
        "ORDER BY id_usuario LIMIT 1"
    )
    assert consulta["parametros"] == ("propietario",)


def test_lector_no_puede_eliminar_actividad(monkeypatch):
    controller = ActividadController()
    eliminaciones = []
    monkeypatch.setattr(
        controller.auth,
        "obtener_usuario_actual",
        lambda: {"id_usuario": 2, "rol": "lector"},
    )
    monkeypatch.setattr(controller.actividad_dao, "eliminar", lambda id_actividad: eliminaciones.append(id_actividad))

    resultado = controller.eliminar_actividad(5)

    assert resultado[0] is False
    assert "lector" in resultado[1]
    assert eliminaciones == []


def test_roles_con_permiso_de_escritura():
    assert AuthController.usuario_puede_escribir({"rol": "propietario"})
    assert AuthController.usuario_puede_escribir({"rol": "administrador"})
    assert not AuthController.usuario_puede_escribir({"rol": "lector"})


def test_validar_datos_registro_rechaza_campos_incompletos_o_invalidos():
    from pantallas.login.controller import ControladorLogin

    assert ControladorLogin._validar_datos_registro("", "García", "ana", "ana@test.com", "Pass123!") == "Completa todos los campos."
    assert ControladorLogin._validar_datos_registro("Ana1", "García", "ana", "ana@test.com", "Pass123!") == "El nombre no puede contener números."
    assert ControladorLogin._validar_datos_registro("Ana", "Gar2cía", "ana", "ana@test.com", "Pass123!") == "El apellido no puede contener números."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "an", "ana@test.com", "Pass123!") == "El nombre de usuario debe tener al menos 3 caracteres."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana user", "ana@test.com", "Pass123!") == "El nombre de usuario no puede contener espacios."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana", "correo", "Pass123!") == "Ingresa un correo válido."
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana", "ana@test.com", "1234567") == "La contraseña debe tener al menos 8 caracteres."
    assert "60 caracteres" in ControladorLogin._validar_datos_registro("A" * 61, "García", "ana", "ana@test.com", "Pass123!")
    assert "60 caracteres" in ControladorLogin._validar_datos_registro("Ana", "García", "ana", "a" * 50 + "@example.com", "Pass123!")
    assert "60 caracteres" in ControladorLogin._validar_datos_registro("Ana", "García", "ana", "ana@test.com", "P" * 61)
    assert ControladorLogin._validar_datos_registro("Ana", "García", "ana", "ana@test.com", "12345678") is None


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


def test_login_conserva_el_rol_del_usuario_en_la_sesion(monkeypatch):
    controller = AuthController()
    monkeypatch.setattr(db_module, "sesion_actual", None)
    monkeypatch.setattr(
        controller.usuario_dao,
        "obtener_por_email",
        lambda email: {
            "id_usuario": 3,
            "username": "ana",
            "email": "ana@test.com",
            "password_hash": "hash",
            "nombre_completo": "Ana García",
            "email_verificado": True,
            "rol": "administrador",
            "activo": True,
        },
    )
    monkeypatch.setattr(controller.usuario_dao, "verificar_password", lambda password, hashed: True)

    assert controller.login("ana@test.com", "Pass123!") is True
    assert controller.obtener_usuario_actual()["rol"] == "administrador"


def test_generar_docx_crea_archivo_docx_con_contenido(tmp_path):
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
    resultado = InformeWordService().generar_docx(datos, str(ruta))

    assert resultado == str(ruta)
    assert ruta.exists()
    assert zipfile.is_zipfile(ruta)

    with zipfile.ZipFile(ruta) as archivo:
        assert "word/document.xml" in archivo.namelist()
        contenido = archivo.read("word/document.xml").decode("utf-8", errors="ignore")
        assert "DPPPS N°___" in contenido
        assert "Oficio de entrega de informe de FEBRERO 2026" not in contenido
        assert "San Cristóbal" in contenido


def test_generar_docx_actualiza_fecha_de_cabecera_con_la_fecha_actual(tmp_path):
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
    InformeWordService().generar_docx(datos, str(ruta))

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


def test_generar_docx_inyecta_totales_reales_en_la_plantilla(tmp_path):
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
    resultado = InformeWordService().generar_docx(datos, str(ruta))

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


def test_generar_docx_conecta_todos_los_tipos_de_actividad_en_la_plantilla(tmp_path):
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
    resultado = InformeWordService().generar_docx(datos, str(ruta))

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
