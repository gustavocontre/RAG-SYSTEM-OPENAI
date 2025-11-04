"""
Interfaz web con Gradio para el sistema RAG
"""

import gradio as gr
import requests
import logging
import re
from typing import Tuple, List
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")


def remove_emojis(text: str) -> str:
    """Elimina emojis de un texto"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

# Tema personalizado
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="gray",
    font=["Inter", "sans-serif"]
)


# Nota: El historial de conversación se maneja directamente por Gradio


def process_query(question: str, history: List) -> Tuple[List, str]:
    """
    Procesa una consulta del usuario
    
    Args:
        question: Pregunta del usuario
        history: Historial de conversación de Gradio (formato messages)
        
    Returns:
        Historial actualizado y respuesta
    """
    if not question.strip():
        return history, ""
    
    try:
        # Llamar a la API
        response = requests.post(
            f"{API_URL}/query",
            json={
                "question": question,
                "top_k": 5,
                "return_sources": True
            },
            timeout=180  # Aumentado para modelo local en CPU
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['answer']
            
            # Eliminar emojis de la respuesta
            answer = remove_emojis(str(answer))
            
            # Añadir fuentes si están disponibles
            if result.get('sources'):
                sources_text = "\n\n**Fuentes:**\n"
                for i, source in enumerate(result['sources'][:3], 1):
                    sources_text += f"- {source.get('filename', 'Unknown')} "
                    sources_text += f"(Score: {source.get('score', 0):.2f})\n"
                answer += sources_text
            
            # Actualizar historial (formato messages)
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})
            return history, ""
            
        else:
            # Obtener detalles del error de la respuesta
            try:
                error_detail = response.json().get('detail', response.text)
            except:
                error_detail = response.text
            
            error_msg = f"Error al procesar la consulta (Código {response.status_code})\n\nDetalles: {error_detail}"
            logger.error(f"Error en consulta: {error_msg}")
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": error_msg})
            return history, ""
            
    except requests.exceptions.ConnectionError as e:
        error_msg = "Error: No se puede conectar a la API. Verifica que el servidor API esté corriendo en http://localhost:8000"
        logger.error(f"Error de conexión: {str(e)}")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": error_msg})
        return history, ""
    except requests.exceptions.Timeout as e:
        error_msg = "Error: La consulta tardó demasiado tiempo. Intenta de nuevo."
        logger.error(f"Timeout: {str(e)}")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": error_msg})
        return history, ""
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        error_msg = f"Error inesperado: {str(e)}\n\nVerifica los logs del servidor para más detalles."
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": error_msg})
        return history, ""


def upload_document(file) -> str:
    """
    Sube y procesa un documento
    
    Args:
        file: Archivo subido por el usuario
        
    Returns:
        Mensaje de resultado
    """
    if file is None:
        return "Por favor selecciona un archivo"
    
    try:
        with open(file, 'rb') as f:
            files = {'file': (os.path.basename(file), f, 'application/octet-stream')}
            response = requests.post(f"{API_URL}/upload", files=files, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return f"Documento procesado exitosamente!\n\n" \
                   f"Archivo: {result['filename']}\n" \
                   f"Chunks creados: {result['chunks_created']}\n" \
                   f"Caracteres: {result['total_chars']:,}"
        else:
            # Obtener detalles del error
            try:
                error_detail = response.json().get('detail', response.text)
            except:
                error_detail = response.text
            logger.error(f"Error subiendo documento: {error_detail}")
            return f"Error al procesar documento (Código {response.status_code})\n\nDetalles: {error_detail}"
            
    except requests.exceptions.ConnectionError as e:
        error_msg = "Error: No se puede conectar a la API. Verifica que el servidor API esté corriendo en http://localhost:8000"
        logger.error(f"Error de conexión: {str(e)}")
        return error_msg
    except requests.exceptions.Timeout as e:
        error_msg = "Error: La subida del documento tardó demasiado tiempo. Intenta con un archivo más pequeño."
        logger.error(f"Timeout: {str(e)}")
        return error_msg
    except Exception as e:
        logger.error(f"Error subiendo archivo: {str(e)}")
        return f"Error inesperado: {str(e)}\n\nVerifica los logs del servidor para más detalles."


def get_stats():
    """Obtiene estadísticas de la base de datos"""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            return f"**Estadísticas de la Base de Datos**\n\n" \
                   f"Documentos únicos: {stats['unique_documents']}\n" \
                   f"Chunks totales: {stats['total_chunks']}"
        else:
            try:
                error_detail = response.json().get('detail', response.text)
            except:
                error_detail = response.text
            logger.error(f"Error obteniendo estadísticas: {error_detail}")
            return f"Error obteniendo estadísticas (Código {response.status_code})\n\nDetalles: {error_detail}"
    except requests.exceptions.ConnectionError as e:
        error_msg = "Error: No se puede conectar a la API. Verifica que el servidor API esté corriendo en http://localhost:8000"
        logger.error(f"Error de conexión: {str(e)}")
        return error_msg
    except requests.exceptions.Timeout as e:
        error_msg = "Error: La consulta de estadísticas tardó demasiado tiempo."
        logger.error(f"Timeout: {str(e)}")
        return error_msg
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return f"Error inesperado: {str(e)}\n\nVerifica los logs del servidor para más detalles."


def create_interface():
    """Crea la interfaz de Gradio"""
    
    # Títulos sin emojis
    page_title = remove_emojis("Sistema RAG - Asistente de Conocimiento")
    main_title = remove_emojis("Sistema RAG - Asistente de Conocimiento para Desarrolladores")
    
    with gr.Blocks(theme=theme, title=page_title) as demo:
        
        # Título principal
        gr.Markdown(
            f"""
            # {main_title}
            
            Sistema de **Recuperación Aumentada por Generación (RAG)** que permite realizar 
            consultas sobre documentación técnica indexada.
            
            ---
            """
        )
        
        with gr.Tabs():
            # Tab de Chat
            with gr.Tab("Chat"):
                gr.Markdown("### Realiza consultas sobre la documentación")
                
                chatbot = gr.Chatbot(
                    label="Conversación",
                    height=500,
                    show_copy_button=True,
                    type="messages"
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Tu pregunta",
                        placeholder="Escribe tu pregunta aquí...",
                        scale=4
                    )
                    submit_btn = gr.Button("Enviar", variant="primary", scale=1)
                
                msg.submit(process_query, [msg, chatbot], [chatbot, msg])
                submit_btn.click(process_query, [msg, chatbot], [chatbot, msg])
                
                gr.Markdown("**Tip:** Puedes preguntar sobre conceptos, código, ejemplos, etc.")
            
            # Tab de Documentos
            with gr.Tab("Subir Documentos"):
                gr.Markdown("### Procesa documentación técnica (PDF, TXT, MD)")
                
                file_input = gr.File(
                    label="Seleccionar archivo",
                    file_types=[".pdf", ".txt", ".md"]
                )
                
                upload_btn = gr.Button("Procesar Documento", variant="primary")
                upload_result = gr.Textbox(label="Resultado", lines=5)
                
                upload_btn.click(upload_document, file_input, upload_result)
            
            # Tab de Estadísticas
            with gr.Tab("Estadísticas"):
                gr.Markdown("### Estado de la base de datos")
                
                stats_display = gr.Markdown()
                refresh_btn = gr.Button("Actualizar Estadísticas", variant="secondary")
                
                refresh_btn.click(get_stats, None, stats_display)
                
                # Cargar estadísticas al inicio
                demo.load(get_stats, None, stats_display)
        
        # Footer
        gr.Markdown(
            """
            ---
            ### Instrucciones de Uso
            
            1. **Sube documentos**: Ve a la pestaña "Subir Documentos" y carga archivos PDF, TXT o MD
            2. **Haz preguntas**: En la pestaña "Chat" puedes consultar sobre el contenido indexado
            3. **Revisa estadísticas**: Consulta cuántos documentos y chunks tienes indexados
            
            **Nota:** Asegúrate de que la API esté ejecutándose en `http://localhost:8000`
            """
        )
        
        # Fila de estado
        gr.Markdown("Sistema operativo | Asegúrate de tener documentos indexados")
    
    return demo


def main():
    """Función principal"""
    logger.info("Iniciando interfaz Gradio")
    
    # Crear y lanzar la interfaz
    demo = create_interface()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()


