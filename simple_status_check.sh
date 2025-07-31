#!/bin/bash

# Simple GitHub Workflow Status Checker
echo "🔍 Verificando estado del workflow..."

# Intentar obtener el estado básico
echo "Ejecutando: gh run list --limit=2"
gh run list --limit=2 2>/dev/null | head -10 || {
    echo "❌ Error al obtener workflows"
    echo "Verificando conexión y autenticación..."
    gh auth status || echo "Problema de autenticación"
    exit 1
}

echo ""
echo "✅ GitHub CLI funcionando correctamente"
echo ""
echo "💡 Puedes ver el progreso del workflow en:"
echo "   https://github.com/kno/PDFCombiner/actions"
echo ""
echo "🔄 Para ver workflows en tiempo real:"
echo "   gh run list --workflow=build-release.yml"
echo ""
echo "📊 Para ver releases:"
echo "   gh release list"
