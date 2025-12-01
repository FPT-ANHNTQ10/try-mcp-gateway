"""Base tool class for all MCP tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..data_loader import DataLoader
from ..utils import ToolExecutionError, logger


class BaseTool(ABC):
    """Base class for all MCP tools."""

    def __init__(self, data_loader: DataLoader):
        """
        Initialize base tool.

        Args:
            data_loader: DataLoader instance for accessing data
        """
        self.data_loader = data_loader
        self.tool_name = self.__class__.__name__

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            String output of tool execution

        Raises:
            ToolExecutionError: If execution fails
        """
        pass

    def _format_result(self, title: str, content: str) -> str:
        """
        Format tool result with title and content.

        Args:
            title: Result title
            content: Result content

        Returns:
            Formatted result string
        """
        separator = "=" * 60
        return f"{separator}\n{title}\n{separator}\n{content}\n"

    def _format_section(self, title: str, items: list[str]) -> str:
        """
        Format a section with title and items.

        Args:
            title: Section title
            items: List of items to display

        Returns:
            Formatted section string
        """
        if not items:
            return f"[{title}]: No items\n"

        lines = [f"\n{title}:"]
        for i, item in enumerate(items, 1):
            lines.append(f"  {i}. {item}")
        return "\n".join(lines)

    def _log_execution(self, **kwargs: Any) -> None:
        """
        Log tool execution.

        Args:
            **kwargs: Parameters passed to tool
        """
        params_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.info(f"Executing {self.tool_name}: {params_str}")

    def _log_error(self, error: Exception) -> None:
        """
        Log tool error.

        Args:
            error: Exception that occurred
        """
        logger.error(f"Error in {self.tool_name}: {str(error)}")
