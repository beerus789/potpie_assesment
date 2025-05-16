from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import torch
from app.constant import FILE_SETTINGS


class Embedder:
    def __init__(
        self,
        model_name=FILE_SETTINGS.MODEL_NAME,
        chunk_size=FILE_SETTINGS.CHUNK_SIZE_WORDS,
        chunk_overlap=FILE_SETTINGS.CHUNK_OVERLAP,
    ):
        # Use GPU if available, else fallback to CPU
        device = FILE_SETTINGS.CUDA if torch.cuda.is_available() else FILE_SETTINGS.CPU
        self.model = SentenceTransformer(model_name, device=device)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for embedding.
        Each chunk is chunk_size words, with chunk_overlap words overlap.
        """
        words = text.split()
        step = max(1, self.chunk_size - self.chunk_overlap)
        chunks = []
        for i in range(0, len(words), step):
            chunk = words[i : i + self.chunk_size]
            chunks.append(" ".join(chunk))
        return [c for c in chunks if c.strip()]

    def embed(self, text: str) -> Tuple[List[List[float]], List[str]]:
        """
        Embed the text by chunking and running through the model.
        Returns a tuple of (embeddings, chunk_texts).
        """
        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError("No text found for embedding.")
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings], chunks
