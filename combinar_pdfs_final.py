#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Combiner Pro - Interactive PDF merging tool
==============================================

Professional-grade PDF combination with advanced features:
- Interactive file selection with filtering
- Visual reordering with keyboard navigation
- Smart title extraction and correction
- Clickable index generation

Version: 3.0
"""

# Standard library
import os
import glob
import re
import sys
import termios
import tty
from io import BytesIO
from datetime import datetime, timedelta
from time import time

# Third-party libraries
import PyPDF2
import fitz
import inquirer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import blue, black
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth


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
# CORE UTILITIES
# ============================================================================

class FileUtils:
    """File system utilities for PDF operations."""

    @staticmethod
    def find_pdfs():
        """Find all PDF files in current directory."""
        return sorted(glob.glob("*.pdf"))

    @staticmethod
    def get_file_size_mb(filepath):
        """Get file size in MB."""
        try:
            return os.path.getsize(filepath) / (1024 * 1024)
        except OSError:
            return 0

    @staticmethod
    def get_modification_time(filepath):
        """Get file modification time."""
        try:
            return os.path.getmtime(filepath)
        except OSError:
            return 0


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
# FILTERING SYSTEM
# ============================================================================

class PDFFilter:
    """Advanced filtering system for PDF files."""

    def __init__(self, files):
        self.original_files = files
        self.current_files = files.copy()

    def filter_by_pattern(self, pattern):
        """Filter files by text pattern."""
        if not pattern:
            return self.current_files

        pattern_lower = pattern.lower()
        return [f for f in self.current_files if pattern_lower in f.lower()]

    def filter_by_date(self, days):
        """Filter files by modification date."""
        if days is None:
            return self.current_files

        cutoff = time() - (days * 24 * 60 * 60)
        return [f for f in self.current_files
                if FileUtils.get_modification_time(f) > cutoff]

    def filter_by_size(self, size_range):
        """Filter files by size range."""
        if not size_range:
            return self.current_files

        result = []
        for file in self.current_files:
            size_mb = FileUtils.get_file_size_mb(file)
            if size_range == 'small' and size_mb < 1:
                result.append(file)
            elif size_range == 'medium' and 1 <= size_mb <= 10:
                result.append(file)
            elif size_range == 'large' and size_mb > 10:
                result.append(file)
        return result

    def reset(self):
        """Reset to original file list."""
        self.current_files = self.original_files.copy()
        return self.current_files

    def apply_filters(self):
        """Interactive filter application."""
        while True:
            print(f"\n📊 Files: {len(self.current_files)}")
            print("🔍 Filter options:")
            print("  1. Text/name  2. Date  3. Size")
            print("  4. Reset      5. View  ⏎ Continue")

            choice = input("\nOption: ").strip()

            if choice == "":
                return self.current_files
            elif choice == "1":
                pattern = input("Search text: ").strip()
                if pattern:
                    filtered = self.filter_by_pattern(pattern)
                    if filtered:
                        self.current_files = filtered
                        print(f"✅ {len(filtered)} files found")
                    else:
                        print("❌ No matches")
            elif choice == "2":
                self._date_filter_menu()
            elif choice == "3":
                self._size_filter_menu()
            elif choice == "4":
                self.reset()
                print(f"🗑️ Reset: {len(self.current_files)} files")
            elif choice == "5":
                self._show_files()
            else:
                print("❌ Invalid option")

    def _date_filter_menu(self):
        """Date filtering submenu."""
        print("\n📅 Filter by date:")
        print("  1. Last 24h  2. Last week  3. Last month  4. All")

        choice = input("Date option: ").strip()
        date_map = {"1": 1, "2": 7, "3": 30, "4": None}

        if choice in date_map:
            filtered = self.filter_by_date(date_map[choice])
            if filtered:
                self.current_files = filtered
                print(f"✅ {len(filtered)} files from selected period")

    def _size_filter_menu(self):
        """Size filtering submenu."""
        print("\n📏 Filter by size:")
        print("  1. Small (<1MB)  2. Medium (1-10MB)  3. Large (>10MB)  4. All")

        choice = input("Size option: ").strip()
        size_map = {"1": "small", "2": "medium", "3": "large", "4": None}

        if choice in size_map and choice != "4":
            filtered = self.filter_by_size(size_map[choice])
            if filtered:
                self.current_files = filtered
                print(f"✅ {len(filtered)} {size_map[choice]} files")

    def _show_files(self):
        """Display current file list."""
        print(f"\n👁️ Current files ({len(self.current_files)}):")
        for i, file in enumerate(self.current_files, 1):
            size_mb = FileUtils.get_file_size_mb(file)
            print(f"  {i:2d}. {file} ({size_mb:.1f}MB)")


# ============================================================================
# INTERACTIVE REORDERING
# ============================================================================

class InteractiveReorder:
    """Advanced keyboard-driven reordering interface."""

    def __init__(self, files):
        self.files = files.copy()
        self.titles = [TextProcessor.extract_title(f) for f in files]
        self.selected_index = 0

    def reorder(self):
        """Main reordering interface."""
        print("\n🔄 Interactive Reordering")
        print("Use ↑↓ to navigate, j/k to move, ⏎ to confirm, q to cancel")

        while True:
            self._display()
            key = self._get_key()

            if key in ['\r', '\n']:  # Enter
                return self.files
            elif key == 'q':  # Quit
                return None
            elif key == '\x1b[A':  # Up arrow
                self.selected_index = max(0, self.selected_index - 1)
            elif key == '\x1b[B':  # Down arrow
                self.selected_index = min(len(self.files) - 1, self.selected_index + 1)
            elif key == 'k' and self.selected_index > 0:  # Move up
                self._swap(self.selected_index, self.selected_index - 1)
                self.selected_index -= 1
            elif key == 'j' and self.selected_index < len(self.files) - 1:  # Move down
                self._swap(self.selected_index, self.selected_index + 1)
                self.selected_index += 1

    def _display(self):
        """Display current file order."""
        self._clear_screen()
        print("🔄 INTERACTIVE REORDERING")
        print("=" * 50)
        print("📋 Current order:")
        print("-" * 20)

        for i, (file, title) in enumerate(zip(self.files, self.titles)):
            marker = "→ ◆" if i == self.selected_index else "  ○"
            print(f"{marker} {i+1:2d}. {title}")
            if i == self.selected_index:
                print(f"      📄 {os.path.basename(file)}")

        print(f"\n🎯 Position: {self.selected_index + 1}/{len(self.files)}")

    def _get_key(self):
        """Capture keyboard input including arrow keys."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if key == '\x1b':  # Escape sequence
                key += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def _clear_screen(self):
        """Clear terminal screen."""
        print('\033[2J\033[H', end='')

    def _swap(self, i, j):
        """Swap two items in both files and titles lists."""
        self.files[i], self.files[j] = self.files[j], self.files[i]
        self.titles[i], self.titles[j] = self.titles[j], self.titles[i]


