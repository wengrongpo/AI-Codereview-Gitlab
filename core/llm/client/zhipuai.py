import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from zhipuai import ZhipuAI

from core.llm.client.base import BaseClient
from core.llm.types import NotGiven, NOT_GIVEN


class ZhipuAIClient(BaseClient):
    def __init__(self, api_key: str = None):
        if not os.getenv("ZHIPUAI_API_KEY"):
            load_dotenv()
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set it in the environment variables.")

        self.client = ZhipuAI(api_key=api_key)
        self.default_model = os.getenv("ZHIPUAI_API_MODEL", "GLM-4-Flash")

    def completions(self,
                    messages: List[Dict[str, str]],
                    model: Optional[str] | NotGiven = NOT_GIVEN,
                    ) -> str:
        model = model or self.default_model
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return completion.choices[0].message.content
