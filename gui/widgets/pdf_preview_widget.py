"""
Widget de previsualización de PDFs
"""
import os
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QHBoxLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QPixmap, QPainter, QImage
from gui.styles import FileManagerStyles
from utils.localization import _

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFRenderThread(QThread):
    """Thread para renderizar páginas PDF sin bloquear la UI"""
    page_rendered = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.pdf_path = None
        self.page_number = 0
        self.zoom_level = 1.0
        self.doc = None

    def set_pdf(self, pdf_path: str):
        """Establecer el PDF a renderizar"""
        self.pdf_path = pdf_path
        if self.doc:
            self.doc.close()
            self.doc = None

    def set_page(self, page_number: int, zoom_level: float = 1.0):
        """Establecer la página a renderizar"""
        self.page_number = page_number
        self.zoom_level = zoom_level

    def run(self):
        """Renderizar la página del PDF"""
        if not self.pdf_path or not PYMUPDF_AVAILABLE:
            return

        try:
            if not self.doc:
                self.doc = fitz.open(self.pdf_path)

            if 0 <= self.page_number < len(self.doc):
                page = self.doc[self.page_number]
                mat = fitz.Matrix(self.zoom_level, self.zoom_level)
                pix = page.get_pixmap(matrix=mat)

                # Convertir a QPixmap
                img_data = pix.tobytes("ppm")
                qimg = QImage.fromData(img_data)
                qpixmap = QPixmap.fromImage(qimg)

                self.page_rendered.emit(qpixmap)
            else:
                self.error_occurred.emit(_("Número de página inválido"))

        except Exception as e:
            self.error_occurred.emit(str(e))

    def cleanup(self):
        """Limpiar recursos"""
        if self.doc:
            self.doc.close()
            self.doc = None


