"""
Ventana principal de la aplicación
"""
from typing import List, Dict
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QCheckBox, QMessageBox,
                            QFileDialog, QWidget, QFrame, QListWidgetItem)
from PyQt6.QtCore import Qt

from .widgets import DragDropListWidget
from .file_manager_widget import FileManagerWidget
from .styles import StyleManager, ButtonStyle
from core.file_manager import FileManager, FileManagerError, DirectoryEntry
from core.pdf_combiner import PDFCombinerService, PDFCombinerError
from utils.text_processor import TextProcessor
from config.settings import AppConfig

class PDFCombinerGUI(QMainWindow):
    """Ventana principal de PDF Combiner Pro"""

    def __init__(self):
        super().__init__()
        self.selected_files: List[str] = []

        self._setup_services()
        self._init_ui()

    def _setup_services(self):
        """Configurar servicios de la aplicación"""
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
        # Crear el widget de gestión de archivos
        self.file_manager_widget = FileManagerWidget()

        # Crear frame de control central
        self.center_frame = self._create_control_frame()

        # Agregar al layout principal
        self.main_layout.addWidget(self.file_manager_widget)
        self.main_layout.addWidget(self.center_frame)

        # Proporciones
        self.main_layout.setStretch(0, 3)  # File manager toma más espacio
        self.main_layout.setStretch(1, 0)  # Control frame mantiene tamaño mínimo

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        # Conectar señales del file manager widget
        self.file_manager_widget.files_selected.connect(self._on_files_selected)
        self.file_manager_widget.current_directory_changed.connect(self._on_directory_changed)

    def _on_files_selected(self, files: List[str]):
        """Manejar cambio en archivos seleccionados"""
        self.selected_files = files.copy()

        # Actualizar etiqueta de información
        count = len(self.selected_files)
        if count == 0:
            self.files_info_label.setText("0 archivos seleccionados")
        elif count == 1:
            self.files_info_label.setText("1 archivo seleccionado")
        else:
            self.files_info_label.setText(f"{count} archivos seleccionados")

    def _on_directory_changed(self, directory: str):
        """Manejar cambio de directorio"""
        # Podemos agregar lógica adicional si es necesario
        pass

    def _create_styled_button(self, text: str, style: ButtonStyle, callback=None) -> QPushButton:
        """Crear botón con estilo"""
        button = QPushButton(text)
        button.setStyleSheet(StyleManager.get_button_style(style))
        if callback:
            button.clicked.connect(callback)
        return button

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

        # Título
        title_label = QLabel("Controles")
        title_label.setStyleSheet("font-weight: bold; color: #2196F3; padding: 10px; font-size: 14px;")
        center_layout.addWidget(title_label)

        # Información de archivos seleccionados
        self.files_info_label = QLabel("0 archivos seleccionados")
        self.files_info_label.setStyleSheet("""
            QLabel {
                color: palette(text);
                background-color: palette(base);
                padding: 8px;
                border: 1px solid palette(mid);
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.files_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.files_info_label)

        center_layout.addStretch()

        # Checkbox para índice
        self.create_index_checkbox = QCheckBox("Crear índice interactivo")
        self.create_index_checkbox.setChecked(True)
        self.create_index_checkbox.setStyleSheet("color: #2196F3; font-weight: bold; padding: 10px;")
        center_layout.addWidget(self.create_index_checkbox)

        # Botón combinar
        btn_combine = self._create_styled_button("🔗 Combinar PDFs", ButtonStyle.PRIMARY, self._combine_pdfs)
        btn_combine.setMinimumHeight(50)
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

    def _validate_selection(self) -> bool:
        """Validar selección de archivos"""
        if not self.selected_files:
            QMessageBox.warning(self, "Advertencia", "No hay ficheros seleccionados.")
            return False
        return True

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

        # F5 para refrescar
        if key == Qt.Key.Key_F5:
            self.file_manager_widget.refresh()
        else:
            super().keyPressEvent(event)
