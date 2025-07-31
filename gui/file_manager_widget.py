"""
Widget de gestión de archivos refactorizado usando QTreeView, QTableView y QFileSystemModel
"""
from typing import List, Dict, Optional, Set
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeView, QListView, QLabel, QPushButton,
    QFrame, QHeaderView, QMessageBox, QFileDialog, QCheckBox
)
from PyQt6.QtCore import (
    Qt, QModelIndex, pyqtSignal,
    QDir, QSortFilterProxyModel, QTimer
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QPainter, QFileSystemModel, QDropEvent
from core.file_manager import FileManager, FileManagerError
from utils.text_processor import TextProcessor
from gui.styles import FileManagerStyles

class CustomListView(QListView):
    """ListView personalizado para detectar la posición real del drop"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.actual_drop_row = -1

    def dropEvent(self, event: QDropEvent):
        """Capturar la posición real del drop"""
        drop_index = self.indexAt(event.position().toPoint())
        if drop_index.isValid():
            self.actual_drop_row = drop_index.row()
        else:
            self.actual_drop_row = -1

        # Pasar la información al modelo antes del drop
        if hasattr(self.model(), 'set_actual_drop_row'):
            self.model().set_actual_drop_row(self.actual_drop_row)

        super().dropEvent(event)

class PDFFilterModel(QSortFilterProxyModel):
    """Modelo proxy para filtrar solo archivos PDF y directorios, con navegación hacia arriba integrada"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRecursiveFilteringEnabled(True)
        self.file_manager = None

    def set_file_manager(self, file_manager):
        """Configurar referencia al file manager para navegación"""
        self.file_manager = file_manager

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Filtrar solo directorios y archivos PDF"""
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)

        if source_model.isDir(index):
            return True

        filename = source_model.fileName(index)
        return filename.lower().endswith('.pdf')

class SelectedFilesModel(QStandardItemModel):
    """Modelo para archivos seleccionados - solo títulos con soporte drag and drop"""

    # Señal emitida cuando el orden de los archivos cambia
    files_reordered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files: List[str] = []
        # Variables para rastrear drag and drop
        self.drag_source_row = -1
        self.drag_file_path = None
        self.actual_drop_row = -1  # Posición real del drop desde CustomListView

    def supportedDropActions(self):
        """Acciones de drop soportadas"""
        return Qt.DropAction.MoveAction

    def flags(self, index):
        """Flags para cada item - habilitar drag and drop"""
        default_flags = super().flags(index)
        if index.isValid():
            return default_flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return default_flags | Qt.ItemFlag.ItemIsDropEnabled

    def mimeData(self, indexes):
        """Capturar datos del elemento que se está arrastrando"""
        if indexes:
            index = indexes[0]
            self.drag_source_row = index.row()
            item = self.itemFromIndex(index)
            if item:
                self.drag_file_path = item.data(Qt.ItemDataRole.UserRole)
            else:
                self.drag_file_path = None
        return super().mimeData(indexes)

    def set_actual_drop_row(self, row: int):
        """Establecer la posición real del drop desde CustomListView"""
        self.actual_drop_row = row

    def dropMimeData(self, data, action, row, column, parent):
        """Manejar el drop de items para reordenar manualmente"""
        if action != Qt.DropAction.MoveAction:
            return False

        if self.drag_source_row == -1 or not self.drag_file_path:
            return super().dropMimeData(data, action, row, column, parent)

        # Determinar la posición de destino - usar la posición real si está disponible
        target_row = self.actual_drop_row if self.actual_drop_row != -1 else row
        if target_row == -1:
            target_row = len(self.selected_files)

        # Ajustar target_row si está moviendo hacia abajo
        if self.drag_source_row < target_row:
            target_row -= 1

        # Hacer el movimiento manualmente
        if self.drag_source_row != target_row and 0 <= target_row <= len(self.selected_files):
            # Mover en la lista de archivos
            file_path = self.selected_files.pop(self.drag_source_row)
            self.selected_files.insert(target_row, file_path)

            # Actualizar el modelo para reflejar el nuevo orden
            self._rebuild_model()

            # Emitir señal de cambio
            self.files_reordered.emit()

            # Limpiar variables de drag
            self.drag_source_row = -1
            self.drag_file_path = None
            self.actual_drop_row = -1

            return True
        else:
            self.drag_source_row = -1
            self.drag_file_path = None
            self.actual_drop_row = -1
            return False

    def moveRows(self, sourceParent, sourceFirst, sourceLast, destinationParent, destinationChild):
        """Implementar moveRows para manejar el movimiento de filas correctamente"""
        if sourceParent != destinationParent:
            return False

        # Verificar que los índices sean válidos
        if (sourceFirst < 0 or sourceFirst >= self.rowCount() or
            sourceLast < 0 or sourceLast >= self.rowCount() or
            destinationChild < 0 or destinationChild > self.rowCount()):
            return False

        # Llamar a la implementación base
        result = super().moveRows(sourceParent, sourceFirst, sourceLast, destinationParent, destinationChild)
        return result

    def removeRows(self, row, count, parent=QModelIndex()):
        """Override removeRows para manejar eliminaciones durante drag and drop"""
        result = super().removeRows(row, count, parent)
        return result

    def insertRows(self, row, count, parent=QModelIndex()):
        """Override insertRows para manejar inserciones durante drag and drop"""
        result = super().insertRows(row, count, parent)
        return result

    def _rebuild_model(self):
        """Reconstruir el modelo basado en la lista actual de archivos"""
        # Limpiar modelo actual
        self.clear()

        # Recrear items basado en el orden actual
        for i, file_path in enumerate(self.selected_files):
            path_obj = Path(file_path)
            title = TextProcessor.extract_title(path_obj.name)

            title_item = QStandardItem(title)
            title_item.setData(file_path, Qt.ItemDataRole.UserRole)
            title_item.setIcon(self._get_pdf_icon())

            self.appendRow(title_item)

    def _sync_selected_files_from_model(self):
        """Sincronizar la lista de archivos con el orden actual del modelo"""
        old_files = self.selected_files.copy()
        new_files = []

        # Reconstruir la lista basada en el orden actual del modelo
        for i in range(self.rowCount()):
            item = self.item(i)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path and file_path not in new_files:  # Evitar duplicados
                    new_files.append(file_path)

        # Solo actualizar si realmente cambió algo
        if new_files != old_files:
            self.selected_files = new_files
            self.files_reordered.emit()

    def add_file(self, file_path: str) -> bool:
        """Agregar archivo a la selección"""
        if file_path in self.selected_files:
            return False

        self.selected_files.append(file_path)

        # Crear elemento solo con título
        path_obj = Path(file_path)
        title = TextProcessor.extract_title(path_obj.name)

        # Crear item
        title_item = QStandardItem(title)
        title_item.setData(file_path, Qt.ItemDataRole.UserRole)
        title_item.setIcon(self._get_pdf_icon())

        # Agregar item
        self.appendRow(title_item)
        return True

    def remove_file(self, row: int) -> bool:
        """Remover archivo por índice de fila"""
        if 0 <= row < len(self.selected_files):
            self.selected_files.pop(row)
            self.removeRow(row)
            return True
        return False

    def move_file(self, from_row: int, to_row: int) -> bool:
        """Mover archivo de una posición a otra"""
        if (0 <= from_row < len(self.selected_files) and
            0 <= to_row < len(self.selected_files) and
            from_row != to_row):

            # Mover en la lista
            file_path = self.selected_files.pop(from_row)
            self.selected_files.insert(to_row, file_path)

            # Mover en el modelo
            items = self.takeRow(from_row)
            self.insertRow(to_row, items)
            return True
        return False

    def clear_files(self):
        """Limpiar todos los archivos seleccionados"""
        self.selected_files.clear()
        self.clear()

    def get_selected_files(self) -> List[str]:
        """Obtener lista de archivos seleccionados"""
        return self.selected_files.copy()

    def _get_pdf_icon(self) -> QIcon:
        """Crear icono para archivos PDF"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(Qt.GlobalColor.red)
        painter.setPen(Qt.GlobalColor.darkRed)
        painter.drawRoundedRect(2, 2, 12, 12, 2, 2)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(4, 12, "PDF")
        painter.end()

        return QIcon(pixmap)

class FileManagerWidget(QWidget):
    """Widget completo de gestión de archivos con vistas múltiples"""

    # Señales
    files_selected = pyqtSignal(list)  # Emitida cuando cambian los archivos seleccionados
    current_directory_changed = pyqtSignal(str)  # Emitida cuando cambia el directorio
    combine_requested = pyqtSignal()  # Emitida cuando se solicita combinar PDFs

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_manager = FileManager()
        self.selected_files_set: Set[str] = set()

        self._setup_ui()
        self._setup_models()
        self._setup_connections()
        self._update_current_directory()

    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)

        # Header con información del directorio actual (altura fija)
        self._create_header_section(layout)

        # Splitter principal con ambas listas (expandible)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)  # stretch factor = 1, se expande

        # Panel izquierdo: navegación por directorios
        left_panel = self._create_directory_panel()
        splitter.addWidget(left_panel)

        # Panel derecho: archivos seleccionados
        right_panel = self._create_selected_files_panel()
        splitter.addWidget(right_panel)

        # Configurar proporciones del splitter - ambos paneles iguales
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 400])

        # Sección de controles debajo de ambas listas (altura fija)
        self._create_controls_section(layout)

    def _create_header_section(self, layout: QVBoxLayout):
        """Crear sección de header con información del directorio"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)

        # Título
        title_label = QLabel("Gestor de Archivos PDF")
        title_label.setStyleSheet(FileManagerStyles.SECTION_TITLE_LARGE)
        header_layout.addWidget(title_label)

        # Solo directorio actual - sin botones de navegación
        # Etiqueta del directorio actual
        self.current_dir_label = QLabel()
        self.current_dir_label.setStyleSheet(FileManagerStyles.CURRENT_DIR_LABEL)
        header_layout.addWidget(self.current_dir_label)

        # Configurar altura fija para el header
        header_frame.setMaximumHeight(90)
        header_frame.setMinimumHeight(90)

        layout.addWidget(header_frame)

    def _create_controls_section(self, layout: QVBoxLayout):
        """Crear sección de controles debajo de las listas"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_layout = QHBoxLayout(controls_frame)

        # Espaciado
        controls_layout.addStretch()

        # Checkbox para crear índice interactivo
        self.create_index_checkbox = QCheckBox("Crear índice interactivo")
        self.create_index_checkbox.setChecked(True)
        self.create_index_checkbox.setStyleSheet(FileManagerStyles.CREATE_INDEX_CHECKBOX)
        # Asegurar que el checkbox tenga suficiente espacio
        self.create_index_checkbox.setMinimumWidth(200)
        controls_layout.addWidget(self.create_index_checkbox)

        # Espaciado
        controls_layout.addSpacing(20)

        # Botón combinar
        self.combine_button = QPushButton("🔗 Combinar PDFs")
        self.combine_button.setMinimumHeight(40)
        self.combine_button.setEnabled(False)  # Inicialmente deshabilitado
        self.combine_button.setStyleSheet(FileManagerStyles.COMBINE_BUTTON)
        controls_layout.addWidget(self.combine_button)

        # Espaciado
        controls_layout.addStretch()

        # Configurar altura fija para los controles
        controls_frame.setMaximumHeight(70)
        controls_frame.setMinimumHeight(70)

        layout.addWidget(controls_frame)

    def _create_directory_panel(self) -> QWidget:
        """Crear panel de navegación por directorios - solo vista de árbol"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)

        # Título del panel
        title_label = QLabel("Explorador de Archivos")
        title_label.setStyleSheet(FileManagerStyles.SECTION_TITLE)
        layout.addWidget(title_label)

        # Botón de subir directorio (aparece cuando es necesario)
        self.parent_dir_button = QPushButton("📁 ⬆️ Directorio superior")
        self.parent_dir_button.setStyleSheet(FileManagerStyles.PARENT_DIR_BUTTON)
        self.parent_dir_button.setVisible(False)  # Inicialmente oculto
        layout.addWidget(self.parent_dir_button)

        # Vista de árbol únicamente
        self.tree_view = QTreeView()
        self._setup_tree_view()
        layout.addWidget(self.tree_view)

        # Botón de agregar
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("→ Agregar")
        self.add_button.setStyleSheet(FileManagerStyles.ADD_BUTTON)
        self.add_button.setEnabled(False)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        layout.addLayout(buttons_layout)

        return panel

    def _create_selected_files_panel(self) -> QWidget:
        """Crear panel de archivos seleccionados - solo títulos"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)

        # Título del panel
        title_label = QLabel("Archivos Seleccionados")
        title_label.setStyleSheet(FileManagerStyles.SECTION_TITLE)
        layout.addWidget(title_label)

        # Lista de archivos seleccionados
        self.selected_list = CustomListView()
        self.selected_list.setAlternatingRowColors(True)

        # Habilitar drag and drop para reordenar
        self.selected_list.setDragDropMode(QListView.DragDropMode.InternalMove)
        self.selected_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.selected_list.setDragEnabled(True)
        self.selected_list.setAcceptDrops(True)
        self.selected_list.setDropIndicatorShown(True)

        # Estilos para la lista de seleccionados
        self.selected_list.setStyleSheet(FileManagerStyles.SELECTED_LIST)
        layout.addWidget(self.selected_list)

        # Botones de control
        buttons_layout = QHBoxLayout()

        self.move_up_button = QPushButton("↑ Subir")
        self.move_down_button = QPushButton("↓ Bajar")
        self.remove_button = QPushButton("✕ Eliminar")
        self.clear_button = QPushButton("🗑 Limpiar Todo")

        # Estilos para botones
        for button in [self.move_up_button, self.move_down_button, self.remove_button, self.clear_button]:
            button.setStyleSheet(FileManagerStyles.CONTROL_BUTTON_BASE)
            button.setEnabled(False)

        self.remove_button.setStyleSheet(FileManagerStyles.DANGER_BUTTON)

        self.clear_button.setStyleSheet(FileManagerStyles.DANGER_BUTTON)

        buttons_layout.addWidget(self.move_up_button)
        buttons_layout.addWidget(self.move_down_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.clear_button)

        layout.addLayout(buttons_layout)

        return panel

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

        # Modelo para archivos seleccionados
        self.selected_model = SelectedFilesModel()
        self.selected_list.setModel(self.selected_model)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        # Navegación con botón de directorio superior
        self.parent_dir_button.clicked.connect(self._navigate_to_parent)

        # Selección en vista de archivos
        self.tree_view.selectionModel().selectionChanged.connect(self._on_file_selection_changed)

        # Doble click para navegar/agregar
        self.tree_view.doubleClicked.connect(self._on_file_double_clicked)
        self.tree_view.doubleClicked.connect(self._on_file_double_clicked)

        # Botones de archivo
        self.add_button.clicked.connect(self._add_selected_files)

        # Selección en lista de archivos seleccionados
        self.selected_list.selectionModel().selectionChanged.connect(self._on_selected_files_selection_changed)

        # Reordenamiento por drag and drop
        self.selected_model.files_reordered.connect(self._update_selected_buttons_state)
        self.selected_model.files_reordered.connect(lambda: self.files_selected.emit(self.selected_model.get_selected_files()))

        # Botones de control de archivos seleccionados
        self.move_up_button.clicked.connect(self._move_selected_up)
        self.move_down_button.clicked.connect(self._move_selected_down)
        self.remove_button.clicked.connect(self._remove_selected_files)
        self.clear_button.clicked.connect(self._clear_selected_files)

    def _update_current_directory(self):
        """Actualizar información del directorio actual"""
        current_path = Path(self.file_manager.current_directory)
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

        # Configurar raíz de la vista de árbol
        root_index = self.fs_model.index(str(current_path))
        proxy_root = self.filter_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_root)

        # Mostrar/ocultar botón de directorio superior
        can_go_up = self.file_manager.can_go_up()
        self.parent_dir_button.setVisible(can_go_up)

        # Emitir señal
        self.current_directory_changed.emit(str(current_path))

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
                self._update_current_directory()
        else:
            # Agregar archivo PDF
            file_path = self.fs_model.filePath(source_index)
            if file_path.lower().endswith('.pdf'):
                self._add_file_to_selection(file_path)

    def _navigate_to_parent(self):
        """Navegar al directorio padre"""
        if self.file_manager.go_up():
            self._update_current_directory()

    def _add_selected_files(self):
        """Agregar archivos seleccionados a la lista"""
        selection = self.tree_view.selectionModel().selectedIndexes()

        added_files = []
        for index in selection:
            if index.column() == 0:  # Solo procesar la primera columna
                source_index = self.filter_model.mapToSource(index)
                if not self.fs_model.isDir(source_index):
                    file_path = self.fs_model.filePath(source_index)
                    if file_path.lower().endswith('.pdf'):
                        if self._add_file_to_selection(file_path):
                            added_files.append(file_path)

        if added_files:
            self._emit_files_changed()

    def _add_file_to_selection(self, file_path: str) -> bool:
        """Agregar un archivo a la selección"""
        if file_path not in self.selected_files_set:
            if self.selected_model.add_file(file_path):
                self.selected_files_set.add(file_path)
                self._update_selected_buttons_state()
                return True
        return False

    def _on_selected_files_selection_changed(self):
        """Manejar cambio de selección en archivos seleccionados"""
        self._update_selected_buttons_state()

    def _update_selected_buttons_state(self):
        """Actualizar estado de botones de archivos seleccionados"""
        has_files = len(self.selected_model.selected_files) > 0
        has_selection = len(self.selected_list.selectionModel().selectedRows()) > 0

        self.clear_button.setEnabled(has_files)
        self.remove_button.setEnabled(has_selection)
        self.move_up_button.setEnabled(has_selection)
        self.move_down_button.setEnabled(has_selection)

        # Actualizar también el botón de combinar
        self.combine_button.setEnabled(has_files)

    def _move_selected_up(self):
        """Mover archivo seleccionado hacia arriba"""
        selected_rows = [index.row() for index in self.selected_list.selectionModel().selectedRows()]

        if selected_rows:
            row = min(selected_rows)
            if row > 0:
                if self.selected_model.move_file(row, row - 1):
                    # Mantener selección
                    self.selected_list.selectionModel().setCurrentIndex(
                        self.selected_model.index(row - 1, 0),
                        self.selected_list.selectionModel().SelectionFlag.ClearAndSelect
                    )
                    self._emit_files_changed()

    def _move_selected_down(self):
        """Mover archivo seleccionado hacia abajo"""
        selected_rows = [index.row() for index in self.selected_list.selectionModel().selectedRows()]

        if selected_rows:
            row = max(selected_rows)
            if row < len(self.selected_model.selected_files) - 1:
                if self.selected_model.move_file(row, row + 1):
                    # Mantener selección
                    self.selected_list.selectionModel().setCurrentIndex(
                        self.selected_model.index(row + 1, 0),
                        self.selected_list.selectionModel().SelectionFlag.ClearAndSelect
                    )
                    self._emit_files_changed()

    def _remove_selected_files(self):
        """Remover archivos seleccionados"""
        selected_rows = sorted([index.row() for index in self.selected_list.selectionModel().selectedRows()],
                              reverse=True)

        for row in selected_rows:
            if 0 <= row < len(self.selected_model.selected_files):
                file_path = self.selected_model.selected_files[row]
                self.selected_files_set.discard(file_path)
                self.selected_model.remove_file(row)

        self._update_selected_buttons_state()
        self._emit_files_changed()

    def _clear_selected_files(self):
        """Limpiar todos los archivos seleccionados"""
        self.selected_files_set.clear()
        self.selected_model.clear_files()
        self._update_selected_buttons_state()
        self._emit_files_changed()

    def _emit_files_changed(self):
        """Emitir señal de cambio en archivos seleccionados"""
        files = self.selected_model.get_selected_files()
        self.files_selected.emit(files)

        # Controlar estado del botón de combinar
        self.combine_button.setEnabled(len(files) > 0)

    # Métodos públicos para interacción externa

    def get_selected_files(self) -> List[str]:
        """Obtener lista de archivos seleccionados"""
        return self.selected_model.get_selected_files()

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
        self._clear_selected_files()
