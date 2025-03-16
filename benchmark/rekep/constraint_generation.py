import base64
import os
from volcenginesdkarkruntime import Ark

class ConstraintGenerator():
    def __init__(self, doubao_config):
        self.client = Ark(api_key=doubao_config.api_key)
        self.model_config = doubao_config.model_config
        self.messages = []
        self.connection_status = True
        self.doubao_config = doubao_config
        with open("/home/arlen/arlen/miaa_sim_khl/benchmark/rekep/asset/prompt_template.txt", "r") as f:
            self.prompt_template = f.read()

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

    def generate(self, text, color_image, append_messages=False):
        """
        发送包含图片的查询请求
        :param color_image: 图片路径
        :param text: 用户文本输入
        :param append_messages: 是否追加消息到历史记录
        :return: 模型回复
        """
        self.connection_status = True
        base64_image = self.encode_image(color_image)
        # full_prompt = self.doubao_config.single_en_prompt.replace(command_token, text)
        full_prompt = self.prompt_template.format(instruction=text)

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


