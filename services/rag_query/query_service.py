"""
Servicio de Consultas RAG
Implementa búsqueda semántica y generación de respuestas con LLM
"""

import os
import logging
import re
from typing import List, Dict, Optional

# Cargar configuración centralizada
try:
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(parent_dir))
    from config.settings import settings
except ImportError:
    # Fallback: cargar variables de entorno desde .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    settings = None

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI
from langchain_core.documents import Document
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


def remove_emojis(text: str) -> str:
    """Elimina emojis de un texto"""
    # Patrón para eliminar emojis (Unicode ranges)
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGQueryService:
    """Servicio de consultas RAG con búsqueda semántica"""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        persist_directory: str = "./data/chroma_db",
        llm_model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        temperature: float = 0.0,
        top_k: int = 5
    ):
        """
        Inicializa el servicio de consultas RAG
        
        Args:
            embedding_model: Modelo de embeddings
            persist_directory: Directorio de ChromaDB
            llm_model: Modelo LLM a usar
            openai_api_key: API key de OpenAI
            temperature: Temperatura para el LLM
            top_k: Número de chunks a recuperar
        """
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        # Leer modelo desde configuración centralizada o variable de entorno
        if llm_model is None:
            if settings:
                llm_model = settings.LLM_MODEL
            else:
                llm_model = os.getenv("LLM_MODEL", "gpt-4-turbo")
        self.llm_model = llm_model
        self.temperature = temperature
        self.top_k = top_k
        
        # Cargar modelo de embeddings
        logger.info(f"Cargando modelo de embeddings: {embedding_model}")
        self.embed_model = SentenceTransformer(embedding_model)
        
        # Inicializar ChromaDB
        logger.info(f"Conectando a ChromaDB en {persist_directory}")
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        # Obtener o crear colección si no existe
        try:
            self.collection = self.client.get_collection(name="documents")
        except Exception:
            logger.info("Colección 'documents' no existe, creándola...")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
        
        # Inicializar LLM (local o OpenAI)
        if settings:
            use_local_llm = settings.USE_LOCAL_LLM
            local_model_path = settings.LOCAL_MODEL_PATH
        else:
            use_local_llm = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
            local_model_path = os.getenv("LOCAL_MODEL_PATH", "./models/codellama-7b-programming")
        
        # Verificar si es modelo local
        if use_local_llm or "codellama" in self.llm_model.lower() or "local" in self.llm_model.lower():
            logger.info(f"Inicializando modelo local: {self.llm_model}")
            try:
                from services.llm.local_llm import LocalCodeLlamaLLM
                
                # Verificar si hay modelo base local
                base_model_path = os.getenv("BASE_MODEL_PATH", None)
                if base_model_path and not os.path.exists(base_model_path):
                    logger.warning(f"BASE_MODEL_PATH especificado pero no existe: {base_model_path}")
                    base_model_path = None
                
                self.llm = LocalCodeLlamaLLM(
                    model_path=local_model_path,
                    base_model_path=base_model_path,  # Usar modelo base local si está disponible
                    temperature=0.3,  # Reducido para respuestas más rápidas y deterministas
                    max_tokens=250,  # Reducido para respuestas más rápidas
                    use_greedy=True  # Greedy decoding más rápido en CPU
                )
                logger.info("Modelo local cargado exitosamente")
            except Exception as e:
                logger.error(f"Error cargando modelo local: {e}")
                logger.warning("Fallando a OpenAI...")
                use_local_llm = False
        
        # Si no es modelo local, usar OpenAI
        if not use_local_llm:
            if openai_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
            else:
                # Intentar obtener de configuración centralizada primero
                if settings:
                    openai_api_key = settings.get_openai_key()
                else:
                    openai_api_key = os.environ.get("OPENAI_API_KEY")
                
            if not openai_api_key:
                logger.warning("No se proporcionó OPENAI_API_KEY. Las consultas pueden fallar.")
                logger.warning("Configura OPENAI_API_KEY en el archivo .env o usa el script: python scripts/setup_env.py")
            
            logger.info(f"Inicializando LLM: {self.llm_model}")
            # Configurar timeout y límites para mejorar velocidad
            self.llm = ChatOpenAI(
                model=self.llm_model,
                temperature=temperature,
                timeout=30.0,  # Timeout de 30 segundos
                max_retries=2,  # Reintentos limitados
                max_tokens=500  # Limitar tokens para respuestas más rápidas
            )
        
        # Prompt template para RAG (adaptado para modelos locales)
        is_local = hasattr(self.llm, '_llm_type') and 'local' in self.llm._llm_type
        
        if is_local:
            # Para modelos locales, usar PromptTemplate simple
            from langchain_core.prompts import PromptTemplate
            prompt_text = """Eres un asistente de conocimiento experto que ayuda a desarrolladores 
con información técnica. Responde de manera clara y precisa basándote ÚNICAMENTE 
en el contexto proporcionado. Si el contexto no contiene información suficiente 
para responder, indica que no tienes esa información.

IMPORTANTE: No uses emojis en tus respuestas.

Contexto relevante:
{context}

Instrucciones:
- Usa SOLO la información del contexto proporcionado
- Si necesitas hacer suposiciones, indícalo claramente
- Proporciona ejemplos de código si son relevantes
- Sé conciso pero completo
- NO uses emojis

Pregunta: {question}

Respuesta:"""
            self.rag_prompt = PromptTemplate(template=prompt_text, input_variables=["context", "question"])
            self.chain = self.rag_prompt | self.llm
        else:
            # Para OpenAI, usar ChatPromptTemplate
            self.rag_prompt = ChatPromptTemplate.from_messages([
                ("system", """Eres un asistente de conocimiento experto que ayuda a desarrolladores 
con información técnica. Responde de manera clara y precisa basándote ÚNICAMENTE 
en el contexto proporcionado. Si el contexto no contiene información suficiente 
para responder, indica que no tienes esa información.

IMPORTANTE: No uses emojis en tus respuestas.

Contexto relevante:
{context}

Instrucciones:
- Usa SOLO la información del contexto proporcionado
- Si necesitas hacer suposiciones, indícalo claramente
- Proporciona ejemplos de código si son relevantes
- Sé conciso pero completo
- NO uses emojis"""),
                ("human", "Pregunta: {question}")
            ])
            self.chain = self.rag_prompt | self.llm | StrOutputParser()
        
        logger.info("RAGQueryService inicializado correctamente")
    
    def search_similar_chunks(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Realiza búsqueda semántica de chunks similares
        
        Args:
            query: Pregunta o query del usuario
            top_k: Número de resultados a retornar
            filter_metadata: Filtros adicionales para metadata
            
        Returns:
            Lista de chunks relevantes con scores
        """
        top_k = top_k or self.top_k
        
        logger.info(f"Buscando {top_k} chunks similares para: {query}")
        
        # Generar embedding de la query
        query_embedding = self.embed_model.encode(query).tolist()
        
        # Búsqueda en ChromaDB
        where_clause = filter_metadata if filter_metadata else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Preparar resultados
        chunks = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                chunks.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': 1 - results['distances'][0][i]  # Convertir distancia a score
                })
        
        logger.info(f"Encontrados {len(chunks)} chunks relevantes")
        return chunks
    
    def format_context(self, chunks: List[Dict]) -> str:
        """
        Formatea los chunks como contexto para el prompt
        
        Args:
            chunks: Lista de chunks recuperados
            
        Returns:
            Contexto formateado
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Fuente {i}] (Score: {chunk['score']:.3f})\n"
                f"{chunk['text']}\n"
            )
        return "\n---\n\n".join(context_parts)
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        return_sources: bool = True,
        filter_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Realiza una consulta RAG completa
        
        Args:
            question: Pregunta del usuario
            top_k: Número de chunks a recuperar
            return_sources: Si retornar información de fuentes
            filter_metadata: Filtros para metadata
            
        Returns:
            Respuesta completa con metadatos
        """
        logger.info(f"Procesando consulta: {question}")
        
        # Búsqueda semántica
        chunks = self.search_similar_chunks(
            question,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        if not chunks:
            return {
                'answer': "No se encontró información relevante en la base de datos para responder a tu pregunta.",
                'sources': [],
                'num_chunks': 0
            }
        
        # Formatear contexto
        context = self.format_context(chunks)
        
        # Generar respuesta con LLM
        logger.info("Generando respuesta con LLM")
        answer = self.chain.invoke({
            "context": context,
            "question": question
        })
        
        # Eliminar emojis de la respuesta
        answer = remove_emojis(str(answer))
        
        # Preparar respuesta
        result = {
            'answer': answer,
            'num_chunks': len(chunks)
        }
        
        if return_sources:
            result['sources'] = [
                {
                    'filename': chunk['metadata'].get('filename', 'unknown'),
                    'chunk_index': chunk['metadata'].get('chunk_index', -1),
                    'score': chunk['score']
                }
                for chunk in chunks
            ]
        
        logger.info("Consulta procesada exitosamente")
        return result
    
    def get_all_documents(self) -> List[str]:
        """
        Obtiene lista de todos los documentos únicos en la base
        
        Returns:
            Lista de doc_ids únicos
        """
        results = self.collection.peek(limit=10000)
        if results and results['metadatas']:
            unique_docs = set([m.get('doc_id') for m in results['metadatas']])
            return list(unique_docs)
        return []


def main():
    """Función principal para testing"""
    # Nota: Requiere OPENAI_API_KEY configurada
    service = RAGQueryService()
    
    # Ejemplo de consulta
    # response = service.query("¿Qué es un transformer?")
    # print(f"Respuesta: {response['answer']}")
    # print(f"Fuentes: {response['sources']}")


if __name__ == "__main__":
    main()


