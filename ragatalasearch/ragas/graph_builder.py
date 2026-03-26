"""
Raga Similarity Graph Builder
Builds a graph of ragas based on similarity of arohanam and avarohanam notes.
Uses Jaccard similarity + Longest Common Subsequence to compute edge weights.
Considers both the notes present and their order in the raga sequences.
"""

import networkx as nx
from itertools import combinations
from typing import Dict, Set, Tuple, List
from django.db import transaction

from ragas.models import Raga, RagaEdge


def extract_notes(arohanam: str, avarohanam: str) -> Set[str]:
    """
    Extract unique notes from arohanam and avarohanam strings.
    Notes are space-separated in CSV data (e.g., "S R1 G1 M1 P D1 N1 S")
    
    Args:
        arohanam: String of space-separated notes in ascending order
        avarohanam: String of space-separated notes in descending order
    
    Returns:
        Set of unique notes
    """
    notes = set()
    if arohanam:
        notes.update(arohanam.strip().split())
    if avarohanam:
        notes.update(avarohanam.strip().split())
    return notes


def extract_note_sequences(arohanam: str, avarohanam: str) -> Tuple[List[str], List[str]]:
    """
    Extract note sequences preserving their order.
    
    Args:
        arohanam: String of space-separated notes in ascending order
        avarohanam: String of space-separated notes in descending order
    
    Returns:
        Tuple of (arohanam_sequence, avarohanam_sequence) as lists of notes
    """
    asc_sequence = arohanam.strip().split() if arohanam else []
    desc_sequence = avarohanam.strip().split() if avarohanam else []
    return asc_sequence, desc_sequence


def longest_common_subsequence(seq1: List[str], seq2: List[str]) -> int:
    """
    Calculate the length of the longest common subsequence between two sequences.
    LCS measures how many notes appear in the same order in both ragas.
    
    Args:
        seq1: First sequence of notes
        seq2: Second sequence of notes
    
    Returns:
        Length of LCS
    """
    if not seq1 or not seq2:
        return 0
    
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]


def calculate_sequence_similarity(arohanam1: str, avarohanam1: str, 
                                  arohanam2: str, avarohanam2: str) -> float:
    """
    Calculate sequence similarity considering the order of notes.
    Compares arohanam sequences and avarohanam sequences separately.
    
    Args:
        arohanam1, avarohanam1: Note sequences from first raga
        arohanam2, avarohanam2: Note sequences from second raga
    
    Returns:
        Sequence similarity score (0-1)
    """
    asc1, desc1 = extract_note_sequences(arohanam1, avarohanam1)
    asc2, desc2 = extract_note_sequences(arohanam2, avarohanam2)
    
    if not asc1 or not asc2 or not desc1 or not desc2:
        return 0.0
    
    # Calculate LCS for arohanam (ascending)
    lcs_asc = longest_common_subsequence(asc1, asc2)
    max_asc = max(len(asc1), len(asc2))
    sim_asc = lcs_asc / max_asc if max_asc > 0 else 0
    
    # Calculate LCS for avarohanam (descending)
    lcs_desc = longest_common_subsequence(desc1, desc2)
    max_desc = max(len(desc1), len(desc2))
    sim_desc = lcs_desc / max_desc if max_desc > 0 else 0
    
    # Average of arohanam and avarohanam sequence similarity
    return (sim_asc + sim_desc) / 2


def calculate_combined_similarity(notes1: Set[str], notes2: Set[str],
                                 arohanam1: str, avarohanam1: str,
                                 arohanam2: str, avarohanam2: str) -> Tuple[float, int, int]:
    """
    Calculate similarity considering both note content and order.
    Combines Jaccard similarity (content) with sequence similarity (order).
    
    Args:
        notes1, notes2: Sets of unique notes from each raga
        arohanam1, avarohanam1: Full note sequences from first raga
        arohanam2, avarohanam2: Full note sequences from second raga
    
    Returns:
        Tuple of (combined_similarity_score, num_shared_notes, total_unique_notes)
    """
    if not notes1 or not notes2:
        return 0.0, 0, 0
    
    # Jaccard similarity (60% weight) - content matching
    intersection = notes1 & notes2
    union = notes1 | notes2
    
    shared_count = len(intersection)
    union_count = len(union)
    
    jaccard_sim = shared_count / union_count if union_count > 0 else 0.0
    
    # Sequence similarity (40% weight) - order matching
    sequence_sim = calculate_sequence_similarity(arohanam1, avarohanam1,
                                               arohanam2, avarohanam2)
    
    # Combined similarity: weighted average
    # More weight on Jaccard (notes must match) but also consider order
    combined_similarity = (0.6 * jaccard_sim) + (0.4 * sequence_sim)
    
    return combined_similarity, shared_count, union_count


