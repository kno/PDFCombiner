"""
Widget de controles inferiores
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton,
    QFrame
)
from PyQt6.QtCore import pyqtSignal
from gui.styles import FileManagerStyles
from utils.localization import _


class ControlsWidget(QWidget):
    """Widget de controles inferiores con checkbox y botón de combinar"""

    # Señales
    combine_requested = pyqtSignal()  # Solicitud de combinar PDFs

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_layout = QHBoxLayout(controls_frame)

        # Espaciado
        controls_layout.addStretch()

        # Checkbox para crear índice interactivo
        self.create_index_checkbox = QCheckBox(_("Crear índice interactivo"))
        self.create_index_checkbox.setChecked(True)
        self.create_index_checkbox.setStyleSheet(FileManagerStyles.CREATE_INDEX_CHECKBOX)
        # Asegurar que el checkbox tenga suficiente espacio
        self.create_index_checkbox.setMinimumWidth(200)
        controls_layout.addWidget(self.create_index_checkbox)

        # Espaciado
        controls_layout.addSpacing(20)

        # Botón combinar
        self.combine_button = QPushButton(_("🔗 Combinar PDFs"))
        self.combine_button.setMinimumHeight(40)
        self.combine_button.setEnabled(False)  # Inicialmente deshabilitado
        self.combine_button.setStyleSheet(FileManagerStyles.COMBINE_BUTTON)
        controls_layout.addWidget(self.combine_button)

        # Espaciado
        controls_layout.addStretch()

        # Configurar altura fija para los controles
        controls_frame.setMaximumHeight(70)
        controls_frame.setMinimumHeight(70)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(controls_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        self.combine_button.clicked.connect(self.combine_requested.emit)

    def update_combine_button_state(self, has_files: bool):
        """Actualizar estado del botón de combinar"""
        self.combine_button.setEnabled(has_files)

    def is_create_index_checked(self) -> bool:
        """Verificar si el checkbox de crear índice está marcado"""
        return self.create_index_checkbox.isChecked()

    def reload_texts(self):
        """Recarga los textos de la interfaz para el idioma actual."""
        print("[DEBUG] ControlsWidget.reload_texts called")
        self.create_index_checkbox.setText(_("Crear índice interactivo"))
        self.combine_button.setText(_("🔗 Combinar PDFs"))
