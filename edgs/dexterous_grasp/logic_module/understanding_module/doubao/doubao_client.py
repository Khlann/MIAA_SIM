import base64
import os
from volcenginesdkarkruntime import Ark
from dexterous_grasp.config import command_token
from dexterous_grasp.logger_module import LoggerValidator

class DoubaoClient(LoggerValidator):
    def __init__(self, doubao_config, logger_manager=None):
        super().__init__(logger_manager)
        self.client = Ark(api_key=doubao_config.api_key)
        self.model_config = doubao_config.model_config
        self.messages = []
        self.connection_status = True
        self.doubao_config = doubao_config

    def encode_image(self, image_path):
        """
        将指定路径的图片转换为 Base64 编码
        :param image_path: 图片路径
        :return: Base64 编码的图片数据
        """
        file_extension = os.path.splitext(image_path)[1][1:].lower()
        with open(image_path, "rb") as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
            if file_extension == "png":
                return f"data:image/png;base64,{base64_data}"
            elif file_extension == "jpg" or file_extension == "jpeg":
                return f"data:image/jpeg;base64,{base64_data}"
            elif file_extension == "webp":
                return f"data:image/webp;base64,{base64_data}"
            else:
                raise ValueError("Unsupported image format")

    def understand_image_by_text(self, text, color_image, append_messages=False):
        """
        发送包含图片的查询请求
        :param color_image: 图片路径
        :param text: 用户文本输入
        :param append_messages: 是否追加消息到历史记录
        :return: 模型回复
        """
        self.connection_status = True
        self.logger_manager.logger.info(f"Sending text to GPT-4: {text}")
        base64_image = self.encode_image(color_image)
        full_prompt = self.doubao_config.single_en_prompt.replace(command_token, text)

        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": full_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": base64_image
                    }
                }
            ]
        }

        if append_messages:
            self.messages.append(user_message)
        else:
            temp_messages = [user_message]

        messages_to_send = self.messages if append_messages else temp_messages

        response = self.client.chat.completions.create(
            messages=messages_to_send,
            **self.model_config
        )

        model_reply = response.choices[0].message
        model_reply_dict = {
            "role": model_reply.role,
            "content": model_reply.content
        }

        if append_messages:
            self.messages.append(model_reply_dict)

        result = model_reply.content
        return result


if __name__ == "__main__":
    # 配置信息
    api_key = "e90d7e28-2908-45c1-b321-fe71c1a9a9c7"
    model_config = {
        "model": "doubao-1-5-vision-pro-32k-250115",
        "max_tokens": 200,
        "temperature": 0.7,
        "stream": False,
        "stop": ["结束"]
    }

    # 创建 DoubaoClient 实例
    doubao_client = DoubaoClient(api_key, model_config)

    # 测试追加消息模式
    color_image = "/home/arlen/arlen/miaa_sim/atomic_tasks/color_image.png"
    # reply1 = doubao_client.send_image_query(color_image, "图片里讲了什么?")
    # print("追加消息模式 - 第一轮回复:", reply1)
    # reply2 = doubao_client.send_image_query(color_image, "还有其他细节吗?")
    # print("追加消息模式 - 第二轮回复:", reply2)

    # 测试单次调用模式
    reply3 = doubao_client.send_image_query(color_image, "这张图片主要颜色是什么?", append_messages=False)
    print("单次调用模式 - 回复:", reply3)