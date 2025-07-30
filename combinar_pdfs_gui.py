import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QListWidget, QPushButton, QLabel, QCheckBox, QMessageBox,
                            QFileDialog, QWidget, QListWidgetItem, QFrame)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from pdf_utils import AdvancedPDFCombiner, TextProcessor

class DragDropListWidget(QListWidget):
    """Lista personalizada con soporte para drag & drop y tooltips"""

    def __init__(self, parent=None, show_tooltips=True):
        super().__init__(parent)
        self.show_tooltips = show_tooltips
        self.file_tooltips = {}
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        # Solo habilitar drag & drop en la lista de seleccionados
        if parent and hasattr(parent, 'is_selected_list'):
            self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        else:
            self.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)

    def set_tooltips(self, tooltips_dict):
        """Establecer el diccionario de tooltips"""
        self.file_tooltips = tooltips_dict

    def mouseMoveEvent(self, event):
        """Mostrar tooltip al mover el mouse"""
        if self.show_tooltips:
            item = self.itemAt(event.pos())
            if item:
                row = self.row(item)
                if row in self.file_tooltips:
                    self.setToolTip(f"📄 {self.file_tooltips[row]}")
                else:
                    self.setToolTip("")
            else:
                self.setToolTip("")
        super().mouseMoveEvent(event)

class PDFCombinerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.file_tooltips = {}
        self.selected_tooltips = {}
        self.init_ui()
        self.populate_file_list()

    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("PDF Combiner Pro - Qt Edition")
        self.setGeometry(100, 100, 900, 500)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)

        # Frame izquierdo - Navegador de archivos
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_frame.setMinimumWidth(280)
        left_layout = QVBoxLayout(left_frame)

        # Etiqueta del navegador
        lbl_files = QLabel("Navegador de archivos")
        lbl_files.setStyleSheet("font-weight: bold; color: #2196F3; padding: 5px;")
        left_layout.addWidget(lbl_files)

        # Lista de archivos
        self.file_listbox = DragDropListWidget(show_tooltips=True)
        self.file_listbox.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.file_listbox.itemDoubleClicked.connect(self.on_file_double_click)
        left_layout.addWidget(self.file_listbox)

        # Frame central - Controles
        center_frame = QFrame()
        center_frame.setMaximumWidth(120)
        center_layout = QVBoxLayout(center_frame)
        center_layout.addStretch()

        # Botón añadir
        btn_add = QPushButton("Añadir →")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_add.clicked.connect(self.add_selected_files)
        center_layout.addWidget(btn_add)

        # Checkbox para índice
        self.create_index_checkbox = QCheckBox("Crear índice interactivo")
        self.create_index_checkbox.setChecked(True)
        self.create_index_checkbox.setStyleSheet("color: #2196F3; font-weight: bold; padding: 5px;")
        center_layout.addWidget(self.create_index_checkbox)

        # Botón combinar
        btn_combine = QPushButton("Combinar PDFs")
        btn_combine.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_combine.clicked.connect(self.combine_pdfs)
        center_layout.addWidget(btn_combine)

        center_layout.addStretch()

        # Frame derecho - Archivos seleccionados
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_frame.setMinimumWidth(280)
        right_layout = QVBoxLayout(right_frame)

        # Etiqueta de seleccionados
        lbl_selected = QLabel("Ficheros seleccionados")
        lbl_selected.setStyleSheet("font-weight: bold; color: #2196F3; padding: 5px;")
        right_layout.addWidget(lbl_selected)

        # Lista de seleccionados
        self.selected_listbox = DragDropListWidget(show_tooltips=True)
        self.selected_listbox.is_selected_list = True  # Marcar como lista de seleccionados
        self.selected_listbox.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        right_layout.addWidget(self.selected_listbox)

        # Botones de control
        buttons_layout = QHBoxLayout()

        btn_up = QPushButton("↑ Subir")
        btn_up.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        btn_up.clicked.connect(self.move_up)
        buttons_layout.addWidget(btn_up)

        btn_down = QPushButton("↓ Bajar")
        btn_down.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        btn_down.clicked.connect(self.move_down)
        buttons_layout.addWidget(btn_down)

        buttons_layout.addStretch()

        btn_remove = QPushButton("Eliminar")
        btn_remove.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        btn_remove.clicked.connect(self.remove_selected)
        buttons_layout.addWidget(btn_remove)

        right_layout.addLayout(buttons_layout)

        # Agregar frames al layout principal
        main_layout.addWidget(left_frame)
        main_layout.addWidget(center_frame)
        main_layout.addWidget(right_frame)

        # Establecer proporciones
        main_layout.setStretch(0, 2)  # Frame izquierdo
        main_layout.setStretch(1, 0)  # Frame central
        main_layout.setStretch(2, 2)  # Frame derecho

    def populate_file_list(self):
        """Poblar la lista de archivos PDF"""
        self.file_listbox.clear()
        self.file_tooltips.clear()

        try:
            pdfs = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]

            for i, filename in enumerate(sorted(pdfs)):
                # Extraer título usando TextProcessor
                title = TextProcessor.extract_title(filename)

                # Añadir elemento a la lista con solo el título
                item = QListWidgetItem(title)
                self.file_listbox.addItem(item)

                # Guardar mapeo para tooltip
                self.file_tooltips[i] = filename

            # Establecer tooltips en la lista
            self.file_listbox.set_tooltips(self.file_tooltips)

        except Exception as e:
            QMessageBox.warning(self, "Advertencia", f"Error al cargar archivos: {e}")

    def add_selected_files(self):
        """Añadir archivos seleccionados a la lista de la derecha"""
        selected_items = self.file_listbox.selectedItems()

        for item in selected_items:
            row = self.file_listbox.row(item)
            if row in self.file_tooltips:
                filename = self.file_tooltips[row]
                if filename not in self.selected_files:
                    self.selected_files.append(filename)

        self.refresh_selected_listbox()

    def on_file_double_click(self, item):
        """Manejar doble click en archivo"""
        row = self.file_listbox.row(item)
        if row in self.file_tooltips:
            filename = self.file_tooltips[row]
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self.refresh_selected_listbox()

    def refresh_selected_listbox(self):
        """Actualizar la lista de archivos seleccionados"""
        self.selected_listbox.clear()
        self.selected_tooltips.clear()

        for i, filename in enumerate(self.selected_files):
            # Extraer título
            title = TextProcessor.extract_title(filename)

            # Añadir elemento con solo el título
            item = QListWidgetItem(title)
            self.selected_listbox.addItem(item)

            # Guardar mapeo para tooltip
            self.selected_tooltips[i] = filename

        # Establecer tooltips
        self.selected_listbox.set_tooltips(self.selected_tooltips)

    def remove_selected(self):
        """Eliminar archivo seleccionado de la lista"""
        current_row = self.selected_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.selected_files):
            self.selected_files.pop(current_row)
            self.refresh_selected_listbox()

    def move_up(self):
        """Mover archivo hacia arriba en la lista"""
        current_row = self.selected_listbox.currentRow()
        if current_row > 0:
            # Intercambiar elementos
            self.selected_files[current_row], self.selected_files[current_row-1] = \
                self.selected_files[current_row-1], self.selected_files[current_row]

            # Actualizar lista y mantener selección
            self.refresh_selected_listbox()
            self.selected_listbox.setCurrentRow(current_row - 1)

    def move_down(self):
        """Mover archivo hacia abajo en la lista"""
        current_row = self.selected_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.selected_files) - 1:
            # Intercambiar elementos
            self.selected_files[current_row], self.selected_files[current_row+1] = \
                self.selected_files[current_row+1], self.selected_files[current_row]

            # Actualizar lista y mantener selección
            self.refresh_selected_listbox()
            self.selected_listbox.setCurrentRow(current_row + 1)

    def combine_pdfs(self):
        """Combinar los PDFs seleccionados"""
        if not self.selected_files:
            QMessageBox.warning(self, "Advertencia", "No hay ficheros seleccionados.")
            return

        # Diálogo para guardar archivo
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF combinado",
            "",
            "PDF files (*.pdf)"
        )

        if not output_file:
            return

        try:
            # Generar títulos automáticamente
            titles = [TextProcessor.extract_title(f) for f in self.selected_files]

            # Crear combinador avanzado
            combiner = AdvancedPDFCombiner(self.selected_files, titles)

            # Combinar con o sin índice
            if self.create_index_checkbox.isChecked():
                final_file = combiner.combine_with_index(output_file)
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"PDF combinado con índice interactivo guardado como:\n{final_file}"
                )
            else:
                final_file = combiner.combine_simple(output_file)
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"PDF combinado guardado como:\n{final_file}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo combinar los PDFs:\n{e}")
            import traceback
            traceback.print_exc()

    def keyPressEvent(self, event):
        """Manejar eventos de teclado"""
        # Tab para cambiar entre listas
        if event.key() == Qt.Key.Key_Tab:
            if self.file_listbox.hasFocus():
                self.selected_listbox.setFocus()
                if self.selected_listbox.count() > 0:
                    self.selected_listbox.setCurrentRow(0)
            elif self.selected_listbox.hasFocus():
                self.file_listbox.setFocus()
                if self.file_listbox.count() > 0:
                    self.file_listbox.setCurrentRow(0)

        # Enter para añadir archivos
        elif event.key() == Qt.Key.Key_Return and self.file_listbox.hasFocus():
            self.add_selected_files()

        # Shift + flechas para reordenar en lista de seleccionados
        elif (event.modifiers() & Qt.KeyboardModifier.ShiftModifier and
              self.selected_listbox.hasFocus()):
            if event.key() == Qt.Key.Key_Up:
                self.move_up()
            elif event.key() == Qt.Key.Key_Down:
                self.move_down()

        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)

    # Establecer estilo oscuro moderno
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QFrame {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 5px;
        }
        QListWidget {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px;
            selection-background-color: #0078d4;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #555555;
        }
        QListWidget::item:selected {
            background-color: #0078d4;
        }
        QListWidget::item:hover {
            background-color: #505050;
        }
        QLabel {
            color: #ffffff;
        }
        QCheckBox {
            color: #ffffff;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QCheckBox::indicator:unchecked {
            background-color: #404040;
            border: 2px solid #555555;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
        }
    """)

    window = PDFCombinerGUI()
    window.show()

    return app.exec()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(main())
    else:
        # Mantener compatibilidad con uso como módulo
        app = PDFCombinerGUI()
        app.mainloop = lambda: main()
