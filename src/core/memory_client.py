import os
from dotenv import load_dotenv
from mem0 import AsyncMemory
from mem0.configs.base import MemoryConfig, VectorStoreConfig, LlmConfig, EmbedderConfig

load_dotenv()

config = MemoryConfig(
    vector_store=VectorStoreConfig(
        provider="chroma",
        config={
            "path": "chroma_db", 
            
            "collection_name": "debate_memory",
        }
    ),
    llm=LlmConfig(
        provider="groq",
        config={
            "model": "llama-3.1-8b-instant",
            "api_key": os.getenv("GROQ_API_KEY")
        }
    ),
    embedder=EmbedderConfig(
        provider="huggingface",
        config={
            "model": "all-MiniLM-L6-v2"
        }
    )
)

memory_client = AsyncMemory(config=config)