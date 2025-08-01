"""
GUI module for PDF Combiner Pro
"""
from .main_window import PDFCombinerGUI
from .file_manager_widget import FileManagerWidget
from .styles import StyleManager, ButtonStyle

__all__ = [
    'PDFCombinerGUI',
    'FileManagerWidget',
    'StyleManager',
    'ButtonStyle'
]
