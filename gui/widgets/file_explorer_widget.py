"""
Widget explorador de archivos
"""
import gettext
from typing import List, Set
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLabel, QPushButton,
    QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from gui.pdf_filter_model import PDFFilterModel
from core.file_manager import FileManager
from gui.styles import FileManagerStyles

# Setup for localization
try:
    es = gettext.translation('messages', localedir='locale', languages=['es'])
    es.install()
    _ = es.gettext
except FileNotFoundError:
    # Fallback if translation file is not found
    _ = gettext.gettext


class FileExplorerWidget(QWidget):
    """Widget del explorador de archivos con navegación por directorios"""

    # Señales
    files_ready_to_add = pyqtSignal(list)  # Archivos listos para agregar
    directory_changed = pyqtSignal(str)    # Directorio cambió

    def __init__(self, file_manager: FileManager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.selected_files_set: Set[str] = set()

        self._setup_ui()
        self._setup_models()
        self._setup_connections()

    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)

        # Título del panel
        title_label = QLabel(_("Explorador de Archivos"))
        title_label.setStyleSheet(FileManagerStyles.SECTION_TITLE)
        layout.addWidget(title_label)

        # Caja de texto para filtro rápido (regex)
        self.filter_line_edit = QLineEdit()
        self.filter_line_edit.setPlaceholderText(_("Filtrar por expresión regular..."))
        self.filter_line_edit.setClearButtonEnabled(True)
        self.filter_line_edit.setMinimumHeight(28)
        layout.addWidget(self.filter_line_edit)

        # Botón de subir directorio (aparece cuando es necesario)
        self.parent_dir_button = QPushButton(_("📁 ⬆️ Directorio superior"))
        self.parent_dir_button.setStyleSheet(FileManagerStyles.PARENT_DIR_BUTTON)
        self.parent_dir_button.setVisible(False)  # Inicialmente oculto
        layout.addWidget(self.parent_dir_button)

        # Vista de árbol únicamente
        self.tree_view = QTreeView()
        self._setup_tree_view()
        layout.addWidget(self.tree_view)

        # Botón de agregar
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton(_("→ Agregar"))
        self.add_button.setStyleSheet(FileManagerStyles.ADD_BUTTON)
        self.add_button.setEnabled(False)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        layout.addLayout(buttons_layout)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(panel)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def _setup_tree_view(self):
        """Configurar vista de árbol"""
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)

        # Ocultar la cabecera "Name"
        self.tree_view.setHeaderHidden(True)

        # Estilos adaptativos para tema oscuro
        self.tree_view.setStyleSheet(FileManagerStyles.TREE_VIEW)

    def _setup_models(self):
        """Configurar modelos de datos"""
        # Modelo del sistema de archivos
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath('')
        self.fs_model.setNameFilters(['*.pdf'])
        self.fs_model.setNameFilterDisables(False)

        # Modelo proxy para filtrar
        self.filter_model = PDFFilterModel()
        self.filter_model.setSourceModel(self.fs_model)
        # Configurar referencia al file manager para navegación
        self.filter_model.set_file_manager(self.file_manager)

        # Configurar vista de árbol con el modelo filtrado
        self.tree_view.setModel(self.filter_model)

        # Ocultar columnas innecesarias en la vista de árbol
        for column in range(1, self.fs_model.columnCount()):
            self.tree_view.hideColumn(column)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        # Navegación con botón de directorio superior
        self.parent_dir_button.clicked.connect(self._navigate_to_parent)

        # Filtro rápido: actualizar el modelo proxy al cambiar el texto (wildcards)
        self.filter_line_edit.textChanged.connect(self._on_filter_text_changed)

        # Selección en vista de archivos
        self.tree_view.selectionModel().selectionChanged.connect(self._on_file_selection_changed)

        # Doble click para navegar/agregar
        self.tree_view.doubleClicked.connect(self._on_file_double_clicked)

        # Botones de archivo
        self.add_button.clicked.connect(self._add_selected_files)

    def _on_filter_text_changed(self, text):
        """Actualizar el filtro wildcard del modelo proxy"""
        self.filter_model.set_wildcard_filter(text)
        self.filter_model.invalidateFilter()

    def _on_file_selection_changed(self):
        """Manejar cambio de selección en archivos"""
        selection = self.tree_view.selectionModel().selectedIndexes()

        # Verificar si hay archivos PDF seleccionados
        has_pdf_files = False
        for index in selection:
            if index.column() == 0:  # Solo considerar la primera columna
                source_index = self.filter_model.mapToSource(index)
                if not self.fs_model.isDir(source_index):
                    file_path = self.fs_model.filePath(source_index)
                    if file_path.lower().endswith('.pdf'):
                        has_pdf_files = True
                        break

        self.add_button.setEnabled(has_pdf_files)

    def _on_file_double_clicked(self, index: QModelIndex):
        """Manejar doble click en archivo o directorio"""
        # Mapear al modelo fuente
        source_index = self.filter_model.mapToSource(index)

        # Verificar que el índice fuente sea válido
        if not source_index.isValid():
            return

        if self.fs_model.isDir(source_index):
            # Navegar al directorio
            dir_path = self.fs_model.filePath(source_index)
            if self.file_manager.set_current_directory(dir_path):
                self.update_current_directory()
        else:
            # Emitir archivo PDF para agregar
            file_path = self.fs_model.filePath(source_index)
            if file_path.lower().endswith('.pdf'):
                self.files_ready_to_add.emit([file_path])

    def _navigate_to_parent(self):
        """Navegar al directorio padre"""
        if self.file_manager.go_up():
            self.update_current_directory()

    def _add_selected_files(self):
        """Agregar archivos seleccionados a la lista"""
        selection = self.tree_view.selectionModel().selectedIndexes()

        selected_files = []
        for index in selection:
            if index.column() == 0:  # Solo procesar la primera columna
                source_index = self.filter_model.mapToSource(index)
                if not self.fs_model.isDir(source_index):
                    file_path = self.fs_model.filePath(source_index)
                    if file_path.lower().endswith('.pdf'):
                        selected_files.append(file_path)

        if selected_files:
            self.files_ready_to_add.emit(selected_files)

    def update_current_directory(self):
        """Actualizar información del directorio actual"""
        current_path = Path(self.file_manager.current_directory)

        # Configurar raíz de la vista de árbol
        root_index = self.fs_model.index(str(current_path))
        proxy_root = self.filter_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_root)

        # Mostrar/ocultar botón de directorio superior
        can_go_up = self.file_manager.can_go_up()
        self.parent_dir_button.setVisible(can_go_up)

        # Emitir señal
        self.directory_changed.emit(str(current_path))

    def set_selected_files_set(self, selected_files_set: Set[str]):
        """Establecer el set de archivos ya seleccionados para evitar duplicados"""
        self.selected_files_set = selected_files_set
