

<img src="assets/anthropic_logo.svg" alt="Claude Sonnet" width="40" style="vertical-align:middle; margin-right:8px;"/> <img src="assets/chatgpt_logo.svg" alt="GPT" width="40" style="vertical-align:middle; margin-right:8px;"/>

> **Disclaimer:** Esta aplicación ha sido construida con la ayuda de Vibe Coding, utilizando modelos de IA avanzados como Claude Sonnet (Anthropic) y GPT (OpenAI).

---

# PDF Combiner Pro

* [Versión en Inglés](README.md)

**PDF Combiner Pro** es una herramienta profesional para combinar y fusionar archivos PDF con características avanzadas como generación automática de índices interactivos, extracción inteligente de títulos y una interfaz gráfica moderna.

## 🚀 Características Principales

- **Interfaz Gráfica Moderna**: Diseño con tema oscuro y controles intuitivos
- **Soporte Multiidioma**: Interface disponible en Español e Inglés
- **Combinación Inteligente**: Fusiona múltiples PDFs manteniendo la calidad original
- **Índice Interactivo**: Genera automáticamente un índice con enlaces clickeables
- **Explorador de Archivos Integrado**: Navega y selecciona archivos fácilmente
- **Drag & Drop**: Arrastra y suelta archivos directamente en la aplicación
- **Extracción de Títulos**: Reconoce automáticamente títulos desde nombres de archivos
- **Corrección de Acentos**: Corrige automáticamente caracteres especiales
- **Reordenamiento Visual**: Organiza los archivos mediante una interfaz visual
- **Modo Línea de Comandos**: También funciona desde terminal para uso avanzado

## 📋 Requisitos del Sistema

- **Python 3.8 o superior**
- **macOS, Windows o Linux**
- **512MB de RAM disponible** (para archivos PDF típicos)
- **50MB de espacio libre en disco**

## 🛠️ Instalación

### 1. Clonar o Descargar el Proyecto

```bash
# Si tienes git instalado
git clone https://github.com/kno/PDFCombiner.git
cd PDFCombiner

# O simplemente descarga y descomprime el archivo ZIP desde:
# https://github.com/kno/PDFCombiner/archive/main.zip
```

### 2. Crear el Entorno Virtual

```bash
# Navegar a la carpeta del proyecto
cd PDFCombiner

# Crear entorno virtual
python3 -m venv pdf_combiner

# Activar entorno virtual
# En macOS/Linux:
source pdf_combiner/bin/activate

# En Windows:
# pdf_combiner\Scripts\activate
```

### 3. Instalar Dependencias

```bash
# Actualizar pip a la última versión
pip install --upgrade pip

# Instalar todas las dependencias necesarias
pip install -r requirements.txt
```

### 4. Verificar la Instalación

```bash
# Probar que todo funciona correctamente
python main.py
```

## 🎯 Uso del Programa

### 🌍 Selección de Idioma

La aplicación soporta múltiples idiomas y se adapta automáticamente según la configuración de tu sistema:

**Idiomas disponibles:**
- 🇪🇸 **Español** (por defecto)
- 🇺🇸 **English**

**Para cambiar el idioma manualmente:**

```bash
# Ejecutar en Español
LANG=es_ES.UTF-8 python main.py

# Ejecutar en Inglés
LANG=en_US.UTF-8 python main.py
```

**Script de prueba incluido:**
```bash
# Probar todos los idiomas automáticamente
python test_languages.py
```

### Interfaz Gráfica (Recomendado)

1. **Ejecutar la aplicación**:
   ```bash
   # Asegúrate de que el entorno virtual esté activado
   source pdf_combiner/bin/activate
   python main.py
   ```

2. **Usar la aplicación**:
   - **Explorador de archivos**: Navega por tus carpetas en el panel izquierdo
   - **Drag & Drop**: Arrastra archivos PDF al panel derecho
   - **Reordenar**: Usa los botones ↑ ↓ o arrastra elementos para reordenar
   - **Combinar**: Haz clic en "Combinar PDFs" y elige dónde guardar el resultado

3. **Opciones avanzadas**:
   - ✅ **Crear índice interactivo**: Genera enlaces clickeables en la primera página
   - **Nombre de salida personalizado**: Especifica el nombre del archivo resultado

