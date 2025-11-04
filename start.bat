@echo off
echo ============================================
echo Sistema RAG - Inicio Rapido
echo ============================================
echo.

REM Verificar que Docker esté corriendo
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop no está corriendo.
    echo Por favor, inicia Docker Desktop y vuelve a ejecutar este script.
    pause
    exit /b 1
)

echo [OK] Docker está corriendo
echo.

REM Verificar que la API key esté configurada
findstr /C:"tu_api_key_aqui" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo [ADVERTENCIA] La API key de OpenAI no está configurada en .env
    echo Por favor, edita el archivo .env y configura tu OPENAI_API_KEY
    echo.
    pause
)

echo Iniciando servicios...
echo.
docker-compose up

