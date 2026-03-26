# Raga Tala Search

A Django web application for exploring and searching Indian classical (Carnatic) music ragas and talas with machine learning-powered semantic similarity search.

## Features

### 🔍 Multiple Search Methods
- **Name Search**: Find ragas by their traditional names
- **Arohanam Search**: Search by ascending note sequences
- **Avarohanam Search**: Search by descending note sequences
- **Semantic Similarity Search**: ML-powered search using contrastive learning embeddings
- **Hybrid Similarity Ranking**: Combines embedding similarity with note content + order similarity for more musically relevant results

### 🤖 Machine Learning Integration
- **Contrastive Learning Model**: Trained embeddings for semantic similarity
- **Real-time Recommendations**: Instant similar raga suggestions
- **Vector Search**: Efficient similarity computation using cosine similarity
- **Feature Extraction**: Multi-representation encoding of note sequences
- **Order-aware Matching**: Includes sequence position/fidelity (arohanam and avarohanam order) in ranking and result explanation

### 📊 Graph Visualization
- Interactive raga similarity graphs
- Network analysis of raga relationships
- Visual exploration of melodic connections

## Technical Implementation

### ML Pipeline
1. **Feature Extraction**: Convert note sequences into rich text representations
2. **Embedding Generation**: Use Sentence Transformers (all-MiniLM-L6-v2) for semantic embeddings
3. **Similarity Search**: Cosine similarity on 384-dimensional vectors
4. **Real-time API**: Django REST Framework integration

### Architecture
- **Backend**: Django 6.0+ with SQLite
- **ML Framework**: Transformers, Sentence Transformers
- **Frontend**: Bootstrap 4, HTML5 Canvas for graph visualization
- **APIs**: RESTful endpoints for similarity search

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/raga-tala-search.git
cd raga-tala-search
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
cd ragatalasearch
python manage.py migrate
```

4. Generate embeddings for semantic search:
```bash
python manage.py generate_embeddings
```

5. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Semantic Similarity Search
```http
POST /ragas/api/similarity/search/
Content-Type: application/json

{
  "raga_id": 1,
  "top_k": 10
}
```

### Generate Embeddings
```http
POST /ragas/api/embeddings/generate/
```

### Embedding Status
```http
GET /ragas/api/embeddings/status/
```

## Usage

1. **Traditional Search**: Use the search forms to find ragas by name or note sequences
2. **Semantic Search**: Click "Find Similar Ragas" to use ML-powered similarity search
3. **Graph Exploration**: View interactive similarity graphs and network analysis
4. **API Integration**: Use REST APIs for programmatic access

## Model Details

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Training**: Contrastive learning on note sequence representations
- **Similarity Metric**: Cosine similarity
- **Performance**: Real-time search across 1000+ ragas

[Check it out](https://ragatalasearch.pythonanywhere.com/)