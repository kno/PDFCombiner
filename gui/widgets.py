"""
Widgets personalizados para la aplicación
"""
import gettext
from typing import Dict, Set, List
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from config.settings import AppConfig

# Setup for localization
try:
    es = gettext.translation('messages', localedir='locale', languages=['es'])
    es.install()
    _ = es.gettext
except FileNotFoundError:
    # Fallback if translation file is not found
    _ = gettext.gettext

class MarkedListWidget(QListWidget):
    """Lista con capacidad de marcado visual"""

    def __init__(self, parent=None, enable_tooltips: bool = True):
        super().__init__(parent)
        self.enable_tooltips = enable_tooltips
        self.file_tooltips: Dict[int, str] = {}
        self.marked_items: Set[int] = set()
        self._setup_widget()

    def _setup_widget(self):
        """Configuración inicial del widget"""
        self.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)

    def paintEvent(self, event):
        """Renderizado personalizado para elementos marcados"""
        super().paintEvent(event)
        self._paint_marked_items()

    def _paint_marked_items(self):
        """Pintar overlay para elementos marcados"""
        if not hasattr(self, 'objectName') or self.objectName() != "file_listbox":
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            for row in self.marked_items:
                self._paint_marked_item(painter, row)
        finally:
            painter.end()

    def _paint_marked_item(self, painter: QPainter, row: int):
        """Pintar un elemento marcado específico"""
        if row >= self.count():
            return

        item_rect = self.visualItemRect(self.item(row))
        if not item_rect.isValid():
            return

        # Fondo verde semitransparente
        color_rgba = AppConfig.MARK_COLOR_RGBA
        painter.fillRect(item_rect, QColor(*color_rgba))

        # Texto negro
        text_color = AppConfig.MARK_TEXT_COLOR
        painter.setPen(QColor(*text_color))
        text = self.item(row).text()
        painter.drawText(
            item_rect.adjusted(8, 0, -8, 0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            text
        )

    def set_tooltips(self, tooltips_dict: Dict[int, str]):
        """Establecer el diccionario de tooltips"""
        self.file_tooltips = tooltips_dict

    def mark_item(self, row: int) -> None:
        """Marcar elemento en la fila especificada"""
        if 0 <= row < self.count():
            self.marked_items.add(row)
            self.viewport().update()

    def unmark_item(self, row: int) -> None:
        """Desmarcar elemento en la fila especificada"""
        self.marked_items.discard(row)
        self.viewport().update()

    def clear_marks(self) -> None:
        """Limpiar todas las marcas"""
        self.marked_items.clear()
        self.viewport().update()

    def update_marks(self, marked_filenames: List[str]) -> None:
        """Actualizar marcas basándose en lista de archivos seleccionados"""
        self.clear_marks()

        # Revisar cada item en la lista
        for row in range(self.count()):
            item = self.item(row)
            if item:
                # Obtener los datos del DirectoryEntry
                entry_data = item.data(Qt.ItemDataRole.UserRole)

                # Importar DirectoryEntry dentro del método para evitar problemas circulares
                from core.file_manager import DirectoryEntry

                if isinstance(entry_data, DirectoryEntry):
                    # Solo marcar archivos PDF, no directorios
                    if not entry_data.is_directory and entry_data.name != "..":
                        file_path = str(entry_data.path)
                        if file_path in marked_filenames:
                            self.mark_item(row)
                else:
                    # Compatibilidad con el sistema anterior
                    if row in self.file_tooltips:
                        filename = self.file_tooltips[row]
                        if filename in marked_filenames:
                            self.mark_item(row)

    def mouseMoveEvent(self, event):
        """Mostrar tooltip al mover el mouse"""
        if self.enable_tooltips:
            item = self.itemAt(event.pos())
            if item:
                row = self.row(item)
                if row in self.file_tooltips:
                    self.setToolTip(_("📄 {}").format(self.file_tooltips[row]))
                else:
                    self.setToolTip("")
            else:
                self.setToolTip("")
        super().mouseMoveEvent(event)

class DragDropListWidget(MarkedListWidget):
    """Lista con soporte para drag & drop"""

    def __init__(self, parent=None, enable_drag_drop: bool = False):
        super().__init__(parent)
        if enable_drag_drop:
            self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
