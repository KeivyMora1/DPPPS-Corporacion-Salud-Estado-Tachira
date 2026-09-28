import os
import re
import shutil
import unicodedata
from datetime import date, datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

from db import VOCERIA_TEMPLATE_PATH, build_voceria_template
from .model import ModeloVoceria
from .view import VistaVoceria


class ControladorVoceria:
    def __init__(self, parent):
        self.modelo = ModeloVoceria()

        self.asic_map = {}
        self.tipo_map = {}
        self.tipo_voceria_map = {}
        self.tipo_voceria_map_normalizada = {}
        self._cargar_catalogos()

        self.vista = VistaVoceria(parent, self)
        self.cargar_datos_tabla()

    @staticmethod
    def _normalizar_texto(valor):
        if valor is None:
            return ""
        valor = unicodedata.normalize("NFKD", str(valor))
        valor = valor.encode("ascii", "ignore").decode("ascii")
        valor = valor.lower().strip()
        valor = re.sub(r"\s+", " ", valor)
        return valor

    def _cargar_catalogos(self):
        try:
            asics = self.modelo.listar_asics()
            self.asic_map = {a["nombre"]: a["id_asic"] for a in asics}

            tipos = self.modelo.listar_tipos_voceria()
            self.tipo_map = {t["nombre"]: t["id_tipo"] for t in tipos}
            self.tipo_voceria_map = {t["nombre"]: t["id_tipo"] for t in tipos}
            self.tipo_voceria_map_normalizada = {
                self._normalizar_texto(nombre): id_tipo
                for nombre, id_tipo in self.tipo_voceria_map.items()
            }
        except Exception as e:
            messagebox.showerror("Error de base de datos", f"No se pudieron cargar los catálogos: {str(e)}")

    def aplicar_filtros(self):
        asic_sel = self.vista.combo_filtro_asic.get()
        tipo_sel = self.vista.combo_filtro_tipo.get()
        f_desde = self.vista.ent_filtro_desde.get().strip()
        f_hasta = self.vista.ent_filtro_hasta.get().strip()

        filtros = {}

        if asic_sel != "Todos":
            filtros["id_asic"] = self.asic_map.get(asic_sel)
        if tipo_sel != "Todos":
            filtros["id_tipo"] = self.tipo_map.get(tipo_sel)

        if f_desde and f_desde != "AAAA-MM-DD":
            try:
                datetime.strptime(f_desde, "%Y-%m-%d")
                filtros["fecha_desde"] = f_desde
            except ValueError:
                messagebox.showerror("Error en Filtros", "La fecha 'Desde' debe tener el formato AAAA-MM-DD (ej: 2026-05-17).")
                return

        if f_hasta and f_hasta != "AAAA-MM-DD":
            try:
                datetime.strptime(f_hasta, "%Y-%m-%d")
                filtros["fecha_hasta"] = f_hasta
            except ValueError:
                messagebox.showerror("Error en Filtros", "La fecha 'Hasta' debe tener el formato AAAA-MM-DD (ej: 2026-05-17).")
                return

        self.cargar_datos_tabla(filtros)

    def limpiar_filtros(self):
        self.vista.combo_filtro_asic.set("Todos")
        self.vista.combo_filtro_tipo.set("Todos")
        self.vista.ent_filtro_desde.set_date("")
        self.vista.ent_filtro_hasta.set_date("")
        self.cargar_datos_tabla()

    def cargar_datos_tabla(self, filtros=None):
        for item in self.vista.tabla.get_children():
            self.vista.tabla.delete(item)

        try:
            lista = self.modelo.listar_vocerias(filtros)
            for voc in lista:
                f_ini = voc.get("fecha_registro") or voc.get("fecha")
                if isinstance(f_ini, (date, datetime)):
                    f_ini = f_ini.strftime("%d/%m/%Y")

                cantidad = voc.get("cantidad_vocerias", 0)

                self.vista.tabla.insert("", "end", iid=str(voc["id_voceria"]), values=(
                    voc["id_voceria"],
                    voc.get("asic_nombre", ""),
                    f_ini,
                    cantidad,
                    voc.get("estado", ""),
                    voc.get("municipio", ""),
                    voc.get("parroquia", ""),
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las vocerías: {str(e)}")

    def abrir_form_nueva(self):
        self.vista.abrir_formulario()

    def editar_seleccionada(self):
        seleccion = self.vista.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una vocería de la tabla para editar.")
            return
        id_voceria = int(seleccion[0])
        try:
            voc = self.modelo.obtener_voceria_completa(id_voceria)
            if not voc:
                messagebox.showerror("Error", "No se pudo recuperar la información de la vocería.")
                return
            self.vista.abrir_formulario(voc)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener la vocería: {str(e)}")

    def eliminar_seleccionada(self):
        seleccion = self.vista.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una vocería de la tabla para eliminar.")
            return
        id_voceria = int(seleccion[0])
        valores = self.vista.tabla.item(seleccion[0])["values"]
        tipo_act = valores[1]
        fecha_act = valores[2]

        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Deseas eliminar la vocería '{tipo_act}' del día {fecha_act}?\nEsta acción no se puede deshacer."):
            try:
                ok, msg = self.modelo.eliminar_voceria(id_voceria)
                if ok:
                    messagebox.showinfo("Éxito", msg)
                    self.cargar_datos_tabla()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la vocería: {str(e)}")

    def on_seleccion_cambio(self, event=None):
        seleccion = self.vista.tabla.selection()
        estado = "normal" if seleccion else "disabled"
        self.vista.btn_editar.configure(state=estado)
        self.vista.btn_eliminar.configure(state=estado)

    def abrir_detalle_voceria(self, event=None):
        seleccion = self.vista.tabla.selection()
        if not seleccion:
            return
        id_voceria = int(seleccion[0])

        try:
            voc = self.modelo.obtener_voceria_completa(id_voceria)
            if not voc:
                messagebox.showerror("Error", "No se pudo recuperar la información de la vocería.")
                return
            self.vista.mostrar_detalle_voceria(voc)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener el detalle: {str(e)}")

    def guardar_voceria(self, ventana, lbl_error, datos_edicion,
                        estado, municipio, parroquia, asic,
                        centro_dispensador, nombre_centro, nombre_comite,
                        items_validos):
        id_asic = self.asic_map.get(asic)

        items = []
        for item in items_validos:
            w = item["widgets"]
            valor_voceria = (w["voceria"].get() or "").strip()
            id_tipo_voceria = (
                self.tipo_voceria_map.get(valor_voceria)
                or self.tipo_voceria_map_normalizada.get(self._normalizar_texto(valor_voceria))
            )

            item_data = {
                "nombres": w["nombres"].get().strip(),
                "ci": w["ci"].get().strip(),
                "telefono": w["tel"].get().strip(),
                "fecha_nacimiento": w["fnac"].get().strip(),
                "edad": w["edad"].get().strip(),
                "id_tipo_voceria": id_tipo_voceria,
                "sexo": w["sexo"].get(),
                "profesion": w["prof"].get().strip(),
                "correo": w["correo"].get().strip(),
                "fechas_eleccion": w["felecc"].get().strip(),
            }
            items.append(item_data)

        id_tipo = None
        if items:
            id_tipo = items[0].get("id_tipo_voceria") or next(iter(self.tipo_voceria_map.values()), None)

        id_voceria_guardar = datos_edicion.get("id_voceria") if datos_edicion else None

        ok, msg = self.modelo.guardar_voceria(
            id_asic=id_asic,
            id_tipo=id_tipo,
            estado=estado,
            municipio=municipio,
            parroquia=parroquia,
            centro_dispensador=centro_dispensador,
            nombre_centro=nombre_centro,
            nombre_comite=nombre_comite,
            items=items,
            id_voceria=id_voceria_guardar,
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            ventana.destroy()
            self.cargar_datos_tabla()
        else:
            lbl_error.configure(text=msg)

    def descargar_plantilla(self):
        if not os.path.exists(VOCERIA_TEMPLATE_PATH):
            try:
                build_voceria_template(VOCERIA_TEMPLATE_PATH)
            except Exception as e:
                messagebox.showerror("Plantilla no disponible",
                                     f"No se pudo crear la plantilla de vocerías:\n{str(e)}")
                return

        destino = filedialog.asksaveasfilename(
            title="Guardar plantilla de vocerías como...",
            defaultextension=".xlsx",
            initialfile="FORMATO DE DATA COMITES 2026.xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
        )
        if destino:
            shutil.copy2(VOCERIA_TEMPLATE_PATH, destino)
            messagebox.showinfo("Plantilla guardada",
                                f"Plantilla de vocerías guardada en:\n{destino}")

    def abrir_modal_importar(self):
        messagebox.showinfo("Importar", "Función de importar en desarrollo.")

    def _obtener_vocerias_usadas_por_otros(self, item_actual, items_voceria):
        usadas = set()
        for item in items_voceria:
            if item != item_actual and item["frame"].winfo_exists():
                val = item["widgets"]["voceria"].get()
                if val and val not in ("(Sin opciones disponibles)", "Seleccionar vocería..."):
                    usadas.add(val)
        return usadas

    def _actualizar_dropdowns_voceria(self, items_voceria, vocerias_disponibles):
        for item in items_voceria:
            if not item["frame"].winfo_exists():
                continue
            widget = item["widgets"]["voceria"]
            val_actual = widget.get()
            otras_usadas = self._obtener_vocerias_usadas_por_otros(item, items_voceria)
            disponibles_para_este_item = [v for v in vocerias_disponibles if v not in otras_usadas]

            valores = ["Seleccionar vocería..."] + disponibles_para_este_item
            widget.configure(values=valores, state="normal")
            if val_actual in valores:
                widget.set(val_actual)
            else:
                widget.set("Seleccionar vocería...")

    def _actualizar_estado_botones_formulario(self):
        if not hasattr(self.vista, "items_voceria"):
            return

        items_activos = [i for i in self.vista.items_voceria if i["frame"].winfo_exists()]
        count = len(items_activos)

        generales_llenos = self._verificar_generales_llenos()
        todos_items_llenos = items_activos and all(self._verificar_item_completo(i) for i in items_activos)

        self._actualizar_bordes_items(items_activos)

        for item in items_activos:
            item["btn_eliminar"].configure(state="normal")

        if hasattr(self.vista, 'btn_agregar_item') and self.vista.btn_agregar_item.winfo_exists():
            self.vista.btn_agregar_item.configure(state="normal" if count < 10 else "disabled")

        if hasattr(self.vista, 'btn_guardar') and self.vista.btn_guardar.winfo_exists():
            self.vista.btn_guardar.configure(state="normal")
            if count >= 1 and generales_llenos and todos_items_llenos:
                self.vista.lbl_nota_min.configure(text="✓ Todos los campos obligatorios están completos", text_color=self.vista.t["success"])
            elif count >= 1 and not generales_llenos:
                self.vista.lbl_nota_min.configure(text="⚠ Complete los datos generales obligatorios (*)", text_color=self.vista.t["amber"])
            elif count >= 1 and not todos_items_llenos:
                self.vista.lbl_nota_min.configure(text="⚠ Complete todos los campos de cada vocería (*)", text_color=self.vista.t["amber"])
            else:
                self.vista.lbl_nota_min.configure(text="⚠ Debe agregar al menos 1 vocería", text_color=self.vista.t["text_muted"])

    def _verificar_generales_llenos(self):
        estado = self.vista.ent_estado.get().strip() if hasattr(self.vista, "ent_estado") else ""
        municipio = self.vista.ent_municipio.get().strip() if hasattr(self.vista, "ent_municipio") else ""
        parroquia = self.vista.ent_parroquia.get().strip() if hasattr(self.vista, "ent_parroquia") else ""
        asic = self.vista.ent_asic.get().strip() if hasattr(self.vista, "ent_asic") else ""
        centro_dispensador = self.vista.ent_centro_dispensador.get().strip() if hasattr(self.vista, "ent_centro_dispensador") else ""
        nombre_centro = self.vista.ent_nombre_centro.get().strip() if hasattr(self.vista, "ent_nombre_centro") else ""
        nombre_comite = self.vista.ent_nombre_comite.get().strip() if hasattr(self.vista, "ent_nombre_comite") else ""

        if not estado or estado in ("Seleccionar...", ""):
            return False
        if not municipio or municipio in ("Seleccionar...", ""):
            return False
        if not parroquia or parroquia == "Parroquia":
            return False
        if not asic or asic not in self.asic_map:
            return False
        if not centro_dispensador:
            return False
        if not nombre_centro:
            return False
        if not nombre_comite:
            return False
        return True

    def _verificar_item_completo(self, item):
        if not item["frame"].winfo_exists():
            return False
        w = item["widgets"]
        campos_obligatorios = [
            "nombres", "ci", "tel", "fnac", "edad", "voceria", "sexo", "prof", "correo", "felecc"
        ]
        for key in campos_obligatorios:
            widget = w.get(key)
            if not widget:
                return False
            val = widget.get().strip() if hasattr(widget, "get") else ""
            if not val or val in ("(Sin opciones disponibles)", "Seleccionar vocería...", "AAAA-MM-DD", "Edad"):
                return False
            if key == "correo" and "@" not in val:
                return False
            if key == "edad":
                if not val.isdigit() or len(val) > 3 or int(val) > 999:
                    return False
        return True

    def _actualizar_bordes_items(self, items_activos):
        for item in items_activos:
            if not item["frame"].winfo_exists():
                continue
            completo = self._verificar_item_completo(item)
            color = "#317E87" if completo else self.vista.t["border"]
            item["frame"].configure(border_color=color)

    def _renumerar_items(self, items_voceria):
        for idx, item in enumerate(items_voceria):
            if item["frame"].winfo_exists():
                item["index"] = idx + 1
                item["lbl_titulo"].configure(text=f"Vocería #{idx + 1}")
                item["btn_eliminar"].configure(state="normal")
                self.vista._actualizar_header_item(item)

    def agregar_siguiente_voceria(self, frame_items, items_voceria, vocerias_disponibles):
        self.vista._crear_item_voceria(frame_items, items_voceria, vocerias_disponibles, expandido=True)
        self._actualizar_dropdowns_voceria(items_voceria, vocerias_disponibles)
        self._actualizar_estado_botones_formulario()
        self._renumerar_items(items_voceria)

    def _eliminar_item_voceria(self, item_data, items_voceria, vocerias_disponibles):
        if item_data in items_voceria:
            item_data["frame"].destroy()
            items_voceria.remove(item_data)
            self._actualizar_dropdowns_voceria(items_voceria, vocerias_disponibles)
            self._actualizar_estado_botones_formulario()
            self._renumerar_items(items_voceria)


__all__ = ["ControladorVoceria"]
