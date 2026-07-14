# ============================================================
# main.py
# Punto de entrada principal del sistema DPPPS.
# Este es el archivo que debes ejecutar para iniciar la app:
#   python main.py
# ============================================================

import tkinter as tk
import customtkinter as ctk

ctk.set_default_color_theme("blue")


def iniciar_app():
    """
    Función principal que inicia la aplicación.
    Primero muestra la pantalla de login.
    Si el login es exitoso, muestra la ventana principal.
    """
    root = ctk.CTk()

    from pantallas.login     import LoginView
    from pantallas.principal import MainView

    def al_hacer_login():
        root.destroy()
        ventana_principal = ctk.CTk()
        MainView(ventana_principal)
        ventana_principal.mainloop()

    LoginView(root, al_hacer_login)
    root.mainloop()


# ============================================================
# Punto de entrada: solo se ejecuta si corremos este archivo
# directamente (no cuando se importa desde otro módulo)
# ============================================================
if __name__ == "__main__":
    iniciar_app()
