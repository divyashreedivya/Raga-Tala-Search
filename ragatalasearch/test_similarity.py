#!/usr/bin/env python
"""
Test script for the semantic similarity search functionality.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ragatalasearch.settings')
django.setup()

from ragas.models import Raga
from ragas.embedding_model import get_embedding_model

def test_semantic_similarity():
    """Test the semantic similarity functionality"""

    print("Testing Semantic Similarity Search")
    print("=" * 40)

    # Get a sample raga
    try:
        raga = Raga.objects.filter(embedding__isnull=False).exclude(embedding='').first()
        if not raga:
            print("No ragas with embeddings found. Please generate embeddings first.")
            return

        print(f"Query Raga: {raga.name}")
        print(f"Arohanam: {raga.arohanam}")
        print(f"Avarohanam: {raga.avarohanam}")
        print()

        # Get embedding model
        model = get_embedding_model()

        # Get query embedding
        query_embedding = raga.get_embedding()
        print(f"Query embedding dimension: {len(query_embedding)}")

        # Get all embeddings
        all_ragas = Raga.objects.exclude(embedding__isnull=True).exclude(embedding='')
        all_embeddings = {}

        for r in all_ragas:
            try:
                emb = r.get_embedding()
                if emb:
                    all_embeddings[r.id] = emb
            except:
                continue

        print(f"Total ragas with embeddings: {len(all_embeddings)}")

        # Find similar ragas
        similar = model.find_similar_ragas(query_embedding, all_embeddings, top_k=5)

        print("\nTop 5 Similar Ragas:")
        print("-" * 20)
        for i, (raga_id, similarity) in enumerate(similar, 1):
            similar_raga = Raga.objects.get(id=raga_id)
            print(".1f"
                  f"Arohanam: {similar_raga.arohanam}")
            print(f"    Avarohanam: {similar_raga.avarohanam}")
            print()

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_semantic_similarity()