#!/usr/bin/env python3
"""
PDF Combiner Pro - Aplicación principal
"""
import sys
import os
from PyQt6.QtWidgets import QApplication

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import PDFCombinerGUI
from gui.styles import get_dark_theme_stylesheet

def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    app.setStyleSheet(get_dark_theme_stylesheet())

    window = PDFCombinerGUI()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
