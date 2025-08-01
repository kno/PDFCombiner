from PyQt6.QtWidgets import QListView
from PyQt6.QtGui import QDropEvent
from PyQt6.QtCore import QModelIndex

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
