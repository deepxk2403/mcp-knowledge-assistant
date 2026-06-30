"""Local, free embeddings via FastEmbed.

Lazily initialized so importing this module is cheap; the model (~130 MB) is
downloaded/loaded only on first use and cached for the process lifetime.
"""

from typing import List

from app.config import EMBED_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        _model = TextEmbedding(model_name=EMBED_MODEL)
    return _model


def embed(text: str) -> List[float]:
    """Embed a single string into a plain list of floats."""
    vector = next(iter(_get_model().embed([text])))
    return vector.tolist()


def embed_many(texts: List[str]) -> List[List[float]]:
    """Embed a batch of strings (used later for document chunks)."""
    return [v.tolist() for v in _get_model().embed(texts)]
