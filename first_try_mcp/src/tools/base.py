"""
Base classes for MCP tools.

This module provides abstract base classes and interfaces for implementing
MCP tools with consistent structure and behavior.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ToolMetadata(BaseModel):
    """Metadata for a tool."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    version: str = Field(default="1.0.0", description="Tool version")
    author: str = Field(default="", description="Tool author")
    requires_api_key: bool = Field(
        default=False, description="Whether tool requires an API key"
    )


class BaseTool(ABC):
    """
    Abstract base class for MCP tools.

    All tools should inherit from this class and implement the execute method.
    """

    def __init__(self):
        """Initialize the tool."""
        self.metadata = self._get_metadata()
        self.logger = get_logger(
            f"{__name__}.{self.__class__.__name__}",
            tool=self.metadata.name,
        )

    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        """
        Get tool metadata.

        Returns:
            ToolMetadata instance
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Dictionary containing the tool result

        Raises:
            ToolExecutionError: If tool execution fails
        """
        pass

    def validate_input(self, **kwargs: Any) -> None:
        """
        Validate tool input parameters.

        Args:
            **kwargs: Tool-specific parameters

        Raises:
            ValidationError: If validation fails
        """
        pass

    async def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Call the tool (convenience method).

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Dictionary containing the tool result
        """
        self.logger.info(f"Executing tool: {self.metadata.name}", extra=kwargs)
        try:
            self.validate_input(**kwargs)
            result = await self.execute(**kwargs)
            self.logger.info(f"Tool execution successful: {self.metadata.name}")
            return result
        except Exception as e:
            self.logger.error(
                f"Tool execution failed: {self.metadata.name}",
                extra={"error": str(e)},
            )
            raise


class APIBasedTool(BaseTool):
    """
    Base class for tools that interact with external APIs.

    Provides common functionality for API-based tools.
    """

    def __init__(self, base_url: str):
        """
        Initialize API-based tool.

        Args:
            base_url: Base URL for the API
        """
        super().__init__()
        self.base_url = base_url.rstrip("/")

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from base URL and endpoint.

        Args:
            endpoint: API endpoint

        Returns:
            Full URL
        """
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"
