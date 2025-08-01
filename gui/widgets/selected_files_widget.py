"""
Widget de archivos seleccionados
"""
from typing import List, Set
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListView, QLabel, QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from gui.custom_list_view import CustomListView
from gui.selected_files_model import SelectedFilesModel
from gui.styles import FileManagerStyles
from utils.localization import _


class SelectedFilesWidget(QWidget):
    """Widget de archivos seleccionados con controles de reordenamiento"""

    # Señales
    files_changed = pyqtSignal(list)  # Lista de archivos cambió
    selection_changed = pyqtSignal()  # Selección cambió

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files_set: Set[str] = set()

        self._setup_ui()
        self._setup_model()
        self._setup_connections()

    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)

        # Título del panel
        title_label = QLabel(_("Archivos Seleccionados"))
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

        self.move_up_button = QPushButton(_("↑ Subir"))
        self.move_down_button = QPushButton(_("↓ Bajar"))
        self.remove_button = QPushButton(_("✕ Eliminar"))
        self.clear_button = QPushButton(_("🗑 Limpiar Todo"))

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

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(panel)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def _setup_model(self):
        """Configurar modelo de datos"""
        # Modelo para archivos seleccionados
        self.selected_model = SelectedFilesModel()
        self.selected_list.setModel(self.selected_model)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        # Selección en lista de archivos seleccionados
        self.selected_list.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # Reordenamiento por drag and drop
        self.selected_model.files_reordered.connect(self._update_buttons_state)
        self.selected_model.files_reordered.connect(self._emit_files_changed)

        # Botones de control de archivos seleccionados
        self.move_up_button.clicked.connect(self._move_selected_up)
        self.move_down_button.clicked.connect(self._move_selected_down)
        self.remove_button.clicked.connect(self._remove_selected_files)
        self.clear_button.clicked.connect(self._clear_selected_files)

    def _on_selection_changed(self):
        """Manejar cambio de selección en archivos seleccionados"""
        self._update_buttons_state()
        self.selection_changed.emit()

    def _update_buttons_state(self):
        """Actualizar estado de botones de archivos seleccionados"""
        has_files = len(self.selected_model.selected_files) > 0
        has_selection = len(self.selected_list.selectionModel().selectedRows()) > 0

        self.clear_button.setEnabled(has_files)
        self.remove_button.setEnabled(has_selection)
        self.move_up_button.setEnabled(has_selection)
        self.move_down_button.setEnabled(has_selection)

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

        self._update_buttons_state()
        self._emit_files_changed()

    def _clear_selected_files(self):
        """Limpiar todos los archivos seleccionados"""
        self.selected_files_set.clear()
        self.selected_model.clear_files()
        self._update_buttons_state()
        self._emit_files_changed()

    def _emit_files_changed(self):
        """Emitir señal de cambio en archivos seleccionados"""
        files = self.selected_model.get_selected_files()
        self.files_changed.emit(files)

    # Métodos públicos

    def add_files(self, file_paths: List[str]) -> bool:
        """Agregar archivos a la selección"""
        added_any = False
        for file_path in file_paths:
            if file_path not in self.selected_files_set:
                if self.selected_model.add_file(file_path):
                    self.selected_files_set.add(file_path)
                    added_any = True

        if added_any:
            self._update_buttons_state()
            self._emit_files_changed()

        return added_any

    def get_selected_files(self) -> List[str]:
        """Obtener lista de archivos seleccionados"""
        return self.selected_model.get_selected_files()

    def get_selected_titles(self) -> List[str]:
        """Obtener los títulos editados de los archivos seleccionados"""
        return self.selected_model.get_titles()

    def clear_selection(self):
        """Limpiar selección de archivos"""
        self._clear_selected_files()

    def get_selected_files_set(self) -> Set[str]:
        """Obtener el set de archivos seleccionados"""
        return self.selected_files_set
