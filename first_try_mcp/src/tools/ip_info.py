"""
IP geolocation tool using ipapi.co API.

This tool provides IP address geolocation information without requiring an API key.
"""

from typing import Any, Dict
import re

from src.tools.base import APIBasedTool, ToolMetadata
from src.utils.http_client import HTTPClient
from src.utils.exceptions import ToolExecutionError, ValidationError


class IPInfoTool(APIBasedTool):
    """Tool for fetching IP geolocation information."""

    def __init__(self):
        """Initialize IP info tool."""
        super().__init__(base_url="https://ipapi.co")

    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name="ip_info",
            description="Get geolocation information for an IP address",
            version="1.0.0",
            author="Enterprise MCP Server",
            requires_api_key=False,
        )

    def _is_valid_ip(self, ip: str) -> bool:
        """
        Validate IP address format.

        Args:
            ip: IP address string

        Returns:
            True if valid, False otherwise
        """
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        ipv6_pattern = r"^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$"
        
        if re.match(ipv4_pattern, ip):
            octets = ip.split(".")
            return all(0 <= int(octet) <= 255 for octet in octets)
        elif re.match(ipv6_pattern, ip):
            return True
        return False

    def validate_input(self, **kwargs: Any) -> None:
        """Validate input parameters."""
        ip_address = kwargs.get("ip_address")
        
        # If no IP provided, we'll use the current IP
        if ip_address is None or ip_address == "":
            return
            
        if not isinstance(ip_address, str):
            raise ValidationError("ip_address must be a string")
        
        if not self._is_valid_ip(ip_address.strip()):
            raise ValidationError(f"Invalid IP address format: {ip_address}")

    async def execute(self, ip_address: str = "", **kwargs: Any) -> Dict[str, Any]:
        """
        Fetch geolocation information for an IP address.

        Args:
            ip_address: IP address to lookup (empty string for current IP)
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            Dictionary containing IP geolocation data

        Raises:
            ToolExecutionError: If IP info fetch fails
        """
        try:
            # If no IP provided, get info for current IP
            endpoint = f"{ip_address}/json/" if ip_address else "json/"
            url = self._build_url(endpoint)

            async with HTTPClient() as client:
                data = await client.get(url)

            # Check for API error
            if data.get("error"):
                error_msg = data.get("reason", "Unknown error")
                # Provide helpful message for rate limiting
                if "rate limit" in error_msg.lower() or data.get("error") is True:
                    raise ToolExecutionError(
                        f"API rate limit exceeded. The free ipapi.co service limits requests. "
                        f"Please try again later or use a specific IP address."
                    )
                raise ToolExecutionError(f"API error: {error_msg}")

            result = {
                "ip": data.get("ip", ""),
                "location": {
                    "city": data.get("city", ""),
                    "region": data.get("region", ""),
                    "region_code": data.get("region_code", ""),
                    "country": data.get("country_name", ""),
                    "country_code": data.get("country_code", ""),
                    "continent_code": data.get("continent_code", ""),
                    "postal": data.get("postal", ""),
                    "latitude": data.get("latitude", ""),
                    "longitude": data.get("longitude", ""),
                    "timezone": data.get("timezone", ""),
                },
                "network": {
                    "asn": data.get("asn", ""),
                    "org": data.get("org", ""),
                    "isp": data.get("isp", ""),
                },
                "currency": {
                    "code": data.get("currency", ""),
                    "name": data.get("currency_name", ""),
                },
                "languages": data.get("languages", ""),
            }

            return result

        except ToolExecutionError:
            raise
        except Exception as e:
            error_msg = str(e)
            # Check for HTTP 429 (rate limit) in exception message
            if "429" in error_msg:
                raise ToolExecutionError(
                    f"API rate limit exceeded. The free ipapi.co service has strict rate limits. "
                    f"Please try again later."
                ) from e
            raise ToolExecutionError(
                f"Failed to fetch IP info for {ip_address or 'current IP'}: {error_msg}"
            ) from e
