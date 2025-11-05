# Guía para Subir a GitHub

## Paso 1: Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Crea un nuevo repositorio:
   - **Nombre**: `rag-system-openai` (o el que prefieras)
   - **Descripción**: "Sistema RAG con OpenAI para asistente de conocimiento"
   - **Visibilidad**: Público o Privado (según prefieras)
   - **NO inicialices** con README, .gitignore o licencia (ya los tenemos)

## Paso 2: Conectar Repositorio Local con GitHub

Ejecuta estos comandos (reemplaza `TU_USUARIO` y `NOMBRE_REPO`):

```bash
# Agregar remote
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git

# O si prefieres SSH:
git remote add origin git@github.com:TU_USUARIO/NOMBRE_REPO.git
```

## Paso 3: Hacer Commit Inicial

```bash
# Hacer commit de todos los archivos
git commit -m "Sistema RAG completo: API, UI, Docker, Documentación y Métricas"
```

## Paso 4: Subir a GitHub

```bash
# Subir a la rama main (o master)
git branch -M main
git push -u origin main
```

## Comandos Completos (Copia y Pega)

```bash
# 1. Inicializar (ya hecho)
git init

# 2. Agregar archivos (ya hecho)
git add .

# 3. Hacer commit
git commit -m "Sistema RAG completo: API REST, Interfaz Web, Docker, Documentación completa y Sistema de Métricas

- Servicio de procesamiento de documentos (PDF, TXT, MD)
- Servicio de consultas RAG con búsqueda semántica
- Integración con OpenAI GPT-4
- Interfaz web con Gradio
- Base de datos vectorial ChromaDB
- Docker Compose para despliegue
- Sistema de métricas y evaluación
- Documentación completa de APIs
- Configuración segura de secrets"

# 4. Agregar remote (reemplaza con tu URL)
git remote add origin https://github.com/TU_USUARIO/rag-system-openai.git

# 5. Renombrar rama a main
git branch -M main

# 6. Subir a GitHub
git push -u origin main
```

## Verificación

Después de subir, verifica en GitHub:
- ✅ Todos los archivos están presentes
- ✅ El README se muestra correctamente
- ✅ La estructura de carpetas es clara
- ✅ No hay archivos sensibles (.env no debe estar)

## Estructura que se Subirá

```
RAG-system-openai/
├── README.md                    ✅ Documentación principal
├── API_DOCUMENTATION.md         ✅ Documentación de APIs
├── CONFIGURACION.md             ✅ Configuración de secrets
├── EVALUACION_RAG.md            ✅ Estrategias de evaluación
├── EVALUACION_REQUERIMIENTOS.md ✅ Checklist
├── INICIAR_SISTEMA.md           ✅ Guía de inicio
├── requirements.txt             ✅ Dependencias
├── docker-compose.yml           ✅ Orquestación Docker
├── env.example                  ✅ Plantilla de configuración
├── config/                      ✅ Configuración centralizada
├── services/                    ✅ Servicios principales
├── scripts/                     ✅ Scripts utilitarios
├── docker/                      ✅ Dockerfiles
└── data/                        ✅ (Solo estructura, sin datos)
```

## Archivos que NO se Subirán (por .gitignore)

- `.env` (tus secrets)
- `data/chroma_db/` (base de datos)
- `data/uploaded_documents/*` (documentos subidos)
- `data/metrics.json` (métricas generadas)
- `__pycache__/` (caché Python)
- `models/` (modelos descargados)

## Notas Importantes

1. **Nunca subas el archivo `.env`** - Está en `.gitignore` pero verifica
2. **No subas datos sensibles** - Solo código y documentación
3. **Verifica los commits** antes de hacer push
4. **Usa commits descriptivos** para futuras actualizaciones

## Actualizaciones Futuras

Para actualizar el repositorio:

```bash
git add .
git commit -m "Descripción del cambio"
git push
```

