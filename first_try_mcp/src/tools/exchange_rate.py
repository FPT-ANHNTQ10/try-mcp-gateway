"""
Exchange rate tool using exchangerate-api.com.

This tool provides currency exchange rates without requiring an API key.
"""

from typing import Any, Dict
from datetime import datetime

from src.tools.base import APIBasedTool, ToolMetadata
from src.utils.http_client import HTTPClient
from src.utils.exceptions import ToolExecutionError, ValidationError


class ExchangeRateTool(APIBasedTool):
    """Tool for fetching currency exchange rates."""

    def __init__(self):
        """Initialize exchange rate tool."""
        super().__init__(base_url="https://open.er-api.com/v6")

    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name="exchange_rate",
            description="Get currency exchange rates and convert between currencies",
            version="1.0.0",
            author="Enterprise MCP Server",
            requires_api_key=False,
        )

    def validate_input(self, **kwargs: Any) -> None:
        """Validate input parameters."""
        base_currency = kwargs.get("base_currency")
        if not base_currency:
            raise ValidationError("base_currency parameter is required")
        if not isinstance(base_currency, str):
            raise ValidationError("base_currency must be a string")
        if len(base_currency) != 3:
            raise ValidationError("base_currency must be a 3-letter currency code")
        if not base_currency.isalpha():
            raise ValidationError("base_currency must contain only letters")

        target_currency = kwargs.get("target_currency")
        if target_currency is not None:
            if not isinstance(target_currency, str):
                raise ValidationError("target_currency must be a string")
            if len(target_currency) != 3:
                raise ValidationError("target_currency must be a 3-letter currency code")
            if not target_currency.isalpha():
                raise ValidationError("target_currency must contain only letters")

        amount = kwargs.get("amount")
        if amount is not None:
            if not isinstance(amount, (int, float)):
                raise ValidationError("amount must be a number")
            if amount <= 0:
                raise ValidationError("amount must be positive")

    async def execute(
        self,
        base_currency: str,
        target_currency: str | None = None,
        amount: float | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Get exchange rates for a base currency.

        Args:
            base_currency: Base currency code (e.g., 'USD')
            target_currency: Target currency code for conversion (optional)
            amount: Amount to convert (optional, defaults to 1)
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            Dictionary containing exchange rate data

        Raises:
            ToolExecutionError: If exchange rate fetch fails
        """
        try:
            base_currency = base_currency.upper()
            url = self._build_url(f"latest/{base_currency}")

            async with HTTPClient() as client:
                data = await client.get(url)

            # Check for API error
            if data.get("result") == "error":
                error_type = data.get("error-type", "Unknown error")
                raise ToolExecutionError(f"Exchange rate API error: {error_type}")

            rates = data.get("rates", {})
            
            result = {
                "base_currency": data.get("base_code", base_currency),
                "last_update": data.get("time_last_update_utc", ""),
                "next_update": data.get("time_next_update_utc", ""),
            }

            # If target currency specified, provide conversion
            if target_currency:
                target_currency = target_currency.upper()
                if target_currency not in rates:
                    raise ToolExecutionError(
                        f"Target currency '{target_currency}' not found"
                    )
                
                rate = rates[target_currency]
                conversion_amount = amount if amount is not None else 1.0
                
                result["conversion"] = {
                    "from": base_currency,
                    "to": target_currency,
                    "rate": rate,
                    "amount": conversion_amount,
                    "result": conversion_amount * rate,
                }
            else:
                # Return all rates
                result["rates"] = rates
                result["available_currencies"] = list(rates.keys())

            return result

        except ToolExecutionError:
            raise
        except Exception as e:
            raise ToolExecutionError(
                f"Failed to fetch exchange rates for {base_currency}: {str(e)}"
            ) from e
