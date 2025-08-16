

from langchain.llms.base import LLM
from typing import Optional, List
from huggingface_hub import InferenceClient
from pydantic import PrivateAttr
import os

class DeepSeek(LLM):
    model_name: str = "deepseek-ai/DeepSeek-V3"

    # Private attribute (not part of model schema, no validation, no serialization)
    _client: InferenceClient = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = InferenceClient(
            provider="novita",
            api_key=os.getenv("DEEP_SEEK")
        )

    @property
    def _llm_type(self) -> str:
        return "huggingface-chat"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        completion = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message['content']

