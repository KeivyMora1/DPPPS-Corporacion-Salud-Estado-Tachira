import bcrypt

import db.setup as database_setup
from constants import PASSWORD_PROPIETARIO_PREDETERMINADO


def test_setup_crea_propietario_verificado_con_password_hasheado(monkeypatch):
    usuario_creado = {}
    monkeypatch.setattr(
        database_setup, "EMAIL_PROPIETARIO_PREDETERMINADO", "correo-sin-formato"
    )

    class CursorFalso:
        def execute(self, sql, parametros=()):
            if sql.lstrip().lower().startswith("insert into usuario"):
                usuario_creado.update(
                    sql=sql.lower(),
                    username=parametros[0],
                    password_hash=parametros[1],
                    nombre_completo=parametros[2],
                    email=parametros[3],
                )

        def fetchone(self):
            return (0,)

        def close(self):
            pass

    class ConexionFalsa:
        def cursor(self):
            return CursorFalso()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(
        database_setup.mysql.connector,
        "connect",
        lambda **config: ConexionFalsa(),
    )

    database_setup.crear_usuario_propietario()

    assert usuario_creado["username"] == "admin"
    assert usuario_creado["nombre_completo"] == "Usuario propietario"
    assert usuario_creado["email"] == "correo-sin-formato"
    assert "'propietario', true" in usuario_creado["sql"]
    assert bcrypt.checkpw(
        PASSWORD_PROPIETARIO_PREDETERMINADO.encode("utf-8"),
        usuario_creado["password_hash"].encode("utf-8"),
    )


def test_setup_no_crea_propietario_si_ya_hay_usuarios(monkeypatch):
    sentencias = []

    class CursorFalso:
        def execute(self, sql, parametros=()):
            sentencias.append(sql.lower())

        def fetchone(self):
            return (1,)

        def close(self):
            pass

    class ConexionFalsa:
        def cursor(self):
            return CursorFalso()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(
        database_setup.mysql.connector,
        "connect",
        lambda **config: ConexionFalsa(),
    )

    database_setup.crear_usuario_propietario()

    assert len(sentencias) == 1
    assert sentencias[0].startswith("select count(*)")


def test_setup_exige_valor_no_vacio_para_correo_del_propietario(monkeypatch):
    monkeypatch.setattr(database_setup, "EMAIL_PROPIETARIO_PREDETERMINADO", "")

    class CursorFalso:
        def execute(self, sql, parametros=()):
            pass

        def fetchone(self):
            return (0,)

        def close(self):
            pass

    class ConexionFalsa:
        def cursor(self):
            return CursorFalso()

        def close(self):
            pass

    monkeypatch.setattr(
        database_setup.mysql.connector,
        "connect",
        lambda **config: ConexionFalsa(),
    )

    try:
        database_setup.crear_usuario_propietario()
    except ValueError as error:
        assert "OWNER_EMAIL" in str(error)
    else:
        raise AssertionError("El setup debe exigir OWNER_EMAIL antes de crear el propietario.")
