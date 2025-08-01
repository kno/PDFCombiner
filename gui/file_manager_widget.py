"""
Widget de gestión de archivos refactorizado usando widgets especializados
"""
import gettext
from typing import List, Set
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from core.file_manager import FileManager
from gui.widgets import HeaderWidget, FileExplorerWidget, SelectedFilesWidget, ControlsWidget

# Setup for localization
try:
    es = gettext.translation('messages', localedir='locale', languages=['es'])
    es.install()
    _ = es.gettext
except FileNotFoundError:
    # Fallback if translation file is not found
    _ = gettext.gettext


class FileManagerWidget(QWidget):
    """Widget completo de gestión de archivos con widgets especializados"""

    # Señales
    files_selected = pyqtSignal(list)  # Emitida cuando cambian los archivos seleccionados
    current_directory_changed = pyqtSignal(str)  # Emitida cuando cambia el directorio
    combine_requested = pyqtSignal()  # Emitida cuando se solicita combinar PDFs

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_manager = FileManager()
        self.selected_files_set: Set[str] = set()

        self._setup_ui()
        self._setup_connections()
        self._update_current_directory()

    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)

        # Header con información del directorio actual (altura fija)
        self.header_widget = HeaderWidget()
        layout.addWidget(self.header_widget)

        # Splitter principal con ambas listas (expandible)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)  # stretch factor = 1, se expande

        # Panel izquierdo: navegación por directorios
        self.file_explorer = FileExplorerWidget(self.file_manager)
        splitter.addWidget(self.file_explorer)

        # Panel derecho: archivos seleccionados
        self.selected_files = SelectedFilesWidget()
        splitter.addWidget(self.selected_files)

        # Configurar proporciones del splitter - ambos paneles iguales
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 400])

        # Sección de controles debajo de ambas listas (altura fija)
        self.controls_widget = ControlsWidget()
        layout.addWidget(self.controls_widget)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        # Conexiones del explorador de archivos
        self.file_explorer.files_ready_to_add.connect(self._add_files_to_selection)
        self.file_explorer.directory_changed.connect(self._on_directory_changed)

        # Conexiones de archivos seleccionados
        self.selected_files.files_changed.connect(self._on_files_changed)
        self.selected_files.selection_changed.connect(self._update_explorer_files_set)

        # Conexiones de controles
        self.controls_widget.combine_requested.connect(self.combine_requested.emit)

    def _add_files_to_selection(self, file_paths: List[str]):
        """Agregar archivos a la selección"""
        self.selected_files.add_files(file_paths)

    def _on_directory_changed(self, directory_path: str):
        """Manejar cambio de directorio"""
        self.header_widget.update_current_directory(directory_path)
        self.current_directory_changed.emit(directory_path)

    def _on_files_changed(self, files: List[str]):
        """Manejar cambio en archivos seleccionados"""
        self.selected_files_set = self.selected_files.get_selected_files_set()
        self._update_explorer_files_set()
        self.controls_widget.update_combine_button_state(len(files) > 0)
        self.files_selected.emit(files)

    def _update_explorer_files_set(self):
        """Actualizar el set de archivos en el explorador"""
        self.file_explorer.set_selected_files_set(self.selected_files.get_selected_files_set())

    def _update_current_directory(self):
        """Actualizar información del directorio actual"""
        self.file_explorer.update_current_directory()

    # Métodos públicos para interacción externa

    def get_selected_files(self) -> List[str]:
        """Obtener lista de archivos seleccionados"""
        return self.selected_files.get_selected_files()

    def get_selected_titles(self) -> List[str]:
        """Obtener los títulos editados de los archivos seleccionados"""
        return self.selected_files.get_selected_titles()

    def set_current_directory(self, directory: str) -> bool:
        """Establecer directorio actual"""
        if self.file_manager.set_current_directory(directory):
            self._update_current_directory()
            return True
        return False

    def refresh(self):
        """Refrescar vista de archivos"""
        self._update_current_directory()

    def clear_selection(self):
        """Limpiar selección de archivos"""
        self.selected_files.clear_selection()

    def is_create_index_checked(self) -> bool:
        """Verificar si el checkbox de crear índice está marcado"""
        return self.controls_widget.is_create_index_checked()
