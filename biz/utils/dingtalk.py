import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse

import requests
from dotenv import load_dotenv

from biz.utils.log import logger


class DingTalkNotifier:
    def __init__(self, access_token, secret):
        self.access_token = access_token
        self.secret = secret
        self.webhook_url = f"https://oapi.dingtalk.com/robot/send?access_token={self.access_token}"

    def _generate_signature(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode('utf-8'))
        return timestamp, sign

    def _get_post_url(self):
        timestamp, sign = self._generate_signature()
        return f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"

    def send_message(self, content: str, msg_type='text', title='通知', is_at_all=False):
        load_dotenv()
        # 获取环境变量 DINGTALK_ENABLED的值
        if os.environ.get('DINGTALK_ENABLED') not in ('true', '1', 't', 'yes', 'y'):
            logger.info("不发送钉钉消息(DINGTALK_ENABLED=0)。原始消息为:" + content)
            return

        post_url = self._get_post_url()
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
        logger.info("即将发送钉钉消息:" + json.dumps(message))

        response = requests.post(url=post_url, data=json.dumps(message), headers=headers)
        response_data = response.json()
        if response_data.get('errmsg') == 'ok':
            logger.info("钉钉消息发送成功!")
        else:
            logger.error("发送失败:", response_data)
