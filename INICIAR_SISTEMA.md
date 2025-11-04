# Iniciar el Sistema RAG

## Paso 1: Verificar Configuración

Después de configurar tu API key en el archivo `.env`, verifica que todo esté correcto:

```bash
python scripts/check_config.py
```

Si ves `[OK] Configuracion valida!`, puedes continuar.

## Paso 2: Iniciar el Sistema

### Opción A: Iniciar Servidor API

Abre una terminal y ejecuta:

```bash
python -m services.web_interface.api
```

El servidor API estará disponible en: **http://localhost:8000**

### Opción B: Iniciar Interfaz Web (Gradio)

Abre otra terminal y ejecuta:

```bash
python -m services.web_interface.gradio_ui
```

La interfaz web estará disponible en: **http://localhost:7860**

## 📊 Paso 3: Acceder a los Servicios

Una vez iniciados ambos servicios:

1. **API REST**: http://localhost:8000/docs
   - Documentación interactiva (Swagger)
   - Puedes probar los endpoints aquí

2. **Interfaz Web**: http://localhost:7860
   - Interfaz gráfica para hacer consultas
   - Subir documentos
   - Ver historial de conversación

## 🧪 Paso 4: Probar el Sistema

### Desde la Interfaz Web

1. Abre http://localhost:7860
2. Haz una pregunta sobre los documentos cargados
3. El sistema buscará información relevante y generará una respuesta

### Desde la API

```bash
# Hacer una consulta
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué es Python?", "top_k": 5}'
```

## 📈 Ver Métricas

Para ver las métricas del sistema:

```bash
python scripts/generate_metrics_report.py
```

## ⚠️ Solución de Problemas

### Error: "OPENAI_API_KEY no está configurada"

1. Verifica que el archivo `.env` existe
2. Verifica que contiene: `OPENAI_API_KEY=sk-tu_key_real`
3. Asegúrate de haber guardado el archivo
4. Reinicia el servidor si ya estaba corriendo

### Error: "No se puede conectar a la API"

- Verifica que el servidor API está corriendo en el puerto 8000
- Verifica que no hay otro proceso usando ese puerto

### Error: "Base de datos vacía"

- Sube al menos un documento PDF primero
- Usa el endpoint `/upload` o la interfaz web

## 🎯 Siguientes Pasos

1. ✅ Configuración completada
2. ✅ Servidores iniciados
3. 📝 Sube documentos PDF
4. 💬 Haz consultas
5. 📊 Revisa las métricas

¡Listo para usar!

