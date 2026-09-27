import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from datetime import datetime, date

try:
    from tkcalendar import Calendar, DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False


def frame(parent, **kwargs):
    return ctk.CTkFrame(parent, **kwargs)


def frame_transparent(parent, **kwargs):
    return ctk.CTkFrame(parent, fg_color="transparent", **kwargs)


def frame_surface(parent, **kwargs):
    return ctk.CTkFrame(parent, fg_color=kwargs.pop("fg_color", "gray20"), corner_radius=kwargs.pop("corner_radius", 10), **kwargs)


def label(parent, text="", font_size=12, bold=False, **kwargs):
    weight = "bold" if bold else "normal"
    return ctk.CTkLabel(
        parent, text=text,
        font=("Segoe UI", font_size, weight),
        **kwargs
    )


def label_title(parent, text, font_size=20, **kwargs):
    return label(parent, text, font_size, True, **kwargs)


def label_subtitle(parent, text, font_size=10, **kwargs):
    return label(parent, text, font_size, **kwargs)


def label_section(parent, text, font_size=13, **kwargs):
    return label(parent, text, font_size, True, **kwargs)


def btn_nav(parent, text, command, active=False, **kwargs):
    return ctk.CTkButton(
        parent, text=f"  {text}",
        font=("Segoe UI", 13), anchor="w", height=38,
        corner_radius=8, command=command, **kwargs
    )


def btn_primary(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, font=("Segoe UI", 11, "bold"),
        corner_radius=8, command=command, **kwargs
    )


def btn_secondary(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, font=("Segoe UI", 10),
        corner_radius=8, command=command, **kwargs
    )


def btn_danger(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, font=("Segoe UI", 10),
        corner_radius=8, fg_color="#c45050", hover_color="#a83838",
        command=command, **kwargs
    )


def btn_success(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, font=("Segoe UI", 10, "bold"),
        corner_radius=8, fg_color="#317E87", hover_color="#266470",
        command=command, **kwargs
    )


def btn_ghost(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, font=("Segoe UI", 10),
        fg_color="transparent", corner_radius=8,
        command=command, **kwargs
    )


def btn_icon(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, font=("Segoe UI", 14),
        fg_color="transparent", corner_radius=4,
        width=32, height=30, command=command, **kwargs
    )


def separator(parent, horizontal=True, **kwargs):
    if horizontal:
        return ctk.CTkFrame(parent, height=1, corner_radius=0, **kwargs)
    return ctk.CTkFrame(parent, width=1, corner_radius=0, **kwargs)


def canvas_circle(parent, size, **kwargs):
    return tk.Canvas(parent, width=size, height=size, highlightthickness=0, **kwargs)


def scrollable_frame(parent, **kwargs):
    return ctk.CTkScrollableFrame(parent, **kwargs)


def entry(parent, placeholder="", **kwargs):
    e = ctk.CTkEntry(parent, font=("Segoe UI", 11), corner_radius=6, **kwargs)
    if placeholder:
        e.insert(0, placeholder)
    return e


def combobox(parent, values, **kwargs):
    return ctk.CTkOptionMenu(parent, values=values, **kwargs)


def textbox(parent, height=80, **kwargs):
    return ctk.CTkTextbox(parent, font=("Segoe UI", 10), corner_radius=6, height=height, **kwargs)


def treeview_style(style_name, rowheight=28):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(f"{style_name}.Treeview", rowheight=rowheight)
    style.configure(f"{style_name}.Treeview.Heading", font=("Segoe UI", 10, "bold"), relief="flat")
    style.map(f"{style_name}.Treeview", background=[("selected", "#613BE3")])


def card_with_accent(parent, **kwargs):
    return frame(parent, **kwargs)


def entry_with_placeholder(parent, placeholder="", **kwargs):
    """CTkEntry con manejo automático de placeholder."""
    font = kwargs.pop("font", ("Segoe UI", 11))
    e = ctk.CTkEntry(parent, font=font, corner_radius=6, **kwargs)
    if placeholder:
        e.insert(0, placeholder)
        e.configure(text_color="gray50")
        def on_focus_in(event):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.configure(text_color="white")
        def on_focus_out(event):
            if e.get() == "":
                e.insert(0, placeholder)
                e.configure(text_color="gray50")
        e.bind("<FocusIn>", on_focus_in)
        e.bind("<FocusOut>", on_focus_out)
    return e


