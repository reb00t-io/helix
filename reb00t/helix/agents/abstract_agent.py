# abstract_agent.py
from abc import ABC
from typing import Any
import json
import asyncio

from reb00t.common.llm.llm import LLM
from reb00t.common.llm.response import JsonResponse


class AbstractAgent(ABC):
    """Abstract base class for agents that encapsulates LLM client logic."""

    def __init__(self, agent_name, llm=None):
        """
        Initialize the abstract agent with an optional LLM client.

        Args:
            llm: Optional LLM client that provides a generate() method
        """
        if llm is None:
            llm: LLM = LLM(cache=True, instance=agent_name)
        self.llm: LLM = llm

    def generate(self, prompt: str, parse_json: bool = False) -> Any:
        """
        Generate a response using the LLM client or fall back to rule-based logic.

        Args:
            prompt: The prompt to send to the LLM
            parse_json: Whether to attempt parsing the response as JSON; returns JsonResponse if True

        Returns:
            LLM response (string or parsed JSON) or fallback result
        """

        response_format = { "type": "json_object" } if parse_json else None

        try:
            res, _ = asyncio.run(self.llm.query_simple(prompt, response_format=response_format))
        except Exception as e:
            raise e

        if parse_json:
            try:
                res = JsonResponse(res)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse LLM response as JSON: {res}")

        return res
