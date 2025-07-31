"""
Gestión de archivos y operaciones de sistema
"""
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path

class FileManagerError(Exception):
    """Excepción personalizada para errores de gestión de archivos"""
    pass

class FileManager:
    """Gestor de archivos PDF"""

    @staticmethod
    def get_pdf_files(directory: str = ".") -> List[str]:
        """Obtener lista de archivos PDF en directorio"""
        try:
            files = [f for f in os.listdir(directory)
                    if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory, f))]
            return sorted(files)
        except OSError as e:
            raise FileManagerError(f"Error al acceder al directorio: {e}")

    @staticmethod
    def validate_output_path(path: str) -> bool:
        """Validar ruta de salida"""
        if not path:
            return False

        try:
            directory = os.path.dirname(path)
            filename = os.path.basename(path)

            # Verificar que el directorio existe o está vacío (directorio actual)
            directory_valid = os.path.isdir(directory) or directory == ""

            # Verificar que el nombre de archivo es válido
            filename_valid = filename and not any(char in filename for char in '<>:"/\\|?*')

            return directory_valid and filename_valid
        except Exception:
            return False

    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Verificar si un archivo existe"""
        return os.path.isfile(filepath)

    @staticmethod
    def get_file_size(filepath: str) -> Optional[int]:
        """Obtener tamaño de archivo en bytes"""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return None
