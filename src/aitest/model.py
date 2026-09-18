from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .core import ModelAdapter


@dataclass
class HttpModelAdapter(ModelAdapter):
    """Generic JSON-over-HTTP model adapter.

    The endpoint accepts {"prompt": "..."} and returns {"output": "..."} or {"text": "..."}.
    """

    url: str
    timeout: float = 30.0

    def generate(self, prompt: str) -> str:
        payload = json.dumps({"prompt": prompt}).encode("utf-8")
        request = Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"model request failed: {exc}") from exc

        if not isinstance(body, dict):
            raise RuntimeError("model response must be a JSON object")
        output = body.get("output", body.get("text"))
        if not isinstance(output, str):
            raise RuntimeError("model response must contain string field output or text")
        return output
