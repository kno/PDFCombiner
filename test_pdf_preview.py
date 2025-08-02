#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de previsualización de PDFs
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from gui.widgets.pdf_preview_widget import PDFPreviewWidget


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test PDF Preview")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Widget de previsualización
        self.preview_widget = PDFPreviewWidget()
        layout.addWidget(self.preview_widget)
        
        # Botón para cargar PDF
        load_button = QPushButton("Cargar PDF")
        load_button.clicked.connect(self.load_pdf)
        layout.addWidget(load_button)
        
    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar PDF", 
            "", 
            "PDF Files (*.pdf)"
        )
        if file_path:
            self.preview_widget.load_pdf(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())