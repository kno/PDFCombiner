# PDF Combiner Pro - Build Script for Windows
# Este script construye ejecutables localmente en Windows

param(
    [switch]$Clean = $false
)

Write-Host "🚀 PDF Combiner Pro - Build Script para Windows" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "❌ Error: No se detectó un entorno virtual activo" -ForegroundColor Red
    Write-Host "Por favor ejecuta: pdf_combiner\Scripts\activate" -ForegroundColor Yellow
    exit 1
}

# Check if PyInstaller is installed
try {
    pyinstaller --version | Out-Null
} catch {
    Write-Host "📦 Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Create assets directory and placeholder icons if they don't exist
if (-not (Test-Path "assets")) {
    New-Item -ItemType Directory -Path "assets" | Out-Null
}

if (-not (Test-Path "assets\icon.ico")) {
    Write-Host "⚠️  No se encontró icon.ico, creando placeholder..." -ForegroundColor Yellow
    "placeholder" | Out-File -FilePath "assets\icon.ico" -Encoding utf8
}

if (-not (Test-Path "assets\icon.icns")) {
    Write-Host "⚠️  No se encontró icon.icns, creando placeholder..." -ForegroundColor Yellow
    "placeholder" | Out-File -FilePath "assets\icon.icns" -Encoding utf8
}

# Clean previous builds if requested or they exist
if ($Clean -or (Test-Path "build") -or (Test-Path "dist")) {
    Write-Host "🧹 Limpiando builds anteriores..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    Get-ChildItem -Path "." -Filter "PDFCombinerPro-*" | Remove-Item -Force
}

# Build using spec file
Write-Host "🔨 Construyendo ejecutable..." -ForegroundColor Yellow
try {
    pyinstaller PDFCombinerPro.spec
} catch {
    Write-Host "❌ Error durante la construcción: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check build results
Write-Host "🪟 Preparando ejecutable para Windows..." -ForegroundColor Yellow

if (Test-Path "dist\PDFCombinerPro.exe") {
    Write-Host "✅ Ejecutable creado exitosamente" -ForegroundColor Green
    Copy-Item "dist\PDFCombinerPro.exe" "PDFCombinerPro-Windows.exe"
    
    $fileSize = (Get-Item "PDFCombinerPro-Windows.exe").Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    
    Write-Host "📦 Archivo creado: PDFCombinerPro-Windows.exe" -ForegroundColor Green
    Write-Host "   Tamaño: $fileSizeMB MB" -ForegroundColor Cyan
} else {
    Write-Host "❌ Error: No se pudo crear el ejecutable" -ForegroundColor Red
    Write-Host "Contenido del directorio dist:" -ForegroundColor Yellow
    Get-ChildItem -Path "dist" -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""
Write-Host "✅ Build completado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Archivos generados:" -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "PDFCombinerPro-*" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "   $($_.Name) ($size MB)" -ForegroundColor White
}
Write-Host ""
Write-Host "🧪 Para probar el ejecutable:" -ForegroundColor Yellow
Write-Host "   1. Ejecuta directamente: .\PDFCombinerPro-Windows.exe" -ForegroundColor White
Write-Host ""
Write-Host "💡 Nota: Si el ejecutable no funciona, revisa las dependencias en requirements.txt" -ForegroundColor Blue
