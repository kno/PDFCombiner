"""
Text processing utilities for PDF Combiner Pro
"""
import os
import re
from typing import Dict

# Constantes
UUID_PATTERN = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}_(.+)$'

ACCENT_CORRECTIONS = {
    'da': 'día', 'ano': 'año', 'nino': 'niño', 'nina': 'niña',
    'manana': 'mañana', 'espanol': 'español', 'informacion': 'información',
    'evaluacion': 'evaluación', 'presentacion': 'presentación',
    'documentacion': 'documentación'
}

class TextProcessor:
    """Procesador de texto para nombres de archivos PDF"""

    @staticmethod
    def clean_and_capitalize(text: str) -> str:
        """Limpiar texto y aplicar capitalización inteligente con corrección de acentos"""
        words = []
        for word in text.split():
            if word:
                word_lower = word.lower()
                if word_lower in ACCENT_CORRECTIONS:
                    corrected = ACCENT_CORRECTIONS[word_lower]
                    words.append(corrected.capitalize())
                else:
                    words.append(word.capitalize())
        return ' '.join(words)

    @staticmethod
    def extract_title(filename: str) -> str:
        """Extraer título legible del nombre de archivo"""
        name = os.path.splitext(filename)[0]

        # Verificar patrón UUID
        match = re.search(UUID_PATTERN, name, re.UNICODE)
        if match:
            title = match.group(1).replace('_', ' ')
        else:
            title = name.replace('_', ' ').replace('-', ' ')

        return TextProcessor.clean_and_capitalize(title)
