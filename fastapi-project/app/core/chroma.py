import chromadb
from chromadb.config import Settings
from app.constant import DIRECTORY, FILE_SETTINGS, FileFormat
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings


# ChromaDBClient provides an interface to ChromaDB for storing and retrieving document embeddings.
class ChromaDBClient:
    def __init__(
        self,
        persist_directory=DIRECTORY.CHROMA_DIR.value,
        collection_name=FileFormat.DOCUMENTS.value,
    ):
        # Initialize ChromaDB persistent client and collection
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)

    def asset_exists(self, asset_id: str) -> bool:
        """
        Check if any chunk exists for the given asset_id in the collection.
        Returns True if found, else False.
        """
        results = self.collection.get(
            where={FileFormat.ASSET_ID.value: asset_id}, include=[FileFormat.METADATAS.value]
        )
        return bool(results and results.get("metadatas"))

    def get_retriever(self, asset_id: str):
        """
        Return a retriever that only searches chunks matching the given asset_id.
        Uses LangChain's Chroma VectorStore wrapper for advanced retrieval.
        """

        # Set up the retriever that queries only chunks matching this asset_id
        embedding_function = HuggingFaceEmbeddings(
            model_name=FILE_SETTINGS.MODEL_NAME
        )
        store = Chroma(
            client=self.client,
            collection_name=self.collection.name,
            embedding_function=embedding_function,
        )
        retriever = store.as_retriever(
            search_kwargs={
                FileFormat.FILTER.value: {FileFormat.ASSET_ID.value: asset_id}
            }
        )
        return retriever
