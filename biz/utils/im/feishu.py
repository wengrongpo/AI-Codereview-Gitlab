import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.contact.v3 import *
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
        self.default_webhook_url = webhook_url or os.environ.get('FEISHU_WEBHOOK_URL', '')
        self.enabled = os.environ.get('FEISHU_ENABLED', '0') == '1'
        self.app_id = os.environ.get('FEISHU_APP_ID', '')
        self.app_secret = os.environ.get('FEISHU_APP_SECRET', '')
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

    def _get_webhook_url(self, project_name=None, url_slug=None):
        """
        获取项目对应的 Webhook URL
        :param project_name: 项目名称
        :return: Webhook URL
        :raises ValueError: 如果未找到 Webhook URL
        """
        # 如果未提供 project_name，直接返回默认的 Webhook URL
        if not project_name:
            if self.default_webhook_url:
                return self.default_webhook_url
            else:
                raise ValueError("未提供项目名称，且未设置默认的 飞书 Webhook URL。")

        # 构造目标键
        target_key_project = f"FEISHU_WEBHOOK_URL_{project_name.upper()}"
        target_key_url_slug = f"FEISHU_WEBHOOK_URL_{url_slug.upper()}"

        # 遍历环境变量
        for env_key, env_value in os.environ.items():
            env_key_upper = env_key.upper()
            if env_key_upper == target_key_project:
                return env_value  # 找到项目名称对应的 Webhook URL，直接返回
            if env_key_upper == target_key_url_slug:
                return env_value  # 找到 GitLab URL 对应的 Webhook URL，直接返回

        # 如果未找到匹配的环境变量，降级使用全局的 Webhook URL
        if self.default_webhook_url:
            return self.default_webhook_url

        # 如果既未找到匹配项，也没有默认值，抛出异常
        raise ValueError(f"未找到项目 '{project_name}' 对应的 Feishu Webhook URL，且未设置默认的 Webhook URL。")

    def send_message(self, content, msg_type='text', title=None, is_at_all=False, project_name=None, url_slug=None):
        """
        发送飞书消息
        :param content: 消息内容
        :param msg_type: 消息类型，支持text和markdown
        :param title: 消息标题(markdown类型时使用)
        :param is_at_all: 是否@所有人
        :param project_name: 项目名称
        """
        if not self.enabled:
            logger.info("飞书推送未启用")
            return

        try:
            post_url = self._get_webhook_url(project_name=project_name, url_slug=url_slug)
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
                url=post_url,
                json=data,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                logger.error(f"飞书消息发送失败! webhook_url:{post_url}, error_msg:{response.text}")
                return

            result = response.json()
            if result.get('msg') != "success":
                logger.error(f"发送飞书消息失败! webhook_url:{post_url},errmsg:{result}")
            else:
                logger.info(f"飞书消息发送成功! webhook_url:{post_url}")

        except Exception as e:
            logger.error(f"飞书消息发送失败! ", e)

    def send_message_personally(self, content, msg_type='text', title=None, developer_name=None):
        """
        发送飞书消息
        :param content: 消息内容
        :param msg_type: 消息类型，支持text和markdown
        :param title: 消息标题(markdown类型时使用)
        :param developer_name: 开发者名称
        """
        if not self.enabled:
            logger.info("飞书推送未启用")
            return
        
        if not developer_name:
            logger.error("开发者名称不能为空")
            return
        
        user_id=self.fetch_user_id_by_email(developer_name)
        
        if not user_id:
            logger.error(f"未找到开发者 {developer_name} 的飞书用户ID")
            return
        
        if msg_type == 'markdown':
            msg_type='interactive'
            template_id=os.getenv('FEISHU_TEMPLATE_ID')
            template_version_name=os.getenv('FEISHU_TEMPLATE_VERSION_NAME')
            data={
                "data": {
                    "template_id": template_id,
                    "template_variable": {
                        "content": content,
                        "title": title,
                    },
                    "template_version_name": template_version_name
                },
                "type": "template"
            }
        else:
            data = {
                "msg_type": "text",
                "content": {
                    "text": content
                },
            }
        try:
            # 构造请求对象
            request: CreateMessageRequest = CreateMessageRequest.builder() \
                .receive_id_type("user_id") \
                .request_body(CreateMessageRequestBody.builder()
                    .receive_id(user_id)
                    .msg_type(msg_type)
                    .content(json.dumps(data))
                    .build()) \
                .build()
            
            # 发起请求
            response: CreateMessageResponse = self.client.im.v1.message.create(request)
            # 处理失败返回
            if not response.success():
                logger.error(f"飞书消息发送失败! code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
                return

            # 处理业务结果
            logger.info(lark.JSON.marshal(response.data, indent=4))
        
        except Exception as e:
            logger.error(f"飞书消息发送失败! ", e)
            
    def fetch_user_id_by_email(self, developer: str) -> str :
        email=f'{developer}@thinkingdata.cn'
        # 构造请求对象
        request: BatchGetIdUserRequest = BatchGetIdUserRequest.builder() \
            .user_id_type("user_id") \
            .request_body(BatchGetIdUserRequestBody.builder()
                .emails([email])
                .mobiles([])
                .include_resigned(True)
                .build()) \
            .build()

        # 发起请求
        response: BatchGetIdUserResponse = self.client.contact.v3.user.batch_get_id(request)

        # 处理失败返回
        if not response.success():
            logger.error(
                f"client.contact.v3.user.batch_get_id failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        logger.info(lark.JSON.marshal(response.data, indent=4))
        resopose=json.loads(lark.JSON.marshal(response.data, indent=4))
        return resopose.get('user_list')[0].get("user_id")