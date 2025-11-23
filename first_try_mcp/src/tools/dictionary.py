"""
Dictionary tool using Free Dictionary API.

This tool provides word definitions, pronunciations, and examples without requiring an API key.
"""

from typing import Any, Dict, List

from src.tools.base import APIBasedTool, ToolMetadata
from src.utils.http_client import HTTPClient
from src.utils.exceptions import ToolExecutionError, ValidationError


class DictionaryTool(APIBasedTool):
    """Tool for looking up word definitions."""

    def __init__(self):
        """Initialize dictionary tool."""
        super().__init__(base_url="https://api.dictionaryapi.dev/api/v2/entries/en")

    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name="dictionary",
            description="Look up word definitions, pronunciations, and examples",
            version="1.0.0",
            author="Enterprise MCP Server",
            requires_api_key=False,
        )

    def validate_input(self, **kwargs: Any) -> None:
        """Validate input parameters."""
        word = kwargs.get("word")
        if not word:
            raise ValidationError("word parameter is required")
        if not isinstance(word, str):
            raise ValidationError("word must be a string")
        if len(word.strip()) == 0:
            raise ValidationError("word cannot be empty")
        if not word.replace("-", "").replace("'", "").isalpha():
            raise ValidationError("word must contain only letters, hyphens, or apostrophes")

    async def execute(self, word: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Look up a word in the dictionary.

        Args:
            word: Word to look up
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            Dictionary containing word definitions and related information

        Raises:
            ToolExecutionError: If dictionary lookup fails
        """
        try:
            word = word.strip().lower()
            url = self._build_url(word)

            async with HTTPClient() as client:
                data = await client.get(url)

            # API returns a list of entries
            if not data or not isinstance(data, list):
                raise ToolExecutionError(f"No definition found for '{word}'")

            entry = data[0]
            
            # Extract phonetics
            phonetics = []
            for phonetic in entry.get("phonetics", []):
                if phonetic.get("text") or phonetic.get("audio"):
                    phonetics.append({
                        "text": phonetic.get("text", ""),
                        "audio": phonetic.get("audio", ""),
                    })

            # Extract meanings
            meanings = []
            for meaning in entry.get("meanings", []):
                part_of_speech = meaning.get("partOfSpeech", "")
                definitions = []
                
                for defn in meaning.get("definitions", []):
                    definitions.append({
                        "definition": defn.get("definition", ""),
                        "example": defn.get("example", ""),
                        "synonyms": defn.get("synonyms", []),
                        "antonyms": defn.get("antonyms", []),
                    })
                
                meanings.append({
                    "part_of_speech": part_of_speech,
                    "definitions": definitions,
                    "synonyms": meaning.get("synonyms", []),
                    "antonyms": meaning.get("antonyms", []),
                })

            result = {
                "word": entry.get("word", word),
                "phonetics": phonetics,
                "meanings": meanings,
                "source_urls": entry.get("sourceUrls", []),
            }

            return result

        except ToolExecutionError:
            raise
        except Exception as e:
            raise ToolExecutionError(
                f"Failed to look up word '{word}': {str(e)}"
            ) from e
