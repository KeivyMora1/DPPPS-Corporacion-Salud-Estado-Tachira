import threading
from datetime import date
from tkinter import filedialog, messagebox

from .model import ModeloReporte
from .view import VistaReporte


class ControladorReporte:
    def __init__(self, parent):
        self.modelo = ModeloReporte()
        self._previo = None
        self.vista = VistaReporte(parent, self)

        if self.modelo.get_usuario() is None:
            self.vista.parent.after(0, lambda: messagebox.showwarning(
                "Sesión no activa",
                "Debes iniciar sesión antes de acceder a reportes."
            ))

    def iniciar_previo(self):
        if self.modelo.get_usuario() is None:
            messagebox.showwarning("Sesión no activa", "Debes iniciar sesión antes de generar reportes.")
            return

        f_ini = self.vista.leer_fecha(self.vista._entry_f_ini)
        f_fin = self.vista.leer_fecha(self.vista._entry_f_fin)

        if not f_ini or not f_fin:
            messagebox.showerror("Fecha inválida", "Por favor ingresa ambas fechas válidas (YYYY-MM-DD).")
            return

        if f_fin < f_ini:
            messagebox.showerror("Rango inválido", "La fecha de fin no puede ser anterior a la fecha de inicio.")
            return

        titulo = self.vista._entry_titulo.get().strip() or "Informe Consolidado"
        if len(titulo) > 200 or any(ord(caracter) < 32 for caracter in titulo):
            messagebox.showerror("Título inválido", "El título no puede superar 200 caracteres ni contener controles.")
            return
        id_asic = self.vista.leer_asics_seleccionados()

        self.vista.parent.configure(cursor="wait")

        def _tarea():
            try:
                previo = self.modelo.generar_previo(f_ini, f_fin, id_asic, titulo)
                self.vista.parent.after(0, lambda p=previo: self._recibir_previo(p))
            except Exception as exc:
                self.vista.parent.after(0, lambda e=exc: self.vista.mostrar_error(e))

        threading.Thread(target=_tarea, daemon=True).start()

    def _recibir_previo(self, previo):
        self._previo = previo
        self.vista.mostrar_paso2(previo)

    def exportar_word(self):
        if not self._previo:
            return
        titulo = self._previo.get("titulo", "informe")
        nombre_sugerido = f"{titulo.replace(' ', '_')[:40]}_{date.today()}.docx"
        ruta = filedialog.asksaveasfilename(
            title="Guardar Word como…",
            defaultextension=".docx",
            initialfile=nombre_sugerido,
            filetypes=[("Word", "*.docx")],
        )
        if not ruta:
            return
        self.vista.parent.configure(cursor="wait")

        def _tarea():
            try:
                self.modelo.generar_docx(self._previo, ruta)
                self.vista.parent.after(0, lambda: (
                    self.vista.parent.configure(cursor=""),
                    messagebox.showinfo("Word generado", f"Documento Word guardado en:\n{ruta}")
                ))
            except Exception as exc:
                self.vista.parent.after(0, lambda e=exc: (
                    self.vista.parent.configure(cursor=""),
                    messagebox.showerror("Error al generar Word", str(e))
                ))

        threading.Thread(target=_tarea, daemon=True).start()


__all__ = ["ControladorReporte"]
