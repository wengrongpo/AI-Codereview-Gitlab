import re
from typing import Dict, Any

import yaml

from biz.utils.log import logger
from biz.llm.factory import Factory


class CodeBaseReviewer:
    def __init__(self):
        self.client = Factory().getClient()
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """加载提示词配置"""
        prompt_templates_file = "conf/prompt_templates.yml"
        try:
            with open(prompt_templates_file, "r") as file:
                prompts = yaml.safe_load(file)["codebase_review_prompt"]
                system_prompt = prompts["system_prompt"]
                user_prompt = prompts["user_prompt"]

                if not system_prompt or not user_prompt:
                    raise ValueError("提示词配置为空或格式不正确")

                return {
                    "system_message": {"role": "system", "content": system_prompt},
                    "user_message": {"role": "user", "content": user_prompt},
                }
        except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
            logger.error(f"加载提示词配置失败: {e}")
            raise Exception(f"提示词配置加载失败: {e}")

    def review_code(self, language: str, directory_structure: str) -> str:
        """Review代码，并返回结果"""
        messages = [
            self.prompts["system_message"],
            {
                "role": "user",
                "content": self.prompts["user_message"]["content"].format(
                    language=language,
                    directory_structure=directory_structure,
                ),
            },
        ]
        return self.call_llm(messages)

    def call_llm(self, messages: list) -> str:
        logger.debug(f"向AI发送请求, message:{messages})")
        review_result = self.client.completions(
            messages=messages
        )
        logger.debug(f"收到AI返回结果:{review_result}")
        return review_result
