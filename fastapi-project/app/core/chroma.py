import chromadb
from chromadb.config import Settings

class ChromaDBClient:
    def __init__(self, persist_directory="./chroma_migrated", collection_name="documents"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)

    def asset_exists(self, asset_id: str) -> bool:
        # Check if any chunk exists for the asset_id
        results = self.collection.get(where={"asset_id": asset_id}, include=["metadatas"])
        return bool(results and results.get("metadatas"))

    def get_retriever(self, asset_id: str):
        # Use the LangChain VectorStore wrapper over Chroma
        from langchain.vectorstores import Chroma
        from langchain.embeddings import HuggingFaceEmbeddings

        # Set up the retriever that queries only chunks matching this asset_id
        # Filter via where_metadata
        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        store = Chroma(
            client=self.client,
            collection_name=self.collection.name,
            embedding_function=embedding_function,
        )
        retriever = store.as_retriever(
            search_kwargs={"filter": {"asset_id": asset_id}}
        )
        return retriever