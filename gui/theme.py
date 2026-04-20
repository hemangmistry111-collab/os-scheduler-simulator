from tkinter import ttk


class _Dark:
    NAME = "dark"

    BG_APP        = "#0d1117"
    BG_SURFACE    = "#161b22"
    BG_SURFACE_2  = "#1c2128"
    BG_INPUT      = "#0b0f14"

    BORDER        = "#30363d"
    BORDER_SOFT   = "#21262d"
    BORDER_FOCUS  = "#58a6ff"

    TEXT_PRIMARY   = "#e6edf3"
    TEXT_SECONDARY = "#b1bac4"
    TEXT_MUTED     = "#7d8590"
    TEXT_SUBTLE    = "#484f58"

    PRIMARY        = "#2f81f7"
    PRIMARY_HOVER  = "#1f6feb"
    PRIMARY_TEXT   = "#ffffff"

    GHOST_BG       = "#21262d"
    GHOST_BG_HOVER = "#30363d"
    GHOST_TEXT     = "#c9d1d9"

    ACCENT         = "#d29922"
    ACCENT_SOFT    = "#e3b341"

    SUCCESS        = "#3fb950"
    WARNING        = "#d29922"
    DANGER         = "#f85149"
    INFO           = "#58a6ff"

    ROW_EVEN        = "#0d1117"
    ROW_ODD         = "#161b22"
    ROW_SELECTED    = "#1f6feb"
    ROW_SELECTED_FG = "#ffffff"
    ROW_HOVER       = "#1c2128"

    GANTT_COLORS = [
        "#58a6ff",
        "#3fb950",
        "#d29922",
        "#bc8cff",
        "#ff7b72",
        "#39c5cf",
        "#f778ba",
    ]


class _Light:
    NAME = "light"

    BG_APP        = "#f6f8fa"
    BG_SURFACE    = "#ffffff"
    BG_SURFACE_2  = "#f6f8fa"
    BG_INPUT      = "#ffffff"

    BORDER        = "#d0d7de"
    BORDER_SOFT   = "#eaeef2"
    BORDER_FOCUS  = "#0969da"

    TEXT_PRIMARY   = "#1f2328"
    TEXT_SECONDARY = "#424a53"
    TEXT_MUTED     = "#656d76"
    TEXT_SUBTLE    = "#8c959f"

    PRIMARY        = "#0969da"
    PRIMARY_HOVER  = "#0550ae"
    PRIMARY_TEXT   = "#ffffff"

    GHOST_BG       = "#f6f8fa"
    GHOST_BG_HOVER = "#eaeef2"
    GHOST_TEXT     = "#24292f"

    ACCENT         = "#9a6700"
    ACCENT_SOFT    = "#bf8700"

    SUCCESS        = "#1a7f37"
    WARNING        = "#9a6700"
    DANGER         = "#cf222e"
    INFO           = "#0969da"

    ROW_EVEN        = "#ffffff"
    ROW_ODD         = "#f6f8fa"
    ROW_SELECTED    = "#ddf4ff"
    ROW_SELECTED_FG = "#0550ae"
    ROW_HOVER       = "#eaeef2"

    GANTT_COLORS = [
        "#0969da",
        "#1a7f37",
        "#bf8700",
        "#8250df",
        "#cf222e",
        "#1b7c83",
        "#bf3989",
    ]


class Palette:
    _active = _Dark

    @classmethod
    def set_theme(cls, name):
        cls._active = _Light if name == "light" else _Dark
        for attr in dir(cls._active):
            if attr.startswith("_") or attr == "NAME":
                continue
            setattr(cls, attr, getattr(cls._active, attr))

    @classmethod
    def current_name(cls):
        return cls._active.NAME


Palette.set_theme("dark")


