"""
Servicio de combinación de PDFs
"""
from typing import List
from utils.text_processor import TextProcessor

# Mantener compatibilidad con pdf_utils.py existente
try:
    from pdf_utils import AdvancedPDFCombiner
except ImportError:
    # Fallback en caso de que no se pueda importar
    AdvancedPDFCombiner = None

class PDFCombinerError(Exception):
    """Excepción para errores de combinación de PDFs"""
    pass

class PDFCombinerService:
    """Servicio para combinar archivos PDF"""

    def __init__(self):
        if AdvancedPDFCombiner is None:
            raise PDFCombinerError("No se pudo cargar el combinador de PDFs")

    def combine(self, files: List[str], output_path: str, create_index: bool = True) -> str:
        """
        Combinar archivos PDF

        Args:
            files: Lista de archivos PDF a combinar
            output_path: Ruta del archivo de salida
            create_index: Si crear índice interactivo

        Returns:
            Ruta del archivo creado

        Raises:
            PDFCombinerError: Si hay error en la combinación
        """
        if not files:
            raise PDFCombinerError("No hay archivos para combinar")

        try:
            # Generar títulos automáticamente
            titles = [TextProcessor.extract_title(f) for f in files]

            # Crear combinador
            combiner = AdvancedPDFCombiner(files, titles)

            # Combinar con o sin índice
            if create_index:
                result_path = combiner.combine_with_index(output_path)
            else:
                result_path = combiner.combine_simple(output_path)

            return result_path

        except Exception as e:
            raise PDFCombinerError(f"Error al combinar PDFs: {e}")

    def validate_files(self, files: List[str]) -> List[str]:
        """
        Validar que los archivos existen y son PDFs válidos

        Returns:
            Lista de archivos que no son válidos
        """
        invalid_files = []

        for file in files:
            try:
                import os
                if not os.path.isfile(file):
                    invalid_files.append(f"{file}: Archivo no encontrado")
                elif not file.lower().endswith('.pdf'):
                    invalid_files.append(f"{file}: No es un archivo PDF")
            except Exception as e:
                invalid_files.append(f"{file}: Error al validar - {e}")

        return invalid_files
