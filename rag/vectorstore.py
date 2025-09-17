from typing import List, Optional, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .chunker import Document


class VectorStore:
    """Vector storage and retrieval using FAISS"""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(embedding_model)
        self.documents: List[Document] = []
        self.index: Optional[faiss.Index] = None
        self.embeddings: Optional[np.ndarray] = None

    def add_documents(self, documents: List[Document]):
        if not documents:
            print("⚠️ No documents to add to vector store")
            return

        self.documents.extend(documents)

        texts = [doc.content for doc in documents]
        new_embeddings = self.encoder.encode(texts)
        if len(new_embeddings.shape) == 1:
            new_embeddings = new_embeddings.reshape(1, -1)

        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)

        print(f"Added {len(documents)} documents to vector store. Total: {len(self.documents)}")

    def search(self, query: str, k: int = 5, company_filter: Optional[str] = None) -> List[Tuple[Document, float]]:
        if self.index is None:
            return []

        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        scores, indices = self.index.search(query_embedding, min(k * 2, len(self.documents)))

        results: List[Tuple[Document, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                if company_filter and doc.company != company_filter:
                    continue
                results.append((doc, float(score)))
                if len(results) >= k:
                    break
        return results


