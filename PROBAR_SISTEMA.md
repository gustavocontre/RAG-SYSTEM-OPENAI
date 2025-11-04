# Cómo Probar el Sistema RAG

## Verificación Rápida

### 1. Verificar Configuración

```bash
# Verificar que .env esté configurado
cat .env | grep USE_LOCAL_LLM

# Debe mostrar: USE_LOCAL_LLM=true
```

### 2. Verificar Token de HuggingFace

```bash
# Verificar autenticación
huggingface-cli whoami

# Si no está autenticado:
huggingface-cli login
# Pega tu token cuando se solicite
```

### 3. Iniciar el Servidor

**Terminal 1 - API Server:**
```bash
python -m services.web_interface.api
```

**Terminal 2 - Interfaz Web (opcional):**
```bash
python -m services.web_interface.gradio_ui
```

### 4. Probar Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Hacer una consulta:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué es Python?", "top_k": 3}'
```

## Qué Esperar

### Primera Vez (sin caché):
1. **Carga del modelo**: 5-10 minutos
   - Descarga modelo base desde HuggingFace (~13GB)
   - Carga adaptadores LoRA
   - Mensajes en consola sobre el progreso

2. **Logs esperados:**
   ```
   INFO: Token de HuggingFace encontrado
   INFO: Cargando modelo desde ./models/codellama-7b-programming
   INFO: Tokenizer cargado desde modelo fine-tuned
   INFO: Usando modelo base local: ... (o descargando de HuggingFace)
   INFO: Modelo fine-tuned con LoRA cargado
   INFO: Modelo listo para inferencia
   ```

### Siguientes Veces (con caché):
- Carga más rápida: 1-2 minutos
- Usa el caché local de HuggingFace

## Solución de Problemas

### Error: "Token de HuggingFace no encontrado"
```bash
huggingface-cli login
```

### Error: "403 Forbidden" al cargar modelo
- Verifica que tengas acceso al repositorio CodeLlama
- Ve a: https://huggingface.co/meta-llama/CodeLlama-7b-Instruct-hf
- Asegúrate de haber aceptado los términos

### Error: "CUDA out of memory"
- El modelo requiere GPU con al menos 8GB VRAM
- O usa CPU (más lento pero funciona)

### El servidor no responde
- Espera más tiempo (primera carga puede tardar 10+ minutos)
- Revisa los logs en la terminal para ver el progreso

## Acceder a la Interfaz

Una vez que el servidor esté corriendo:

- **API Docs**: http://localhost:8000/docs
- **Interfaz Web**: http://localhost:7860 (si iniciaste gradio_ui)

