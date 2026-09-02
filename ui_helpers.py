import customtkinter as ctk
import tkinter as tk
from tkinter import ttk


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