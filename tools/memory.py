import os
import hashlib
import logging
import threading
from typing import List, Dict, Any, Optional
import chromadb

# Setup institutional logging format
logger = logging.getLogger("MemoryDB")

# Create a thread lock to prevent concurrent SQLite write conflicts
_db_lock = threading.Lock()

# Initialize ChromaDB client safely
try:
    # Ensure the storage directory exists
    os.makedirs("memory_db", exist_ok=True)
    client = chromadb.PersistentClient(path="memory_db")
    collection = client.get_or_create_collection("agent_memory")
    logger.info("ChromaDB persistent vector memory engine initialized successfully.")
except Exception as init_err:
    logger.critical(f"Failed to initialize persistent vector store: {init_err}", exc_info=True)
    raise init_err


def generate_deterministic_id(text: str) -> str:
    """
    Generates a deterministic SHA-256 hash string for any given text block.
    This protects against Python's default runtime hash randomization,
    ensuring identical content maps to the exact same ID across system restarts.
    """
    if not text:
        return "empty_document"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_memory(text: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Persists a research output, document, or signal into vector database memory.
    Thread-safe and idempotent (re-saving identical text updates/upserts rather than duplicating).
    """
    if not text or not text.strip():
        logger.warning("Storage Aborted: Memory text payload is empty.")
        return

    cleaned_text = text.strip()
    doc_id = generate_deterministic_id(cleaned_text)
    meta = metadata or {}

    logger.info(f"Writing memory segment to vector store. ID: {doc_id[:12]}...")

    with _db_lock:
        try:
            # We use .upsert() instead of .add() so that if the identical text is processed again,
            # ChromaDB safely updates the metadata instead of crashing or creating a duplicate record.
            collection.upsert(
                documents=[cleaned_text],
                metadatas=[meta],
                ids=[doc_id]
            )
            logger.info("Memory segment successfully committed to vector database.")
        except Exception as write_err:
            logger.error(f"Failed to write memory segment to ChromaDB: {write_err}", exc_info=True)


def search_memory(query: str, n_results: int = 3) -> List[str]:
    """
    Performs a vector search to retrieve relevant context.
    Defensive checking guarantees zero IndexError crashes on empty collections.
    """
    if not query or not query.strip():
        logger.warning("Search Aborted: Query payload is empty.")
        return []

    cleaned_query = query.strip()
    logger.info(f"Searching vector memory for semantic context matching: '{cleaned_query}'")

    with _db_lock:
        try:
            # Check collection count before querying to avoid unnecessary exceptions on empty databases
            if collection.count() == 0:
                logger.info("Semantic database is currently empty. Returning no historical memory.")
                return []

            # ChromaDB handles querying internally
            results = collection.query(
                query_texts=[cleaned_query],
                n_results=min(n_results, collection.count())
            )

            # Defensive structural unpacking
            if not results or "documents" not in results or not results["documents"]:
                return []

            documents_list = results["documents"]
            if len(documents_list) > 0 and isinstance(documents_list[0], list):
                extracted_docs = [str(doc) for doc in documents_list[0] if doc]
                logger.info(f"Semantic search completed. Found {len(extracted_docs)} relevant context matches.")
                return extracted_docs

            return []

        except Exception as query_err:
            logger.error(f"Semantic search query execution encountered an error: {query_err}", exc_info=True)
            return []