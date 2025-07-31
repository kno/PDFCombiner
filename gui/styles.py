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

class StyleManager:
    """Gestor centralizado de estilos"""

    BUTTON_STYLES: Dict[str, str] = {
        ButtonStyle.PRIMARY.value: """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 12px 16px;
                border: none;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """,
        ButtonStyle.SUCCESS.value: """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """,
        ButtonStyle.SECONDARY.value: """
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #616161;
            }
        """,
        ButtonStyle.DANGER.value: """
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """
    }

    @classmethod
    def get_button_style(cls, style_type: ButtonStyle) -> str:
        """Obtener estilo de botón por tipo"""
        return cls.BUTTON_STYLES.get(style_type.value, "")

    @classmethod
    def get_dark_theme(cls) -> str:
        """Obtener tema oscuro completo"""
        return """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QListWidget {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #0078d4;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QListWidget::item:hover {
                background-color: #505050;
            }
            QLabel {
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #404040;
                border: 2px solid #555555;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
            }
        """

def get_dark_theme_stylesheet() -> str:
    """Función de compatibilidad"""
    return StyleManager.get_dark_theme()
