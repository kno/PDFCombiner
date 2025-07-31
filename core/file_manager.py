"""
Gestión de archivos y operaciones de sistema
"""
import os
from typing import List, Dict, Tuple, Optional, NamedTuple
from pathlib import Path

class FileManagerError(Exception):
    """Excepción personalizada para errores de gestión de archivos"""
    pass

class DirectoryEntry(NamedTuple):
    """Entrada de directorio con tipo y nombre"""
    name: str
    path: str
    is_directory: bool
    display_name: str

class FileManager:
    """Gestor de archivos PDF con navegación de directorios"""

    def __init__(self, start_directory: str = "."):
        """Inicializar con directorio de inicio"""
        self.current_directory = os.path.abspath(start_directory)

    def get_current_directory(self) -> str:
        """Obtener directorio actual"""
        return self.current_directory

    def set_current_directory(self, directory: str) -> bool:
        """Cambiar directorio actual"""
        try:
            abs_path = os.path.abspath(directory)
            if os.path.isdir(abs_path):
                self.current_directory = abs_path
                return True
            return False
        except Exception:
            return False

    def can_go_up(self) -> bool:
        """Verificar si se puede subir al directorio padre"""
        parent = os.path.dirname(self.current_directory)
        return parent != self.current_directory  # No estamos en la raíz

    def go_up(self) -> bool:
        """Subir al directorio padre"""
        if self.can_go_up():
            parent = os.path.dirname(self.current_directory)
            return self.set_current_directory(parent)
        return False

    def get_directory_entries(self) -> List[DirectoryEntry]:
        """Obtener entradas del directorio actual (directorios + PDFs)"""
        entries = []

        try:
            # Agregar entrada para subir directorio (si no estamos en la raíz)
            if self.can_go_up():
                entries.append(DirectoryEntry(
                    name="..",
                    path=os.path.dirname(self.current_directory),
                    is_directory=True,
                    display_name="📁 .. (Directorio superior)"
                ))

            # Obtener contenido del directorio
            items = os.listdir(self.current_directory)

            # Separar directorios y archivos PDF
            directories = []
            pdf_files = []

            for item in items:
                item_path = os.path.join(self.current_directory, item)

                if os.path.isdir(item_path):
                    directories.append(DirectoryEntry(
                        name=item,
                        path=item_path,
                        is_directory=True,
                        display_name=f"📁 {item}"
                    ))
                elif item.lower().endswith('.pdf') and os.path.isfile(item_path):
                    # Usar TextProcessor para obtener título si está disponible
                    try:
                        from utils.text_processor import TextProcessor
                        title = TextProcessor.extract_title(item)
                        display_name = f"📄 {title}"
                    except ImportError:
                        display_name = f"📄 {os.path.splitext(item)[0]}"

                    pdf_files.append(DirectoryEntry(
                        name=item,
                        path=item_path,
                        is_directory=False,
                        display_name=display_name
                    ))

            # Ordenar directorios y archivos por separado
            directories.sort(key=lambda x: x.name.lower())
            pdf_files.sort(key=lambda x: x.display_name.lower())

            # Agregar directorios primero, luego PDFs
            entries.extend(directories)
            entries.extend(pdf_files)

        except OSError as e:
            raise FileManagerError(f"Error al acceder al directorio: {e}")

        return entries

    def get_pdf_files_in_current_dir(self) -> List[str]:
        """Obtener solo archivos PDF del directorio actual"""
        try:
            entries = self.get_directory_entries()
            return [entry.name for entry in entries if not entry.is_directory]
        except Exception as e:
            raise FileManagerError(f"Error al obtener archivos PDF: {e}")

    def get_relative_path(self, path: str) -> str:
        """Obtener ruta relativa desde el directorio actual"""
        try:
            return os.path.relpath(path, self.current_directory)
        except Exception:
            return path

    # Métodos estáticos originales mantenidos para compatibilidad
    @staticmethod
    def get_pdf_files(directory: str = ".") -> List[str]:
        """Obtener lista de archivos PDF en directorio ordenada alfabéticamente"""
        try:
            files = [f for f in os.listdir(directory)
                    if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory, f))]
            # Ordenamiento alfabético insensible a mayúsculas/minúsculas
            return sorted(files, key=lambda x: x.lower())
        except OSError as e:
            raise FileManagerError(f"Error al acceder al directorio: {e}")

    @staticmethod
    def get_pdf_files_sorted_by_title(directory: str = ".") -> List[str]:
        """Obtener lista de archivos PDF ordenada por títulos extraídos"""
        try:
            from utils.text_processor import TextProcessor

            files = [f for f in os.listdir(directory)
                    if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory, f))]

            # Ordenar por título extraído (insensible a mayúsculas/minúsculas)
            return sorted(files, key=lambda x: TextProcessor.extract_title(x).lower())
        except OSError as e:
            raise FileManagerError(f"Error al acceder al directorio: {e}")
        except ImportError as e:
            # Fallback a ordenamiento por nombre de archivo si no se puede importar TextProcessor
            return FileManager.get_pdf_files(directory)

    @staticmethod
    def get_pdf_files(directory: str = ".") -> List[str]:
        """Obtener lista de archivos PDF en directorio ordenada alfabéticamente"""
        try:
            files = [f for f in os.listdir(directory)
                    if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory, f))]
            # Ordenamiento alfabético insensible a mayúsculas/minúsculas
            return sorted(files, key=lambda x: x.lower())
        except OSError as e:
            raise FileManagerError(f"Error al acceder al directorio: {e}")

    @staticmethod
    def get_pdf_files_sorted_by_title(directory: str = ".") -> List[str]:
        """Obtener lista de archivos PDF ordenada por títulos extraídos"""
        try:
            from utils.text_processor import TextProcessor

            files = [f for f in os.listdir(directory)
                    if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory, f))]

            # Ordenar por título extraído (insensible a mayúsculas/minúsculas)
            return sorted(files, key=lambda x: TextProcessor.extract_title(x).lower())
        except OSError as e:
            raise FileManagerError(f"Error al acceder al directorio: {e}")
        except ImportError as e:
            # Fallback a ordenamiento por nombre de archivo si no se puede importar TextProcessor
            return FileManager.get_pdf_files(directory)

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
