"""Central Asynchronous HTTP Client with Caching, Rate-Limiting, and Retry Logic.

Provides robust HTTP access to open-data APIs with:
- Polite User-Agent headers
- Configurable connection/read timeouts
- Bounded concurrency via asyncio semaphores
- Exponential backoff retry on transient upstream failures
- Respect for HTTP 429 and Retry-After headers
- Response size inspection to prevent memory exhaustion
- In-memory deterministic query cache with configurable TTL
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Optional
import httpx
from app.core.config import settings
from app.integrations.base import (
    AuthenticationError,
    ConnectionTimeoutError,
    ConnectorError,
    NotFoundError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached upstream API response."""

    def __init__(self, data: Any, status_code: int, ttl_seconds: int):
        self.data = data
        self.status_code = status_code
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class KathaHTTPClient:
    """Robust, polite asynchronous HTTP client for KathaYantra API integrations."""

    def __init__(
        self,
        user_agent: Optional[str] = None,
        connect_timeout: Optional[float] = None,
        read_timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        max_concurrency: Optional[int] = None,
        cache_ttl_seconds: Optional[int] = None,
        max_response_size: Optional[int] = None,
    ):
        self.user_agent = user_agent or settings.KATHAYANTRA_USER_AGENT
        self.connect_timeout = connect_timeout or settings.HTTP_CONNECT_TIMEOUT
        self.read_timeout = read_timeout or settings.HTTP_READ_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else settings.HTTP_MAX_RETRIES
        self.max_concurrency = max_concurrency or settings.HTTP_MAX_CONCURRENCY
        self.cache_ttl_seconds = cache_ttl_seconds or settings.HTTP_CACHE_TTL_SECONDS
        self.max_response_size = max_response_size or settings.MAX_RESPONSE_SIZE_BYTES

        self._semaphore = asyncio.Semaphore(self.max_concurrency)
        self._cache: dict[str, CacheEntry] = {}
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            limits = httpx.Limits(
                max_keepalive_connections=self.max_concurrency * 2,
                max_connections=self.max_concurrency * 4,
            )
            timeout = httpx.Timeout(
                timeout=self.read_timeout,
                connect=self.connect_timeout,
                read=self.read_timeout,
            )
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "application/json",
            }
            self._client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                headers=headers,
                follow_redirects=True,
            )
        return self._client

    @staticmethod
    def compute_cache_key(method: str, url: str, params: Optional[dict[str, Any]] = None, body: Optional[str] = None) -> str:
        """Compute a deterministic hash for caching based on method, URL, and sorted parameters."""
        normalized_params = ""
        if params:
            sorted_items = sorted((str(k), str(v)) for k, v in params.items() if v is not None)
            normalized_params = json.dumps(sorted_items)
        raw_key = f"{method.upper()}:{url}:{normalized_params}:{body or ''}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    async def get_json(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        source_id: Optional[str] = None,
        use_cache: bool = True,
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """Fetch JSON data from URL with caching, concurrency bounds, and retries."""
        cache_key = self.compute_cache_key("GET", url, params)
        ttl = ttl_seconds or self.cache_ttl_seconds

        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired:
                logger.debug("Cache hit for URL: %s", url)
                return entry.data
            else:
                del self._cache[cache_key]

        async with self._semaphore:
            data = await self._execute_with_retry("GET", url, params=params, headers=headers, source_id=source_id)
            if use_cache and data is not None:
                self._cache[cache_key] = CacheEntry(data, status_code=200, ttl_seconds=ttl)
            return data

    async def post_json_or_sparql(
        self,
        url: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        source_id: Optional[str] = None,
        use_cache: bool = True,
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """Execute a POST query (e.g. SPARQL query) with caching and retries."""
        body_repr = json.dumps(data, sort_keys=True) if data else None
        cache_key = self.compute_cache_key("POST", url, params, body_repr)
        ttl = ttl_seconds or self.cache_ttl_seconds

        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired:
                return entry.data
            else:
                del self._cache[cache_key]

        async with self._semaphore:
            result = await self._execute_with_retry("POST", url, data=data, params=params, headers=headers, source_id=source_id)
            if use_cache and result is not None:
                self._cache[cache_key] = CacheEntry(result, status_code=200, ttl_seconds=ttl)
            return result

    async def _execute_with_retry(
        self,
        method: str,
        url: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        source_id: Optional[str] = None,
    ) -> Any:
        client = self._get_client()
        attempt = 0
        backoff = 0.5

        merged_headers = {}
        if headers:
            merged_headers.update(headers)

        while True:
            attempt += 1
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=merged_headers)
                elif method.upper() == "POST":
                    response = await client.post(url, data=data, params=params, headers=merged_headers)
                else:
                    response = await client.request(method, url, params=params, data=data, headers=merged_headers)

                # Check response size limit
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > self.max_response_size:
                    raise ConnectorError(
                        f"Response size {content_length} exceeds limit of {self.max_response_size} bytes",
                        source_id=source_id,
                    )

                # HTTP Status handling
                if response.status_code == 200:
                    return response.json()

                if response.status_code == 404:
                    raise NotFoundError(f"Resource not found at {url}", source_id=source_id)

                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed ({response.status_code}) for {url}: {response.text[:200]}",
                        source_id=source_id,
                        status_code=response.status_code,
                    )

                if response.status_code == 429:
                    retry_after_str = response.headers.get("Retry-After")
                    retry_after = int(retry_after_str) if (retry_after_str and retry_after_str.isdigit()) else None
                    if attempt <= self.max_retries and retry_after is not None and retry_after <= 5:
                        logger.warning("HTTP 429 encountered for %s. Sleeping for %ds", url, retry_after)
                        await asyncio.sleep(retry_after)
                        continue
                    raise RateLimitError(
                        f"Rate limit exceeded (HTTP 429) for {url}",
                        source_id=source_id,
                        retry_after=retry_after,
                    )

                # 5xx Server errors - retry
                if response.status_code in (500, 502, 503, 504):
                    if attempt <= self.max_retries:
                        logger.warning(
                            "Transient HTTP %d for %s (attempt %d/%d). Backing off %.1fs",
                            response.status_code,
                            url,
                            attempt,
                            self.max_retries,
                            backoff,
                        )
                        await asyncio.sleep(backoff)
                        backoff *= 2.0
                        continue
                    raise ConnectorError(
                        f"Upstream server error HTTP {response.status_code} for {url} after {attempt} attempts",
                        source_id=source_id,
                        status_code=response.status_code,
                    )

                # Other HTTP errors
                raise ConnectorError(
                    f"Unexpected HTTP {response.status_code} from {url}: {response.text[:200]}",
                    source_id=source_id,
                    status_code=response.status_code,
                )

            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException) as exc:
                if attempt <= self.max_retries:
                    logger.warning(
                        "Timeout connecting to %s (attempt %d/%d). Backing off %.1fs",
                        url,
                        attempt,
                        self.max_retries,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue
                raise ConnectionTimeoutError(
                    f"Connection timed out for {url} after {attempt} attempts: {exc}",
                    source_id=source_id,
                ) from exc

            except httpx.NetworkError as exc:
                if attempt <= self.max_retries:
                    logger.warning(
                        "Network error connecting to %s (attempt %d/%d). Backing off %.1fs",
                        url,
                        attempt,
                        self.max_retries,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue
                raise ConnectorError(
                    f"Network error connecting to {url}: {exc}",
                    source_id=source_id,
                ) from exc

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()

    async def close(self) -> None:
        """Close underlying HTTP client connections."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# Shared singleton client instance
_default_http_client: Optional[KathaHTTPClient] = None


def get_http_client() -> KathaHTTPClient:
    """Retrieve or create the global shared KathaHTTPClient instance."""
    global _default_http_client
    if _default_http_client is None:
        _default_http_client = KathaHTTPClient()
    return _default_http_client
