from tkinter import ttk


class Palette:

    BG_APP        = "#0f172a"
    BG_SURFACE    = "#1e293b"
    BG_SURFACE_2  = "#273449"
    BG_INPUT      = "#0b1220"

    BORDER        = "#334155"
    BORDER_SOFT   = "#1f2a3d"
    BORDER_FOCUS  = "#6366f1"

    TEXT_PRIMARY   = "#f1f5f9"
    TEXT_SECONDARY = "#cbd5e1"
    TEXT_MUTED     = "#94a3b8"
    TEXT_SUBTLE    = "#64748b"

    PRIMARY        = "#6366f1"
    PRIMARY_HOVER  = "#4f46e5"
    PRIMARY_TEXT   = "#ffffff"

    GHOST_BG       = "#1e293b"
    GHOST_BG_HOVER = "#2a3a55"
    GHOST_TEXT     = "#e2e8f0"

    ACCENT         = "#f59e0b"
    ACCENT_SOFT    = "#fbbf24"

    SUCCESS        = "#10b981"
    DANGER         = "#ef4444"

    ROW_EVEN        = "#172033"
    ROW_ODD         = "#1c2741"
    ROW_SELECTED    = "#312e81"
    ROW_SELECTED_FG = "#ffffff"

    GANTT_COLORS = [
        "#6366f1",
        "#0ea5e9",
        "#14b8a6",
        "#8b5cf6",
        "#f59e0b",
        "#ec4899",
        "#22c55e",
    ]


def configure_ttk_styles(ui_font):
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Scheduler.TNotebook",
        background=Palette.BG_APP, borderwidth=0, tabmargins=[0, 0, 0, 10])
    style.configure(
        "Scheduler.TNotebook.Tab",
        background=Palette.BG_SURFACE,
        foreground=Palette.TEXT_MUTED,
        padding=(22, 12), borderwidth=0,
        font=(ui_font, 10, "bold"),
    )
    style.map(
        "Scheduler.TNotebook.Tab",
        background=[("selected", Palette.PRIMARY), ("active", Palette.BG_SURFACE_2)],
        foreground=[("selected", Palette.PRIMARY_TEXT), ("active", Palette.TEXT_PRIMARY)],
    )

    style.configure(
        "TScrollbar",
        troughcolor=Palette.BG_SURFACE,
        background=Palette.BORDER,
        bordercolor=Palette.BG_SURFACE,
        arrowcolor=Palette.TEXT_MUTED,
    )
    style.map(
        "TScrollbar",
        background=[("active", Palette.TEXT_SUBTLE)],
    )

    style.configure(
        "Scheduler.Treeview",
        background=Palette.BG_INPUT,
        foreground=Palette.TEXT_PRIMARY,
        fieldbackground=Palette.BG_INPUT,
        borderwidth=0, rowheight=38,
        font=(ui_font, 10),
    )
    style.map(
        "Scheduler.Treeview",
        background=[("selected", Palette.ROW_SELECTED)],
        foreground=[("selected", Palette.ROW_SELECTED_FG)],
    )
    style.configure("Scheduler.Treeview", bordercolor=Palette.BORDER)
    style.configure(
        "Scheduler.Treeview.Heading",
        background=Palette.BG_SURFACE_2,
        foreground=Palette.TEXT_SECONDARY,
        borderwidth=0, relief="flat",
        padding=(12, 10),
        font=(ui_font, 9, "bold"),
    )
    style.map(
        "Scheduler.Treeview.Heading",
        background=[("active", Palette.BORDER)],
    )

    style.configure(
        "Scheduler.TCombobox",
        fieldbackground=Palette.BG_INPUT,
        background=Palette.BG_INPUT,
        foreground=Palette.TEXT_PRIMARY,
        arrowcolor=Palette.PRIMARY,
        bordercolor=Palette.BORDER,
        lightcolor=Palette.BORDER,
        darkcolor=Palette.BORDER,
        padding=10,
    )
    style.map(
        "Scheduler.TCombobox",
        fieldbackground=[("readonly", Palette.BG_INPUT)],
        background=[("readonly", Palette.BG_INPUT)],
        foreground=[("readonly", Palette.TEXT_PRIMARY)],
        selectforeground=[("readonly", Palette.TEXT_PRIMARY)],
        selectbackground=[("readonly", Palette.BG_INPUT)],
        bordercolor=[("focus", Palette.BORDER_FOCUS)],
        lightcolor=[("focus", Palette.BORDER_FOCUS)],
        darkcolor=[("focus", Palette.BORDER_FOCUS)],
    )

    return style


def build_widget_styles(ui_font, mono_font):
    entry_style = {
        "font": (ui_font, 10),
        "bg": Palette.BG_INPUT, "fg": Palette.TEXT_PRIMARY,
        "insertbackground": Palette.PRIMARY,
        "relief": "flat", "bd": 0,
        "highlightthickness": 1,
        "highlightbackground": Palette.BORDER,
        "highlightcolor": Palette.BORDER_FOCUS,
    }
    button_style = {
        "font": (ui_font, 10, "bold"),
        "bg": Palette.PRIMARY, "fg": Palette.PRIMARY_TEXT,
        "activebackground": Palette.PRIMARY_HOVER,
        "activeforeground": Palette.PRIMARY_TEXT,
        "relief": "flat", "bd": 0, "cursor": "hand2",
        "padx": 20, "pady": 11,
    }
    secondary_button_style = {
        "font": (ui_font, 10, "bold"),
        "bg": Palette.GHOST_BG, "fg": Palette.GHOST_TEXT,
        "activebackground": Palette.GHOST_BG_HOVER,
        "activeforeground": Palette.TEXT_PRIMARY,
        "relief": "flat", "bd": 0, "cursor": "hand2",
        "padx": 20, "pady": 11,
    }
    danger_button_style = {
        "font": (ui_font, 10, "bold"),
        "bg": Palette.GHOST_BG, "fg": Palette.DANGER,
        "activebackground": "#3b1218", "activeforeground": "#fca5a5",
        "relief": "flat", "bd": 0, "cursor": "hand2",
        "padx": 20, "pady": 11,
    }
    text_style = {
        "font": (mono_font, 10),
        "bg": Palette.BG_INPUT, "fg": Palette.TEXT_PRIMARY,
        "insertbackground": Palette.PRIMARY,
        "relief": "flat", "bd": 0,
        "padx": 16, "pady": 14,
        "highlightthickness": 1,
        "highlightbackground": Palette.BORDER,
        "highlightcolor": Palette.BORDER_FOCUS,
    }
    return {
        "entry": entry_style,
        "button": button_style,
        "secondary_button": secondary_button_style,
        "danger_button": danger_button_style,
        "text": text_style,
    }