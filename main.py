import customtkinter as ctk

from utils import set_favicon

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def iniciar_app():
    root = ctk.CTk()
    set_favicon(root)
    from pantallas.login import LoginView
    from pantallas.principal import MainView
    
    login_view = None
    login_controller = None
    
    def al_hacer_login():
        nonlocal login_view, login_controller
        if login_controller and hasattr(login_controller, '_after_ids'):
            for aid in login_controller._after_ids:
                try:
                    root.after_cancel(aid)
                except Exception:
                    pass
        if login_view and hasattr(login_view, '_after_ids'):
            for aid in login_view._after_ids:
                try:
                    root.after_cancel(aid)
                except Exception:
                    pass
        root.destroy()
        ventana_principal = ctk.CTk()
        set_favicon(ventana_principal)
        MainView(ventana_principal)
        ventana_principal.mainloop()
    
    from pantallas.login.controller import ControladorLogin
    login_controller = ControladorLogin(root, al_hacer_login)
    login_view = login_controller.vista
    root.mainloop()


if __name__ == "__main__":
    iniciar_app()
