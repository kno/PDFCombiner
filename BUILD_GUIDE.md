# PDF Combiner Pro - Guía de Construcción de Ejecutables

Este documento explica cómo crear versiones ejecutables de PDF Combiner Pro para diferentes sistemas operativos usando GitHub Actions y también cómo construir localmente.

## 🚀 Construcción Automática con GitHub Actions

### Configuración

El proyecto incluye un workflow de GitHub Actions (`.github/workflows/build-release.yml`) que automáticamente construye ejecutables para macOS y Windows cuando:

1. **Se crea un tag de versión** (ej: `v1.0.0`, `v2.1.3`)
2. **Se ejecuta manualmente** desde la interfaz de GitHub

### Crear un Release Automático

1. **Commitea todos los cambios**:
   ```bash
   git add .
   git commit -m "Preparar release v1.0.0"
   ```

2. **Crea y pushea un tag de versión**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **El workflow se ejecutará automáticamente** y:
   - Construirá ejecutables para macOS y Windows
   - Creará un release en GitHub
   - Subirá los archivos ejecutables como assets del release

### Ejecutar Manualmente

1. Ve a tu repositorio en GitHub
2. Navega a **Actions** → **Build and Release PDF Combiner Pro**
3. Haz clic en **Run workflow**
4. Los ejecutables se crearán como artifacts (no como release)

## 🛠️ Construcción Local

### macOS/Linux

```bash
# 1. Activar entorno virtual
source pdf_combiner/bin/activate

# 2. Ejecutar script de construcción
./build.sh
```

### Windows

```powershell
# 1. Activar entorno virtual
pdf_combiner\Scripts\activate

# 2. Ejecutar script de construcción
.\build.ps1
```

### Construcción Manual

Si prefieres ejecutar PyInstaller directamente:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable usando el archivo spec
pyinstaller PDFCombinerPro.spec
```

## 📁 Estructura de Archivos Generados

```
dist/
├── PDFCombinerPro.app/          # macOS (app bundle)
└── PDFCombinerPro.exe           # Windows

# Archivos finales para distribución:
PDFCombinerPro-macOS.zip         # macOS comprimido
PDFCombinerPro-Windows.exe       # Windows listo para usar
```

## 🎯 Requisitos del Sistema

### Para Desarrollo
- Python 3.8+
- PyInstaller
- Todas las dependencias de `requirements.txt`

### Para Usuarios Finales

#### macOS
- macOS 10.14 (Mojave) o superior
- 512MB RAM disponible
- 100MB espacio libre

#### Windows
- Windows 10 o superior
- 512MB RAM disponible
- 100MB espacio libre

## 🔧 Personalización

### Iconos Personalizados

1. **Crear iconos**:
   - macOS: archivo `.icns` (1024x1024 recomendado)
   - Windows: archivo `.ico` (256x256 recomendado)

2. **Colocar en `assets/`**:
   ```
   assets/
   ├── icon.icns    # macOS
   └── icon.ico     # Windows
   ```

### Modificar el Archivo Spec

Edita `PDFCombinerPro.spec` para:
- Agregar archivos adicionales
- Cambiar opciones de construcción
- Incluir librerías específicas

Ejemplo de modificaciones comunes:

```python
# Agregar archivos de datos
datas = [
    ('mi_archivo.txt', '.'),
    ('carpeta_completa', 'carpeta_destino'),
]

# Agregar imports ocultos
hiddenimports = [
    'mi_modulo_especial',
]

# Cambiar nombre del ejecutable
name='MiAplicacion'
```

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError" en el ejecutable

**Solución**: Agregar el módulo a `hiddenimports` en el archivo spec:

```python
hiddenimports = [
    'mi_modulo_faltante',
]
```

### Error: "No such file or directory" para archivos de datos

**Solución**: Agregar archivos a `datas` en el archivo spec:

```python
datas = [
    ('archivo_faltante.txt', '.'),
]
```

### Ejecutable muy grande

**Soluciones**:
1. Usar `--exclude-module` para módulos innecesarios
2. Activar UPX compression: `upx=True`
3. Eliminar archivos de debug: `debug=False`

### Error en macOS: "App is damaged"

**Solución**: Firmar la aplicación o permitir apps de desarrolladores no identificados:

```bash
# Para usuarios finales
sudo spctl --master-disable

# Para desarrolladores (requiere Apple Developer account)
codesign --force --deep --sign "Developer ID" PDFCombinerPro.app
```

## 📊 Optimización del Tamaño

### Técnicas para Reducir el Tamaño

1. **Excluir módulos innecesarios**:
   ```python
   excludes = ['tkinter', 'matplotlib', 'numpy']
   ```

2. **Usar imports específicos**:
   ```python
   # En lugar de: import PyQt6
   # Usar: from PyQt6.QtWidgets import QApplication
   ```

3. **Comprimir con UPX**:
   ```python
   upx=True,
   upx_exclude=[],
   ```

### Tamaños Típicos

- **Sin optimizar**: 80-150MB
- **Optimizado**: 40-80MB
- **Altamente optimizado**: 20-40MB

## 🚀 Distribución

### GitHub Releases (Automático)

Los releases se crean automáticamente con:
- Changelog generado
- Assets para descarga
- Instrucciones de instalación

### Distribución Manual

1. **Subir a cloud storage** (Google Drive, Dropbox)
2. **Crear instalador** (NSIS para Windows, DMG para macOS)
3. **Distribuir via web** o email

## 🔐 Seguridad

### Firmado de Código

#### macOS
```bash
# Requiere Apple Developer Certificate
codesign --force --deep --sign "Developer ID Application: Tu Nombre" PDFCombinerPro.app
```

#### Windows
```bash
# Requiere Code Signing Certificate
signtool sign /f certificate.p12 /p password PDFCombinerPro.exe
```

### Verificación de Integridad

Genera checksums para verificación:

```bash
# SHA256
shasum -a 256 PDFCombinerPro-*.* > checksums.txt

# En Windows
certutil -hashfile PDFCombinerPro-Windows.exe SHA256
```

---

## 📞 Soporte

Si tienes problemas con la construcción de ejecutables:

1. Revisa los logs de GitHub Actions
2. Ejecuta la construcción local primero
3. Verifica que todas las dependencias estén instaladas
4. Consulta la documentación de PyInstaller

Para más información, consulta:
- [Documentación de PyInstaller](https://pyinstaller.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
