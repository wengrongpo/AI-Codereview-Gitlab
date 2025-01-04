import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from core.llm.client.base import BaseClient
from core.llm.types import NotGiven, NOT_GIVEN


class DeepSeekClient(BaseClient):
    def __init__(self, api_key: str = None):
        if not os.getenv("DEEPSEEK_API_KEY"):
            load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set it in the environment variables.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) # DeepSeek supports OpenAI API SDK
        self.default_model = os.getenv("DEEPSEEK_API_MODEL", "deepseek-chat")

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
