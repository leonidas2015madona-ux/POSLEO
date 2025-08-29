# assets/styles.py
# Colores principales
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#3498db"
ACCENT_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
LIGHT_BG = "#ecf0f1"
DARK_TEXT = "#2c3e50"
LIGHT_TEXT = "#ffffff"

# Fuentes
TITLE_FONT = ("Roboto", 24, "bold")
HEADER_FONT = ("Roboto", 18, "bold")
SUBHEADER_FONT = ("Roboto", 14, "bold")
TEXT_FONT = ("Roboto", 12)
SMALL_FONT = ("Roboto", 10)

# Dimensiones
BUTTON_HEIGHT = 40
INPUT_HEIGHT = 35
TABLE_ROW_HEIGHT = 30

# Estilos específicos para componentes
ENTRY_STYLE = {
    "height": INPUT_HEIGHT,
    "font": TEXT_FONT,
    "border_width": 1,
    "corner_radius": 4
}

BUTTON_STYLE = {
    "height": BUTTON_HEIGHT,
    "font": TEXT_FONT,
    "corner_radius": 4
}

PRIMARY_BUTTON_STYLE = {
    **BUTTON_STYLE,
    "fg_color": SECONDARY_COLOR,
    "hover_color": "#2980b9",
    "text_color": LIGHT_TEXT
}

ACCENT_BUTTON_STYLE = {
    **BUTTON_STYLE,
    "fg_color": ACCENT_COLOR,
    "hover_color": "#c0392b",
    "text_color": LIGHT_TEXT
}

SUCCESS_BUTTON_STYLE = {
    **BUTTON_STYLE,
    "fg_color": SUCCESS_COLOR,
    "hover_color": "#27ae60",
    "text_color": LIGHT_TEXT
}