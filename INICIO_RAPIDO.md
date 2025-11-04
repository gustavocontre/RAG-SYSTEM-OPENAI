# Inicio Rápido - Versión OpenAI

## Pasos para empezar

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar API Key**:
   - Edita `.env` y agrega tu `OPENAI_API_KEY`
   - Obtén tu key en: https://platform.openai.com/api-keys

3. **Iniciar servidor**:
   ```bash
   python -m services.web_interface.api
   ```

4. **Abrir interfaz** (en otra terminal, opcional):
   ```bash
   python -m services.web_interface.gradio_ui
   ```

5. **Probar**:
   - API Docs: http://localhost:8000/docs
   - Interfaz Web: http://localhost:7860

## Subir documentos

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@ruta/a/tu/documento.pdf"
```

## Hacer consultas

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué es Python?"}'
```

