#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Utils - Common utilities for PDF processing
===============================================

Shared utilities for PDF manipulation, index generation, and link processing.
"""

import os
import re
from io import BytesIO

# Importaciones básicas siempre disponibles
import PyPDF2

# Importaciones opcionales que se cargan cuando se necesitan
def _get_fitz():
    """Lazy import of fitz to avoid startup issues."""
    import fitz
    return fitz

def _get_reportlab():
    """Lazy import of reportlab components."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import blue, black
    from reportlab.lib import colors
    from reportlab.pdfbase.pdfmetrics import stringWidth
    return canvas, letter, blue, black, colors, stringWidth


# ============================================================================
# CONFIGURATION
# ============================================================================

UUID_PATTERN = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}_(.+)$'

ACCENT_CORRECTIONS = {
    'da': 'día', 'ano': 'año', 'nino': 'niño', 'nina': 'niña',
    'manana': 'mañana', 'espanol': 'español', 'informacion': 'información',
    'evaluacion': 'evaluación', 'presentacion': 'presentación',
    'documentacion': 'documentación'
}


# ============================================================================
# TEXT PROCESSING
# ============================================================================

class TextProcessor:
    """Text processing utilities."""

    @staticmethod
    def clean_and_capitalize(text):
        """Clean text and apply smart capitalization with accent correction."""
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
    def extract_title(filename):
        """Extract readable title from filename."""
        name = os.path.splitext(filename)[0]

        # Check for UUID pattern
        match = re.search(UUID_PATTERN, name, re.UNICODE)
        if match:
            title = match.group(1).replace('_', ' ')
        else:
            title = name.replace('_', ' ').replace('-', ' ')

        return TextProcessor.clean_and_capitalize(title)


# ============================================================================
# PDF UTILITIES
# ============================================================================

class PDFUtils:
    """PDF-specific utilities."""

    @staticmethod
    def get_page_count(filepath):
        """Get number of pages in PDF."""
        try:
            with open(filepath, 'rb') as file:
                return len(PyPDF2.PdfReader(file).pages)
        except Exception:
            return 0


# ============================================================================
# INDEX GENERATION
# ============================================================================

class IndexGenerator:
    """Generate clickable PDF index."""

    @staticmethod
    def create_index(start_pages, titles):
        """Create index page with clickable links."""
        canvas, letter, blue, black, colors, stringWidth = _get_reportlab()
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header
        c.setFont("Helvetica-Bold", 20)
        title = "📋 INTERACTIVE INDEX"
        c.drawString((width - c.stringWidth(title, "Helvetica-Bold", 20)) / 2,
                    height - 70, title)

        # Instructions
        c.setFont("Helvetica", 11)
        instruction = "Click any title to jump to that section"
        c.setFillColor(colors.darkblue)
        c.drawString((width - c.stringWidth(instruction, "Helvetica", 11)) / 2,
                    height - 95, instruction)

        # Index entries
        c.setFont("Helvetica", 13)
        y_pos = height - 140

        for i, (title, start_page) in enumerate(zip(titles, start_pages)):
            # Section number
            c.setFillColor(colors.darkblue)
            c.drawString(50, y_pos, f"{i+1:2d}.")

            # Title (clickable)
            c.setFillColor(blue)
            c.drawString(120, y_pos, title)

            # Page number
            c.setFillColor(black)
            c.drawString(width - 80, y_pos, f"p.{start_page}")

            y_pos -= 25

        c.save()
        buffer.seek(0)
        return buffer


class LinkProcessor:
    """Add clickable links to PDF index."""

    @staticmethod
    def add_links(pdf_file, start_pages, titles):
        """Add clickable links to index page."""
        fitz = _get_fitz()
        canvas, letter, blue, black, colors, stringWidth = _get_reportlab()
        
        doc = fitz.open(pdf_file)
        page = doc[0]
        page_height = page.rect.height

        # Index positioning constants
        y_start = page_height - 140
        y_step = 25
        x_start = 120

        for i, (title, start_page) in enumerate(zip(titles, start_pages)):
            text_width = stringWidth(title, 'Helvetica', 13)
            y_pos = y_start - (i * y_step)

            # Convert canvas coordinates to PDF coordinates
            y_bottom = page_height - y_pos - 15
            y_top = page_height - y_pos + 2

            rect = fitz.Rect(x_start, y_bottom, x_start + text_width, y_top)
            page.insert_link({
                "kind": fitz.LINK_GOTO,
                "from": rect,
                "page": start_page - 1
            })

        # Save with links
        output_file = pdf_file.replace('.pdf', '_LINKED.pdf')
        doc.save(output_file)
        doc.close()
        return output_file


# ============================================================================
# ADVANCED PDF COMBINER
# ============================================================================

class AdvancedPDFCombiner:
    """Advanced PDF combination with index and bookmarks."""

    def __init__(self, files, titles=None):
        self.files = files
        self.titles = titles or [TextProcessor.extract_title(f) for f in files]
        self.start_pages = []

    def combine_with_index(self, output_path):
        """Combine PDFs with interactive index and bookmarks."""
        # Calculate page positions
        current_page = 2  # After index
        self.start_pages = []

        for pdf_file in self.files:
            self.start_pages.append(current_page)
            current_page += PDFUtils.get_page_count(pdf_file)

        # Create index
        index_buffer = IndexGenerator.create_index(self.start_pages, self.titles)

        # Merge PDFs
        merger = PyPDF2.PdfWriter()

        # Add index
        index_reader = PyPDF2.PdfReader(index_buffer)
        merger.add_page(index_reader.pages[0])
        merger.add_outline_item("📋 INDEX", 0)

        # Add content bookmark
        content_bookmark = merger.add_outline_item("📚 CONTENT", 1)

        # Add PDFs with bookmarks
        page_index = 1
        for i, (pdf_file, title) in enumerate(zip(self.files, self.titles)):
            with open(pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                merger.add_outline_item(f"📄 {i+1}: {title}", page_index, content_bookmark)

                for page in reader.pages:
                    merger.add_page(page)
                    page_index += 1

        # Save combined PDF
        temp_file = output_path.replace('.pdf', '_temp.pdf')
        with open(temp_file, 'wb') as file:
            merger.write(file)

        # Add clickable links
        final_file = LinkProcessor.add_links(temp_file, self.start_pages, self.titles)

        # Move final file to desired location
        if final_file != output_path:
            os.rename(final_file, output_path)

        # Cleanup temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return output_path

    def combine_simple(self, output_path):
        """Simple PDF combination without index."""
        merger = PyPDF2.PdfWriter()
        
        for pdf_file in self.files:
            with open(pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    merger.add_page(page)

        with open(output_path, 'wb') as file:
            merger.write(file)

        return output_path
