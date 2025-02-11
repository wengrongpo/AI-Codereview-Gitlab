import json
import requests
import os
import re
from biz.utils.log import logger


class FeishuNotifier:
    def __init__(self, webhook_url=None):
        """
        初始化飞书通知器
        :param webhook_url: 飞书机器人webhook地址
        """
        self.webhook_url = webhook_url or os.environ.get('FEISHU_WEBHOOK_URL', '')
        self.enabled = os.environ.get('FEISHU_ENABLED', '0') == '1'

    def format_markdown_content(self, content, title=None):
        """
        格式化markdown内容以适配飞书
        """
        # 处理标题
        formatted_content = f"## {title}\n\n" if title else ""

        # 将内容中的5级以上标题转为4级
        content = re.sub(r'#{5,}\s', '#### ', content)

        # 处理链接格式
        content = re.sub(r'\[(.*?)\]\((.*?)\)', r'[链接]\2', content)

        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)

        formatted_content += content
        return formatted_content

    def send_message(self, content, msg_type='text', title=None, is_at_all=False):
        """
        发送飞书消息
        :param content: 消息内容
        :param msg_type: 消息类型，支持text和markdown
        :param title: 消息标题(markdown类型时使用)
        :param is_at_all: 是否@所有人
        """
        if not self.enabled:
            logger.info("飞书推送未启用")
            return

        if not self.webhook_url:
            logger.error("飞书Webhook URL未配置")
            return

        try:
            if msg_type == 'markdown':
                data = {
                    "msg_type": "interactive",
                    "card": {
                        "schema": "2.0",
                        "config": {
                            "update_multi": True,
                            "style": {
                                "text_size": {
                                    "normal_v2": {
                                        "default": "normal",
                                        "pc": "normal",
                                        "mobile": "heading"
                                    }
                                }
                            }
                        },
                        "body": {
                            "direction": "vertical",
                            "padding": "12px 12px 12px 12px",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": content,
                                    "text_align": "left",
                                    "text_size": "normal_v2",
                                    "margin": "0px 0px 0px 0px"
                                }
                            ]
                        },
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": title
                            },
                            "template": "blue",
                            "padding": "12px 12px 12px 12px"
                        }
                    }
                }
            else:
                data = {
                    "msg_type": "text",
                    "content": {
                        "text": content
                    },
                }

            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                logger.error(f"发送飞书消息失败: {response.text}")
                return

            result = response.json()
            if result.get('errcode') != 0:
                logger.error(f"发送飞书消息失败: {result}")
            else:
                logger.info("飞书消息发送成功")

        except Exception as e:
            logger.error(f"发送飞书消息时发生错误: {str(e)}")
