import chromadb
from chromadb.config import Settings
import logging
from typing import Dict, List, Any

# Configure logging to write to a file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.FileHandler("chromadb_client.log"), logging.StreamHandler()],
)

logger = logging.getLogger("chromadb-client")

# ChromaDBClient provides an interface to ChromaDB for storing and retrieving document embeddings and metadata.
class ChromaDBClient:
    def __init__(
        self, persist_directory="./chroma_migrated", collection_name="documents"
    ):
        # Use the new PersistentClient initialization as per Chroma migration docs
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)

    def file_exists(self, file_name: str) -> bool:
        """
        Query the collection for any chunks where the stored 'file_name' matches exactly.
        Returns True if found, else False.
        """
        results = self.collection.get(
            where={"file_name": file_name}, include=["metadatas"]
        )
        return bool(results.get("metadatas"))

    def store(
        self,
        asset_id: str,
        embeddings: List[List[float]],
        texts: List[str],
        metadata: Dict[str, Any],
    ):
        """
        Store the embeddings and metadata in the collection.
        Each chunk is stored with a unique id and associated metadata.
        """
        n = len(embeddings)
        ids = [f"{asset_id}_{i}" for i in range(n)]
        metadatas = [
            metadata | {"chunk_idx": i, "asset_id": asset_id} for i in range(n)
        ]
        self.collection.add(
            embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids
        )
        logger.info(f"Stored {n} chunks/embeddings for asset_id={asset_id}")

    def list_documents(self):
        """
        Retrieve all documents and their metadata from the collection.
        """
        results = self.collection.get(include=["metadatas", "documents"])
        print("existing documents in ChromaDB:")
        print("-----------------------")
        return results
