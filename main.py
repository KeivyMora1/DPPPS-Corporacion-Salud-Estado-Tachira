import os
import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _set_favicon(ventana):
    """Establece el favicon de la ventana."""
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "images", "logo2.ico")
    if os.path.exists(logo_path):
        try:
            ventana.iconbitmap(logo_path)
        except Exception:
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo_path.replace('.ico', '.png'))
                photo = ImageTk.PhotoImage(img)
                ventana.iconphoto(True, photo)
                ventana._favicon = photo
            except Exception:
                pass


def iniciar_app():
    root = ctk.CTk()
    _set_favicon(root)
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
        _set_favicon(ventana_principal)
        MainView(ventana_principal)
        ventana_principal.mainloop()
    
    from pantallas.login.controller import ControladorLogin
    login_controller = ControladorLogin(root, al_hacer_login)
    login_view = login_controller.vista
    root.mainloop()


if __name__ == "__main__":
    iniciar_app()
