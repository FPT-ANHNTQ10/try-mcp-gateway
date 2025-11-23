"""
Enterprise MCP HTTP Server

A production-ready MCP server with multiple free API integrations.
"""

from fastmcp import FastMCP
from typing import Dict, Any

from src.config import settings
from src.utils.logger import setup_logging, get_logger
from src.tools.weather import WeatherTool
from src.tools.ip_info import IPInfoTool
from src.tools.dictionary import DictionaryTool
from src.tools.exchange_rate import ExchangeRateTool

# Initialize logging
setup_logging(
    level=settings.log_level,
    log_format=settings.log_format,
    log_file=settings.log_file,
)

logger = get_logger(__name__)

# Initialize MCP server
mcp = FastMCP(settings.server_name)

# Initialize tools
weather_tool = WeatherTool() if settings.enable_weather_tool else None
ip_info_tool = IPInfoTool() if settings.enable_ip_info_tool else None
dictionary_tool = DictionaryTool() if settings.enable_dictionary_tool else None
exchange_rate_tool = ExchangeRateTool() if settings.enable_exchange_rate_tool else None


@mcp.tool()
async def get_weather(location: str) -> Dict[str, Any]:
    """
    Get current weather information for a location.

    Args:
        location: City name, address, or landmark

    Returns:
        Weather data including temperature, conditions, humidity, etc.
    
    Example:
        get_weather(location="London")
        get_weather(location="Tokyo, Japan")
    """
    if not weather_tool:
        return {"error": "Weather tool is disabled"}
    
    logger.info(f"Getting weather for location: {location}")
    return await weather_tool(location=location)


@mcp.tool()
async def get_ip_info(ip_address: str = "") -> Dict[str, Any]:
    """
    Get geolocation information for an IP address.

    Args:
        ip_address: IP address to lookup (leave empty for current IP)

    Returns:
        IP geolocation data including city, country, ISP, etc.
    
    Example:
        get_ip_info()  # Current IP
        get_ip_info(ip_address="8.8.8.8")
    """
    if not ip_info_tool:
        return {"error": "IP info tool is disabled"}
    
    logger.info(f"Getting IP info for: {ip_address or 'current IP'}")
    return await ip_info_tool(ip_address=ip_address)


@mcp.tool()
async def lookup_word(word: str) -> Dict[str, Any]:
    """
    Look up a word in the dictionary.

    Args:
        word: Word to look up

    Returns:
        Dictionary data including definitions, pronunciations, examples, etc.
    
    Example:
        lookup_word(word="serendipity")
        lookup_word(word="ephemeral")
    """
    if not dictionary_tool:
        return {"error": "Dictionary tool is disabled"}
    
    logger.info(f"Looking up word: {word}")
    return await dictionary_tool(word=word)


@mcp.tool()
async def get_exchange_rate(
    base_currency: str,
    target_currency: str = "",
    amount: float = 1.0,
) -> Dict[str, Any]:
    """
    Get currency exchange rates and convert amounts.

    Args:
        base_currency: Base currency code (e.g., 'USD', 'EUR')
        target_currency: Target currency for conversion (optional)
        amount: Amount to convert (default: 1.0)

    Returns:
        Exchange rate data and conversion results
    
    Example:
        get_exchange_rate(base_currency="USD")  # All rates
        get_exchange_rate(base_currency="USD", target_currency="EUR")
        get_exchange_rate(base_currency="USD", target_currency="JPY", amount=100)
    """
    if not exchange_rate_tool:
        return {"error": "Exchange rate tool is disabled"}
    
    logger.info(f"Getting exchange rate: {base_currency} -> {target_currency or 'all'}")
    return await exchange_rate_tool(
        base_currency=base_currency,
        target_currency=target_currency if target_currency else None,
        amount=amount if amount != 1.0 else None,
    )


@mcp.tool()
def greet(name: str) -> str:
    """
    Simple greeting tool (for testing).

    Args:
        name: Name to greet

    Returns:
        Greeting message
    
    Example:
        greet(name="Alice")
    """
    logger.info(f"Greeting: {name}")
    return f"Hello, {name}! Welcome to the Enterprise MCP Server."


def run_server() -> None:
    """Run the MCP HTTP server."""
    logger.info(
        f"Starting {settings.server_name}",
        extra={
            "host": settings.server_host,
            "port": settings.server_port,
            "transport": settings.transport,
            "environment": settings.environment,
        },
    )
    
    # Log enabled tools
    enabled_tools = []
    if settings.enable_weather_tool:
        enabled_tools.append("weather")
    if settings.enable_ip_info_tool:
        enabled_tools.append("ip_info")
    if settings.enable_dictionary_tool:
        enabled_tools.append("dictionary")
    if settings.enable_exchange_rate_tool:
        enabled_tools.append("exchange_rate")
    
    logger.info(f"Enabled tools: {', '.join(enabled_tools)}")
    
    # Run server
    if settings.transport == "http":
        mcp.run(transport="http", host=settings.server_host, port=settings.server_port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
