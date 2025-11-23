"""
Weather information tool using wttr.in API.

This tool provides weather information for any location without requiring an API key.
"""

from typing import Any, Dict
from pydantic import Field

from src.tools.base import APIBasedTool, ToolMetadata
from src.utils.http_client import HTTPClient
from src.utils.exceptions import ToolExecutionError, ValidationError


class WeatherTool(APIBasedTool):
    """Tool for fetching weather information."""

    def __init__(self):
        """Initialize weather tool."""
        super().__init__(base_url="https://wttr.in")

    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name="weather",
            description="Get current weather information for any location",
            version="1.0.0",
            author="Enterprise MCP Server",
            requires_api_key=False,
        )

    def validate_input(self, **kwargs: Any) -> None:
        """Validate input parameters."""
        location = kwargs.get("location")
        if not location:
            raise ValidationError("location parameter is required")
        if not isinstance(location, str):
            raise ValidationError("location must be a string")
        if len(location.strip()) == 0:
            raise ValidationError("location cannot be empty")

    async def execute(self, location: str, format: str = "j1", **kwargs: Any) -> Dict[str, Any]:
        """
        Fetch weather information for a location.

        Args:
            location: Location name (city, address, landmark, etc.)
            format: Response format (j1 for JSON)
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            Dictionary containing weather data

        Raises:
            ToolExecutionError: If weather fetch fails
        """
        try:
            url = self._build_url(location)
            params = {"format": format}

            async with HTTPClient() as client:
                data = await client.get(url, params=params)

            # Extract relevant weather information
            current = data.get("current_condition", [{}])[0]
            location_info = data.get("nearest_area", [{}])[0]

            result = {
                "location": {
                    "name": location_info.get("areaName", [{}])[0].get("value", location),
                    "country": location_info.get("country", [{}])[0].get("value", ""),
                    "region": location_info.get("region", [{}])[0].get("value", ""),
                },
                "current": {
                    "temperature_c": current.get("temp_C", ""),
                    "temperature_f": current.get("temp_F", ""),
                    "feels_like_c": current.get("FeelsLikeC", ""),
                    "feels_like_f": current.get("FeelsLikeF", ""),
                    "condition": current.get("weatherDesc", [{}])[0].get("value", ""),
                    "humidity": current.get("humidity", ""),
                    "precipitation_mm": current.get("precipMM", ""),
                    "pressure_mb": current.get("pressure", ""),
                    "wind_speed_kmph": current.get("windspeedKmph", ""),
                    "wind_direction": current.get("winddir16Point", ""),
                    "cloud_cover": current.get("cloudcover", ""),
                    "uv_index": current.get("uvIndex", ""),
                    "visibility_km": current.get("visibility", ""),
                },
                "observation_time": current.get("observation_time", ""),
            }

            return result

        except Exception as e:
            raise ToolExecutionError(
                f"Failed to fetch weather for {location}: {str(e)}"
            ) from e
