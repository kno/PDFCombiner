
<img src="assets/anthropic_logo.svg" alt="Claude Sonnet" width="40" style="vertical-align:middle; margin-right:8px;"/> <img src="assets/chatgpt_logo.svg" alt="GPT" width="40" style="vertical-align:middle; margin-right:8px;"/>

> **Disclaimer:** This application has been built with the help of Vibe Coding, using advanced AI models like Claude Sonnet (Anthropic) and GPT (OpenAI).

---

# PDF Combiner Pro

* [Versión en Español](README_es.md)

**PDF Combiner Pro** is a professional tool for combining and merging PDF files with advanced features like automatic interactive index generation, intelligent title extraction, and a modern graphical interface.

## 🚀 Key Features

- **Modern Graphical Interface**: Dark theme design with intuitive controls
- **Multi-language Support**: Interface available in Spanish and English
- **Intelligent Combining**: Merges multiple PDFs while maintaining original quality
- **Interactive Index**: Automatically generates an index with clickable links
- **Integrated File Explorer**: Navigate and select files easily
- **PDF Preview**: Preview PDF files before combining them
- **Drag & Drop**: Drag and drop files directly into the application
- **Title Extraction**: Automatically recognizes titles from file names
- **Accent Correction**: Automatically corrects special characters
- **Visual Reordering**: Organize files through a visual interface
- **Command Line Mode**: Also works from terminal for advanced usage

## 📋 System Requirements

- **Python 3.8 or higher**
- **macOS, Windows or Linux**
- **512MB available RAM** (for typical PDF files)
- **50MB free disk space**

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
# If you have git installed
git clone https://github.com/kno/PDFCombiner.git
cd PDFCombiner

# Or simply download and extract the ZIP file from:
# https://github.com/kno/PDFCombiner/archive/main.zip
```

### 2. Create Virtual Environment

```bash
# Navigate to project folder
cd PDFCombiner

# Create virtual environment
python3 -m venv pdf_combiner

# Activate virtual environment
# On macOS/Linux:
source pdf_combiner/bin/activate

# On Windows:
# pdf_combiner\Scripts\activate
```

### 3. Install Dependencies

```bash
# Update pip to latest version
pip install --upgrade pip

# Install all necessary dependencies
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Test that everything works correctly
python main.py
```

## 🎯 How to Use

### 🌍 Language Selection

The application supports multiple languages and automatically adapts to your system configuration:

**Available languages:**
- 🇪🇸 **Spanish** (default)
- 🇺🇸 **English**

**To manually change language:**

```bash
# Run in Spanish
LANG=es_ES.UTF-8 python main.py

# Run in English
LANG=en_US.UTF-8 python main.py
```

**Included test script:**
```bash
# Test all languages automatically
python test_languages.py
```

### Graphical Interface (Recommended)

1. **Run the application**:
   ```bash
   # Make sure virtual environment is activated
   source pdf_combiner/bin/activate
   python main.py
   ```

2. **Use the application**:
   - **File explorer**: Navigate through your folders in the left panel
   - **Drag & Drop**: Drag PDF files to the right panel
   - **Reorder**: Use ↑ ↓ buttons or drag elements to reorder
   - **Combine**: Click "Combine PDFs" and choose where to save the result

3. **Advanced options**:
   - ✅ **Create interactive index**: Generates clickable links on the first page
   - **Custom output name**: Specify the name of the result file

### Command Line (Advanced)

```bash
# Run command line version
python combinar_pdfs.py

# Or use basic GUI version
python combinar_pdfs_gui.py
```

## 📁 Project Structure

```
combinar_pdfs/
├── main.py                 # Main entry point (modern GUI)
├── combinar_pdfs.py        # Command line version
├── combinar_pdfs_gui.py    # Alternative basic GUI
├── requirements.txt        # Project dependencies
├── README.md              # This file
├── README_es.md           # Spanish README
├── config/                # Application configuration
│   ├── settings.py
│   └── __init__.py
├── core/                  # Main program logic
│   ├── file_manager.py    # File management
│   ├── pdf_combiner.py    # Combination service
│   └── __init__.py
├── gui/                   # Graphical interface
│   ├── main_window.py     # Main window
│   ├── file_manager_widget.py  # Explorer widget
│   ├── widgets.py         # Custom widgets
│   ├── styles.py          # Styles and themes
│   └── __init__.py
├── utils/                 # Utilities
│   ├── text_processor.py  # Text processing
│   ├── localization.py    # Multi-language support
│   └── __init__.py
├── locale/                # Translation files
│   ├── en/LC_MESSAGES/    # English translations
│   ├── es/LC_MESSAGES/    # Spanish translations
│   └── messages.pot       # Translation template
├── pdf_utils.py          # Legacy PDF utilities
└── pdfs/                 # Example folder with PDFs
```

## ⚙️ Advanced Configuration

### Configuration Variables

You can modify the `config/settings.py` file to customize:

- **Visual theme** (light/dark)
- **Default directory**
- **File name patterns**
- **Text correction settings**

### Supported Formats

- **Input**: PDF files (.pdf)
- **Output**: PDF with interactive index and clickable links

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"

```bash
# Make sure virtual environment is activated
source pdf_combiner/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "PyQt6 doesn't install correctly"

```bash
# On macOS with Homebrew
brew install qt6

# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

### Error: "Permission denied" on macOS

```bash
# Give execution permissions
chmod +x main.py
```

### Large Files Issue

- **For files >50MB**: Processing may be slower
- **For multiple large files**: Use command line version which is more efficient
- **If process is slow**: Make sure to close other memory-consuming applications

## 🔧 Development

### Run in Development Mode

```bash
# Activate virtual environment
source pdf_combiner/bin/activate

# Run with detailed logs
python main.py --debug
```

### Dependencies Structure

Main dependencies are:

- **PyQt6**: Modern graphical interface
- **PyPDF2**: Basic PDF manipulation
- **PyMuPDF (fitz)**: Advanced PDF processing
- **ReportLab**: PDF generation with indexes
- **Pillow**: Image processing
- **Inquirer**: Interactive command line interface
- **Babel**: Internationalization support

## 📝 Usage Examples

### Case 1: Combine Course PDFs

1. Open the application: `python main.py`
2. Navigate to the folder with course PDFs
3. Select files in order (Day 1, Day 2, etc.)
4. Enable "Create interactive index"
5. Combine and get a PDF with navigation

### Case 2: Compile Work Documents

1. Drag multiple PDF documents to the work area
2. Reorder by importance using the controls
3. Specify a descriptive name for the final file
4. Combine and get a single organized document

## 🆘 Support

If you encounter problems:

1. **Check logs**: The application shows detailed errors
2. **Verify dependencies**: `pip list` to see installed packages
3. **Try command line version**: More stable for large files
4. **Restart virtual environment**: Deactivate and activate again

## 📄 License

This project is free to use for educational and personal purposes.

---

**PDF Combiner Pro** - Professional tool for combining PDFs with style 🎨
