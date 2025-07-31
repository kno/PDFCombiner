# 🚀 PDF Combiner Pro - Releases y Ejecutables

## Resumen

He configurado tu proyecto para crear automáticamente versiones ejecutables para **macOS** y **Windows** usando **GitHub Actions**. Aquí te explico todo lo que se ha agregado y cómo usarlo.

## 📁 Archivos Agregados

### 1. GitHub Actions Workflow
- **`.github/workflows/build-release.yml`** - Workflow que construye ejecutables automáticamente

### 2. Scripts de Construcción Local
- **`build.sh`** - Script para macOS/Linux
- **`build.ps1`** - Script para Windows PowerShell
- **`test_build.py`** - Script de verificación de dependencias

### 3. Configuración de PyInstaller
- **`PDFCombinerPro.spec`** - Configuración detallada para PyInstaller
- **`assets/`** - Directorio para iconos (placeholder incluido)

### 4. Documentación
- **`BUILD_GUIDE.md`** - Guía completa de construcción
- **`.gitignore`** - Actualizado para ignorar archivos de build
- **`requirements.txt`** - Actualizado con PyInstaller

## 🎯 Cómo Crear un Release

### Opción 1: Release Automático (Recomendado)

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

3. **¡Listo!** GitHub Actions automáticamente:
   - ✅ Construye ejecutables para macOS y Windows
   - ✅ Crea un release público
   - ✅ Sube los archivos ejecutables
   - ✅ Genera notas de release automáticas

### Opción 2: Ejecutar Manualmente

1. Ve a tu repositorio en GitHub
2. **Actions** → **Build and Release PDF Combiner Pro**
3. **Run workflow** → **Run workflow**
4. Los ejecutables se crearán como artifacts para descargar

## 🛠️ Construcción Local (Para Pruebas)

### Verificar que Todo Funciona
```bash
# Activar entorno virtual
source pdf_combiner/bin/activate

# Probar dependencias
python test_build.py
```

### Construir Ejecutable Local

#### macOS/Linux:
```bash
source pdf_combiner/bin/activate
./build.sh
```

#### Windows:
```powershell
pdf_combiner\Scripts\activate
.\build.ps1
```

## 📦 Archivos Generados

### Usuarios Recibirán:
- **`PDFCombinerPro-macOS.zip`** - App bundle para macOS
- **`PDFCombinerPro-Windows.exe`** - Ejecutable para Windows

### Tamaños Aproximados:
- macOS: ~60-80MB comprimido
- Windows: ~40-60MB

## 🎨 Personalización

### Agregar Iconos Personalizados

1. **Crear iconos**:
   - macOS: `assets/icon.icns` (1024x1024)
   - Windows: `assets/icon.ico` (256x256)

2. **Los ejecutables usarán automáticamente** estos iconos

### Modificar Configuración de Build

Edita `PDFCombinerPro.spec` para:
- Cambiar nombre del ejecutable
- Agregar archivos adicionales
- Incluir librerías específicas
- Optimizar tamaño

## 🔧 Configuración del Repositorio

### Variables de Entorno (GitHub)
No necesitas configurar nada especial. El workflow usa:
- `GITHUB_TOKEN` (automático)
- Secrets del repositorio (si usas firmado de código)

### Permisos Necesarios
El workflow necesita permisos para:
- ✅ Leer código fuente
- ✅ Crear releases
- ✅ Subir assets

## 📋 Lista de Verificación

### Antes del Primer Release

- [ ] **Probar localmente**: `python test_build.py`
- [ ] **Verificar iconos**: Colocar archivos en `assets/` (opcional)
- [ ] **Actualizar README**: Agregar instrucciones de descarga
- [ ] **Probar build local**: `./build.sh` o `.\build.ps1`

### Para Cada Release

- [ ] **Actualizar versión** en archivos relevantes
- [ ] **Probar funcionalidad** completa
- [ ] **Crear tag**: `git tag v1.0.0`
- [ ] **Push tag**: `git push origin v1.0.0`
- [ ] **Verificar release** en GitHub

## 🚨 Solución de Problemas

### El Workflow Falla

1. **Revisa logs** en GitHub Actions
2. **Verifica que** `requirements.txt` esté actualizado
3. **Prueba localmente** primero

### Ejecutable No Funciona

1. **Ejecuta** `python test_build.py`
2. **Revisa** archivos faltantes en `.spec`
3. **Agrega** imports ocultos si es necesario

### Tamaño Muy Grande

1. **Edita** `PDFCombinerPro.spec`
2. **Agrega** módulos a `excludes`
3. **Activa** compresión UPX

## 🎉 ¡Estás Listo!

Tu proyecto ahora puede:

✅ **Crear ejecutables automáticamente** con cada release
✅ **Funcionar en macOS y Windows** sin Python instalado
✅ **Distribuirse fácilmente** a través de GitHub Releases
✅ **Ser probado localmente** antes de publicar

### Próximo Paso

Ejecuta esto para crear tu primer release:

```bash
git add .
git commit -m "Agregar sistema de builds automáticos"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

¡En unos minutos tendrás ejecutables listos para descargar! 🚀