def calculate_jaccard_similarity(notes1: Set[str], notes2: Set[str]) -> Tuple[float, int, int]:
    """
    Calculate Jaccard similarity between two sets of notes.
    Jaccard similarity = |intersection| / |union|
    
    Args:
        notes1: Set of notes from first raga
        notes2: Set of notes from second raga
    
    Returns:
        Tuple of (similarity_score, num_shared_notes, total_unique_notes)
    """
    if not notes1 or not notes2:
        return 0.0, 0, 0
    
    intersection = notes1 & notes2
    union = notes1 | notes2
    
    shared_count = len(intersection)
    union_count = len(union)
    
    similarity = shared_count / union_count if union_count > 0 else 0.0
    
    return similarity, shared_count, union_count



def build_raga_graph(similarity_threshold: float = 0.3) -> nx.Graph:
    """
    Build a similarity graph of ragas based on shared notes and their order.
    
    Uses a combined similarity metric:
    - 60% weight: Jaccard similarity (which notes are shared)
    - 40% weight: Sequence similarity (order of notes in arohanam/avarohanam)
    
    Args:
        similarity_threshold: Minimum combined similarity to create an edge (0-1)
    
    Returns:
        NetworkX Graph object with ragas as nodes and similarities as edges
    
    Raises:
        ValueError: If similarity_threshold is not between 0 and 1
    """
    if not (0 <= similarity_threshold <= 1):
        raise ValueError("similarity_threshold must be between 0 and 1")
    
    # Create graph
    graph = nx.Graph()
    
    # Get all ragas from database
    all_ragas = list(Raga.objects.all())
    
    if len(all_ragas) < 2:
        raise ValueError("Need at least 2 ragas to build a graph")
    
    # Extract notes for all ragas
    raga_notes: Dict[int, Set[str]] = {}
    for raga in all_ragas:
        raga_notes[raga.id] = extract_notes(raga.arohanam, raga.avarohanam)
        # Add raga as node with metadata
        graph.add_node(
            raga.id,
            name=raga.name,
            arohanam=raga.arohanam,
            avarohanam=raga.avarohanam,
            notes_count=len(raga_notes[raga.id])
        )
    
    # Calculate pairwise similarities and add edges
    edges_to_create = []
    
    for raga1, raga2 in combinations(all_ragas, 2):
        notes1 = raga_notes[raga1.id]
        notes2 = raga_notes[raga2.id]
        
        # Use combined similarity that considers both note content and order
        similarity, shared, total = calculate_combined_similarity(
            notes1, notes2,
            raga1.arohanam, raga1.avarohanam,
            raga2.arohanam, raga2.avarohanam
        )
        
        # Only add edge if similarity exceeds threshold
        if similarity >= similarity_threshold:
            graph.add_edge(
                raga1.id,
                raga2.id,
                weight=similarity,
                shared_notes=shared,
                total_notes=total
            )
            edges_to_create.append({
                'source_raga_id': raga1.id,
                'target_raga_id': raga2.id,
                'similarity_score': similarity,
                'shared_notes': shared,
                'total_notes': total
            })
    
    return graph, edges_to_create


@transaction.atomic
def store_edges_in_database(edges_data: list) -> int:
    """
    Store edge data in the RagaEdge model.
    Clears existing edges and stores new ones.
    
    Args:
        edges_data: List of edge dictionaries with source, target, and scores
    
    Returns:
        Number of edges created
    """
    # Clear existing edges
    RagaEdge.objects.all().delete()
    
    # Create new edges
    edges_to_create = [
        RagaEdge(
            source_raga_id=edge['source_raga_id'],
            target_raga_id=edge['target_raga_id'],
            similarity_score=edge['similarity_score'],
            shared_notes=edge['shared_notes'],
            total_notes=edge['total_notes']
        )
        for edge in edges_data
    ]
    
    created_edges = RagaEdge.objects.bulk_create(edges_to_create)
    return len(created_edges)


