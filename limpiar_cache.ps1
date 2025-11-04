# Script para limpiar cache del sistema RAG

Write-Host "=== LIMPIEZA DE CACHE ===" -ForegroundColor Cyan
Write-Host ""

# 1. Cache de HuggingFace (modelos descargados)
Write-Host "1. CACHE DE HUGGINGFACE" -ForegroundColor Yellow
$hfCache = "$env:USERPROFILE\.cache\huggingface"
if (Test-Path $hfCache) {
    $size = (Get-ChildItem $hfCache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "   Tamano: $([math]::Round($size, 2)) GB" -ForegroundColor Gray
    $response = Read-Host "   Limpiar cache de HuggingFace? (s/n)"
    if ($response -eq "s" -or $response -eq "S") {
        Remove-Item "$hfCache\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   Cache de HuggingFace limpiado" -ForegroundColor Green
    }
} else {
    Write-Host "   No se encontro cache de HuggingFace" -ForegroundColor Gray
}

Write-Host ""

# 2. Cache de Python (pip)
Write-Host "2. CACHE DE PYTHON (pip)" -ForegroundColor Yellow
$pipCache = "$env:LOCALAPPDATA\pip\cache"
if (Test-Path $pipCache) {
    $size = (Get-ChildItem $pipCache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "   Tamano: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
    $response = Read-Host "   Limpiar cache de pip? (s/n)"
    if ($response -eq "s" -or $response -eq "S") {
        Remove-Item "$pipCache\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   Cache de pip limpiado" -ForegroundColor Green
    }
} else {
    Write-Host "   No se encontro cache de pip" -ForegroundColor Gray
}

Write-Host ""

# 3. Cache de ChromaDB (base de datos vectorial)
Write-Host "3. CACHE DE CHROMADB (base de datos)" -ForegroundColor Yellow
$chromaPath = ".\data\chroma_db"
if (Test-Path $chromaPath) {
    $size = (Get-ChildItem $chromaPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "   Tamano: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
    Write-Host "   ADVERTENCIA: Esto eliminara todos los documentos indexados" -ForegroundColor Red
    $response = Read-Host "   Limpiar base de datos ChromaDB? (s/n)"
    if ($response -eq "s" -or $response -eq "S") {
        Remove-Item "$chromaPath\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   Base de datos ChromaDB limpiada" -ForegroundColor Green
    }
} else {
    Write-Host "   No se encontro base de datos ChromaDB" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== LIMPIEZA COMPLETADA ===" -ForegroundColor Cyan
