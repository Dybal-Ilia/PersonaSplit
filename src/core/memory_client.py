import asyncio
import inspect
import os
from collections.abc import Iterable, Sequence

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_postgres import Column, PGEngine, PGVectorStore
from langchain_postgres.v2.indexes import HNSWIndex

from src.utils.logger import logger

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
TABLE_NAME = os.getenv("TABLE_NAME", "memory")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "384"))
CONNECTION_STRING = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


class MemoryClient:
    def __init__(self) -> None:
        self._engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
        self._embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self._vectorstore: PGVectorStore | None = None
        self._init_lock = asyncio.Lock()

    async def _ensure_vectorstore(self) -> None:
        if self._vectorstore is not None:
            return

        async with self._init_lock:
            if self._vectorstore is not None:
                return

            try:
                await self._engine.ainit_vectorstore_table(
                    table_name=TABLE_NAME,
                    vector_size=VECTOR_SIZE,
                    metadata_columns=[
                        Column("agent_name", "TEXT"),
                        Column("session_id", "TEXT"),
                    ],
                )
            except Exception as exc:
                logger.debug(f"Vectorstore table init skipped: {exc}")

            store_candidate = PGVectorStore.create(
                engine=self._engine,
                table_name=TABLE_NAME,
                embedding_service=self._embedding,
                metadata_columns=["agent_name", "session_id"],
            )
            store = (
                await store_candidate
                if inspect.isawaitable(store_candidate)
                else store_candidate
            )

            try:
                index = HNSWIndex()
                store.apply_vector_index(index)
            except Exception as exc:
                if "already exists" in str(exc):
                    logger.debug("Index already exists, skipping creation.")
                else:
                    logger.error(f"Error creating index: {exc}")

            self._vectorstore = store

    async def add(
        self,
        documents: Sequence[Document] | Document,
        *,
        session_id: str | None = None,
        agent_name: str | None = None,
    ) -> list[str]:
        await self._ensure_vectorstore()
        if self._vectorstore is None:
            raise RuntimeError("Vectorstore not initialized")

        if isinstance(documents, Document):
            docs_list = [documents]
        elif isinstance(documents, Iterable):
            docs_list = list(documents)
        else:
            raise TypeError("documents must be a Document or iterable of Documents")

        if not all(isinstance(doc, Document) for doc in docs_list):
            raise TypeError("documents iterable must contain Document instances")

        if not docs_list:
            return []

        for doc in docs_list:
            metadata = dict(doc.metadata) if doc.metadata else {}
            if session_id is not None:
                metadata.setdefault("session_id", session_id)
            if agent_name is not None:
                metadata.setdefault("agent_name", agent_name)
            doc.metadata = metadata

        add_async = getattr(self._vectorstore, "aadd_documents", None)
        if add_async is not None:
            await add_async(docs_list)
        else:
            await asyncio.to_thread(self._vectorstore.add_documents, docs_list)
        return [doc.page_content for doc in docs_list]

    async def search(
        self,
        query: str,
        *,
        k: int = 5,
        session_id: str | None = None,
        agent_name: str | None = None,
    ) -> list[str]:
        await self._ensure_vectorstore()
        if self._vectorstore is None:
            raise RuntimeError("Vectorstore not initialized")

        filters = {}
        if session_id is not None:
            filters["session_id"] = session_id
        if agent_name is not None:
            filters["agent_name"] = agent_name
        filter_arg = filters or None

        search_async = getattr(self._vectorstore, "asimilarity_search", None)
        if search_async is not None:
            results = await search_async(query=query, k=k, filter=filter_arg)
        else:
            results = await asyncio.to_thread(
                self._vectorstore.similarity_search,
                query,
                k,
                filter_arg,
            )
        return [doc.page_content for doc in results]


memory_client = MemoryClient()