### Línea de Comandos (Avanzado)

```bash
# Ejecutar versión de línea de comandos
python combinar_pdfs.py

# O usar la versión con GUI básica
python combinar_pdfs_gui.py
```

## 📁 Estructura del Proyecto

```
combinar_pdfs/
├── main.py                 # Punto de entrada principal (GUI moderna)
├── combinar_pdfs.py        # Versión línea de comandos
├── combinar_pdfs_gui.py    # GUI básica alternativa
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Este archivo
├── config/                # Configuración de la aplicación
│   ├── settings.py
│   └── __init__.py
├── core/                  # Lógica principal del programa
│   ├── file_manager.py    # Gestión de archivos
│   ├── pdf_combiner.py    # Servicio de combinación
│   └── __init__.py
├── gui/                   # Interfaz gráfica
│   ├── main_window.py     # Ventana principal
│   ├── file_manager_widget.py  # Widget explorador
│   ├── widgets.py         # Widgets personalizados
│   ├── styles.py          # Estilos y temas
│   └── __init__.py
├── utils/                 # Utilidades
│   ├── text_processor.py  # Procesamiento de texto
│   └── __init__.py
├── pdf_utils.py          # Utilidades PDF legacy
└── pdfs/                 # Carpeta de ejemplo con PDFs
```

## ⚙️ Configuración Avanzada

### Variables de Configuración

Puedes modificar el archivo `config/settings.py` para personalizar:

- **Tema visual** (claro/oscuro)
- **Directorio por defecto**
- **Patrones de nombres de archivos**
- **Configuraciones de corrección de texto**

### Formatos Soportados

- **Entrada**: Archivos PDF (.pdf)
- **Salida**: PDF con índice interactivo y enlaces clickeables

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"

```bash
# Asegúrate de que el entorno virtual esté activado
source pdf_combiner/bin/activate

# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "PyQt6 no se instala correctamente"

```bash
# En macOS con Homebrew
brew install qt6

# Reinstalar PyQt6
pip uninstall PyQt6
pip install PyQt6
```

### Error: "Permission denied" en macOS

```bash
# Dar permisos de ejecución
chmod +x main.py
```

### Problema con Archivos Grandes

- **Para archivos >50MB**: El procesamiento puede ser más lento
- **Para múltiples archivos grandes**: Usa la versión de línea de comandos que es más eficiente
- **Si el proceso es lento**: Asegúrate de cerrar otras aplicaciones que consuman mucha memoria

## 🔧 Desarrollo

### Ejecutar en Modo Desarrollo

```bash
# Activar entorno virtual
source pdf_combiner/bin/activate

# Ejecutar con logs detallados
python main.py --debug
```

### Estructura de Dependencias

Las dependencias principales son:

- **PyQt6**: Interfaz gráfica moderna
- **PyPDF2**: Manipulación básica de PDFs
- **PyMuPDF (fitz)**: Procesamiento avanzado de PDFs
- **ReportLab**: Generación de PDFs con índices
- **Pillow**: Procesamiento de imágenes
- **Inquirer**: Interfaz de línea de comandos interactiva

## 📝 Ejemplos de Uso

### Caso 1: Combinar PDFs de un Curso

1. Abre la aplicación: `python main.py`
2. Navega a la carpeta con los PDFs del curso
3. Selecciona los archivos en orden (Día 1, Día 2, etc.)
4. Activa "Crear índice interactivo"
5. Combina y obtén un PDF con navegación

### Caso 2: Compilar Documentos de Trabajo

1. Arrastra múltiples documentos PDF al área de trabajo
2. Reordena según importancia usando los controles
3. Especifica un nombre descriptivo para el archivo final
4. Combina y obtén un documento único organizado

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa los logs**: La aplicación muestra errores detallados
2. **Verifica dependencias**: `pip list` para ver paquetes instalados
3. **Prueba versión línea de comandos**: Más estable para archivos grandes
4. **Reinicia entorno virtual**: Desactiva y activa de nuevo

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y personales.

---

**PDF Combiner Pro** - Herramienta profesional para combinar PDFs con estilo 🎨