# ============================================================================
# PDF GENERATION
# ============================================================================

class IndexGenerator:
    """Generate clickable PDF index."""

    @staticmethod
    def create_index(start_pages, titles):
        """Create index page with clickable links."""
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


class PDFCombiner:
    """Main PDF combination logic."""

    def __init__(self, files, titles):
        self.files = files
        self.titles = titles
        self.start_pages = []

    def combine(self):
        """Combine PDFs with index and bookmarks."""
        print("\n🚀 Combining PDFs...")

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
        output_file = "PDF_Combined_Interactive.pdf"
        with open(output_file, 'wb') as file:
            merger.write(file)

        # Add clickable links
        final_file = LinkProcessor.add_links(output_file, self.start_pages, self.titles)

        # Cleanup intermediate file
        os.remove(output_file)

        return final_file


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class PDFCombinerApp:
    """Main application controller."""

    def run(self):
        """Execute the complete PDF combination workflow."""
        print("🚀 PDF COMBINER PRO")
        print("=" * 50)

        # Step 1: File discovery and filtering
        files = FileUtils.find_pdfs()
        if not files:
            print("❌ No PDF files found")
            return

        filter_system = PDFFilter(files)
        filtered_files = filter_system.apply_filters()

        if not filtered_files:
            print("❌ No files selected")
            return

        # Step 2: File selection
        selected_files = self._select_files(filtered_files)
        if not selected_files:
            print("❌ No files selected")
            return

        # Step 3: Reordering
        reorder_system = InteractiveReorder(selected_files)
        ordered_files = reorder_system.reorder()
        if not ordered_files:
            print("❌ Operation cancelled")
            return

        # Step 4: Title editing
        titles = self._edit_titles(ordered_files)

        # Step 5: Combination
        combiner = PDFCombiner(ordered_files, titles)
        output_file = combiner.combine()

        # Final summary
        file_size = FileUtils.get_file_size_mb(output_file)
        print(f"✅ Success: {output_file} ({file_size:.1f}MB)")

    def _select_files(self, files):
        """Interactive file selection."""
        questions = [
            inquirer.Checkbox(
                'files',
                message="Select files to combine",
                choices=files,
                default=files[:3] if len(files) >= 3 else files
            )
        ]

        answers = inquirer.prompt(questions)
        return answers['files'] if answers else []

    def _edit_titles(self, files):
        """Interactive title editing."""
        titles = []
        for file in files:
            suggested = TextProcessor.extract_title(file)
            questions = [
                inquirer.Text(
                    'title',
                    message=f"Title for '{os.path.basename(file)}'",
                    default=suggested
                )
            ]
            answers = inquirer.prompt(questions)
            titles.append(answers['title'] if answers else suggested)
        return titles


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Application entry point."""
    try:
        app = PDFCombinerApp()
        app.run()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
