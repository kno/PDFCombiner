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

        # Agregar al layout principal
        self.main_layout.addWidget(self.file_manager_widget)

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        # Conectar señales del file manager widget
        self.file_manager_widget.files_selected.connect(self._on_files_selected)
        self.file_manager_widget.current_directory_changed.connect(self._on_directory_changed)

        # Conectar el botón de combinar del file manager widget
        self.file_manager_widget.combine_button.clicked.connect(self._combine_pdfs)

    def _on_files_selected(self, files: List[str]):
        """Manejar cambio en archivos seleccionados"""
        self.selected_files = files.copy()

        # Habilitar/deshabilitar botón de combinar
        self.file_manager_widget.combine_button.setEnabled(len(self.selected_files) > 0)

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

    def _validate_selection(self) -> bool:
        """Validar selección de archivos"""
        if not self.selected_files:
            QMessageBox.warning(self, "Advertencia", "No hay ficheros seleccionados.")
            return False
        return True

    def _combine_pdfs(self):
        """Combinar PDFs usando los títulos editados del listado"""
        # Sincronizar la lista de archivos seleccionados directamente del widget
        self.selected_files = self.file_manager_widget.get_selected_files()

        if not self._validate_selection():
            return

        output_file = self._get_output_file()
        if not output_file:
            return

        if not self.pdf_service:
            QMessageBox.critical(self, "Error", "Servicio PDF no disponible")
            return

        # Obtener los títulos editados del listado
        edited_titles = self.file_manager_widget.get_selected_titles()

        try:
            result = self.pdf_service.combine(
                files=self.selected_files,
                output_path=output_file,
                create_index=self.file_manager_widget.create_index_checkbox.isChecked(),
                titles=edited_titles
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
        if self.file_manager_widget.create_index_checkbox.isChecked():
            message = f"PDF combinado con índice interactivo guardado como:\n{result_path}"
        else:
            message = f"PDF combinado guardado como:\n{result_path}"
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
        if self.file_manager_widget.create_index_checkbox.isChecked():
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
