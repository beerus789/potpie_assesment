from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2", chunk_size=500, chunk_overlap=50):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = words[i:i+self.chunk_size]
            chunks.append(' '.join(chunk))
        return [c for c in chunks if c.strip()]

    def embed(self, text: str) -> Tuple[List[List[float]], List[str]]:
        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError("No text found for embedding.")
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings], chunks