from db import AuthController


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
