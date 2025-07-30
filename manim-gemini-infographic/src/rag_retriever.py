import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "./manim_rag_db/manim_faiss.index"
CHUNKS_PATH = "./manim_rag_db/manim_chunks.pkl"
METADATA_PATH = "./manim_rag_db/manim_metadata.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"

_model = None
_index = None
_chunks = None
_metadata = None


def _load_resources():
    global _model, _index, _chunks, _metadata
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    if _index is None:
        _index = faiss.read_index(INDEX_PATH)
    if _chunks is None:
        with open(CHUNKS_PATH, "rb") as f:
            _chunks = pickle.load(f)
    if _metadata is None:
        with open(METADATA_PATH, "rb") as f:
            _metadata = pickle.load(f)


def retrieve_relevant_docs(query, top_k=5):
    """Retrieve top_k relevant documentation chunks for the query."""
    _load_resources()
    query_emb = _model.encode([query])
    distances, indices = _index.search(np.array(query_emb), top_k)
    results = [(_chunks[i], _metadata[i]) for i in indices[0]]
    return results 