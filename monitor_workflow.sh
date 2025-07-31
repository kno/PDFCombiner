#!/bin/bash

# Workflow Monitor
# Monitorea automáticamente el progreso del workflow hasta que termine

WORKFLOW_ID="16657340404"
CHECK_INTERVAL=30  # segundos entre verificaciones

echo "👀 Monitoreando workflow ID: $WORKFLOW_ID"
echo "🔄 Verificando cada $CHECK_INTERVAL segundos..."
echo "   Presiona Ctrl+C para detener el monitoreo"
echo ""

# Función para obtener el estado del workflow
get_workflow_status() {
    gh run list --limit=5 --json=status,conclusion,displayTitle,databaseId 2>/dev/null | \
    jq -r --arg id "$WORKFLOW_ID" '.[] | select(.databaseId == ($id | tonumber)) | "\(.status)|\(.conclusion)|\(.displayTitle)"' 2>/dev/null || echo "error|error|Error obteniendo estado"
}

# Función para obtener releases
check_releases() {
    RELEASE_COUNT=$(gh release list --limit=1 --json=tagName 2>/dev/null | jq length 2>/dev/null || echo "0")
    if [ "$RELEASE_COUNT" -gt 0 ]; then
        echo "🎉 ¡NUEVO RELEASE ENCONTRADO!"
        gh release list --limit=1 --json=tagName,name,createdAt,assets 2>/dev/null | \
        jq -r '.[] | "   📦 \(.name // .tagName)\n   🔗 Creado: \(.createdAt)\n   📎 Assets: \(.assets | length) archivos"' 2>/dev/null || echo "   Detalles no disponibles"
        return 0
    fi
    return 1
}

# Monitoreo principal
PREVIOUS_STATUS=""
while true; do
    CURRENT_TIME=$(date "+%H:%M:%S")
    STATUS_INFO=$(get_workflow_status)
    
    if [ "$STATUS_INFO" = "error|error|Error obteniendo estado" ]; then
        echo "[$CURRENT_TIME] ❌ Error obteniendo estado del workflow"
        echo "                   Reintentando en $CHECK_INTERVAL segundos..."
        sleep $CHECK_INTERVAL
        continue
    fi
    
    STATUS=$(echo "$STATUS_INFO" | cut -d'|' -f1)
    CONCLUSION=$(echo "$STATUS_INFO" | cut -d'|' -f2)
    TITLE=$(echo "$STATUS_INFO" | cut -d'|' -f3)
    
    # Solo mostrar si el estado cambió
    if [ "$STATUS_INFO" != "$PREVIOUS_STATUS" ]; then
        echo "[$CURRENT_TIME] 📊 Estado: $STATUS"
        if [ "$CONCLUSION" != "" ] && [ "$CONCLUSION" != "null" ]; then
            echo "                   Resultado: $CONCLUSION"
        fi
        echo "                   Workflow: $TITLE"
        PREVIOUS_STATUS="$STATUS_INFO"
    else
        # Mostrar un punto para indicar que sigue monitoreando
        echo -n "."
    fi
    
    # Verificar si terminó
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "🏁 ¡Workflow completado!"
        
        if [ "$CONCLUSION" = "success" ]; then
            echo "   ✅ Resultado: ÉXITO"
            echo ""
            echo "🔍 Verificando si se creó un release..."
            sleep 5  # Esperar un poco para que se cree el release
            
            if check_releases; then
                echo ""
                echo "🎊 ¡PROCESO COMPLETADO EXITOSAMENTE!"
                echo "   Los ejecutables están listos para descargar"
            else
                echo "   ⚠️  No se encontró release automático"
                echo "   Verifica manualmente: https://github.com/kno/PDFCombiner/releases"
            fi
        else
            echo "   ❌ Resultado: $CONCLUSION"
            echo ""
            echo "🔍 Para ver detalles del error:"
            echo "   gh run view $WORKFLOW_ID --log"
            echo "   o visita: https://github.com/kno/PDFCombiner/actions/runs/$WORKFLOW_ID"
        fi
        
        echo ""
        echo "✅ Monitoreo completado"
        break
    fi
    
    sleep $CHECK_INTERVAL
done
