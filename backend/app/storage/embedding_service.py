"""
EmbeddingService — embeddings via any OpenAI-compatible /embeddings endpoint
(OpenRouter by default; works with OpenAI, Ollama's /v1, etc.)

Vector dimension is configured via EMBEDDING_DIMENSIONS and must match
the chosen model (text-embedding-3-small = 1536).
"""

import time
import logging
from typing import List, Optional

import requests

from ..config import Config

logger = logging.getLogger('mirofish.embedding')


class EmbeddingService:
    """Generate embeddings via an OpenAI-compatible API."""

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        dimensions: Optional[int] = None,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        self.model = model or Config.EMBEDDING_MODEL
        self.base_url = (base_url or Config.EMBEDDING_BASE_URL).rstrip('/')
        self.api_key = api_key or Config.EMBEDDING_API_KEY
        self.dimensions = dimensions or Config.EMBEDDING_DIMENSIONS
        self.max_retries = max_retries
        self.timeout = timeout
        self._embed_url = f"{self.base_url}/embeddings"

        # Simple in-memory cache (text -> embedding vector)
        # Using dict instead of lru_cache because lists aren't hashable
        self._cache: dict[str, List[float]] = {}
        self._cache_max_size = 2000

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Float vector of Config.EMBEDDING_DIMENSIONS size

        Raises:
            EmbeddingError: If the request fails after retries
        """
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed empty text")

        text = text.strip()

        # Check cache
        if text in self._cache:
            return self._cache[text]

        vectors = self._request_embeddings([text])
        vector = vectors[0]

        # Cache result
        self._cache_put(text, vector)

        return vector

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Processes in batches (OpenRouter accepts up to ~96 inputs per request).

        Args:
            texts: List of input texts
            batch_size: Number of texts per request

        Returns:
            List of embedding vectors (same order as input)
        """
        if not texts:
            return []

        results: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        # Check cache first
        for i, text in enumerate(texts):
            text = text.strip() if text else ""
            if text in self._cache:
                results[i] = self._cache[text]
            elif text:
                uncached_indices.append(i)
                uncached_texts.append(text)
            else:
                # Empty text — zero vector
                results[i] = [0.0] * self.dimensions

        # Batch-embed uncached texts
        if uncached_texts:
            all_vectors: List[List[float]] = []
            for start in range(0, len(uncached_texts), batch_size):
                batch = uncached_texts[start:start + batch_size]
                vectors = self._request_embeddings(batch)
                all_vectors.extend(vectors)

            # Place results and cache
            for idx, vec, text in zip(uncached_indices, all_vectors, uncached_texts):
                results[idx] = vec
                self._cache_put(text, vec)

        return results  # type: ignore

    def _request_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        POST to the OpenAI-compatible /embeddings endpoint with retry.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (input order)
        """
        payload = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float",
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self._embed_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()

                items = data.get("data", [])
                if len(items) != len(texts):
                    raise EmbeddingError(
                        f"Expected {len(texts)} embeddings, got {len(items)}"
                    )

                # API may return items out of order; sort by index
                items.sort(key=lambda item: item.get("index", 0))
                embeddings = [item["embedding"] for item in items]

                for vec in embeddings:
                    if len(vec) != self.dimensions:
                        raise EmbeddingError(
                            f"Model returned {len(vec)}-dim vectors but "
                            f"EMBEDDING_DIMENSIONS={self.dimensions}. "
                            f"Fix EMBEDDING_DIMENSIONS in .env to match the model."
                        )

                return embeddings

            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(
                    f"Embedding API connection failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(
                    f"Embedding API request timed out (attempt {attempt + 1}/{self.max_retries})"
                )
            except requests.exceptions.HTTPError as e:
                last_error = e
                logger.error(f"Embedding API HTTP error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    # Rate limit / server error — retry
                    pass
                else:
                    # Other client error (4xx) — don't retry
                    raise EmbeddingError(f"Embedding request failed: {e}") from e
            except (KeyError, ValueError) as e:
                raise EmbeddingError(f"Invalid embedding API response: {e}") from e

            # Exponential backoff
            if attempt < self.max_retries - 1:
                wait = 2 ** attempt
                logger.info(f"Retrying in {wait}s...")
                time.sleep(wait)

        raise EmbeddingError(
            f"Embedding request failed after {self.max_retries} retries: {last_error}"
        )

    def _cache_put(self, text: str, vector: List[float]) -> None:
        """Add to cache, evicting oldest entries if full."""
        if len(self._cache) >= self._cache_max_size:
            # Remove ~10% of oldest entries
            keys_to_remove = list(self._cache.keys())[:self._cache_max_size // 10]
            for key in keys_to_remove:
                del self._cache[key]
        self._cache[text] = vector

    def health_check(self) -> bool:
        """Check if the embedding endpoint is reachable."""
        try:
            vec = self.embed("health check")
            return len(vec) > 0
        except Exception:
            return False


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""
    pass
