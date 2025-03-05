import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse

import requests

from biz.utils.log import logger


class DingTalkNotifier:
    def __init__(self, webhook_url=None):
        self.enabled = os.environ.get('DINGTALK_ENABLED', '0') == '1'
        self.default_webhook_url = webhook_url or os.environ.get('DINGTALK_WEBHOOK_URL')

    def _get_webhook_url(self, project_name=None):
        """
        获取项目对应的 Webhook URL
        :param project_name:
        :return:
        """
        if not project_name:
            return self.default_webhook_url

        # 遍历所有环境变量(忽略大小写)，找到项目对应的 Webhook URL
        for env_key, env_value in os.environ.items():
            if env_key.upper() == f"DINGTALK_WEBHOOK_URL_{project_name.upper()}":
                webhook_url = env_value
                break

        # 如果未找到，降级使用全局的 Webhook URL
        if not webhook_url:
            webhook_url = self.default_webhook_url

        if not webhook_url:
            raise ValueError(f"No DingTalk webhook URL found for project {project_name}")
        return webhook_url

    def send_message(self, content: str, msg_type='text', title='通知', is_at_all=False, project_name=None):
        if not self.enabled:
            logger.info("钉钉推送未启用")
            return

        try:
            post_url = self._get_webhook_url(project_name=project_name)
            headers = {
                "Content-Type": "application/json",
                "Charset": "UTF-8"
            }
            if msg_type == 'markdown':
                message = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": title,  # Customize as needed
                        "text": content
                    },
                    "at": {
                        "isAtAll": is_at_all
                    }
                }
            else:
                message = {
                    "msgtype": "text",
                    "text": {
                        "content": content
                    },
                    "at": {
                        "isAtAll": is_at_all
                    }
                }
            response = requests.post(url=post_url, data=json.dumps(message), headers=headers)
            response_data = response.json()
            if response_data.get('errmsg') == 'ok':
                logger.info(f"钉钉消息发送成功! webhook_url:{post_url}")
            else:
                logger.error(f"钉钉消息发送失败! webhook_url:{post_url},errmsg:{response_data.get('errmsg')}")
        except Exception as e:
            logger.error(f"钉钉消息发送失败! ", e)
