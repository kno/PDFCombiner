from typing import List
from pathlib import Path
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QPainter
from utils.text_processor import TextProcessor

class SelectedFilesModel(QStandardItemModel):
    """Modelo para archivos seleccionados - solo títulos con soporte drag and drop"""

    files_reordered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files: List[dict] = []  # cada dict: {'path': str, 'title': str}
        self.drag_source_row = -1
        self.drag_file_path = None
        self.actual_drop_row = -1  # Posición real del drop desde CustomListView

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def flags(self, index):
        default_flags = super().flags(index)
        if index.isValid():
            return default_flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return default_flags | Qt.ItemFlag.ItemIsDropEnabled

    def mimeData(self, indexes):
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
        self.actual_drop_row = row

    def dropMimeData(self, data, action, row, column, parent):
        if action != Qt.DropAction.MoveAction:
            return False
        if self.drag_source_row == -1 or not self.drag_file_path:
            return super().dropMimeData(data, action, row, column, parent)
        target_row = self.actual_drop_row if self.actual_drop_row != -1 else row
        if target_row == -1:
            target_row = len(self.selected_files)
        if self.drag_source_row < target_row:
            target_row -= 1
        if self.drag_source_row != target_row and 0 <= target_row <= len(self.selected_files):
            file_path = self.selected_files.pop(self.drag_source_row)
            self.selected_files.insert(target_row, file_path)
            self._rebuild_model()
            self.files_reordered.emit()
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
        if sourceParent != destinationParent:
            return False
        if (sourceFirst < 0 or sourceFirst >= self.rowCount() or
            sourceLast < 0 or sourceLast >= self.rowCount() or
            destinationChild < 0 or destinationChild > self.rowCount()):
            return False
        result = super().moveRows(sourceParent, sourceFirst, sourceLast, destinationParent, destinationChild)
        return result

    def removeRows(self, row, count, parent=QModelIndex()):
        result = super().removeRows(row, count, parent)
        return result

    def insertRows(self, row, count, parent=QModelIndex()):
        result = super().insertRows(row, count, parent)
        return result

    def _rebuild_model(self):
        self.clear()
        for entry in self.selected_files:
            title_item = QStandardItem(entry['title'])
            title_item.setData(entry['path'], Qt.ItemDataRole.UserRole)
            title_item.setIcon(self._get_pdf_icon())
            title_item.setEditable(True)
            self.appendRow(title_item)

    def _sync_selected_files_from_model(self):
        old_files = self.selected_files.copy()
        new_files = []
        for i in range(self.rowCount()):
            item = self.item(i)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path and file_path not in new_files:
                    new_files.append(file_path)
        if new_files != old_files:
            self.selected_files = new_files
            self.files_reordered.emit()

    def add_file(self, file_path: str) -> bool:
        if any(entry['path'] == file_path for entry in self.selected_files):
            return False
        path_obj = Path(file_path)
        title = TextProcessor.extract_title(path_obj.name)
        entry = {'path': file_path, 'title': title}
        self.selected_files.append(entry)
        title_item = QStandardItem(title)
        title_item.setData(file_path, Qt.ItemDataRole.UserRole)
        title_item.setIcon(self._get_pdf_icon())
        self.appendRow(title_item)
        return True

    def remove_file(self, row: int) -> bool:
        if 0 <= row < len(self.selected_files):
            self.selected_files.pop(row)
            self.removeRow(row)
            return True
        return False

    def move_file(self, from_row: int, to_row: int) -> bool:
        if (0 <= from_row < len(self.selected_files) and
            0 <= to_row < len(self.selected_files) and
            from_row != to_row):
            for i in range(self.rowCount()):
                item = self.item(i)
                if item:
                    self.selected_files[i]['title'] = item.text()
            entry = self.selected_files.pop(from_row)
            self.selected_files.insert(to_row, entry)
            self._rebuild_model()
            return True
        return False

    def clear_files(self):
        self.selected_files.clear()
        self.clear()

    def get_selected_files(self) -> List[str]:
        return [entry['path'] for entry in self.selected_files]

    def _get_pdf_icon(self) -> QIcon:
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

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole and index.isValid():
            row = index.row()
            self.selected_files[row]['title'] = value
        return super().setData(index, value, role)

    def get_titles(self) -> List[str]:
        for i in range(self.rowCount()):
            item = self.item(i)
            if item:
                self.selected_files[i]['title'] = item.text()
        return [entry['title'] for entry in self.selected_files]
