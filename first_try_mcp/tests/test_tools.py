"""
Unit tests for MCP server tools.

Run with: pytest tests/ -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.tools.weather import WeatherTool
from src.tools.ip_info import IPInfoTool
from src.tools.dictionary import DictionaryTool
from src.tools.exchange_rate import ExchangeRateTool
from src.utils.exceptions import ValidationError, ToolExecutionError


class TestWeatherTool:
    """Test suite for WeatherTool."""

    @pytest.fixture
    def weather_tool(self):
        """Create a WeatherTool instance."""
        return WeatherTool()

    def test_metadata(self, weather_tool):
        """Test tool metadata."""
        assert weather_tool.metadata.name == "weather"
        assert weather_tool.metadata.requires_api_key is False
        assert "weather" in weather_tool.metadata.description.lower()

    def test_validate_input_valid(self, weather_tool):
        """Test input validation with valid data."""
        weather_tool.validate_input(location="London")
        # Should not raise

    def test_validate_input_missing(self, weather_tool):
        """Test input validation with missing location."""
        with pytest.raises(ValidationError, match="location parameter is required"):
            weather_tool.validate_input()

    def test_validate_input_empty(self, weather_tool):
        """Test input validation with empty location."""
        with pytest.raises(ValidationError, match="location cannot be empty"):
            weather_tool.validate_input(location="   ")

    def test_validate_input_invalid_type(self, weather_tool):
        """Test input validation with invalid type."""
        with pytest.raises(ValidationError, match="location must be a string"):
            weather_tool.validate_input(location=123)

    @pytest.mark.asyncio
    async def test_execute_success(self, weather_tool):
        """Test successful weather fetch."""
        mock_data = {
            "current_condition": [{
                "temp_C": "15",
                "temp_F": "59",
                "FeelsLikeC": "14",
                "FeelsLikeF": "57",
                "weatherDesc": [{"value": "Partly cloudy"}],
                "humidity": "72",
                "precipMM": "0.0",
                "pressure": "1013",
                "windspeedKmph": "13",
                "winddir16Point": "WSW",
                "cloudcover": "75",
                "uvIndex": "3",
                "visibility": "10",
                "observation_time": "02:15 PM",
            }],
            "nearest_area": [{
                "areaName": [{"value": "London"}],
                "country": [{"value": "United Kingdom"}],
                "region": [{"value": "Greater London"}],
            }],
        }

        with patch("src.tools.weather.HTTPClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_data
            mock_client.return_value = mock_instance

            result = await weather_tool.execute(location="London")

            assert result["location"]["name"] == "London"
            assert result["current"]["temperature_c"] == "15"
            assert result["current"]["condition"] == "Partly cloudy"


class TestIPInfoTool:
    """Test suite for IPInfoTool."""

    @pytest.fixture
    def ip_info_tool(self):
        """Create an IPInfoTool instance."""
        return IPInfoTool()

    def test_metadata(self, ip_info_tool):
        """Test tool metadata."""
        assert ip_info_tool.metadata.name == "ip_info"
        assert ip_info_tool.metadata.requires_api_key is False

    def test_is_valid_ip_ipv4(self, ip_info_tool):
        """Test IPv4 validation."""
        assert ip_info_tool._is_valid_ip("8.8.8.8") is True
        assert ip_info_tool._is_valid_ip("192.168.1.1") is True
        assert ip_info_tool._is_valid_ip("256.1.1.1") is False
        assert ip_info_tool._is_valid_ip("1.2.3") is False

    def test_validate_input_valid(self, ip_info_tool):
        """Test input validation with valid IP."""
        ip_info_tool.validate_input(ip_address="8.8.8.8")
        ip_info_tool.validate_input(ip_address="")  # Empty for current IP
        # Should not raise

    def test_validate_input_invalid(self, ip_info_tool):
        """Test input validation with invalid IP."""
        with pytest.raises(ValidationError, match="Invalid IP address format"):
            ip_info_tool.validate_input(ip_address="invalid")

    @pytest.mark.asyncio
    async def test_execute_success(self, ip_info_tool):
        """Test successful IP info fetch."""
        mock_data = {
            "ip": "8.8.8.8",
            "city": "Mountain View",
            "region": "California",
            "region_code": "CA",
            "country_name": "United States",
            "country_code": "US",
            "continent_code": "NA",
            "postal": "94035",
            "latitude": "37.386",
            "longitude": "-122.0838",
            "timezone": "America/Los_Angeles",
            "asn": "AS15169",
            "org": "GOOGLE",
            "isp": "Google LLC",
            "currency": "USD",
            "currency_name": "US Dollar",
            "languages": "en-US",
        }

        with patch("src.tools.ip_info.HTTPClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_data
            mock_client.return_value = mock_instance

            result = await ip_info_tool.execute(ip_address="8.8.8.8")

            assert result["ip"] == "8.8.8.8"
            assert result["location"]["city"] == "Mountain View"
            assert result["network"]["org"] == "GOOGLE"


class TestDictionaryTool:
    """Test suite for DictionaryTool."""

    @pytest.fixture
    def dictionary_tool(self):
        """Create a DictionaryTool instance."""
        return DictionaryTool()

    def test_metadata(self, dictionary_tool):
        """Test tool metadata."""
        assert dictionary_tool.metadata.name == "dictionary"
        assert dictionary_tool.metadata.requires_api_key is False

    def test_validate_input_valid(self, dictionary_tool):
        """Test input validation with valid word."""
        dictionary_tool.validate_input(word="hello")
        dictionary_tool.validate_input(word="well-being")
        # Should not raise

    def test_validate_input_invalid(self, dictionary_tool):
        """Test input validation with invalid word."""
        with pytest.raises(ValidationError):
            dictionary_tool.validate_input()  # Missing word
        
        with pytest.raises(ValidationError):
            dictionary_tool.validate_input(word="")  # Empty
        
        with pytest.raises(ValidationError):
            dictionary_tool.validate_input(word="hello123")  # Contains numbers

    @pytest.mark.asyncio
    async def test_execute_success(self, dictionary_tool):
        """Test successful dictionary lookup."""
        mock_data = [{
            "word": "hello",
            "phonetics": [{"text": "/həˈloʊ/", "audio": ""}],
            "meanings": [{
                "partOfSpeech": "interjection",
                "definitions": [{
                    "definition": "Used as a greeting",
                    "example": "Hello, how are you?",
                    "synonyms": ["hi", "hey"],
                    "antonyms": ["goodbye"],
                }],
                "synonyms": [],
                "antonyms": [],
            }],
            "sourceUrls": ["https://en.wiktionary.org/wiki/hello"],
        }]

        with patch("src.tools.dictionary.HTTPClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_data
            mock_client.return_value = mock_instance

            result = await dictionary_tool.execute(word="hello")

            assert result["word"] == "hello"
            assert len(result["meanings"]) > 0
            assert result["meanings"][0]["part_of_speech"] == "interjection"


class TestExchangeRateTool:
    """Test suite for ExchangeRateTool."""

    @pytest.fixture
    def exchange_rate_tool(self):
        """Create an ExchangeRateTool instance."""
        return ExchangeRateTool()

    def test_metadata(self, exchange_rate_tool):
        """Test tool metadata."""
        assert exchange_rate_tool.metadata.name == "exchange_rate"
        assert exchange_rate_tool.metadata.requires_api_key is False

    def test_validate_input_valid(self, exchange_rate_tool):
        """Test input validation with valid data."""
        exchange_rate_tool.validate_input(base_currency="USD")
        exchange_rate_tool.validate_input(
            base_currency="USD", target_currency="EUR", amount=100
        )
        # Should not raise

    def test_validate_input_invalid(self, exchange_rate_tool):
        """Test input validation with invalid data."""
        with pytest.raises(ValidationError):
            exchange_rate_tool.validate_input()  # Missing base_currency
        
        with pytest.raises(ValidationError, match="3-letter currency code"):
            exchange_rate_tool.validate_input(base_currency="US")  # Too short
        
        with pytest.raises(ValidationError, match="must be positive"):
            exchange_rate_tool.validate_input(base_currency="USD", amount=-10)

    @pytest.mark.asyncio
    async def test_execute_all_rates(self, exchange_rate_tool):
        """Test getting all exchange rates."""
        mock_data = {
            "result": "success",
            "base_code": "USD",
            "time_last_update_utc": "Wed, 20 Nov 2025 00:00:01 +0000",
            "time_next_update_utc": "Thu, 21 Nov 2025 00:00:01 +0000",
            "rates": {
                "EUR": 0.8423,
                "GBP": 0.7321,
                "JPY": 110.25,
            },
        }

        with patch("src.tools.exchange_rate.HTTPClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_data
            mock_client.return_value = mock_instance

            result = await exchange_rate_tool.execute(base_currency="USD")

            assert result["base_currency"] == "USD"
            assert "rates" in result
            assert result["rates"]["EUR"] == 0.8423

    @pytest.mark.asyncio
    async def test_execute_conversion(self, exchange_rate_tool):
        """Test currency conversion."""
        mock_data = {
            "result": "success",
            "base_code": "USD",
            "time_last_update_utc": "Wed, 20 Nov 2025 00:00:01 +0000",
            "time_next_update_utc": "Thu, 21 Nov 2025 00:00:01 +0000",
            "rates": {
                "EUR": 0.8423,
                "GBP": 0.7321,
            },
        }

        with patch("src.tools.exchange_rate.HTTPClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_data
            mock_client.return_value = mock_instance

            result = await exchange_rate_tool.execute(
                base_currency="USD", target_currency="EUR", amount=100
            )

            assert result["conversion"]["from"] == "USD"
            assert result["conversion"]["to"] == "EUR"
            assert result["conversion"]["amount"] == 100
            assert result["conversion"]["result"] == 84.23
