#!/bin/bash

# PDF Combiner Pro - Build Script
# Este script construye ejecutables localmente para pruebas

set -e  # Exit on any error

echo "🚀 PDF Combiner Pro - Build Script"
echo "=================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Error: No se detectó un entorno virtual activo"
    echo "Por favor ejecuta: source pdf_combiner/bin/activate"
    exit 1
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip install pyinstaller
fi

# Create assets directory and placeholder icons if they don't exist
mkdir -p assets
if [[ ! -f "assets/icon.icns" ]]; then
    echo "⚠️  No se encontró icon.icns, creando placeholder..."
    echo "placeholder" > assets/icon.icns
fi

if [[ ! -f "assets/icon.ico" ]]; then
    echo "⚠️  No se encontró icon.ico, creando placeholder..."
    echo "placeholder" > assets/icon.ico
fi

# Clean previous builds
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.spec.bak
rm -f PDFCombinerPro-*.zip PDFCombinerPro-*.exe

# Build using spec file
echo "🔨 Construyendo ejecutable..."
pyinstaller PDFCombinerPro.spec

# Check build results
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🍎 Preparando bundle para macOS..."
    if [[ -d "dist/PDFCombinerPro.app" ]]; then
        echo "✅ App bundle creado exitosamente"
        zip -r PDFCombinerPro-macOS.zip dist/PDFCombinerPro.app
        echo "📦 Archivo creado: PDFCombinerPro-macOS.zip"
        echo "   Tamaño: $(du -h PDFCombinerPro-macOS.zip | cut -f1)"
    else
        echo "❌ Error: No se pudo crear el app bundle"
        ls -la dist/
        exit 1
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    echo "🪟 Preparando ejecutable para Windows..."
    if [[ -f "dist/PDFCombinerPro.exe" ]]; then
        echo "✅ Ejecutable creado exitosamente"
        cp dist/PDFCombinerPro.exe PDFCombinerPro-Windows.exe
        echo "📦 Archivo creado: PDFCombinerPro-Windows.exe"
        echo "   Tamaño: $(du -h PDFCombinerPro-Windows.exe | cut -f1)"
    else
        echo "❌ Error: No se pudo crear el ejecutable"
        ls -la dist/
        exit 1
    fi
else
    # Linux or other
    echo "🐧 Sistema detectado: $OSTYPE"
    if [[ -f "dist/PDFCombinerPro" ]]; then
        echo "✅ Ejecutable creado exitosamente"
        cp dist/PDFCombinerPro PDFCombinerPro-Linux
        echo "📦 Archivo creado: PDFCombinerPro-Linux"
        echo "   Tamaño: $(du -h PDFCombinerPro-Linux | cut -f1)"
    else
        echo "❌ Error: No se pudo crear el ejecutable"
        ls -la dist/
        exit 1
    fi
fi

echo ""
echo "✅ Build completado exitosamente!"
echo ""
echo "📁 Archivos generados:"
ls -la PDFCombinerPro-* 2>/dev/null || echo "   (No se encontraron archivos finales)"
echo ""
echo "🧪 Para probar el ejecutable:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   1. Descomprime: unzip PDFCombinerPro-macOS.zip"
    echo "   2. Ejecuta: open dist/PDFCombinerPro.app"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "   1. Ejecuta directamente: ./PDFCombinerPro-Windows.exe"
else
    echo "   1. Da permisos: chmod +x PDFCombinerPro-Linux"
    echo "   2. Ejecuta: ./PDFCombinerPro-Linux"
fi
echo ""
echo "💡 Nota: Si el ejecutable no funciona, revisa las dependencias en requirements.txt"