class PDFPreviewWidget(QWidget):
    """Widget para previsualizar archivos PDF"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pdf_path: Optional[str] = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0

        self.render_thread = PDFRenderThread()
        self.render_thread.page_rendered.connect(self._on_page_rendered)
        self.render_thread.error_occurred.connect(self._on_render_error)

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)

        # Título del panel
        self.title_label = QLabel(_("Vista Previa PDF"))
        self.title_label.setStyleSheet(FileManagerStyles.SECTION_TITLE)
        layout.addWidget(self.title_label)

        # Controles de navegación
        controls_layout = QHBoxLayout()

        # Botón página anterior
        self.prev_button = QPushButton("◀")
        self.prev_button.setMaximumWidth(30)
        self.prev_button.setEnabled(False)
        controls_layout.addWidget(self.prev_button)

        # Selector de página
        self.page_text = QLineEdit()
        self.page_text.setPlaceholderText("Página")
        self.page_text.setMaximumWidth(50)
        self.page_text.setMinimumWidth(50)
        self.page_text.setMinimumHeight(28)
        self.page_text.setEnabled(False)
        controls_layout.addWidget(self.page_text)

        # Etiqueta de total de páginas
        self.total_pages_label = QLabel("/ 0")
        controls_layout.addWidget(self.total_pages_label)

        # Botón página siguiente
        self.next_button = QPushButton("▶")
        self.next_button.setMaximumWidth(30)
        self.next_button.setEnabled(False)
        controls_layout.addWidget(self.next_button)

        controls_layout.addStretch()

        # Controles de zoom
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setMaximumWidth(30)
        self.zoom_out_button.setEnabled(False)
        controls_layout.addWidget(self.zoom_out_button)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.zoom_label)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setMaximumWidth(30)
        self.zoom_in_button.setEnabled(False)
        controls_layout.addWidget(self.zoom_in_button)

        layout.addLayout(controls_layout)

        # Área de scroll para la imagen
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label para mostrar la imagen
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText(_("Selecciona un archivo PDF para previsualizar"))
        self.image_label.setStyleSheet("QLabel { color: #888; padding: 20px; }")

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(panel)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Verificar disponibilidad de PyMuPDF
        if not PYMUPDF_AVAILABLE:
            self.image_label.setText(_("PyMuPDF no está instalado.\nInstala con: pip install PyMuPDF"))

    def _setup_connections(self):
        """Configurar conexiones de señales"""
        self.prev_button.clicked.connect(self._go_to_previous_page)
        self.next_button.clicked.connect(self._go_to_next_page)
        self.page_text.textChanged.connect(self._on_page_changed)
        self.zoom_in_button.clicked.connect(self._zoom_in)
        self.zoom_out_button.clicked.connect(self._zoom_out)

    def load_pdf(self, pdf_path: str):
        """Cargar un archivo PDF para previsualizar"""
        if not PYMUPDF_AVAILABLE:
            return

        if not pdf_path or not os.path.exists(pdf_path):
            self.clear_preview()
            return

        self.current_pdf_path = pdf_path
        self.current_page = 0

        # Obtener información del PDF
        try:
            import fitz
            doc = fitz.open(pdf_path)
            self.total_pages = len(doc)
            doc.close()

            # Actualizar controles
            self.page_text.setText("1")
            self.page_text.setEnabled(True)
            self.total_pages_label.setText(f"/ {self.total_pages}")

            # Habilitar botones
            self._update_navigation_buttons()
            self.zoom_in_button.setEnabled(True)
            self.zoom_out_button.setEnabled(True)

            # Actualizar título con nombre del archivo
            filename = Path(pdf_path).name
            self.title_label.setText(f"{_('Vista Previa PDF')}: {filename}")

            # Renderizar primera página
            self.render_thread.set_pdf(pdf_path)
            self._render_current_page()

        except Exception as e:
            self.image_label.setText(f"{_('Error al cargar PDF')}: {str(e)}")
            self.clear_preview()

    def clear_preview(self):
        """Limpiar la vista previa"""
        self.current_pdf_path = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0

        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(_("Selecciona un archivo PDF para previsualizar"))

        # Deshabilitar controles
        self.page_text.setEnabled(False)
        self.page_text.setText("1")
        self.total_pages_label.setText("/ 0")
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.zoom_in_button.setEnabled(False)
        self.zoom_out_button.setEnabled(False)
        self.zoom_label.setText("100%")

        self.title_label.setText(_("Vista Previa PDF"))

    def _render_current_page(self):
        """Renderizar la página actual"""
        if self.current_pdf_path and 0 <= self.current_page < self.total_pages:
            self.render_thread.set_page(self.current_page, self.zoom_level)
            self.render_thread.start()

    @pyqtSlot(QPixmap)
    def _on_page_rendered(self, pixmap: QPixmap):
        """Manejar página renderizada"""
        self.image_label.setPixmap(pixmap)

    @pyqtSlot(str)
    def _on_render_error(self, error_msg: str):
        """Manejar error de renderizado"""
        self.image_label.setText(f"{_('Error')}: {error_msg}")

    def _go_to_previous_page(self):
        """Ir a la página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self.page_text.setText(str(self.current_page + 1))

    def _go_to_next_page(self):
        """Ir a la página siguiente"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.page_text.setText(str(self.current_page + 1))

    def _on_page_changed(self, value: str):
        """Manejar cambio de página desde spinbox"""
        self.current_page = int(value) - 1
        self._update_navigation_buttons()
        self._render_current_page()

    def _update_navigation_buttons(self):
        """Actualizar estado de botones de navegación"""
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < self.total_pages - 1)

    def _zoom_in(self):
        """Aumentar zoom"""
        if self.zoom_level < 3.0:
            self.zoom_level += 0.25
            self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
            self._render_current_page()

    def _zoom_out(self):
        """Disminuir zoom"""
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.25
            self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
            self._render_current_page()

    def reload_texts(self):
        """Recargar textos para cambio de idioma"""
        self.title_label.setText(_("Vista Previa PDF"))
        if not self.current_pdf_path:
            self.image_label.setText(_("Selecciona un archivo PDF para previsualizar"))
        if not PYMUPDF_AVAILABLE:
            self.image_label.setText(_("PyMuPDF no está instalado.\nInstala con: pip install PyMuPDF"))

    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        self.render_thread.cleanup()
        self.render_thread.quit()
        self.render_thread.wait()
        super().closeEvent(event)