"""
Widget de gestión de archivos refactorizado usando widgets especializados
"""
from typing import List, Set
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from core.file_manager import FileManager
from gui.widgets import HeaderWidget, FileExplorerWidget, SelectedFilesWidget, ControlsWidget, PDFPreviewWidget
from utils.localization import _

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

        # Splitter principal horizontal con tres paneles
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter, 1)  # stretch factor = 1, se expande

        # Splitter izquierdo para explorador y archivos seleccionados
        left_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_splitter)

        # Panel izquierdo: navegación por directorios
        self.file_explorer = FileExplorerWidget(self.file_manager)
        left_splitter.addWidget(self.file_explorer)

        # Panel central: archivos seleccionados
        self.selected_files = SelectedFilesWidget()
        left_splitter.addWidget(self.selected_files)

        # Panel derecho: vista previa de PDF
        self.pdf_preview = PDFPreviewWidget()
        main_splitter.addWidget(self.pdf_preview)

        # Configurar proporciones del splitter principal
        # Explorador + Seleccionados: 60%, Vista previa: 40%
        main_splitter.setStretchFactor(0, 3)  # Panel izquierdo (explorador + seleccionados)
        main_splitter.setStretchFactor(1, 2)  # Panel derecho (vista previa)
        main_splitter.setSizes([600, 400])

        # Configurar proporciones del splitter izquierdo
        left_splitter.setStretchFactor(0, 1)  # Explorador
        left_splitter.setStretchFactor(1, 1)  # Archivos seleccionados
        left_splitter.setSizes([300, 300])

        # Sección de controles debajo de todo (altura fija)
        self.controls_widget = ControlsWidget()
        layout.addWidget(self.controls_widget)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        # Conexiones del explorador de archivos
        self.file_explorer.files_ready_to_add.connect(self._add_files_to_selection)
        self.file_explorer.directory_changed.connect(self._on_directory_changed)
        
        # Conectar selección de archivo en el explorador para previsualización
        self.file_explorer.tree_view.selectionModel().selectionChanged.connect(
            self._on_explorer_selection_changed
        )

        # Conexiones de archivos seleccionados
        self.selected_files.files_changed.connect(self._on_files_changed)
        self.selected_files.selection_changed.connect(self._update_explorer_files_set)

        # Conexiones de controles
        self.controls_widget.combine_requested.connect(self.combine_requested.emit)

    def _on_explorer_selection_changed(self):
        """Manejar cambio de selección en el explorador para actualizar vista previa"""
        selection = self.file_explorer.tree_view.selectionModel().selectedIndexes()
        
        # Buscar el primer archivo PDF seleccionado
        for index in selection:
            if index.column() == 0:  # Solo considerar la primera columna
                source_index = self.file_explorer.filter_model.mapToSource(index)
                if not self.file_explorer.fs_model.isDir(source_index):
                    file_path = self.file_explorer.fs_model.filePath(source_index)
                    if file_path.lower().endswith('.pdf'):
                        # Cargar el PDF en la vista previa
                        self.pdf_preview.load_pdf(file_path)
                        return
        
        # Si no hay PDF seleccionado, limpiar vista previa
        self.pdf_preview.clear_preview()

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

    def reload_texts(self):
        """Recarga los textos de la interfaz para el idioma actual."""
        print("[DEBUG] FileManagerWidget.reload_texts called")
        self.header_widget.reload_texts()
        self.file_explorer.reload_texts()
        self.selected_files.reload_texts()
        self.controls_widget.reload_texts()
        self.pdf_preview.reload_texts()