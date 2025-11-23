"""
HTTP client utilities with retry logic and error handling.
"""

import asyncio
from typing import Any
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import settings
from src.utils.logger import get_logger
from src.utils.exceptions import APIError, TimeoutError as MCPTimeoutError

logger = get_logger(__name__)


class HTTPClient:
    """HTTP client with retry logic and error handling."""

    def __init__(
        self,
        timeout: int | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
    ):
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Base delay between retries
        """
        self.timeout = timeout or settings.request_timeout
        self.max_retries = max_retries or settings.max_retries
        self.retry_delay = retry_delay or settings.retry_delay
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HTTPClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Perform GET request with retry logic.

        Args:
            url: URL to request
            params: Query parameters
            headers: Request headers

        Returns:
            JSON response data

        Raises:
            APIError: If the request fails
            MCPTimeoutError: If the request times out
        """
        if not self._client:
            raise RuntimeError("HTTPClient must be used as a context manager")

        try:
            logger.info(f"GET request to {url}", extra={"params": params})
            response = await self._client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout for {url}", extra={"error": str(e)})
            raise MCPTimeoutError(f"Request to {url} timed out") from e

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error for {url}",
                extra={
                    "status_code": e.response.status_code,
                    "response": e.response.text,
                },
            )
            raise APIError(
                f"HTTP {e.response.status_code} error for {url}",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

        except httpx.RequestError as e:
            logger.error(f"Request error for {url}", extra={"error": str(e)})
            raise APIError(f"Request failed for {url}: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error for {url}", extra={"error": str(e)})
            raise APIError(f"Unexpected error for {url}: {str(e)}") from e

    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Perform POST request with retry logic.

        Args:
            url: URL to request
            data: Form data
            json: JSON data
            headers: Request headers

        Returns:
            JSON response data

        Raises:
            APIError: If the request fails
            MCPTimeoutError: If the request times out
        """
        if not self._client:
            raise RuntimeError("HTTPClient must be used as a context manager")

        try:
            logger.info(f"POST request to {url}")
            response = await self._client.post(
                url, data=data, json=json, headers=headers
            )
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout for {url}", extra={"error": str(e)})
            raise MCPTimeoutError(f"Request to {url} timed out") from e

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error for {url}",
                extra={
                    "status_code": e.response.status_code,
                    "response": e.response.text,
                },
            )
            raise APIError(
                f"HTTP {e.response.status_code} error for {url}",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

        except httpx.RequestError as e:
            logger.error(f"Request error for {url}", extra={"error": str(e)})
            raise APIError(f"Request failed for {url}: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error for {url}", extra={"error": str(e)})
            raise APIError(f"Unexpected error for {url}: {str(e)}") from e
