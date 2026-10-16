import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from datetime import datetime, date

try:
    from tkcalendar import Calendar
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
    if label_text:
        lbl = ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 10, "bold"))
        lbl.pack(anchor="w")
    max_val = 10 ** max_digits - 1
    ent = tk.Spinbox(parent, from_=0, to=max_val, font=("Arial", 11), width=8, **kwargs)
    ent.pack(fill="x", pady=(2, 0))
    ent.delete(0, tk.END)
    ent.insert(0, str(default))
    
    def _validar_longitud(e):
        if len(ent.get()) > max_digits:
            ent.delete(max_digits, tk.END)
        if on_change:
            on_change()
    
    ent.bind("<KeyRelease>", _validar_longitud)
    if on_change:
        ent.configure(command=on_change)
    return ent


class CTkDatePicker(ctk.CTkFrame):
    """Selector de fecha con calendario desplegable, estilo CTkEntry."""
    def __init__(self, parent, placeholder="AAAA-MM-DD", font=("Arial", 11),
                 fg_color="#20053D", text_color="#CBE1DB", border_color="#345572",
                 border_width=2, corner_radius=6, height=28, width=None,
                 default_today=True, max_date=None, min_date=None, **kwargs):
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
        self._date_selected_callback = None
        self.grid_columnconfigure(0, weight=1)

        entry_kwargs = {}
        if width is not None:
            entry_kwargs["width"] = max(width - 36, 40)

        self.entry = ctk.CTkEntry(
            self,
            font=font,
            fg_color=fg_color,
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
                maxdate=max_date,
                mindate=min_date,
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
                if self._date_selected_callback:
                    self._date_selected_callback()
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

    def set_date_selected_callback(self, callback):
        self._date_selected_callback = callback

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


def date_picker(parent, placeholder="AAAA-MM-DD", font=None, fg_color="#20053D", text_color="#CBE1DB", border_color="#345572", default_today=True, max_date=None, min_date=None, **kwargs):
    """Campo de fecha con selector de calendario estilo CTkEntry."""
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
        max_date=max_date,
        min_date=min_date,
        **kwargs
    )


