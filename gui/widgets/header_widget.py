"""
Widget de cabecera con título y directorio actual
"""
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox
from gui.styles import FileManagerStyles
from utils.localization import _


from PyQt6.QtCore import pyqtSignal

class HeaderWidget(QWidget):
    """Widget de cabecera con información del directorio actual"""

    language_changed = pyqtSignal(str)

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
        title_label = QLabel(_("Gestor de Archivos PDF"))
        title_label.setStyleSheet(FileManagerStyles.SECTION_TITLE_LARGE)
        header_layout.addWidget(title_label)

        # Fila horizontal para directorio y selector de idioma
        row_layout = QHBoxLayout()

        # Etiqueta del directorio actual (acortada)
        self.current_dir_label = QLabel()
        self.current_dir_label.setStyleSheet(FileManagerStyles.CURRENT_DIR_LABEL)
        self.current_dir_label.setMaximumWidth(320)  # Limitar ancho
        self.current_dir_label.setMinimumHeight(30)
        row_layout.addWidget(self.current_dir_label)

        # ComboBox de idiomas
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Español", "es")
        self.language_combo.setMaximumWidth(120)
        self.language_combo.setMinimumHeight(30)
        row_layout.addWidget(self.language_combo)

        # Conectar cambio de idioma
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)

        header_layout.addLayout(row_layout)

        # Configurar altura fija para el header
        header_frame.setMaximumHeight(90)
        header_frame.setMinimumHeight(90)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def _on_language_changed(self, idx):
        lang_code = self.language_combo.currentData()
        self.language_changed.emit(lang_code)

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

        self.current_dir_label.setText(_("📁 {}").format(display_path))

    def reload_texts(self):
        print(f"[DEBUG] HeaderWidget.reload_texts called. Current language: {self.language_combo.currentData()}")
        frame = self.findChild(QFrame)
        if frame:
            for child in frame.children():
                if isinstance(child, QLabel):
                    child.setText(_("Gestor de Archivos PDF"))
                    break
        self.update_current_directory(self.current_dir_label.text())
