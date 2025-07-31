import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QListWidget, QPushButton, QLabel, QCheckBox, QMessageBox,
                            QFileDialog, QWidget, QListWidgetItem, QFrame)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from pdf_utils import AdvancedPDFCombiner, TextProcessor

# Constantes de estilo
BUTTON_STYLES = {
    'primary': """
        QPushButton {
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            padding: 12px 16px;
            border: none;
            border-radius: 4px;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
    """,
    'success': """
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
    """,
    'secondary': """
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
    """,
    'danger': """
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
    """
}

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

    def create_styled_button(self, text, style_type, callback=None):
        """Crear botón con estilo predefinido"""
        button = QPushButton(text)
        button.setStyleSheet(BUTTON_STYLES[style_type])
        if callback:
            button.clicked.connect(callback)
        return button

    def create_styled_label(self, text):
        """Crear etiqueta con estilo consistente"""
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; color: #2196F3; padding: 5px;")
        return label

    def create_list_frame(self, title, list_widget, buttons_layout=None):
        """Crear frame consistente para listas"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setMinimumWidth(280)
        layout = QVBoxLayout(frame)

        # Añadir título
        layout.addWidget(self.create_styled_label(title))

        # Añadir lista
        layout.addWidget(list_widget)

        # Añadir botones si se proporcionan
        if buttons_layout:
            layout.addLayout(buttons_layout)

        return frame

    def setup_list_widget(self, is_selected_list=False, multi_selection=False):
        """Configurar widget de lista con opciones consistentes"""
        list_widget = DragDropListWidget(show_tooltips=True)

        if is_selected_list:
            list_widget.is_selected_list = True
            list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        else:
            list_widget.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)

        if multi_selection:
            list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        return list_widget

    def populate_list_with_titles(self, list_widget, files, tooltips_dict):
        """Poblar lista con títulos y configurar tooltips"""
        list_widget.clear()
        tooltips_dict.clear()

        for i, filename in enumerate(files):
            title = TextProcessor.extract_title(filename)
            item = QListWidgetItem(title)
            list_widget.addItem(item)
            tooltips_dict[i] = filename

        list_widget.set_tooltips(tooltips_dict)

    def move_item_in_list(self, direction):
        """Mover elemento en la lista (direction: 'up' o 'down')"""
        current_row = self.selected_listbox.currentRow()

        if direction == 'up' and current_row > 0:
            new_row = current_row - 1
        elif direction == 'down' and current_row >= 0 and current_row < len(self.selected_files) - 1:
            new_row = current_row + 1
        else:
            return  # No se puede mover

        # Intercambiar elementos
        self.selected_files[current_row], self.selected_files[new_row] = \
            self.selected_files[new_row], self.selected_files[current_row]

        # Actualizar lista y mantener selección
        self.refresh_selected_listbox()
        self.selected_listbox.setCurrentRow(new_row)

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
        self.file_listbox = self.setup_list_widget(multi_selection=True)
        self.file_listbox.itemDoubleClicked.connect(self.on_file_double_click)
        left_frame = self.create_list_frame("Navegador de archivos", self.file_listbox)

        # Frame central - Controles
        center_frame = self.create_center_frame()

        # Frame derecho - Archivos seleccionados
        self.selected_listbox = self.setup_list_widget(is_selected_list=True)
        self.selected_listbox.itemDoubleClicked.connect(self.on_selected_double_click)
        buttons_layout = self.create_control_buttons_layout()
        right_frame = self.create_list_frame("Ficheros seleccionados", self.selected_listbox, buttons_layout)

        # Agregar frames al layout principal
        main_layout.addWidget(left_frame)
        main_layout.addWidget(center_frame)
        main_layout.addWidget(right_frame)

        # Establecer proporciones
        main_layout.setStretch(0, 2)  # Frame izquierdo
        main_layout.setStretch(1, 0)  # Frame central
        main_layout.setStretch(2, 2)  # Frame derecho

    def create_center_frame(self):
        """Crear frame central con controles"""
        center_frame = QFrame()
        center_frame.setMaximumWidth(180)
        center_layout = QVBoxLayout(center_frame)
        center_layout.addStretch()

        # Botón añadir
        btn_add = self.create_styled_button("Añadir →", 'success', self.add_selected_files)
        center_layout.addWidget(btn_add)

        # Checkbox para índice
        self.create_index_checkbox = QCheckBox("Crear índice interactivo")
        self.create_index_checkbox.setChecked(True)
        self.create_index_checkbox.setStyleSheet("color: #2196F3; font-weight: bold; padding: 5px;")
        center_layout.addWidget(self.create_index_checkbox)

        # Botón combinar
        btn_combine = self.create_styled_button("Combinar PDFs", 'primary', self.combine_pdfs)
        center_layout.addWidget(btn_combine)

        center_layout.addStretch()
        return center_frame

    def create_control_buttons_layout(self):
        """Crear layout de botones de control"""
        buttons_layout = QHBoxLayout()

        btn_up = self.create_styled_button("↑ Subir", 'secondary', self.move_up)
        btn_down = self.create_styled_button("↓ Bajar", 'secondary', self.move_down)
        btn_remove = self.create_styled_button("Eliminar", 'danger', self.remove_selected)

        buttons_layout.addWidget(btn_up)
        buttons_layout.addWidget(btn_down)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_remove)

        return buttons_layout

    def populate_file_list(self):
        """Poblar la lista de archivos PDF"""
        try:
            pdfs = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
            self.populate_list_with_titles(self.file_listbox, sorted(pdfs), self.file_tooltips)
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

    def handle_file_action(self, item, action_type):
        """Manejar acciones sobre archivos (add/remove)"""
        if action_type == 'add':
            row = self.file_listbox.row(item)
            if row in self.file_tooltips:
                filename = self.file_tooltips[row]
                if filename not in self.selected_files:
                    self.selected_files.append(filename)
                    self.refresh_selected_listbox()
        elif action_type == 'remove':
            row = self.selected_listbox.row(item)
            if 0 <= row < len(self.selected_files):
                self.selected_files.pop(row)
                self.refresh_selected_listbox()

    def on_file_double_click(self, item):
        """Manejar doble click en archivo"""
        self.handle_file_action(item, 'add')

    def on_selected_double_click(self, item):
        """Manejar doble click en archivo seleccionado para eliminarlo"""
        self.handle_file_action(item, 'remove')

    def refresh_selected_listbox(self):
        """Actualizar la lista de archivos seleccionados"""
        self.populate_list_with_titles(self.selected_listbox, self.selected_files, self.selected_tooltips)

    def remove_selected(self):
        """Eliminar archivo seleccionado de la lista"""
        current_row = self.selected_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.selected_files):
            self.selected_files.pop(current_row)
            self.refresh_selected_listbox()

    def move_up(self):
        """Mover archivo hacia arriba en la lista"""
        self.move_item_in_list('up')

    def move_down(self):
        """Mover archivo hacia abajo en la lista"""
        self.move_item_in_list('down')

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
            self._process_pdf_combination(output_file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo combinar los PDFs:\n{e}")
            import traceback
            traceback.print_exc()

    def _process_pdf_combination(self, output_file):
        """Procesar la combinación de PDFs"""
        # Generar títulos automáticamente
        titles = [TextProcessor.extract_title(f) for f in self.selected_files]

        # Crear combinador avanzado
        combiner = AdvancedPDFCombiner(self.selected_files, titles)

        # Combinar con o sin índice
        if self.create_index_checkbox.isChecked():
            final_file = combiner.combine_with_index(output_file)
            message = f"PDF combinado con índice interactivo guardado como:\n{final_file}"
        else:
            final_file = combiner.combine_simple(output_file)
            message = f"PDF combinado guardado como:\n{final_file}"

        QMessageBox.information(self, "Éxito", message)

    def keyPressEvent(self, event):
        """Manejar eventos de teclado"""
        key = event.key()
        modifiers = event.modifiers()

        # Tab para cambiar entre listas
        if key == Qt.Key.Key_Tab:
            self._handle_tab_navigation()
        # Enter para añadir archivos
        elif key == Qt.Key.Key_Return and self.file_listbox.hasFocus():
            self.add_selected_files()
        # Shift + flechas para reordenar en lista de seleccionados
        elif (modifiers & Qt.KeyboardModifier.ShiftModifier and
              self.selected_listbox.hasFocus()):
            if key == Qt.Key.Key_Up:
                self.move_up()
            elif key == Qt.Key.Key_Down:
                self.move_down()
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

def main():
    app = QApplication(sys.argv)

    # Establecer estilo oscuro moderno
    app.setStyleSheet(get_dark_theme_stylesheet())

    window = PDFCombinerGUI()
    window.show()

    return app.exec()

def get_dark_theme_stylesheet():
    """Obtener la hoja de estilos del tema oscuro"""
    return """
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
    """

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(main())
    else:
        # Mantener compatibilidad con uso como módulo
        app = PDFCombinerGUI()
        app.mainloop = lambda: main()
