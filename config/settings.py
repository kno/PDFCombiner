"""
Configuration settings for PDF Combiner Pro
"""

class AppConfig:
    """Configuración principal de la aplicación"""
    WINDOW_TITLE = "PDF Combiner Pro"
    WINDOW_SIZE = (900, 500)
    WINDOW_MIN_SIZE = (800, 400)
    SUPPORTED_EXTENSIONS = ['.pdf']
    MAX_FILES = 100

    # Configuración de UI
    FRAME_MIN_WIDTH = 280
    CENTER_FRAME_WIDTH = 180

    # Colores para marcado
    MARK_COLOR_RGBA = (76, 175, 80, 180)  # Verde semitransparente
    MARK_TEXT_COLOR = (0, 0, 0)  # Negro

    # Configuración de archivos
    DEFAULT_OUTPUT_NAME = "PDF_Combinado.pdf"
