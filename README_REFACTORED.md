# PDF Combiner Pro - Refactored

## 📁 Estructura del Proyecto

```
combinar_pdfs/
├── main.py                 # Punto de entrada principal
├── combinar_pdfs_gui.py   # Archivo original (mantenido para compatibilidad)
├── pdf_utils.py           # Utilidades PDF originales
├── requirements.txt       # Dependencias
│
├── config/                # Configuración
│   ├── __init__.py
│   └── settings.py        # Configuraciones de la aplicación
│
├── core/                  # Lógica de negocio
│   ├── __init__.py
│   ├── file_manager.py    # Gestión de archivos
│   └── pdf_combiner.py    # Servicio de combinación PDF
│
├── gui/                   # Interfaz de usuario
│   ├── __init__.py
│   ├── main_window.py     # Ventana principal
│   ├── widgets.py         # Widgets personalizados
│   └── styles.py          # Estilos y temas
│
└── utils/                 # Utilidades
    ├── __init__.py
    └── text_processor.py  # Procesamiento de texto
```

## 🚀 Uso

### Ejecutar la aplicación refactorizada:
```bash
python main.py
```

### Ejecutar la aplicación original:
```bash
python combinar_pdfs_gui.py
```

## 🔧 Mejoras Implementadas

### 1. **Separación de Responsabilidades**
- **GUI**: Lógica de interfaz separada en `gui/`
- **Core**: Lógica de negocio en `core/`
- **Utils**: Utilidades reutilizables en `utils/`
- **Config**: Configuración centralizada en `config/`

### 2. **Widgets Personalizados**
- `MarkedListWidget`: Lista con marcado visual
- `DragDropListWidget`: Lista con drag & drop

### 3. **Gestión de Estilos**
- `StyleManager`: Gestor centralizado de estilos
- Enum `ButtonStyle` para tipos de botones
- Tema oscuro mejorado

### 4. **Servicios**
- `FileManager`: Gestión de archivos del sistema
- `PDFCombinerService`: Servicio de combinación PDF
- `TextProcessor`: Procesamiento de texto

### 5. **Configuración Centralizada**
- `AppConfig`: Configuraciones de la aplicación
- Constantes centralizadas
- Configuración de colores y tamaños

## 🎯 Beneficios

- ✅ **Mantenibilidad**: Código más fácil de mantener y extender
- ✅ **Testabilidad**: Cada módulo puede ser testeado independientemente
- ✅ **Legibilidad**: Código más claro y bien organizado
- ✅ **Reutilización**: Componentes reutilizables
- ✅ **Escalabilidad**: Fácil agregar nuevas funcionalidades
- ✅ **Compatibilidad**: Mantiene compatibilidad con código existente

## 🔄 Migración

La aplicación refactorizada mantiene todas las funcionalidades originales:
- Navegador de archivos PDF
- Marcado visual de archivos seleccionados
- Drag & drop para reordenar
- Combinación con/sin índice interactivo
- Atajos de teclado
- Tema oscuro

## 📝 Notas Técnicas

- Mantiene compatibilidad con `pdf_utils.py` existente
- Usa type hints para mejor documentación
- Manejo de errores mejorado con excepciones específicas
- Logging estructurado (preparado para implementar)
- Configuración flexible y extensible
