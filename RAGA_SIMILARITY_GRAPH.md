# Raga Similarity Graph Implementation

## Overview

This implementation adds a comprehensive Raga Similarity Graph feature to the Raga-Tala-Search project. It enables users to explore relationships between ragas based on shared musical notes (arohanam and avarohanam).

## Features

### 1. **Graph Building with NetworkX**
- Calculates **Jaccard similarity** between ragas based on shared notes
- Fully configurable similarity threshold (0-1)
- Stores edges in database for persistence and querying
- Supports analyzing 981 Carnatic ragas with 379,570+ similarity relationships

### 2. **Data Models**
- **RagaEdge Model**: Stores similarity relationships
  - `source_raga`: Foreign key to source Raga
  - `target_raga`: Foreign key to target Raga
  - `similarity_score`: Jaccard similarity (0-1)
  - `shared_notes`: Number of common notes
  - `total_notes`: Total unique notes in union

### 3. **API Endpoints**

#### Get Graph Data
```
GET /ragas/api/graph/data/
```
Returns JSON with nodes and links formatted for visualization.

```json
{
  "nodes": [
    {
      "id": 1,
      "name": "Raga Name",
      "arohanam": "S R1 G1 M1 P D1 N1 S",
      "avarohanam": "S N1 D1 P M1 G1 R1 S",
      "note_count": 7
    }
  ],
  "links": [
    {
      "source": 1,
      "target": 2,
      "weight": 0.65,
      "shared_notes": 6,
      "total_notes": 9
    }
  ],
  "total_nodes": 981,
  "total_links": 379570
}
```

#### Build/Rebuild Graph
```
POST /ragas/api/graph/build/?threshold=0.3
```
Rebuilds the similarity graph with specified threshold.

#### Get Raga Neighbors
```
GET /ragas/api/graph/neighbors/<raga_id>/
```
Returns similar ragas for a specific raga, sorted by similarity score.

### 4. **Web Visualization**

Access the interactive graph at: `/ragas/graph/`

Features:
- **Force-Directed Layout**: Canvas-based animation using force simulation
- **Interactive Nodes**: Click nodes to see details and similar ragas
- **Real-time Statistics**: Shows graph density, nodes, edges
- **Responsive Design**: Works on different screen sizes
- **Controls**: Load/rebuild graph, view node details

### 5. **Management Command**

Generate or update the graph from command line:

```bash
# Build graph with default threshold (0.3)
python manage.py build_raga_graph

# Build with custom threshold
python manage.py build_raga_graph --threshold 0.5

# View help
python manage.py build_raga_graph --help
```

Output example:
```
Building Raga Similarity Graph with threshold=0.3...
Total ragas in database: 981

==============================================================
✓ Graph built successfully!
==============================================================

Statistics:
  - Nodes (Ragas): 981
  - Edges (Similarities): 379570
  - Graph Density: 0.0784
  - Connected Components: 1
  - Similarity Threshold: 0.30
  - Edges Stored in DB: 379570
  - Average Node Degree: 774.47

You can now view the graph at: /ragas/graph/
```

## Installation & Setup

### 1. Dependencies Added
```
Django==4.2.11
networkx==2.6
django-cors-headers==3.11.0
djangorestframework==3.17.1
```

### 2. Database Migration
```bash
python manage.py makemigrations ragas
python manage.py migrate
```

### 3. Load Raga Data
```bash
python manage.py runscript scripts.ragas_load
```

### 4. Build Graph
```bash
python manage.py build_raga_graph --threshold 0.3
```

## Technical Details

### Similarity Algorithm

The project uses a multi-step similarity strategy to make results musically meaningful.

#### 1. Raga Similarity Graph (note-based)
- Computes **note-content similarity** using **Jaccard index** over unique notes from arohanam + avarohanam.
- Computes **order similarity** using **longest common subsequence (LCS)** for arohanam and avarohanam separately, then averages.
- Combines them as:
  - `combined_similarity = 0.6 * jaccard + 0.4 * sequence_similarity`
- Edges are kept when `combined_similarity >= threshold` (default 0.3).

**Jaccard component**:
$$\text{Jaccard} = \frac{|A \cap B|}{|A \cup B|}$$
Where A/B are unique note sets for two ragas.

**Sequence component**:
- Arohanam similarity = LCS(arohanam1, arohanam2) / max(len(arohanam1), len(arohanam2))
- Avarohanam similarity = LCS(avarohanam1, avarohanam2) / max(len(avarohanam1), len(avarohanam2))
- Sequence similarity = (arohanam_similarity + avarohanam_similarity) / 2

#### 2. Semantic similarity search (embedding + musical content)
- The API-based search uses model embeddings to find the top K candidates by cosine similarity.
- Then it re-ranks candidates by mixing:
  - 60% semantic embedding score (cosine similarity)
  - 40% musical similarity (same combined formula from graph builder)
- This gives stronger priority to shared swaras and sequence order while still using learned semantic relationships.

### Graph Statistics for Current Dataset

- **Total Ragas**: 981
- **Similarity Edges (threshold 0.3)**: 379,570
- **Graph Density**: 0.0784 (7.84% of possible connections)
- **Average Node Degree**: 774.47 (each raga similar to ~774 others)
- **Connected Components**: 1 (all ragas are connected)

### Visualization Technology

- **Canvas-based**: Uses HTML5 Canvas for efficient rendering
- **Force Simulation**: D3-inspired force-directed layout
- **Physics**:
  - Repulsive forces between all node pairs
  - Attractive forces between connected nodes
  - Damping for stability
  - Alpha decay for convergence

### Similarity Threshold Recommendations

- **0.1-0.2**: Very broad connections (conservative threshold)
- **0.3-0.4**: Balanced (default, good for general exploration)  
- **0.5-0.6**: Stricter connections (similar ragas only)
- **0.7+**: Very strict (highly similar ragas only)

