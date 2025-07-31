"""
Estilos y temas para la aplicación
"""
from enum import Enum
from typing import Dict

class ButtonStyle(Enum):
    """Tipos de estilos de botones"""
    PRIMARY = "primary"
    SUCCESS = "success"
    SECONDARY = "secondary"
    DANGER = "danger"

class ColorPalette:
    """Paleta de colores centralizada para toda la aplicación"""

    # Colores primarios
    PRIMARY_BLUE = "#2196F3"
    PRIMARY_BLUE_HOVER = "#1976D2"
    PRIMARY_BLUE_PRESSED = "#1565C0"
    PRIMARY_BLUE_LIGHT = "#E3F2FD"

    # Colores de éxito (verde)
    SUCCESS_GREEN = "#4CAF50"
    SUCCESS_GREEN_HOVER = "#45a049"
    SUCCESS_GREEN_PRESSED = "#388E3C"
    SUCCESS_GREEN_DARK = "#2E7D32"

    # Colores de peligro (rojo)
    DANGER_RED = "#d32f2f"
    DANGER_RED_HOVER = "#b71c1c"
    DANGER_RED_LIGHT = "#ffebee"
    DANGER_RED_PRESSED = "#ffcdd2"
    DANGER_RED_DARK = "#F44336"
    DANGER_RED_VERY_DARK = "#B71C1C"

    # Colores de texto
    TEXT_WHITE = "#FFFFFF"
    TEXT_BLACK = "#000000"

    # Colores grises
    GRAY_LIGHT = "#9E9E9E"
    GRAY_MEDIUM = "#757575"
    GRAY_DARK = "#616161"

    # Colores de tema oscuro
    DARK_BG_MAIN = "#2b2b2b"
    DARK_BG_SECONDARY = "#3c3c3c"
    DARK_BG_TERTIARY = "#404040"
    DARK_BG_HOVER = "#505050"
    DARK_BORDER = "#555555"
    DARK_ACCENT = "#0078d4"

    # Colores para drag and drop
    DROP_INDICATOR = "#FFD700"  # Dorado para indicador de drop
    DRAG_ACTIVE = "#E8F5E8"     # Verde claro para item siendo arrastrado