def generate_raga_similarity_graph(similarity_threshold: float = 0.3) -> Dict:
    """
    Main function to generate and store the raga similarity graph.
    
    Args:
        similarity_threshold: Minimum similarity to create edges
    
    Returns:
        Dictionary with statistics about the generated graph
    """
    # Build the graph
    graph, edges_data = build_raga_graph(similarity_threshold)
    
    # Store edges in database
    edges_count = store_edges_in_database(edges_data)
    
    # Calculate graph statistics
    stats = {
        'nodes_count': graph.number_of_nodes(),
        'edges_count': graph.number_of_edges(),
        'density': nx.density(graph),
        'connected_components': nx.number_connected_components(graph),
        'similarity_threshold': similarity_threshold,
        'edges_stored': edges_count,
        'graph': graph
    }
    
    return stats


def get_graph_data_for_visualization() -> Dict:
    """
    Prepare graph data for HTML5 Canvas visualization.
    
    Returns:
        Dictionary with 'nodes' and 'links' arrays formatted for Canvas rendering
    """
    ragas = Raga.objects.all()
    edges = RagaEdge.objects.select_related('source_raga', 'target_raga').all()
    
    # Create nodes array
    nodes = []
    for raga in ragas:
        note_count = len(extract_notes(raga.arohanam, raga.avarohanam))
        nodes.append({
            'id': raga.id,
            'name': raga.name,
            'label': raga.name,
            'title': f"{raga.name}\nNotes: {note_count}",
            'arohanam': raga.arohanam,
            'avarohanam': raga.avarohanam,
            'note_count': note_count,
            'value': note_count,  # For sizing nodes
        })
    
    # Create links array
    links = []
    for edge in edges:
        links.append({
            'source': edge.source_raga_id,
            'target': edge.target_raga_id,
            'value': edge.similarity_score,
            'weight': edge.similarity_score,
            'shared_notes': edge.shared_notes,
            'total_notes': edge.total_notes,
            'label': f"Similarity: {edge.similarity_score:.2%}"
        })
    
    return {
        'nodes': nodes,
        'links': links,
        'total_nodes': len(nodes),
        'total_links': len(links)
    }


def get_raga_neighbors(raga_id: int, depth: int = 1) -> Dict:
    """
    Get neighbors of a raga in the similarity graph.
    
    Args:
        raga_id: ID of the raga to find neighbors for
        depth: How many levels deep to traverse
    
    Returns:
        Dictionary with neighbors and their connection strengths
    """
    raga = Raga.objects.get(id=raga_id)
    
    neighbors = {
        'raga': {
            'id': raga.id,
            'name': raga.name,
            'arohanam': raga.arohanam,
            'avarohanam': raga.avarohanam,
        },
        'similar_ragas': []
    }
    
    # Get direct connections
    edges = RagaEdge.objects.filter(
        source_raga_id=raga_id
    ).select_related('target_raga') | RagaEdge.objects.filter(
        target_raga_id=raga_id
    ).select_related('source_raga')
    
    seen = {raga_id}
    
    for edge in edges:
        connected_raga = edge.target_raga if edge.source_raga_id == raga_id else edge.source_raga
        
        if connected_raga.id not in seen:
            seen.add(connected_raga.id)
            notes = extract_notes(connected_raga.arohanam, connected_raga.avarohanam)
            neighbors['similar_ragas'].append({
                'id': connected_raga.id,
                'name': connected_raga.name,
                'arohanam': connected_raga.arohanam,
                'avarohanam': connected_raga.avarohanam,
                'similarity_score': edge.similarity_score,
                'shared_notes': edge.shared_notes,
                'note_count': len(notes)
            })
    
    # Sort by similarity
    neighbors['similar_ragas'].sort(
        key=lambda x: x['similarity_score'],
        reverse=True
    )
    
    return neighbors
