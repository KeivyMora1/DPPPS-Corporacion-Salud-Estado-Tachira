import os
import random
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from ..daos import UsuarioDAO
from ..utils import get_connection
from ..validators import validar_correo

sesion_actual = None

class AuthController:
    def __init__(self):
        self.usuario_dao = UsuarioDAO()

    @staticmethod
    def _generar_codigo(longitud=6):
        return str(random.randint(10 ** (longitud - 1), (10 ** longitud) - 1))

    def _enviar_codigo_por_email(self, email, codigo, tipo):
        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "587"))
        usuario = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        if not host or not usuario or not password:
            return False

        asunto = "Código de verificación" if tipo == "verificacion" else "Código para recuperar tu contraseña"
        cuerpo = (
            f"Tu código es: {codigo}\n\n"
            f"Este código vence en 10 minutos."
        )

        try:
            msg = EmailMessage()
            msg["From"] = usuario
            msg["To"] = email
            msg["Subject"] = asunto
            msg.set_content(cuerpo, charset="utf-8")

            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(usuario, password)
                server.send_message(msg)
            return True
        except Exception as exc:
            print(f"[WARN] No se pudo enviar el correo: {exc}")
            return False

    def registrar_usuario(self, nombre, apellido, email, password, username=None,
                          cuenta_administrador=False, password_propietario=None):
        email = (email or "").strip().lower()
        nombre = (nombre or "").strip()
        apellido = (apellido or "").strip()
        username = (username or email).strip()

        if not nombre or not apellido or not email or not password or not username:
            return {"success": False, "message": "Completa todos los campos."}
        if not validar_correo(email) or len(email) > 60:
            return {"success": False, "message": "Ingresa un correo válido."}
        if not 3 <= len(username) <= 50:
            return {"success": False, "message": "El nombre de usuario debe tener entre 3 y 50 caracteres."}
        if any(caracter.isspace() for caracter in username):
            return {"success": False, "message": "El nombre de usuario no puede contener espacios."}
        if len(nombre) < 2 or len(nombre) > 60 or any(caracter.isdigit() for caracter in nombre):
            return {"success": False, "message": "El nombre debe tener entre 2 y 60 caracteres y no contener números."}
        if len(apellido) < 2 or len(apellido) > 60 or any(caracter.isdigit() for caracter in apellido):
            return {"success": False, "message": "El apellido debe tener entre 2 y 60 caracteres y no contener números."}
        if len(f"{nombre} {apellido}") > 120:
            return {"success": False, "message": "El nombre completo no puede superar 120 caracteres."}
        if len(password) < 8:
            return {"success": False, "message": "La contraseña debe tener al menos 8 caracteres."}
        if len(password) > 60:
            return {"success": False, "message": "La contraseña no puede superar 60 caracteres."}
        if len(password.encode("utf-8")) > 72:
            return {"success": False, "message": "La contraseña no puede superar 72 bytes."}
        propietario = self.usuario_dao.obtener_propietario()
        if cuenta_administrador and propietario:
            if not password_propietario or not self.usuario_dao.verificar_password(
                password_propietario, propietario["password_hash"]
            ):
                return {"success": False, "message": "La contraseña del usuario propietario es incorrecta."}
        if self.usuario_dao.obtener_por_email(email):
            return {"success": False, "message": "Este correo ya está registrado."}
        if self.usuario_dao.obtener_por_username(username):
            return {"success": False, "message": "Este nombre de usuario ya está en uso."}

        codigo = self._generar_codigo()
        expiracion = datetime.now() + timedelta(minutes=10)
        try:
            self.usuario_dao.crear(
                username=username,
                password=password,
                nombre_completo=f"{nombre.strip()} {apellido.strip()}".strip(),
                email=email.lower().strip(),
                nombre=nombre.strip(),
                apellido=apellido.strip(),
                codigo_verificacion=codigo,
                codigo_verificacion_expira=expiracion,
                rol="administrador" if cuenta_administrador and propietario else "lector",
                administrador_autorizado=bool(cuenta_administrador and propietario),
            )
            enviado = self._enviar_codigo_por_email(email, codigo, "verificacion")
            respuesta = {
                "success": True,
                "message": "Cuenta creada. Revisa tu correo para verificarla.",
            }
            if not enviado:
                respuesta["message"] = (
                    "Cuenta creada. No se pudo enviar el correo en este momento. "
                    "Intenta nuevamente más tarde."
                )
            return respuesta
        except Exception as exc:
            print(f"[ERROR] Error al registrar usuario: {exc}")
            return {"success": False, "message": "No se pudo crear la cuenta."}

    def verificar_email(self, email, codigo):
        email = (email or "").strip().lower()
        codigo_str = str(codigo or "").strip()
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return False
        if len(codigo_str) != 6 or not codigo_str.isdigit():
            return False
        if usuario.get("codigo_verificacion") != codigo_str:
            return False
        expiracion = usuario.get("codigo_verificacion_expira")
        if expiracion is None:
            return False
        if isinstance(expiracion, str):
            try:
                expiracion = datetime.fromisoformat(expiracion.replace("Z", "+00:00"))
            except ValueError:
                return False
        if datetime.now() > expiracion:
            return False
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET email_verificado = TRUE, codigo_verificacion = NULL, codigo_verificacion_expira = NULL WHERE id_usuario = %s",
            (usuario["id_usuario"],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def reenviar_codigo_verificacion(self, email):
        email = (email or "").strip().lower()
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return {"success": False, "message": "No existe una cuenta con ese correo."}

        codigo = self._generar_codigo()
        expiracion = datetime.now() + timedelta(minutes=10)
        self.usuario_dao.guardar_codigo_verificacion(email, codigo, expiracion)
        enviado = self._enviar_codigo_por_email(email, codigo, "verificacion")
        respuesta = {"success": True, "message": "Se envió un nuevo código a tu correo."}
        if not enviado:
            respuesta["message"] = (
                "Se generó un nuevo código, pero no se pudo enviar el correo en este momento. "
                "Intenta nuevamente más tarde."
            )
        return respuesta

    def login(self, credential, password):
        global sesion_actual
        if not isinstance(credential, str) or not isinstance(password, str):
            return False
        if len(credential.strip()) > 60 or len(password) > 60 or len(password.encode("utf-8")) > 72:
            return False
        email = credential.strip().lower()
        usuario = self.usuario_dao.obtener_por_email(email) if "@" in email else self.usuario_dao.obtener_por_username(email)
        if usuario is None:
            return False
        if usuario.get("email_verificado") in (False, 0, None):
            return False
        password_correcta = self.usuario_dao.verificar_password(
            password,
            usuario["password_hash"]
        )
        if not password_correcta:
            return False
        sesion_actual = {
            "id_usuario": usuario["id_usuario"],
            "username": usuario.get("username") or usuario.get("email"),
            "nombre_completo": usuario.get("nombre_completo") or f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip(),
            "email": usuario.get("email"),
            "rol": usuario.get("rol") or "lector",
        }
        return True

    def solicitar_recuperacion(self, email):
        email = (email or "").strip().lower()
        if not validar_correo(email):
            return {"success": False, "message": "Ingresa un correo válido."}
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return {"success": False, "message": "No existe una cuenta con ese correo."}
        codigo = self._generar_codigo()
        expiracion = datetime.now() + timedelta(minutes=10)
        self.usuario_dao.guardar_codigo_recuperacion(email, codigo, expiracion)
        enviado = self._enviar_codigo_por_email(email, codigo, "recuperacion")
        respuesta = {"success": True, "message": "Se envió un código a tu correo."}
        if not enviado:
            respuesta["message"] = (
                "No se pudo enviar el correo en este momento. Intenta nuevamente más tarde."
            )
        return respuesta

    def cambiar_password_con_codigo(self, email, codigo, nueva_password):
        email = (email or "").strip().lower()
        codigo = str(codigo or "").strip()
        nueva_password = nueva_password or ""
        if not validar_correo(email):
            return {"success": False, "message": "Ingresa un correo válido."}
        if len(codigo) != 6 or not codigo.isdigit():
            return {"success": False, "message": "El código debe tener exactamente 6 dígitos numéricos."}
        if len(nueva_password) < 8:
            return {"success": False, "message": "La contraseña debe tener al menos 8 caracteres."}
        if len(nueva_password.encode("utf-8")) > 72:
            return {"success": False, "message": "La contraseña no puede superar 72 bytes."}
        usuario = self.usuario_dao.obtener_por_email(email)
        if usuario is None:
            return {"success": False, "message": "No existe una cuenta con ese correo."}
        if usuario.get("codigo_recuperacion") != str(codigo).strip():
            return {"success": False, "message": "Código incorrecto."}
        if usuario.get("codigo_recuperacion_expira") is None or datetime.now() > usuario["codigo_recuperacion_expira"]:
            return {"success": False, "message": "El código ha expirado."}
        self.usuario_dao.cambiar_password(usuario["id_usuario"], nueva_password)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET codigo_recuperacion = NULL, codigo_recuperacion_expira = NULL WHERE id_usuario = %s",
            (usuario["id_usuario"],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True, "message": "Contraseña actualizada correctamente."}

    def logout(self):
        global sesion_actual
        sesion_actual = None

    def obtener_usuario_actual(self):
        return sesion_actual

    def hay_sesion_activa(self):
        return sesion_actual is not None

    def puede_escribir(self):
        return self.usuario_puede_escribir(sesion_actual)

    @staticmethod
    def usuario_puede_escribir(usuario):
        return bool(
            usuario
            and usuario.get("rol", "propietario") in ("propietario", "administrador")
        )

    @staticmethod
    def mensaje_sin_permiso():
        return "Tu rol de lector no permite crear, editar ni eliminar información."