def spinbox_numeric(parent, label_text="", default=0, on_change=None, max_digits=5, **kwargs):
    """Campo numérico (Spinbox) con label opcional."""
    if label_text:
        lbl = ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 10, "bold"))
        lbl.pack(anchor="w")
    max_val = 10 ** max_digits - 1
    ent = tk.Spinbox(parent, from_=0, to=max_val, font=("Arial", 11), width=8, **kwargs)
    ent.pack(fill="x", pady=(2, 0))
    ent.delete(0, tk.END)
    ent.insert(0, str(default))
    
    # Validar longitud máxima al escribir
    def _validar_longitud(e):
        if len(ent.get()) > max_digits:
            ent.delete(max_digits, tk.END)
        if on_change:
            on_change()
    
    ent.bind("<KeyRelease>", _validar_longitud)
    if on_change:
        ent.configure(command=on_change)
    return ent


def form_field_row(parent, fields, label_width=10):
    """Crea una fila de campos de formulario (label + entry) en columnas."""
    # fields: lista de dicts con keys: label, placeholder, width, etc.
    pass  # placeholder for future use


class CTkDatePicker(ctk.CTkFrame):
    """
    Selector de fecha interactivo con apariencia y dimensiones idénticas a un CTkEntry,
    con botón desplegable de calendario.
    """
    def __init__(self, parent, placeholder="AAAA-MM-DD", font=("Arial", 11),
                 fg_color="#20053D", text_color="#CBE1DB", border_color="#345572",
                 border_width=2, corner_radius=6, height=28, width=None,
                 default_today=True, **kwargs):
        frame_kwargs = {}
        if width is not None:
            frame_kwargs["width"] = width
        super().__init__(
            parent,
            fg_color=fg_color,
            border_color=border_color,
            border_width=border_width,
            corner_radius=corner_radius,
            height=height,
            **frame_kwargs
        )
        self._default_border = border_color
        self._focus_border = "#613BE3"
        self._placeholder = placeholder
        self._text_color = text_color
        self._dim_color = "gray50"
        self.grid_columnconfigure(0, weight=1)

        entry_kwargs = {}
        if width is not None:
            entry_kwargs["width"] = max(width - 36, 40)

        self.entry = ctk.CTkEntry(
            self,
            font=font,
            fg_color="transparent",
            text_color=text_color,
            border_width=0,
            height=height - 4,
            **entry_kwargs
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(8, 2), pady=2)

        if default_today:
            self.entry.insert(0, date.today().strftime("%Y-%m-%d"))
        elif placeholder:
            self.entry.insert(0, placeholder)
            self.entry.configure(text_color=self._dim_color)

        self.btn_cal = ctk.CTkButton(
            self,
            text="📅",
            width=26,
            height=height - 6,
            font=("Segoe UI Emoji", 11),
            fg_color="transparent",
            hover_color="#2f4d6a",
            text_color=text_color,
            corner_radius=4,
            command=self.toggle_calendar
        )
        self.btn_cal.grid(row=0, column=1, padx=(0, 4), pady=2)

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        if HAS_CALENDAR:
            self._top_cal = tk.Toplevel(self)
            self._top_cal.withdraw()
            self._top_cal.overrideredirect(True)

            self.cal = Calendar(
                self._top_cal,
                date_pattern="yyyy-mm-dd",
                background="#26405E",
                foreground="#CBE1DB",
                headersbackground="#20053D",
                headersforeground="#CBE1DB",
                selectbackground="#613BE3",
                selectforeground="white",
                normalbackground="#20053D",
                normalforeground="#CBE1DB",
                weekendbackground="#26405E",
                weekendforeground="#CBE1DB",
                othermonthforeground="#5a7a85",
                othermonthbackground="#1a2f45",
                font=("Arial", 9)
            )
            self.cal.pack()
            self.cal.bind("<<CalendarSelected>>", self._on_date_selected)
        else:
            self._top_cal = None
            self.cal = None

    def _on_focus_in(self, event=None):
        self.configure(border_color=self._focus_border)
        if self._placeholder and self.entry.get() == self._placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(text_color=self._text_color)

    def _on_focus_out(self, event=None):
        self.configure(border_color=self._default_border)
        if self._placeholder and not self.entry.get().strip():
            self.entry.insert(0, self._placeholder)
            self.entry.configure(text_color=self._dim_color)

    def _on_date_selected(self, event=None):
        if self.cal:
            sel = self.cal.selection_get()
            if sel:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, sel.strftime("%Y-%m-%d"))
                self.entry.configure(text_color=self._text_color)
        if self._top_cal:
            self._top_cal.withdraw()

    def toggle_calendar(self):
        if not self._top_cal or not self.cal:
            return
        if self._top_cal.winfo_ismapped():
            self._top_cal.withdraw()
        else:
            try:
                cur_text = self.get()
                if cur_text:
                    d = datetime.strptime(cur_text, "%Y-%m-%d").date()
                    self.cal.selection_set(d)
                else:
                    self.cal.selection_set(date.today())
            except Exception:
                pass

            self.update_idletasks()
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height() + 2
            self._top_cal.geometry(f"+{x}+{y}")
            self._top_cal.deiconify()
            self._top_cal.lift()
            self._top_cal.attributes("-topmost", True)
            self._bind_outside_click()

    def _bind_outside_click(self):
        top_win = self.winfo_toplevel()
        def _check_click(e):
            if not self._top_cal or not self._top_cal.winfo_ismapped():
                try:
                    top_win.unbind("<ButtonPress-1>", click_id)
                except Exception:
                    pass
                return
            try:
                x, y = self._top_cal.winfo_pointerxy()
                xc = self._top_cal.winfo_rootx()
                yc = self._top_cal.winfo_rooty()
                w = self._top_cal.winfo_width()
                h = self._top_cal.winfo_height()
                if not (xc <= x <= xc + w and yc <= y <= yc + h):
                    bx = self.btn_cal.winfo_rootx()
                    by = self.btn_cal.winfo_rooty()
                    bw = self.btn_cal.winfo_width()
                    bh = self.btn_cal.winfo_height()
                    if not (bx <= x <= bx + bw and by <= y <= by + bh):
                        self._top_cal.withdraw()
                        top_win.unbind("<ButtonPress-1>", click_id)
            except Exception:
                pass
        click_id = top_win.bind("<ButtonPress-1>", _check_click, add="+")

    def get(self):
        val = self.entry.get().strip()
        if self._placeholder and val == self._placeholder:
            return ""
        return val

    def get_date(self):
        val = self.get()
        if not val:
            return None
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except Exception:
            return None

    def delete(self, first, last=None):
        return self.entry.delete(first, last)

    def insert(self, index, string):
        self.entry.configure(text_color=self._text_color)
        return self.entry.insert(index, string)

    def set_date(self, d):
        if not d:
            self.delete(0, tk.END)
            if self._placeholder:
                self.entry.insert(0, self._placeholder)
                self.entry.configure(text_color=self._dim_color)
            return

        if isinstance(d, (date, datetime)):
            txt = d.strftime("%Y-%m-%d")
            if self.cal:
                try:
                    self.cal.selection_set(d)
                except Exception:
                    pass
        else:
            txt = str(d).strip()
            if self.cal:
                try:
                    parsed = datetime.strptime(txt, "%Y-%m-%d").date()
                    self.cal.selection_set(parsed)
                except Exception:
                    pass
        self.entry.delete(0, tk.END)
        self.entry.insert(0, txt)
        self.entry.configure(text_color=self._text_color)

    def bind(self, sequence=None, func=None, add="+"):
        if add is None:
            add = "+"
        return self.entry.bind(sequence, func, add=add)

    def unbind(self, sequence=None, funcid=None):
        return self.entry.unbind(sequence, funcid)


