import json
import os
import time
from typing import Any, Dict

from openai import OpenAI


class LLMClient:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        base_url = os.getenv("OPENAI_BASE_URL")
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

    def generate_json(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                )

                text = response.choices[0].message.content or ""
                return self._parse_json(text)
            except Exception as exc:
                last_error = exc
                if attempt < max_retries:
                    time.sleep(0.6 * (attempt + 1))
                    continue
                raise

        if last_error:
            raise last_error
        raise RuntimeError("LLM request failed without an error")

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and start < end:
                return json.loads(text[start : end + 1])
            raise ValueError("Model output is not valid JSON")
