#!/usr/bin/env python3
"""
GitHub Actions Workflow Analyzer
Analiza el workflow de GitHub Actions para identificar problemas comunes
"""
import os
import yaml
import json

def check_workflow_file():
    """Analiza el archivo de workflow para problemas comunes"""
    print("🔍 Analizando workflow de GitHub Actions...")
    
    workflow_path = ".github/workflows/build-release.yml"
    if not os.path.exists(workflow_path):
        print("  ❌ Archivo de workflow no encontrado")
        return False
    
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Problemas comunes a verificar
        issues = []
        suggestions = []
        
        # 1. Verificar versiones de actions
        if 'actions/checkout@v4' in content:
            print("  ✅ Usando actions/checkout@v4")
        else:
            issues.append("Versión de checkout posiblemente obsoleta")
        
        if 'actions/setup-python@v4' in content:
            print("  ⚠️  setup-python@v4 podría ser obsoleto")
            suggestions.append("Considera actualizar a setup-python@v5")
        
        # 2. Verificar actions obsoletas
        if 'actions/create-release@v1' in content:
            issues.append("actions/create-release@v1 está DEPRECADO")
            suggestions.append("Usar gh CLI o actions/github-script en su lugar")
        
        if 'actions/upload-release-asset@v1' in content:
            issues.append("actions/upload-release-asset@v1 está DEPRECADO")
            suggestions.append("Usar gh CLI para subir assets")
        
        # 3. Verificar comandos específicos de shell
        if 'if [ "${{ matrix.os }}" == "macos-latest" ]; then' in content:
            issues.append("Sintaxis de shell podría fallar en Windows")
            suggestions.append("Usar steps condicionales en lugar de shell scripting")
        
        # 4. Verificar rutas de archivos
        if 'assets/icon.icns' in content and 'assets/icon.ico' in content:
            print("  ✅ Referencias a iconos encontradas")
        
        # Mostrar resultados
        if issues:
            print(f"\n❌ Problemas encontrados ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        
        if suggestions:
            print(f"\n💡 Sugerencias ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"  ❌ Error leyendo workflow: {e}")
        return False

def get_common_workflow_issues():
    """Retorna problemas comunes y sus soluciones"""
    return {
        "actions_deprecadas": {
            "problema": "Uso de GitHub Actions deprecadas",
            "solucion": "Actualizar a versiones modernas o usar gh CLI",
            "afecta": ["create-release@v1", "upload-release-asset@v1"]
        },
        "shell_multiplataforma": {
            "problema": "Scripts de shell que no funcionan en Windows",
            "solucion": "Usar steps separados con condicionales if:",
            "ejemplo": "if: matrix.os == 'macos-latest'"
        },
        "permisos_github": {
            "problema": "Falta permisos GITHUB_TOKEN",
            "solucion": "Agregar permissions: contents: write",
            "ubicacion": "En el job o a nivel de workflow"
        },
        "paths_artifacts": {
            "problema": "Rutas incorrectas para artifacts",
            "solucion": "Verificar que los archivos existen antes de subir",
            "comando": "ls -la antes de upload"
        }
    }

def create_fixed_workflow():
    """Crea una versión corregida del workflow"""
    print("\n🔧 Creando versión corregida del workflow...")
    
    fixed_workflow = """name: Build and Release PDF Combiner Pro

on:
  push:
    tags:
      - 'v*'  # Triggers on version tags like v1.0.0
  workflow_dispatch:  # Allows manual triggering

permissions:
  contents: write  # Needed for creating releases

jobs:
  build:
    name: Build ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: macos-latest
            artifact_name: PDFCombinerPro-macOS
            build_name: PDFCombinerPro
          - os: windows-latest
            artifact_name: PDFCombinerPro-Windows
            build_name: PDFCombinerPro.exe

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install system dependencies (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        brew install qt6

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Create placeholder icons (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        mkdir -p assets
        echo "placeholder" > assets/icon.icns

    - name: Create placeholder icons (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        mkdir -p assets
        echo "placeholder" > assets/icon.ico

    - name: Build executable
      run: |
        pyinstaller PDFCombinerPro.spec

    - name: Prepare macOS artifacts  
      if: matrix.os == 'macos-latest'
      run: |
        ls -la dist/
        if [ -d "dist/PDFCombinerPro.app" ]; then
          zip -r PDFCombinerPro-macOS.zip dist/PDFCombinerPro.app
          echo "macOS app bundle created successfully"
        else
          echo "Error: PDFCombinerPro.app not found"
          exit 1
        fi

    - name: Prepare Windows artifacts
      if: matrix.os == 'windows-latest'
      run: |
        dir dist\\
        if exist "dist\\PDFCombinerPro.exe" (
          copy "dist\\PDFCombinerPro.exe" "PDFCombinerPro-Windows.exe"
          echo "Windows executable prepared successfully"
        ) else (
          echo "Error: PDFCombinerPro.exe not found"
          exit 1
        )

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: ${{ matrix.artifact_name }}
        path: |
          ${{ matrix.os == 'macos-latest' && 'PDFCombinerPro-macOS.zip' || 'PDFCombinerPro-Windows.exe' }}

  release:
    name: Create Release
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    permissions:
      contents: write

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Download all artifacts
      uses: actions/download-artifact@v4

    - name: List downloaded artifacts
      run: |
        echo "Downloaded artifacts:"
        find . -name "*.zip" -o -name "*.exe" | head -10

    - name: Create Release using GitHub CLI
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        # Create release
        gh release create ${{ github.ref_name }} \\
          --title "PDF Combiner Pro ${{ github.ref_name }}" \\
          --notes "## PDF Combiner Pro ${{ github.ref_name }}

        ### 🚀 Descargas
        - **macOS**: Descarga PDFCombinerPro-macOS.zip, descomprime y ejecuta
        - **Windows**: Descarga PDFCombinerPro-Windows.exe y ejecuta directamente

        ### 📋 Características  
        - Interfaz gráfica moderna con tema oscuro
        - Combinación inteligente de PDFs
        - Generación automática de índices interactivos
        - Explorador de archivos integrado
        - Soporte para drag & drop
        - Extracción automática de títulos

        ### 💻 Requisitos del Sistema
        - **macOS**: macOS 10.14 o superior  
        - **Windows**: Windows 10 o superior
        - **RAM**: 512MB disponible
        - **Espacio**: 50MB libres" \\
          PDFCombinerPro-macOS/PDFCombinerPro-macOS.zip \\
          PDFCombinerPro-Windows/PDFCombinerPro-Windows.exe
"""
    
    with open(".github/workflows/build-release-fixed.yml", "w") as f:
        f.write(fixed_workflow)
    
    print("  ✅ Nueva versión guardada como: build-release-fixed.yml")
    print("  💡 Compara ambos archivos y reemplaza el original si está correcto")

def main():
    """Función principal"""
    print("🚀 GitHub Actions Workflow Analyzer")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Verificar workflow actual
    workflow_ok = check_workflow_file()
    
    # Mostrar problemas comunes 
    print("\n🔍 Problemas Comunes en GitHub Actions:")
    issues = get_common_workflow_issues()
    for name, info in issues.items():
        print(f"\n📌 {info['problema']}")
        print(f"   Solución: {info['solucion']}")
        if 'ejemplo' in info:
            print(f"   Ejemplo: {info['ejemplo']}")
    
    # Crear versión corregida
    create_fixed_workflow()
    
    print(f"\n📊 Estado del workflow: {'✅ OK' if workflow_ok else '❌ Necesita correcciones'}")
    
    if not workflow_ok:
        print("\n🔄 Pasos para corregir:")
        print("1. Revisa build-release-fixed.yml")
        print("2. Reemplaza el archivo original si está correcto:")
        print("   mv .github/workflows/build-release-fixed.yml .github/workflows/build-release.yml")
        print("3. Commit y push de los cambios")
        print("4. Crea un tag: git tag v1.0.0 && git push origin v1.0.0")

if __name__ == "__main__":
    main()
