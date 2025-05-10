import chromadb
from chromadb.config import Settings
import logging
from typing import Dict, List, Any

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('chromadb_client.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("chromadb-client")

class ChromaDBClient:
    def __init__(self, persist_directory="./chroma_migrated", collection_name="documents"):
        # Use the new PersistentClient initialization as per Chroma migration docs
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)

    def store(
        self,
        asset_id: str, 
        embeddings: List[List[float]],
        texts: List[str],
        metadata: Dict[str, Any]
    ):
        # # Check for duplicate file name in metadata
        # existing = self.collection.get(
        #     where={"file_name": metadata.get("file_name")},
        #     include=["metadatas", "ids"]
        # )
        # if existing and existing.get("ids"):
        #     raise ValueError(f"Duplicate file name detected: {metadata.get('file_name')}")
        n = len(embeddings)
        ids = [f"{asset_id}_{i}" for i in range(n)]
        metadatas = [metadata | {"chunk_idx": i, "asset_id": asset_id} for i in range(n)]
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Stored {n} chunks/embeddings for asset_id={asset_id}")

    def list_documents(self):
        # Retrieve all documents and their metadata from the collection
        results = self.collection.get(include=["metadatas", "documents", "ids"])
        print(results)
        print("-----------------------")
        return results