class CTkMultiSelectOptionMenu(ctk.CTkFrame):
    """Menú desplegable de selección múltiple estilo CTkOptionMenu."""
    def __init__(self, parent, values=None, placeholder="Todos", width=220, height=28,
                 fg_color="#20053D", button_color="#26405E", button_hover_color="#2f4d6a",
                 text_color="#CBE1DB", dropdown_fg_color="#20053D", dropdown_text_color="#CBE1DB",
                 border_color="#345572", border_width=1, corner_radius=6, command=None, **kwargs):
        super().__init__(
            parent,
            fg_color=fg_color,
            border_color=border_color,
            border_width=border_width,
            corner_radius=corner_radius,
            width=width,
            height=height
        )
        self.grid_propagate(False)
        self.pack_propagate(False)

        self._values = values or []
        self._placeholder = placeholder
        self._command = command
        self._button_color = button_color
        self._button_hover_color = button_hover_color
        self._text_color = text_color
        self._dropdown_fg_color = dropdown_fg_color
        self._border_color = border_color
        self._selected = set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.btn_main = ctk.CTkButton(
            self,
            text=self._placeholder,
            font=("Arial", 10),
            fg_color=fg_color,
            hover_color=button_hover_color,
            text_color=text_color,
            anchor="w",
            corner_radius=corner_radius,
            command=self.toggle_dropdown
        )
        self.btn_main.grid(row=0, column=0, sticky="nsew", padx=(2, 0), pady=1)

        self.btn_arrow = ctk.CTkButton(
            self,
            text="▼",
            width=24,
            font=("Arial", 9),
            fg_color=button_color,
            hover_color=button_hover_color,
            text_color=text_color,
            corner_radius=corner_radius,
            command=self.toggle_dropdown
        )
        self.btn_arrow.grid(row=0, column=1, sticky="ns", padx=(1, 1), pady=1)

        self._top_menu = None
        self._check_vars = {}

    def toggle_dropdown(self):
        if self._top_menu and self._top_menu.winfo_exists() and self._top_menu.winfo_ismapped():
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        if self._top_menu and self._top_menu.winfo_exists():
            self._top_menu.destroy()

        self._top_menu = tk.Toplevel(self)
        self._top_menu.withdraw()
        self._top_menu.overrideredirect(True)
        self._top_menu.attributes("-topmost", True)

        menu_frame = ctk.CTkFrame(
            self._top_menu,
            fg_color=self._dropdown_fg_color,
            border_color=self._border_color,
            border_width=1,
            corner_radius=6
        )
        menu_frame.pack(fill="both", expand=True)

        todos_var = tk.BooleanVar(value=(len(self._selected) == 0))

        def on_toggle_todos():
            if todos_var.get():
                self._selected.clear()
                for v, var in self._check_vars.items():
                    var.set(False)
            self._update_label()
            if self._command:
                self._command(self.get_selected())

        cb_todos = ctk.CTkCheckBox(
            menu_frame,
            text="(Todos)",
            font=("Arial", 10, "bold"),
            text_color=self._text_color,
            fg_color="#613BE3",
            hover_color="#4e2fb8",
            variable=todos_var,
            command=on_toggle_todos,
            height=22,
            checkbox_width=16,
            checkbox_height=16
        )
        cb_todos.pack(anchor="w", padx=10, pady=(8, 4))

        scroll = ctk.CTkScrollableFrame(
            menu_frame,
            fg_color="transparent",
            height=min(max(len(self._values) * 26, 60), 200),
            width=max(self.winfo_width() - 20, 220)
        )
        scroll.pack(fill="both", expand=True, padx=4, pady=(2, 6))

        self._check_vars = {}
        for val in self._values:
            var = tk.BooleanVar(value=(val in self._selected))
            self._check_vars[val] = var

            def on_item_toggle(v=val, bvar=var):
                if bvar.get():
                    self._selected.add(v)
                else:
                    self._selected.discard(v)
                todos_var.set(len(self._selected) == 0)
                self._update_label()
                if self._command:
                    self._command(self.get_selected())

            cb = ctk.CTkCheckBox(
                scroll,
                text=str(val),
                font=("Arial", 10),
                text_color=self._text_color,
                fg_color="#613BE3",
                hover_color="#4e2fb8",
                variable=var,
                command=on_item_toggle,
                height=22,
                checkbox_width=16,
                checkbox_height=16
            )
            cb.pack(anchor="w", padx=4, pady=2)

        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        w = max(self.winfo_width(), 240)
        h = min(max(len(self._values) * 26 + 50, 90), 250)
        self._top_menu.geometry(f"{w}x{h}+{x}+{y}")
        self._top_menu.deiconify()
        self._top_menu.lift()
        self._bind_outside_click()

    def _close_dropdown(self):
        if self._top_menu and self._top_menu.winfo_exists():
            self._top_menu.destroy()
            self._top_menu = None

    def _bind_outside_click(self):
        top_win = self.winfo_toplevel()
        def _check_click(e):
            if not self._top_menu or not self._top_menu.winfo_exists():
                try:
                    top_win.unbind("<ButtonPress-1>", click_id)
                except Exception:
                    pass
                return
            try:
                x, y = self._top_menu.winfo_pointerxy()
                xc = self._top_menu.winfo_rootx()
                yc = self._top_menu.winfo_rooty()
                w = self._top_menu.winfo_width()
                h = self._top_menu.winfo_height()
                if not (xc <= x <= xc + w and yc <= y <= yc + h):
                    bx = self.winfo_rootx()
                    by = self.winfo_rooty()
                    bw = self.winfo_width()
                    bh = self.winfo_height()
                    if not (bx <= x <= bx + bw and by <= y <= by + bh):
                        self._close_dropdown()
                        top_win.unbind("<ButtonPress-1>", click_id)
            except Exception:
                pass
        click_id = top_win.bind("<ButtonPress-1>", _check_click, add="+")

    def _update_label(self):
        if not self._selected:
            self.btn_main.configure(text=self._placeholder)
        elif len(self._selected) == 1:
            self.btn_main.configure(text=list(self._selected)[0])
        elif len(self._selected) <= 2:
            self.btn_main.configure(text=", ".join(list(self._selected)))
        else:
            self.btn_main.configure(text=f"{len(self._selected)} seleccionados")

    def get_selected(self):
        return list(self._selected)

    def get(self):
        return self.get_selected()

    def set_values(self, values):
        self._values = values
        self._selected.clear()
        self._update_label()

    def set_selected(self, selected_list):
        self._selected = set(selected_list) if selected_list else set()
        self._update_label()


def multiselect_option_menu(parent, values=None, placeholder="Todos", width=220, **kwargs):
    """Menú de selección múltiple estilo CTkOptionMenu."""
    return CTkMultiSelectOptionMenu(parent, values=values, placeholder=placeholder, width=width, **kwargs)


def entry_numeric(parent, label_text="", placeholder="", max_digits=5, on_change=None, fg_color=None, text_color=None, border_color=None, **kwargs):
    """Entry numérico con label opcional."""
    if label_text:
        lbl = ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 10, "bold"))
        lbl.pack(anchor="w")
    
    def validar_texto(texto):
        if texto == "":
            return True
        return texto.isdigit() and len(texto) <= max_digits
    
    vcmd = (parent.register(validar_texto), "%P")
    
    e = ctk.CTkEntry(
        parent,
        font=("Arial", 11),
        corner_radius=6,
        fg_color=fg_color,
        text_color=text_color,
        border_color=border_color,
        validate="key",
        validatecommand=vcmd,
        **kwargs
    )
    e.pack(fill="x", pady=(2, 0))
    
    if placeholder:
        e.insert(0, placeholder)
        e.configure(text_color="gray50")
    
    def _validar(entry):
        if on_change:
            on_change()
    
    e.bind("<FocusOut>", lambda ev: _validar(e))
    return e