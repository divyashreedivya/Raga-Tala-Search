"""
Raga Embedding Model using Contrastive Learning
Generates semantic embeddings for ragas based on their note sequences.
"""

import json
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
from django.conf import settings
import os

class RagaEmbeddingModel:
    """
    Contrastive learning model for generating raga embeddings.
    Uses sentence transformers to encode note sequences as semantic vectors.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', embedding_dim: int = 384):
        """
        Initialize the embedding model.

        Args:
            model_name: Pre-trained sentence transformer model name
            embedding_dim: Dimension of output embeddings
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.model = None
        self.scaler = StandardScaler()

    def load_model(self):
        """Load the sentence transformer model"""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        return self.model

    def extract_features(self, arohanam: str, avarohanam: str) -> str:
        """
        Extract features from raga note sequences for embedding.

        Args:
            arohanam: Space-separated ascending notes
            avarohanam: Space-separated descending notes

        Returns:
            Combined text representation for embedding
        """
        # Clean and combine note sequences
        asc_notes = arohanam.strip() if arohanam else ""
        desc_notes = avarohanam.strip() if avarohanam else ""

        # Create multiple representations for richer embeddings
        features = []

        # Full sequence
        full_sequence = f"{asc_notes} {desc_notes}".strip()
        if full_sequence:
            features.append(f"Full sequence: {full_sequence}")

        # Individual sequences
        if asc_notes:
            features.append(f"Ascending: {asc_notes}")
        if desc_notes:
            features.append(f"Descending: {desc_notes}")

        # Note transitions (pairs)
        if asc_notes:
            asc_list = asc_notes.split()
            for i in range(len(asc_list) - 1):
                features.append(f"Ascending transition: {asc_list[i]} -> {asc_list[i+1]}")

        if desc_notes:
            desc_list = desc_notes.split()
            for i in range(len(desc_list) - 1):
                features.append(f"Descending transition: {desc_list[i]} -> {desc_list[i+1]}")

        # Unique notes
        all_notes = set()
        if asc_notes:
            all_notes.update(asc_notes.split())
        if desc_notes:
            all_notes.update(desc_notes.split())

        if all_notes:
            features.append(f"Unique notes: {' '.join(sorted(all_notes))}")

        return " | ".join(features)

    def generate_embedding(self, features: str) -> List[float]:
        """
        Generate embedding vector from extracted features.

        Args:
            features: Text features extracted from raga

        Returns:
            Embedding vector as list of floats
        """
        self.load_model()

        # Encode the features
        embedding = self.model.encode(features, convert_to_numpy=True)

        # Normalize the embedding
        embedding = embedding / np.linalg.norm(embedding)

        return embedding.tolist()

    def generate_embeddings_batch(self, raga_features: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple ragas in batch.

        Args:
            raga_features: List of feature strings for each raga

        Returns:
            List of embedding vectors
        """
        self.load_model()

        # Encode all features at once
        embeddings = self.model.encode(raga_features, convert_to_numpy=True, batch_size=32)

        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        embeddings = embeddings / norms

        return embeddings.tolist()

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def find_similar_ragas(self, query_embedding: List[float],
                          all_embeddings: Dict[int, List[float]],
                          top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Find most similar ragas using vector similarity.

        Args:
            query_embedding: Embedding of the query raga
            all_embeddings: Dict mapping raga_id to embedding
            top_k: Number of similar ragas to return

        Returns:
            List of (raga_id, similarity_score) tuples
        """
        similarities = []

        for raga_id, embedding in all_embeddings.items():
            similarity = self.compute_similarity(query_embedding, embedding)
            similarities.append((raga_id, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]


# Global model instance
_embedding_model = None

def get_embedding_model() -> RagaEmbeddingModel:
    """Get or create the global embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = RagaEmbeddingModel()
    return _embedding_model