def configure_ttk_styles(ui_font):
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Scheduler.TNotebook",
        background=Palette.BG_APP,
        borderwidth=0,
        tabmargins=[0, 0, 0, 8],
    )
    style.configure(
        "Scheduler.TNotebook.Tab",
        background=Palette.BG_APP,
        foreground=Palette.TEXT_MUTED,
        padding=(20, 12),
        borderwidth=0,
        font=(ui_font, 10),
    )
    style.map(
        "Scheduler.TNotebook.Tab",
        background=[("selected", Palette.BG_SURFACE), ("active", Palette.BG_SURFACE_2)],
        foreground=[("selected", Palette.PRIMARY), ("active", Palette.TEXT_PRIMARY)],
        font=[("selected", (ui_font, 10, "bold"))],
    )

    style.configure(
        "TScrollbar",
        troughcolor=Palette.BG_APP,
        background=Palette.BORDER,
        bordercolor=Palette.BG_APP,
        arrowcolor=Palette.TEXT_MUTED,
        relief="flat",
    )
    style.map(
        "TScrollbar",
        background=[("active", Palette.TEXT_SUBTLE)],
    )

    style.configure(
        "Scheduler.Treeview",
        background=Palette.BG_SURFACE,
        foreground=Palette.TEXT_PRIMARY,
        fieldbackground=Palette.BG_SURFACE,
        borderwidth=0,
        rowheight=36,
        font=(ui_font, 10),
    )
    style.map(
        "Scheduler.Treeview",
        background=[("selected", Palette.ROW_SELECTED)],
        foreground=[("selected", Palette.ROW_SELECTED_FG)],
    )
    style.configure("Scheduler.Treeview", bordercolor=Palette.BORDER_SOFT)
    style.configure(
        "Scheduler.Treeview.Heading",
        background=Palette.BG_SURFACE_2,
        foreground=Palette.TEXT_MUTED,
        borderwidth=0,
        relief="flat",
        padding=(12, 12),
        font=(ui_font, 9, "bold"),
    )
    style.map(
        "Scheduler.Treeview.Heading",
        background=[("active", Palette.BORDER_SOFT)],
    )

    style.configure(
        "Scheduler.TCombobox",
        fieldbackground=Palette.BG_INPUT,
        background=Palette.BG_INPUT,
        foreground=Palette.TEXT_PRIMARY,
        arrowcolor=Palette.TEXT_MUTED,
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
        "bg": Palette.BG_INPUT,
        "fg": Palette.TEXT_PRIMARY,
        "insertbackground": Palette.PRIMARY,
        "relief": "flat",
        "bd": 0,
        "highlightthickness": 1,
        "highlightbackground": Palette.BORDER,
        "highlightcolor": Palette.BORDER_FOCUS,
    }
    button_style = {
        "font": (ui_font, 10, "bold"),
        "bg": Palette.PRIMARY,
        "fg": Palette.PRIMARY_TEXT,
        "activebackground": Palette.PRIMARY_HOVER,
        "activeforeground": Palette.PRIMARY_TEXT,
        "relief": "flat",
        "bd": 0,
        "cursor": "hand2",
        "padx": 18,
        "pady": 10,
    }
    secondary_button_style = {
        "font": (ui_font, 10, "bold"),
        "bg": Palette.GHOST_BG,
        "fg": Palette.GHOST_TEXT,
        "activebackground": Palette.GHOST_BG_HOVER,
        "activeforeground": Palette.TEXT_PRIMARY,
        "relief": "flat",
        "bd": 0,
        "cursor": "hand2",
        "padx": 18,
        "pady": 10,
    }
    danger_button_style = {
        "font": (ui_font, 10, "bold"),
        "bg": Palette.GHOST_BG,
        "fg": Palette.DANGER,
        "activebackground": Palette.GHOST_BG_HOVER,
        "activeforeground": Palette.DANGER,
        "relief": "flat",
        "bd": 0,
        "cursor": "hand2",
        "padx": 18,
        "pady": 10,
    }
    text_style = {
        "font": (mono_font, 10),
        "bg": Palette.BG_INPUT,
        "fg": Palette.TEXT_PRIMARY,
        "insertbackground": Palette.PRIMARY,
        "relief": "flat",
        "bd": 0,
        "padx": 16,
        "pady": 14,
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