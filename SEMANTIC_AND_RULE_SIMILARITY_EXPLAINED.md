# Semantic + Rule-based Similarity in Raga-Tala-Search

This document explains in detail the two similarity components used in the project and how they are combined for final recommendations.

## 1. Semantic Similarity (Embeddings)

### 1.1 What it is
- Uses a pre-trained model (`SentenceTransformer('all-MiniLM-L6-v2')`) to map ragas to 384-d embeddings.
- Encodes raga melody representation text as vectors.

### 1.2 Feature extraction (from `ragas/embedding_model.py`)
- Full sequence: "`<arohanam> <avarohanam>`"
- Ascending: "`<arohanam>`"
- Descending: "`<avarohanam>`"
- Transitions: "`X -> Y`" for each adjacent pair in ascending and descending.
- Unique notes list.

### 1.3 Embedding generation
- `embedding = model.encode(features, convert_to_numpy=True)`
- normalized: `embedding = embedding / np.linalg.norm(embedding)`

### 1.4 Similarity score
- cosine similarity:

```python
similarity = dot(q, c)/(||q||*||c||)
```

- With L2-normalization: roughly `dot(q,c)`.
- Output range ~[0,1] for same-domain ragas.

## 2. Rule-based similarity (note+order)

### 2.1 Jaccard content similarity (notes)
- A = set(arohanam + avarohanam) for raga1
- B = set(arohanam + avarohanam) for raga2

```math
jaccard = |A \cap B| / |A \cup B|
```

### 2.2 Order similarity (LCS)
- `asc_sim = LCS(arohanam1, arohanam2) / max(len(arohanam1), len(arohanam2))`
- `ava_sim = LCS(avarohanam1, avarohanam2) / max(len(avarohanam1), len(avarohanam2))`
- `sequence_sim = (asc_sim + ava_sim) / 2`

### 2.3 Combined note/order score
- `note_score = 0.6 * jaccard + 0.4 * sequence_sim`

## 3. Final Hybrid Score used in API

In `semantic_similarity_search` (ragas/views.py), for each candidate:

```python
combined_score = 0.6 * semantic_score + 0.4 * note_score
```

- `semantic_score`: cosine similarity from embeddings
- `note_score`: rule-based score above
- Sort candidates descending by `combined_score`

## 4. Example

### Query raga
- `Kanakangi`:
  - arohanam: `S R1 G1 M1 P D1 N1 S`
  - avarohanam: `S N1 D1 P M1 G1 R1 S`

### Candidate raga A
- `Rathnangi`:
  - arohanam: `S R1 G1 M1 P D1 N2 S`
  - avarohanam: `S N2 D1 P M1 G1 R1 S`

### Candidate raga B
- `Senavati`:
  - arohanam: `S R1 G2 M1 P D1 N2 S`
  - avarohanam: `S N2 D1 P M1 G2 R1 S`

#### Rule-based part (approx):
- A: jaccard ~ 6/7, seq~0.92, note_score ~0.6*0.857+0.4*0.92=0.879
- B: jaccard ~ 5/7, seq~0.83, note_score ~0.6*0.714+0.4*0.83=0.764

#### Semantic embedding part (for example):
- A: 0.9965
- B: 0.9961

#### Combined score
- A: 0.6*0.9965 + 0.4*0.879 = 0.9494
- B: 0.6*0.9961 + 0.4*0.764 = 0.9002

Therefore result order: A (Rathnangi) above B (Senavati) with `combined_score`.

## 5. Why combination

- 100% embedding may ignore explicit note identity and literal melodic order used in Carnatic analysis.
- 100% rule-based may miss semantic relations from learned context in embeddings.
- hybrid ensures the result is "musically similar + contextually sensible".

## 6. Semantic Relations from Learned Context (Example)

Embeddings capture not just exact token overlap, but broader meaning through training on many examples.

### What it means
- Each raga is converted into a vector from note-sequence text (arohanam/avarohanam + transitions + unique notes).
- The embedding model (`all-MiniLM-L6-v2`) has been trained on large text corpora to map similar concepts close in vector space.
- So `semantic_score` reflects deep relations like:
  - similar melodic contours
  - common movement patterns
  - same family/genre even with different exact notes
- Not merely exact note matching.

### Carnatic Example
Imagine 3 ragas:
1. **Kalyani** (bright major-style with M2: S R2 G3 M2 P D2 N3 S)
2. **Kharaharapriya** (serious/somber with M1: S R2 G2 M1 P D2 N2 S)
3. **Shankarabharanam** (bright major-style with M1 and N2: S R2 G3 M1 P D2 N2 S)

- Rule-based Jaccard shows:
  - Kalyani (S R2 G3 M2 P D2 N3 S) vs Kharaharapriya (S R2 G2 M1 P D2 N2 S): share R2, P, D2 but differ in G (G3 vs G2), M (M2 vs M1), N (N3 vs N2)
  - Kalyani vs Shankarabharanam: share R2, G3, M1, P, D2 but differ in N
- Embedding can also recognize:
  - Kalyani and Shankarabharanam both have bright, uplifting phrase shapes with sharper gandharams/nishadams
  - Kharaharapriya has softer shuddha gandharas and dhaivatas, with more serious musical character
  - so semantic similarity captures these tonal differences beyond numerical note overlap
- This shows how embeddings learn contextual usage patterns and emotional character of ragas from training data.

### Analogy
- Rule-based: "A and B share 90% same words"
- Semantic: "A and B mean similar thing in practice"
- Embedding context = "A is like B because they are used in same musical sense (phrases/feel)"
