"""Local Ollama HTTP Client for KathaYantra AI Services.

Provides asynchronous communication with the local Ollama daemon,
handling model inspection, health diagnostics, chat completion, timeouts,
and retry policies with robust error typing.
"""

import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, Optional
import httpx

from app.core.config import settings
from app.schemas.ai import AIOllamaHealthResponse

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for all Ollama-related communication or inference failures."""


class OllamaConnectionError(OllamaError):
    """Raised when the Ollama local daemon cannot be reached."""


class OllamaTimeoutError(OllamaError):
    """Raised when an inference or health request exceeds configured timeouts."""


class OllamaModelNotFoundError(OllamaError):
    """Raised when the requested model tag is not installed in the local Ollama library."""


class OllamaResponseError(OllamaError):
    """Raised when Ollama returns an unexpected status code or malformed JSON payload."""


class OllamaClient:
    """Async client interfacing with the local Ollama API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        connect_timeout: Optional[float] = None,
        read_timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.OLLAMA_MODEL
        self.connect_timeout = connect_timeout or settings.OLLAMA_CONNECT_TIMEOUT
        self.read_timeout = read_timeout or settings.OLLAMA_READ_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else settings.OLLAMA_MAX_RETRIES

    def _get_client(self) -> httpx.AsyncClient:
        """Create an HTTPX async client with configured timeouts."""
        return httpx.AsyncClient(
            timeout=httpx.Timeout(
                timeout=self.read_timeout,
                connect=self.connect_timeout,
                read=self.read_timeout,
                write=10.0,
            )
        )

    def _model_tag_matches(self, target: str, available_names: list[str]) -> bool:
        """Check whether a target tag matches an installed model tag."""
        target_lower = target.lower().strip()
        for name in available_names:
            name_lower = name.lower().strip()
            if target_lower == name_lower:
                return True
            # Matches 'gemma2' against 'gemma2:latest' or 'gemma2:9b'
            if ":" not in target_lower and name_lower.startswith(f"{target_lower}:"):
                return True
            if ":" in target_lower and name_lower == target_lower:
                return True
        return False

    async def list_models(self) -> list[str]:
        """Fetch all installed model tags from the local Ollama service."""
        url = f"{self.base_url}/api/tags"
        try:
            async with self._get_client() as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    raise OllamaResponseError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")
                data = resp.json()
                models = data.get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Failed to connect to local Ollama at {self.base_url}: {e}") from e
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Timeout while querying Ollama tags at {self.base_url}: {e}") from e
        except Exception as e:
            if isinstance(e, OllamaError):
                raise
            raise OllamaResponseError(f"Unexpected error querying Ollama tags: {e}") from e

    async def check_health(self) -> AIOllamaHealthResponse:
        """Examine local Ollama status and verify whether the configured model is ready."""
        url = f"{self.base_url}/api/tags"
        target_model = self.default_model

        try:
            installed = await self.list_models()
            model_found = self._model_tag_matches(target_model, installed)

            if model_found:
                return AIOllamaHealthResponse(
                    status="available",
                    provider="ollama",
                    base_url=self.base_url,
                    configured_model=target_model,
                    model_available=True,
                    installed_models=installed,
                    message=f"Ollama is running locally and model '{target_model}' is installed and ready.",
                )
            else:
                return AIOllamaHealthResponse(
                    status="model_missing",
                    provider="ollama",
                    base_url=self.base_url,
                    configured_model=target_model,
                    model_available=False,
                    installed_models=installed,
                    message=(
                        f"Ollama service responded, but configured model '{target_model}' was not found. "
                        f"Install it locally via: ollama pull {target_model}"
                    ),
                )
        except OllamaConnectionError as e:
            return AIOllamaHealthResponse(
                status="unavailable",
                provider="ollama",
                base_url=self.base_url,
                configured_model=target_model,
                model_available=False,
                installed_models=[],
                message=f"Local Ollama server is unreachable at {self.base_url}. Start with: ollama serve",
            )
        except Exception as e:
            return AIOllamaHealthResponse(
                status="misconfigured",
                provider="ollama",
                base_url=self.base_url,
                configured_model=target_model,
                model_available=False,
                installed_models=[],
                message=f"Error inspecting Ollama: {str(e)}",
            )

    async def is_available(self) -> bool:
        """Quick boolean test for model availability."""
        health = await self.check_health()
        return health.model_available

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """Execute a non-streaming chat completion request against the local Ollama instance."""
        target_model = model or self.default_model
        temp = temperature if temperature is not None else settings.AI_TEMPERATURE
        tokens = max_tokens if max_tokens is not None else settings.AI_MAX_OUTPUT_TOKENS

        payload: dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temp,
                "num_predict": tokens,
            },
        }

        url = f"{self.base_url}/api/chat"
        attempts = 0
        last_error: Optional[Exception] = None

        while attempts <= self.max_retries:
            attempts += 1
            try:
                async with self._get_client() as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 404:
                        raise OllamaModelNotFoundError(
                            f"Model '{target_model}' not found in Ollama library (HTTP 404)."
                        )
                    if resp.status_code != 200:
                        raise OllamaResponseError(
                            f"Ollama returned HTTP error {resp.status_code}: {resp.text}"
                        )
                    data = resp.json()
                    message = data.get("message", {})
                    content = message.get("content", "")
                    if not content:
                        raise OllamaResponseError("Ollama returned an empty response message content.")
                    return content.strip()

            except (httpx.ConnectError, httpx.NetworkError) as e:
                last_error = OllamaConnectionError(f"Connection to Ollama failed at {self.base_url}: {e}")
                if attempts <= self.max_retries:
                    await asyncio.sleep(0.5 * attempts)
                    continue
                raise last_error from e

            except httpx.TimeoutException as e:
                last_error = OllamaTimeoutError(
                    f"Ollama inference timed out after {self.read_timeout}s for model '{target_model}'."
                )
                raise last_error from e

            except Exception as e:
                if isinstance(e, OllamaError):
                    raise
                raise OllamaResponseError(f"Unexpected error during Ollama inference: {e}") from e

        if last_error:
            raise last_error
        raise OllamaError("Chat completion failed after retries.")


# Central singleton instance
ollama_client = OllamaClient()

