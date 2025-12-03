# theme.py
import tkinter as tk
from tkinter import ttk

def apply_modern_dark_theme(root):
    palette = {
        "bg_main": "#1E1E2E",
        "bg_sidebar": "#181825",
        "bg_card": "#313244",
        "fg_text": "#CDD6F4",
        "fg_muted": "#A6ADC8",
        "accent": "#89B4FA",
        "accent_hover": "#B4BEFE",
        "select_bg": "#45475A",
        "border": "#585B70"
    }

    root.configure(bg=palette["bg_main"])

    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("Main.TFrame", background=palette["bg_main"])
    style.configure("Sidebar.TFrame", background=palette["bg_sidebar"])

    style.configure("TLabel", background=palette["bg_main"], foreground=palette["fg_text"])
    style.configure("Header.TLabel", background=palette["bg_main"], foreground=palette["accent"], font=("Segoe UI", 12, "bold"))

    style.configure("TEntry",
                    fieldbackground=palette["bg_card"],
                    background=palette["bg_card"],
                    foreground=palette["fg_text"],
                    padding=6,
                    bordercolor=palette["border"],
                    relief="flat")

    style.configure("TScrollbar",
                    troughcolor=palette["bg_sidebar"],
                    background=palette["bg_card"],
                    bordercolor=palette["border"])

    return palette
