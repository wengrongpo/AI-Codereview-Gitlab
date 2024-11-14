from biz.utils.log import logger
from core.llm.factory import Factory


class CodeReviewer:
    def __init__(self):
        self.client = Factory().getClient()

    def review_code(self, diffs_text: str, commits_text: str = "") -> str:
        """Review代码，并返回结果"""
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一位资深的软件开发工程师，专注于代码的规范性、功能性、安全性和稳定性。"
                    "你只需要检查严重的问题，例如："
                    "1. 代码逻辑错误或潜在的Bug。"
                    "2. 安全漏洞、未处理的异常等。"
                    "3. 性能问题，例如不必要的循环、无效的资源占用等。"
                    "4. 违反最佳实践的严重问题，如错误的 API 使用或线程安全问题。"
                    "请忽略小的代码格式、命名风格和微小的样式问题。"
                )
            },
            {
                "role": "user",
                "content": (
                    f"以下是某位员工向 GitLab 代码库提交的 Merge Request 代码，请严格审查严重问题。\n"
                    f"代码变更内容：\n{self._sanitize_diffs(diffs_text)}\n\n"
                    f"提交历史（commits）：\n{commits_text}\n"
                    "如果没有严重问题，请返回'代码正常'。否则，请列出问题并给出优化建议。特别说明：简化恢复内容，问题按照重要性从高到低最多返回前三个问题，并给出具体的修改建议。"
                )
            }
        ]
        return self.call_llm(messages)

    def _sanitize_diffs(self, diffs_text: str) -> str:
        """对diffs文本进行预处理（如转义符的处理）"""
        # 这里可以添加具体的预处理逻辑，比如限制长度、转义特殊字符等
        # 简单处理：如果文本过长，可以进行截断或其他预处理
        if len(diffs_text) > 10000:  # 假设10000字符是安全长度
            logger.warning("diffs_text过长，已截断")
            diffs_text = diffs_text[:10000] + '...[内容过长, 已截断]'
        return diffs_text

    def call_llm(self, messages: list) -> str:
        logger.info(f"向AI发送代码Review请求, message:{messages})")
        review_result = self.client.completions(
            messages=messages
        )
        logger.info(f"收到ZhipuAI返回结果:{review_result}")
        return review_result