def date_picker(parent, placeholder="AAAA-MM-DD", font=None, fg_color="#20053D", text_color="#CBE1DB", border_color="#345572", default_today=True, **kwargs):
    """Campo de fecha con selector de calendario con estilo CustomTkinter idéntico a CTkEntry."""
    corner_radius = kwargs.pop("corner_radius", 6)
    border_width = kwargs.pop("border_width", 2)
    return CTkDatePicker(
        parent,
        placeholder=placeholder,
        font=font or ("Arial", 11),
        fg_color=fg_color,
        text_color=text_color,
        border_color=border_color,
        border_width=border_width,
        corner_radius=corner_radius,
        default_today=default_today,
        **kwargs
    )


def entry_numeric(parent, label_text="", placeholder="", max_digits=5, on_change=None, fg_color=None, text_color=None, border_color=None, **kwargs):
    """Entry numérico con label opcional, estilo consistente con CTkEntry."""
    if label_text:
        lbl = ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 10, "bold"))
        lbl.pack(anchor="w")
    
    e = ctk.CTkEntry(
        parent,
        font=("Arial", 11),
        corner_radius=6,
        fg_color=fg_color,
        text_color=text_color,
        border_color=border_color,
        **kwargs
    )
    e.pack(fill="x", pady=(2, 0))
    
    if placeholder:
        e.insert(0, placeholder)
        e.configure(text_color="gray50")
    
    def _validar(entry):
        texto = entry.get()
        # Solo permitir dígitos
        if texto and not texto.isdigit():
            clean = ''.join(filter(str.isdigit, texto))
            entry.delete(0, tk.END)
            entry.insert(0, clean)
        # Limitar longitud
        if len(entry.get()) > max_digits:
            entry.delete(max_digits, tk.END)
        if on_change:
            on_change()
    
    e.bind("<KeyRelease>", lambda ev: _validar(e))
    e.bind("<FocusOut>", lambda ev: _validar(e))
    return e