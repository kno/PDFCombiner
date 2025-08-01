"""
Widget de cabecera con título y directorio actual
"""
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from gui.styles import FileManagerStyles


class HeaderWidget(QWidget):
    """Widget de cabecera con información del directorio actual"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)

        # Título
        title_label = QLabel("Gestor de Archivos PDF")
        title_label.setStyleSheet(FileManagerStyles.SECTION_TITLE_LARGE)
        header_layout.addWidget(title_label)

        # Etiqueta del directorio actual
        self.current_dir_label = QLabel()
        self.current_dir_label.setStyleSheet(FileManagerStyles.CURRENT_DIR_LABEL)
        header_layout.addWidget(self.current_dir_label)

        # Configurar altura fija para el header
        header_frame.setMaximumHeight(90)
        header_frame.setMinimumHeight(90)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def update_current_directory(self, directory_path: str):
        """Actualizar la información del directorio actual"""
        current_path = Path(directory_path)
        home_path = Path.home()

        # Mostrar ruta relativa al home si es posible
        try:
            if current_path.is_relative_to(home_path):
                display_path = "~" / current_path.relative_to(home_path)
            else:
                display_path = current_path
        except:
            display_path = current_path

        self.current_dir_label.setText(f"📁 {display_path}")