class BaseStyles:
    """Estilos base reutilizables"""

    @staticmethod
    def button_base(bg_color: str, text_color: str = ColorPalette.TEXT_WHITE,
                   border_color: str = None, border_radius: str = "6px",
                   padding: str = "8px 12px") -> str:
        """Estilo base para botones"""
        border_color = border_color or bg_color
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: {border_radius};
                padding: {padding};
                font-weight: bold;
            }}
        """

    @staticmethod
    def button_states(hover_bg: str, pressed_bg: str, hover_border: str = None) -> str:
        """Estados hover y pressed para botones"""
        hover_border = hover_border or hover_bg
        return f"""
            QPushButton:hover {{
                background-color: {hover_bg};
                border-color: {hover_border};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
        """

    @staticmethod
    def button_disabled() -> str:
        """Estado deshabilitado para botones"""
        return """
            QPushButton:disabled {
                background-color: palette(window);
                color: palette(disabled-text);
                border-color: palette(midlight);
            }
        """

    @staticmethod
    def list_view_base() -> str:
        """Estilo base para ListView y TreeView"""
        return """
            background-color: palette(base);
            color: palette(text);
            border: 1px solid palette(mid);
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
            alternate-background-color: palette(alternate-base);
        """

    @staticmethod
    def list_item_base(padding: str = "8px") -> str:
        """Estilo base para items de lista"""
        return f"""
            padding: {padding};
            border-bottom: 1px solid palette(midlight);
        """

    @staticmethod
    def list_item_states() -> str:
        """Estados de items de lista"""
        return """
            ::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            ::item:hover {
                background-color: palette(light);
            }
        """

class FileManagerStyles:
    """Estilos específicos para el FileManagerWidget usando composición"""

    # Estilo para el header del directorio actual
    CURRENT_DIR_LABEL = """
        QLabel {
            color: palette(text);
            background-color: palette(base);
            padding: 6px;
            border: 1px solid palette(mid);
            border-radius: 4px;
            font-weight: bold;
        }
    """

    # Estilo para el checkbox de índice interactivo
    CREATE_INDEX_CHECKBOX = f"""
        QCheckBox {{
            color: {ColorPalette.TEXT_WHITE};
            font-weight: bold;
            padding: 8px 12px;
            spacing: 8px;
            font-size: 13px;
            background-color: transparent;
        }}
        QCheckBox:hover {{
            color: {ColorPalette.PRIMARY_BLUE_LIGHT};
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            margin-right: 8px;
        }}
        QCheckBox::indicator:unchecked {{
            border: 2px solid palette(mid);
            background-color: palette(base);
            border-radius: 4px;
        }}
        QCheckBox::indicator:checked {{
            border: 2px solid {ColorPalette.PRIMARY_BLUE};
            background-color: {ColorPalette.PRIMARY_BLUE};
            border-radius: 4px;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIgNkw0LjUgOC41TDEwIDMiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
        }}
    """

    # Estilo para el botón principal de combinar usando composición
    COMBINE_BUTTON = (
        BaseStyles.button_base(
            ColorPalette.PRIMARY_BLUE,
            border_color=ColorPalette.PRIMARY_BLUE_HOVER,
            border_radius="8px",
            padding="8px 20px"
        ) +
        f"""
            QPushButton {{
                font-size: 14px;
            }}
        """ +
        BaseStyles.button_states(
            ColorPalette.PRIMARY_BLUE_HOVER,
            ColorPalette.PRIMARY_BLUE_PRESSED,
            ColorPalette.PRIMARY_BLUE_PRESSED
        ) +
        BaseStyles.button_disabled()
    )

    # Estilo para el botón de agregar archivos usando composición
    ADD_BUTTON = (
        BaseStyles.button_base(
            ColorPalette.SUCCESS_GREEN,
            border_color=ColorPalette.SUCCESS_GREEN_PRESSED,
            padding="8px 16px"
        ) +
        f"""
            QPushButton {{
                font-size: 12px;
            }}
        """ +
        BaseStyles.button_states(
            ColorPalette.SUCCESS_GREEN_HOVER,
            ColorPalette.SUCCESS_GREEN_PRESSED,
            ColorPalette.SUCCESS_GREEN_DARK
        ) +
        BaseStyles.button_disabled()
    )

    # Estilo para el botón de directorio superior
    PARENT_DIR_BUTTON = """
        QPushButton {
            background-color: palette(base);
            color: palette(text);
            border: 1px solid palette(mid);
            border-radius: 4px;
            padding: 8px;
            text-align: left;
            font-weight: normal;
        }
        QPushButton:hover {
            background-color: palette(light);
            border-color: palette(highlight);
        }
        QPushButton:pressed {
            background-color: palette(midlight);
        }
    """

    # Estilo para el TreeView usando composición
    TREE_VIEW = (
        f"QTreeView {{ {BaseStyles.list_view_base()} }}" +
        f"QTreeView::item {{ {BaseStyles.list_item_base('4px')} }}" +
        f"QTreeView{BaseStyles.list_item_states()}"
    )

    # Estilo para el ListView de archivos seleccionados usando composición con drag and drop
    SELECTED_LIST = (
        f"QListView {{ {BaseStyles.list_view_base()} }}" +
        f"QListView::item {{ {BaseStyles.list_item_base()} }}" +
        f"QListView::item:selected {{ font-weight: bold; }}" +
        f"QListView{BaseStyles.list_item_states()}" +
        f"""
        QListView::drop-indicator {{
            background-color: {ColorPalette.DROP_INDICATOR};
            height: 3px;
            border-radius: 1px;
        }}
        QListView::item:hover {{
            background-color: palette(light);
            border-left: 3px solid {ColorPalette.PRIMARY_BLUE};
        }}
        """
    )

    # Estilo base para botones de control usando composición
    CONTROL_BUTTON_BASE = (
        """
        QPushButton {
            background-color: palette(button);
            color: palette(button-text);
            border: 2px solid palette(mid);
            border-radius: 6px;
            padding: 6px 12px;
            margin: 2px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: palette(light);
            border-color: palette(highlight);
        }
        QPushButton:pressed {
            background-color: palette(midlight);
        }
        """ + BaseStyles.button_disabled()
    )

    # Estilo para botones de peligro usando composición
    DANGER_BUTTON = (
        CONTROL_BUTTON_BASE +
        f"""
        QPushButton {{
            color: {ColorPalette.DANGER_RED};
            border-color: {ColorPalette.DANGER_RED};
        }}
        QPushButton:hover {{
            background-color: {ColorPalette.DANGER_RED_LIGHT};
            border-color: {ColorPalette.DANGER_RED_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {ColorPalette.DANGER_RED_PRESSED};
        }}
        """
    )

    # Estilos para títulos de secciones usando colores centralizados
    SECTION_TITLE = f"font-weight: bold; color: {ColorPalette.PRIMARY_BLUE}; padding: 5px;"
    SECTION_TITLE_LARGE = f"font-weight: bold; font-size: 14px; color: {ColorPalette.PRIMARY_BLUE}; padding: 5px;"

class StyleManager:
    """Gestor centralizado de estilos usando composición y colores centralizados"""

    @classmethod
    def _create_button_style(cls, bg_color: str, hover_color: str, pressed_color: str,
                           padding: str = "8px 12px", border_radius: str = "4px") -> str:
        """Crear estilo de botón reutilizable"""
        return (
            BaseStyles.button_base(bg_color, padding=padding, border_radius=border_radius) +
            BaseStyles.button_states(hover_color, pressed_color)
        )

    @classmethod
    def get_button_styles(cls) -> Dict[str, str]:
        """Obtener todos los estilos de botones usando colores centralizados"""
        return {
            ButtonStyle.PRIMARY.value: cls._create_button_style(
                ColorPalette.PRIMARY_BLUE,
                ColorPalette.PRIMARY_BLUE_HOVER,
                ColorPalette.PRIMARY_BLUE_PRESSED,
                padding="12px 16px"
            ) + """
                QPushButton {
                    min-width: 120px;
                }
            """,

            ButtonStyle.SUCCESS.value: cls._create_button_style(
                ColorPalette.SUCCESS_GREEN,
                ColorPalette.SUCCESS_GREEN_HOVER,
                ColorPalette.SUCCESS_GREEN_PRESSED
            ),

            ButtonStyle.SECONDARY.value: cls._create_button_style(
                ColorPalette.GRAY_LIGHT,
                ColorPalette.GRAY_MEDIUM,
                ColorPalette.GRAY_DARK,
                padding="5px 10px",
                border_radius="3px"
            ),

            ButtonStyle.DANGER.value: cls._create_button_style(
                ColorPalette.DANGER_RED_DARK,
                ColorPalette.DANGER_RED,
                ColorPalette.DANGER_RED_VERY_DARK,
                padding="5px 10px",
                border_radius="3px"
            )
        }

    @classmethod
    def get_button_style(cls, style_type: ButtonStyle) -> str:
        """Obtener estilo de botón por tipo"""
        return cls.get_button_styles().get(style_type.value, "")

    @classmethod
    def get_dark_theme(cls) -> str:
        """Obtener tema oscuro completo usando colores centralizados"""
        return f"""
            QMainWindow {{
                background-color: {ColorPalette.DARK_BG_MAIN};
                color: {ColorPalette.TEXT_WHITE};
            }}
            QFrame {{
                background-color: {ColorPalette.DARK_BG_SECONDARY};
                border: 1px solid {ColorPalette.DARK_BORDER};
                border-radius: 5px;
            }}
            QListWidget {{
                background-color: {ColorPalette.DARK_BG_TERTIARY};
                color: {ColorPalette.TEXT_WHITE};
                border: 1px solid {ColorPalette.DARK_BORDER};
                border-radius: 3px;
                padding: 5px;
                selection-background-color: {ColorPalette.DARK_ACCENT};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {ColorPalette.DARK_BORDER};
            }}
            QListWidget::item:selected {{
                background-color: {ColorPalette.DARK_ACCENT};
            }}
            QListWidget::item:hover {{
                background-color: {ColorPalette.DARK_BG_HOVER};
            }}
            QLabel {{
                color: {ColorPalette.TEXT_WHITE};
            }}
            QCheckBox {{
                color: {ColorPalette.TEXT_WHITE};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {ColorPalette.DARK_BG_TERTIARY};
                border: 2px solid {ColorPalette.DARK_BORDER};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ColorPalette.DARK_ACCENT};
                border: 2px solid {ColorPalette.DARK_ACCENT};
            }}
        """

def get_dark_theme_stylesheet() -> str:
    """Función de compatibilidad"""
    return StyleManager.get_dark_theme()
