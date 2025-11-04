# Cómo Limpiar el Caché

## Opción 1: Script Automático (Recomendado)

Ejecuta el script interactivo:

```powershell
.\limpiar_cache.ps1
```

Este script te mostrará el tamaño de cada caché y te pedirá confirmación antes de eliminar.

## Opción 2: Comandos Manuales

### 1. Caché de HuggingFace (modelos descargados)

**Ubicación:** `C:\Users\<TU_USUARIO>\.cache\huggingface`

**Tamaño típico:** ~13GB si descargaste CodeLlama base

**Comando:**
```powershell
Remove-Item "$env:USERPROFILE\.cache\huggingface\*" -Recurse -Force
```

**Nota:** Si limpias esto, tendrás que volver a descargar el modelo base la próxima vez que uses el modelo local.

### 2. Caché de Python (pip)

**Ubicación:** `C:\Users\<TU_USUARIO>\AppData\Local\pip\cache`

**Tamaño típico:** ~100-500 MB

**Comando:**
```powershell
Remove-Item "$env:LOCALAPPDATA\pip\cache\*" -Recurse -Force
```

**Nota:** Esto solo afecta la descarga de paquetes, no los paquetes instalados.

### 3. Base de Datos ChromaDB

**Ubicación:** `.\data\chroma_db`

**⚠️ ADVERTENCIA:** Esto eliminará TODOS los documentos indexados en tu sistema RAG.

**Comando:**
```powershell
Remove-Item ".\data\chroma_db\*" -Recurse -Force
```

**Nota:** Tendrás que volver a subir y procesar todos tus documentos después de esto.

## Verificar Tamaño del Caché

Para ver el tamaño antes de limpiar:

```powershell
# Caché de HuggingFace
$size = (Get-ChildItem "$env:USERPROFILE\.cache\huggingface" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "Caché HuggingFace: $([math]::Round($size, 2)) GB"

# Caché de pip
$size = (Get-ChildItem "$env:LOCALAPPDATA\pip\cache" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Caché pip: $([math]::Round($size, 2)) MB"
```

## Recomendaciones

- **Caché de HuggingFace:** Solo limpia si necesitas espacio. El modelo se volverá a descargar automáticamente.
- **Caché de pip:** Puedes limpiarlo sin problemas, solo hará que pip descargue los paquetes nuevamente.
- **ChromaDB:** Solo limpia si quieres empezar de cero con los documentos.

