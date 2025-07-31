"""
Ventana principal de la aplicación
"""
from typing import List, Dict
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QCheckBox, QMessageBox,
                            QFileDialog, QWidget, QFrame, QListWidgetItem)
from PyQt6.QtCore import Qt

from .widgets import DragDropListWidget
from .styles import StyleManager, ButtonStyle
from core.file_manager import FileManager, FileManagerError
from core.pdf_combiner import PDFCombinerService, PDFCombinerError
from utils.text_processor import TextProcessor
from config.settings import AppConfig

class PDFCombinerGUI(QMainWindow):
    """Ventana principal de PDF Combiner Pro"""

    def __init__(self):
        super().__init__()
        self.selected_files: List[str] = []
        self.file_tooltips: Dict[int, str] = {}
        self.selected_tooltips: Dict[int, str] = {}

        self._setup_services()
        self._init_ui()
        self._load_initial_files()

    def _setup_services(self):
        """Configurar servicios de la aplicación"""
        self.file_manager = FileManager()
        try:
            self.pdf_service = PDFCombinerService()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al inicializar servicio PDF: {e}")
            self.pdf_service = None

    def _init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        self.setGeometry(100, 100, *AppConfig.WINDOW_SIZE)
        self.setMinimumSize(*AppConfig.WINDOW_MIN_SIZE)

        self._create_central_widget()
        self._create_layouts()
        self._setup_connections()

    def _create_central_widget(self):
        """Crear widget central y layouts"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

    def _create_layouts(self):
        """Crear todos los layouts de la interfaz"""
        # Crear frames
        self.left_frame = self._create_file_browser_frame()
        self.center_frame = self._create_control_frame()
        self.right_frame = self._create_selected_files_frame()

        # Agregar al layout principal
        self.main_layout.addWidget(self.left_frame)
        self.main_layout.addWidget(self.center_frame)
        self.main_layout.addWidget(self.right_frame)

        # Proporciones
        self.main_layout.setStretch(0, 2)
        self.main_layout.setStretch(1, 0)
        self.main_layout.setStretch(2, 2)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        self.file_listbox.itemDoubleClicked.connect(self._on_file_double_click)
        self.selected_listbox.itemDoubleClicked.connect(self._on_selected_double_click)

    def _create_file_browser_frame(self) -> QFrame:
        """Crear frame del navegador de archivos"""
        self.file_listbox = DragDropListWidget()
        self.file_listbox.setObjectName("file_listbox")
        self.file_listbox.setSelectionMode(DragDropListWidget.SelectionMode.MultiSelection)

        return self._create_list_frame("Navegador de archivos", self.file_listbox)

    def _create_selected_files_frame(self) -> QFrame:
        """Crear frame de archivos seleccionados"""
        self.selected_listbox = DragDropListWidget(enable_drag_drop=True)
        buttons_layout = self._create_control_buttons_layout()

        return self._create_list_frame("Ficheros seleccionados", self.selected_listbox, buttons_layout)

    def _create_control_frame(self) -> QFrame:
        """Crear frame central con controles"""
        center_frame = QFrame()
        center_frame.setMaximumWidth(AppConfig.CENTER_FRAME_WIDTH)
        center_layout = QVBoxLayout(center_frame)
        center_layout.addStretch()

        # Botón añadir
        btn_add = self._create_styled_button("Añadir →", ButtonStyle.SUCCESS, self._add_selected_files)
        center_layout.addWidget(btn_add)

        # Checkbox para índice
        self.create_index_checkbox = QCheckBox("Crear índice interactivo")
        self.create_index_checkbox.setChecked(True)
        self.create_index_checkbox.setStyleSheet("color: #2196F3; font-weight: bold; padding: 5px;")
        center_layout.addWidget(self.create_index_checkbox)

        # Botón combinar
        btn_combine = self._create_styled_button("Combinar PDFs", ButtonStyle.PRIMARY, self._combine_pdfs)
        center_layout.addWidget(btn_combine)

        center_layout.addStretch()
        return center_frame

    def _create_control_buttons_layout(self) -> QHBoxLayout:
        """Crear layout de botones de control"""
        buttons_layout = QHBoxLayout()

        btn_up = self._create_styled_button("↑ Subir", ButtonStyle.SECONDARY, self._move_up)
        btn_down = self._create_styled_button("↓ Bajar", ButtonStyle.SECONDARY, self._move_down)
        btn_remove = self._create_styled_button("Eliminar", ButtonStyle.DANGER, self._remove_selected)

        buttons_layout.addWidget(btn_up)
        buttons_layout.addWidget(btn_down)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_remove)

        return buttons_layout

    def _create_list_frame(self, title: str, list_widget: DragDropListWidget,
                          buttons_layout=None) -> QFrame:
        """Crear frame consistente para listas"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setMinimumWidth(AppConfig.FRAME_MIN_WIDTH)
        layout = QVBoxLayout(frame)

        # Título
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; color: #2196F3; padding: 5px;")
        layout.addWidget(label)

        # Lista
        layout.addWidget(list_widget)

        # Botones si se proporcionan
        if buttons_layout:
            layout.addLayout(buttons_layout)

        return frame

    def _create_styled_button(self, text: str, style: ButtonStyle, callback=None) -> QPushButton:
        """Crear botón con estilo"""
        button = QPushButton(text)
        button.setStyleSheet(StyleManager.get_button_style(style))
        if callback:
            button.clicked.connect(callback)
        return button

    def _load_initial_files(self):
        """Cargar archivos iniciales"""
        try:
            pdf_files = self.file_manager.get_pdf_files()
            self._populate_list_with_titles(self.file_listbox, pdf_files, self.file_tooltips)
            self._update_visual_marks()
        except FileManagerError as e:
            QMessageBox.warning(self, "Advertencia", f"Error al cargar archivos: {e}")

    def _populate_list_with_titles(self, list_widget: DragDropListWidget,
                                  files: List[str], tooltips_dict: Dict[int, str]):
        """Poblar lista con títulos y configurar tooltips"""
        list_widget.clear()
        tooltips_dict.clear()

        for i, filename in enumerate(files):
            title = TextProcessor.extract_title(filename)
            item = QListWidgetItem(title)
            list_widget.addItem(item)
            tooltips_dict[i] = filename

        list_widget.set_tooltips(tooltips_dict)

    def _add_selected_files(self):
        """Añadir archivos seleccionados a la lista de la derecha"""
        selected_items = self.file_listbox.selectedItems()

        for item in selected_items:
            row = self.file_listbox.row(item)
            if row in self.file_tooltips:
                filename = self.file_tooltips[row]
                if filename not in self.selected_files:
                    self.selected_files.append(filename)

        self._refresh_selected_listbox()
        self._update_visual_marks()

    def _on_file_double_click(self, item: QListWidgetItem):
        """Manejar doble click en archivo"""
        row = self.file_listbox.row(item)
        if row in self.file_tooltips:
            filename = self.file_tooltips[row]
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self._refresh_selected_listbox()
                self._update_visual_marks()

    def _on_selected_double_click(self, item: QListWidgetItem):
        """Manejar doble click en archivo seleccionado para eliminarlo"""
        row = self.selected_listbox.row(item)
        if 0 <= row < len(self.selected_files):
            self.selected_files.pop(row)
            self._refresh_selected_listbox()
            self._update_visual_marks()

    def _refresh_selected_listbox(self):
        """Actualizar la lista de archivos seleccionados"""
        self._populate_list_with_titles(self.selected_listbox, self.selected_files, self.selected_tooltips)

    def _update_visual_marks(self):
        """Actualizar las marcas visuales en la lista de archivos"""
        self.file_listbox.update_marks(self.selected_files)

    def _remove_selected(self):
        """Eliminar archivo seleccionado de la lista"""
        current_row = self.selected_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.selected_files):
            self.selected_files.pop(current_row)
            self._refresh_selected_listbox()
            self._update_visual_marks()

    def _move_up(self):
        """Mover archivo hacia arriba en la lista"""
        self._move_item_in_list('up')

    def _move_down(self):
        """Mover archivo hacia abajo en la lista"""
        self._move_item_in_list('down')

    def _move_item_in_list(self, direction: str):
        """Mover elemento en la lista"""
        current_row = self.selected_listbox.currentRow()

        if direction == 'up' and current_row > 0:
            new_row = current_row - 1
        elif direction == 'down' and current_row >= 0 and current_row < len(self.selected_files) - 1:
            new_row = current_row + 1
        else:
            return

        # Intercambiar elementos
        self.selected_files[current_row], self.selected_files[new_row] = \
            self.selected_files[new_row], self.selected_files[current_row]

        # Actualizar lista y mantener selección
        self._refresh_selected_listbox()
        self.selected_listbox.setCurrentRow(new_row)

    def _combine_pdfs(self):
        """Combinar PDFs - lógica simplificada"""
        if not self._validate_selection():
            return

        output_file = self._get_output_file()
        if not output_file:
            return

        if not self.pdf_service:
            QMessageBox.critical(self, "Error", "Servicio PDF no disponible")
            return

        try:
            result = self.pdf_service.combine(
                files=self.selected_files,
                output_path=output_file,
                create_index=self.create_index_checkbox.isChecked()
            )
            self._show_success_message(result)
        except PDFCombinerError as e:
            self._show_error_message(str(e))
        except Exception as e:
            self._show_error_message(f"Error inesperado: {e}")

    def _validate_selection(self) -> bool:
        """Validar selección de archivos"""
        if not self.selected_files:
            QMessageBox.warning(self, "Advertencia", "No hay ficheros seleccionados.")
            return False
        return True

    def _get_output_file(self) -> str:
        """Obtener archivo de salida"""
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF combinado",
            AppConfig.DEFAULT_OUTPUT_NAME,
            "PDF files (*.pdf)"
        )
        return output_file

    def _show_success_message(self, result_path: str):
        """Mostrar mensaje de éxito"""
        if self.create_index_checkbox.isChecked():
            message = f"PDF combinado con índice interactivo guardado como:\\n{result_path}"
        else:
            message = f"PDF combinado guardado como:\\n{result_path}"
        QMessageBox.information(self, "Éxito", message)

    def _show_error_message(self, error_message: str):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error", error_message)

    def keyPressEvent(self, event):
        """Manejar eventos de teclado"""
        key = event.key()
        modifiers = event.modifiers()

        # Tab para cambiar entre listas
        if key == Qt.Key.Key_Tab:
            self._handle_tab_navigation()
        # Enter para añadir archivos
        elif key == Qt.Key.Key_Return and self.file_listbox.hasFocus():
            self._add_selected_files()
        # Shift + flechas para reordenar en lista de seleccionados
        elif (modifiers & Qt.KeyboardModifier.ShiftModifier and
              self.selected_listbox.hasFocus()):
            if key == Qt.Key.Key_Up:
                self._move_up()
            elif key == Qt.Key.Key_Down:
                self._move_down()
        else:
            super().keyPressEvent(event)

    def _handle_tab_navigation(self):
        """Manejar navegación con Tab entre listas"""
        if self.file_listbox.hasFocus():
            self.selected_listbox.setFocus()
            if self.selected_listbox.count() > 0:
                self.selected_listbox.setCurrentRow(0)
        elif self.selected_listbox.hasFocus():
            self.file_listbox.setFocus()
            if self.file_listbox.count() > 0:
                self.file_listbox.setCurrentRow(0)
