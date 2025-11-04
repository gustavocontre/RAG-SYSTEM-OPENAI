# Script de inicio para el sistema RAG
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Sistema RAG - Inicio Rapido" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker esté corriendo
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker está corriendo" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker Desktop no está corriendo." -ForegroundColor Red
    Write-Host "Por favor, inicia Docker Desktop y vuelve a ejecutar este script." -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Verificar que la API key esté configurada
$envContent = Get-Content .env -ErrorAction SilentlyContinue
if ($envContent -match "tu_api_key_aqui") {
    Write-Host "[ADVERTENCIA] La API key de OpenAI no está configurada en .env" -ForegroundColor Yellow
    Write-Host "Por favor, edita el archivo .env y configura tu OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para continuar de todas formas"
}

Write-Host "Iniciando servicios..." -ForegroundColor Green
Write-Host ""

docker-compose up

