from PyQt6.QtCore import QSortFilterProxyModel, QModelIndex

class PDFFilterModel(QSortFilterProxyModel):
    """Modelo proxy para filtrar solo archivos PDF y directorios, con navegación hacia arriba integrada"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRecursiveFilteringEnabled(True)
        self.file_manager = None
        self.regex_filter = None

    def set_wildcard_filter(self, wildcard_str):
        """Convierte el patrón de wildcard a regex y lo compila"""
        import re
        def escape_except_wildcards(s):
            s = s.replace('*', '__WILDCARD_STAR__').replace('+', '__WILDCARD_PLUS__')
            s = re.escape(s)
            s = s.replace('__WILDCARD_STAR__', '.*').replace('__WILDCARD_PLUS__', '.')
            return s
        pattern = escape_except_wildcards(wildcard_str)
        try:
            self.regex_filter = re.compile(pattern, re.IGNORECASE)
        except Exception:
            self.regex_filter = None

    def set_file_manager(self, file_manager):
        """Configurar referencia al file manager para navegación"""
        self.file_manager = file_manager

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Filtrar solo directorios y archivos PDF, y aplicar filtro regex si existe"""
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        if source_model.isDir(index):
            return True
        filename = source_model.fileName(index)
        if not filename.lower().endswith('.pdf'):
            return False
        if self.regex_filter:
            return bool(self.regex_filter.search(filename))
        return True
