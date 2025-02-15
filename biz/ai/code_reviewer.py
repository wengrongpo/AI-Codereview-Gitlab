import json
import os
from pathlib import Path

from biz.utils.log import logger
from core.llm.factory import Factory


class CodeReviewer:
    def __init__(self):
        self.client = Factory().getClient()
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> dict:
        """加载提示词配置"""
        system_message = os.getenv("CODE_REVIEW_SYSTEM_MESSAGE")
        user_message = os.getenv("CODE_REVIEW_USER_MESSAGE")
        
        if not system_message or not user_message:
            logger.warning("环境变量中未找到提示词配置，使用默认配置")
            return self._get_default_prompts()
            
        return {
            "code_review": {
                "system_message": {
                    "role": "system",
                    "content": system_message
                },
                "user_message": {
                    "role": "user",
                    "content": user_message
                }
            }
        }

    def _get_default_prompts(self) -> dict:
        """获取默认提示词配置"""
        return {
            "code_review": {
                "system_message": {
                    "role": "system",
                    "content": (
                        "你是一位资深的软件开发工程师，专注于代码的规范性、功能性、安全性和稳定性。"
                        "你只需要检查严重的问题，例如："
                        "1. 代码逻辑错误或潜在的Bug。"
                        "2. 安全漏洞、未处理的异常等。"
                        "3. 性能问题，例如不必要的循环、无效的资源占用等。"
                        "4. 违反最佳实践的严重问题，如错误的 API 使用或线程安全问题。"
                        "请忽略小的代码格式、命名风格和微小的样式问题。"
                        "此外，请根据代码的整体质量打分（满分为10分），评分标准包括："
                        "1. 功能实现的正确性与健壮性（4分）。"
                        "2. 安全性与潜在风险（3分）。"
                        "3. 是否符合最佳实践（2分）。"
                        "4. 性能与资源利用效率（1分）。"
                    )
                },
                "user_message": {
                    "role": "user",
                    "content": (
                        "以下是某位员工向 GitLab 代码库提交的 Merge Request 代码，请严格审查严重问题，并对代码质量进行评分。\n"
                        "代码变更内容：\n{diffs_text}\n\n"
                        "提交历史（commits）：\n{commits_text}\n"
                        "如果没有严重问题，请返回'代码正常'并给出评分。"
                        "如果发现严重问题，请列出问题并给出优化建议，特别说明：简化回复内容，问题按照重要性从高到低最多返回前三个问题。"
                        "同时，请给出代码的评分，并解释每一项评分的理由。"
                    )
                }
            }
        }

    def review_code(self, diffs_text: str, commits_text: str = "") -> str:
        """Review代码，并返回结果"""
        prompts = self.prompts["code_review"]
        messages = [
            prompts["system_message"],
            {
                "role": "user",
                "content": prompts["user_message"]["content"].format(
                    diffs_text=diffs_text,
                    commits_text=commits_text
                )
            }
        ]
        return self.call_llm(messages)

    def call_llm(self, messages: list) -> str:
        logger.info(f"向AI发送代码Review请求, message:{messages})")
        review_result = self.client.completions(
            messages=messages
        )
        logger.info(f"收到AI返回结果:{review_result}")
        return review_result
