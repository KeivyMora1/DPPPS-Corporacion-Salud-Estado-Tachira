# ============================================================
# main.py
# Punto de entrada principal del sistema DPPPS.
# Este es el archivo que debes ejecutar para iniciar la app:
#   python main.py
# ============================================================

import tkinter as tk


def iniciar_app():
    """
    Función principal que inicia la aplicación.
    Primero muestra la pantalla de login.
    Si el login es exitoso, muestra la ventana principal.
    """
    # Creamos la ventana raíz de Tkinter
    root = tk.Tk()

    # Importamos las pantallas aquí para evitar importaciones circulares
    from pantallas.login     import LoginView
    from pantallas.principal import MainView

    def al_hacer_login():
        """
        Esta función se llama cuando el login es exitoso.
        Destruye la ventana de login y abre la ventana principal.
        """
        root.destroy()               # Cerramos la ventana de login
        ventana_principal = tk.Tk()  # Creamos una nueva ventana
        MainView(ventana_principal)  # Cargamos la vista principal
        ventana_principal.mainloop() # Iniciamos el loop de la ventana principal

    # Mostramos la pantalla de login
    LoginView(root, al_hacer_login)
    root.mainloop()


# ============================================================
# Punto de entrada: solo se ejecuta si corremos este archivo
# directamente (no cuando se importa desde otro módulo)
# ============================================================
if __name__ == "__main__":
    iniciar_app()
