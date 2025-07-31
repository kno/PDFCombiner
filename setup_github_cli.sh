#!/bin/bash

# GitHub CLI Setup and Status Checker
# Script automático para configurar GitHub CLI y verificar el estado del workflow

set -e

echo "🚀 GitHub CLI Setup y Status Checker"
echo "===================================="

# Verificar si GitHub CLI está instalado
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI no encontrado"
    exit 1
fi

echo "✅ GitHub CLI instalado: $(gh --version | head -1)"

# Verificar autenticación
echo "🔐 Verificando autenticación..."
if gh auth status &> /dev/null; then
    echo "✅ GitHub CLI ya está autenticado"
    USER=$(gh api user --jq .login)
    echo "   Usuario: $USER"
else
    echo "🔑 Configurando autenticación de GitHub CLI..."
    echo "   Se abrirá el navegador para autenticar..."
    echo "   Si no se abre automáticamente, usa el código que aparece"
    
    # Intentar autenticación automática
    gh auth login --git-protocol https --hostname github.com --web
    
    if gh auth status &> /dev/null; then
        echo "✅ Autenticación exitosa"
        USER=$(gh api user --jq .login)
        echo "   Usuario autenticado: $USER"
    else
        echo "❌ Error en la autenticación"
        exit 1
    fi
fi

# Función para verificar el estado del workflow
check_workflow_status() {
    echo ""
    echo "📊 Estado del Workflow de GitHub Actions"
    echo "======================================="
    
    # Obtener los últimos workflow runs
    echo "🔍 Obteniendo últimos workflow runs..."
    
    RUNS=$(gh run list --workflow=build-release.yml --limit=3 --json=status,conclusion,createdAt,displayTitle,url,databaseId 2>/dev/null || echo "[]")
    
    if [ "$RUNS" = "[]" ]; then
        echo "⚠️  No se encontraron workflows con nombre 'build-release.yml'"
        echo "   Intentando buscar workflows genéricos..."
        RUNS=$(gh run list --limit=3 --json=status,conclusion,createdAt,displayTitle,url,databaseId 2>/dev/null || echo "[]")
    fi
    
    if [ "$RUNS" != "[]" ]; then
        echo "$RUNS" | jq -r '.[] | "
🔄 Run: \(.displayTitle // "Sin título")
   Estado: \(.status // "desconocido") 
   Resultado: \(.conclusion // "en progreso")
   Creado: \(.createdAt // "fecha desconocida")
   URL: \(.url // "sin URL")
   ID: \(.databaseId // "sin ID")
"'
    else
        echo "❌ No se pudieron obtener los workflow runs"
        echo "   Posibles causas:"
        echo "   - El repositorio no tiene workflows configurados"
        echo "   - No tienes permisos para ver los workflows"
        echo "   - El workflow aún no se ha ejecutado"
    fi
    
    # Verificar releases
    echo ""
    echo "🚀 Últimos Releases"
    echo "=================="
    
    RELEASES=$(gh release list --limit=3 --json=tagName,name,createdAt,url,assets 2>/dev/null || echo "[]")
    
    if [ "$RELEASES" != "[]" ]; then
        echo "$RELEASES" | jq -r '.[] | "
📦 Release: \(.name // .tagName)
   Tag: \(.tagName)
   Creado: \(.createdAt)
   URL: \(.url)
   Assets: \(.assets | length) archivos"'
        
        # Mostrar assets del último release
        LATEST_ASSETS=$(echo "$RELEASES" | jq -r '.[0].assets[]? | "   📎 \(.name) (\(.size / 1024 / 1024 | floor)MB)"')
        if [ ! -z "$LATEST_ASSETS" ]; then
            echo "   Assets del último release:"
            echo "$LATEST_ASSETS"
        fi
    else
        echo "⚠️  No se encontraron releases"
        echo "   El workflow aún no ha creado ningún release exitoso"
    fi
}

# Función para monitorear workflow en tiempo real
monitor_workflow() {
    echo ""
    echo "👀 Monitoreando workflow en tiempo real..."
    echo "========================================"
    
    # Buscar workflow runs en progreso
    RUNNING_RUNS=$(gh run list --workflow=build-release.yml --limit=1 --json=status,databaseId --jq '.[] | select(.status == "in_progress") | .databaseId' 2>/dev/null || echo "")
    
    if [ ! -z "$RUNNING_RUNS" ]; then
        echo "🔄 Encontrado workflow en progreso (ID: $RUNNING_RUNS)"
        echo "   Siguiendo progreso... (Ctrl+C para detener)"
        gh run watch $RUNNING_RUNS || echo "   ⚠️  No se pudo seguir el workflow automáticamente"
    else
        echo "ℹ️  No hay workflows ejecutándose actualmente"
    fi
}

# Función para disparar workflow manualmente
trigger_workflow() {
    echo ""
    echo "🚀 Disparar Workflow Manualmente"
    echo "==============================="
    
    read -p "¿Quieres disparar el workflow manualmente? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Disparando workflow..."
        if gh workflow run build-release.yml; then
            echo "✅ Workflow disparado exitosamente"
            echo "   Espera unos segundos y ejecuta el script nuevamente para ver el progreso"
        else
            echo "❌ Error disparando workflow"
        fi
    fi
}

# Ejecutar verificaciones
check_workflow_status

# Preguntar si quiere monitorear
echo ""
read -p "¿Quieres monitorear workflows en tiempo real? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    monitor_workflow
fi

# Preguntar si quiere disparar workflow
trigger_workflow

echo ""
echo "✅ Script completado"
echo ""
echo "💡 Comandos útiles para usar después:"
echo "   gh run list                    # Ver todos los workflows"
echo "   gh run view --log             # Ver logs del último run"
echo "   gh release list               # Ver todos los releases"
echo "   gh workflow run build-release.yml  # Disparar workflow manualmente"
