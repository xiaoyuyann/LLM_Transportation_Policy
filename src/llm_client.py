"""
Unified LLM client supporting OpenAI (GPT-4o) and Anthropic (Claude) models.

Usage:
    client = LLMClient(model_name="gpt-4o-2024-08-06")
    response = client.complete(system_prompt, user_prompt)
"""

import json
import os
import re
import traceback

from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Wrapper around OpenAI and Anthropic APIs with a common interface."""

    SUPPORTED_MODELS = {
        "openai": ["gpt-4o-2024-08-06", "gpt-4o-mini"],
        "anthropic": ["claude-sonnet-4-5-20250929", "claude-sonnet-4-6", "claude-opus-4-6"],
    }

    def __init__(self, model_name: str, temperature: float = 0, max_tokens: int = 4096):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.family = self._detect_family(model_name)
        self._client = self._build_client()

    def _detect_family(self, model_name: str) -> str:
        if model_name.startswith("gpt-"):
            return "openai"
        if model_name.startswith("claude-"):
            return "anthropic"
        raise ValueError(
            f"Unrecognized model '{model_name}'. "
            f"Model name must start with 'gpt-' or 'claude-'."
        )

    def _build_client(self):
        if self.family == "openai":
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("Install the openai package: pip install openai")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY not set. Add it to .env or your environment.")
            return OpenAI(api_key=api_key)

        if self.family == "anthropic":
            try:
                import anthropic
            except ImportError:
                raise ImportError("Install the anthropic package: pip install anthropic")
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to .env or your environment.")
            return anthropic.Anthropic(api_key=api_key)

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Strip markdown code fences that Claude sometimes wraps around JSON output,
        e.g. ```json { ... } ``` or ``` { ... } ```.
        Falls back to the raw text if no fence is found.
        """
        text = text.strip()
        # Match ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Also handle a bare leading/trailing fence without closing
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        return text

    def complete(self, system_prompt: str, user_prompt: str) -> dict | None:
        """
        Send a request to the LLM and return the parsed JSON response.

        Returns None if the request fails or the response is not valid JSON.
        """
        try:
            if self.family == "openai":
                resp = self._client.chat.completions.create(
                    model=self.model_name,
                    response_format={"type": "json_object"},
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=120,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return json.loads(resp.choices[0].message.content)

            if self.family == "anthropic":
                resp = self._client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                text = resp.content[0].text if hasattr(resp.content[0], "text") else str(resp.content[0])
                return json.loads(self._extract_json(text))

        except Exception as exc:
            print(f"[ERROR] LLM request failed: {exc}")
            traceback.print_exc()
            return None
