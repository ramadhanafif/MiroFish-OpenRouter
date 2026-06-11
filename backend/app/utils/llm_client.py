"""
LLM Client Wrapper
Unified OpenAI format API calls (OpenRouter, OpenAI, or any compatible server)
"""

import json
import logging
import re
from typing import Any

from openai import OpenAI

from ..config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM Client"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 300.0
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME

        if not self.api_key:
            raise ValueError("LLM_API_KEY not configured")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: dict | None = None,
        retries: int = 2
    ) -> str:
        """
        Send chat request

        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max token count
            response_format: Response format (e.g., JSON mode)
            retries: Extra attempts when the model returns empty content
                     (some models emit native tool-call tokens with no text
                     even when no tools are requested)

        Returns:
            Model response text
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        finish_reason = None
        for attempt in range(retries + 1):
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            if content:
                # Some models (like MiniMax M2.5) include <think>thinking content in response, need to remove
                return re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
            finish_reason = response.choices[0].finish_reason
            if attempt < retries:
                logger.warning(
                    f"LLM returned empty content (finish_reason={finish_reason}), "
                    f"retrying ({attempt + 1}/{retries})"
                )
        raise ValueError(
            f"LLM returned empty content after {retries + 1} attempts "
            f"(finish_reason={finish_reason})"
        )

    def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        retries: int = 2
    ) -> dict[str, Any]:
        """
        Send chat request and return JSON

        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max token count
            retries: Extra attempts when the model returns invalid JSON.
                     Models occasionally produce degenerate output (e.g.
                     endless repetition); a fresh sample usually parses.

        Returns:
            Parsed JSON object
        """
        last_error = None
        for attempt in range(retries + 1):
            try:
                response = self.chat(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
                return self._parse_json(response)
            except ValueError as e:
                last_error = e
                if attempt < retries:
                    logger.warning(
                        f"LLM JSON response invalid, retrying ({attempt + 1}/{retries}): "
                        f"{str(e)[:200]}"
                    )
        raise last_error if last_error is not None else RuntimeError('LLM JSON retries exhausted without an error')

    @staticmethod
    def _parse_json(response: str) -> dict[str, Any]:
        """Parse a JSON object out of an LLM response, tolerating markdown fences and prose."""
        # Clean markdown code block markers
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            pass

        # Some providers ignore response_format and wrap JSON in prose,
        # fall back to the outermost {...} block
        start = cleaned_response.find('{')
        end = cleaned_response.rfind('}')
        if start != -1 and end > start:
            try:
                return json.loads(cleaned_response[start:end + 1])
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Invalid JSON format from LLM: {cleaned_response[:2000]}")
