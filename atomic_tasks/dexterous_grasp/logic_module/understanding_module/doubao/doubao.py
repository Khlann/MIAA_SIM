import base64
import os
# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark


class DoubaoClient:
    def __init__(self, api_key, model_config):
        # 初始化客户端
        self.client = Ark(api_key=api_key)
        # 存储模型配置
        self.model_config = model_config
        # 初始化消息列表
        self.messages = []

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

    def send_image_query(self, image_path, user_question, append_messages=True):
        """
        发送包含图片的查询请求
        :param image_path: 图片路径
        :param user_question: 用户问题
        :param append_messages: 是否追加消息到历史记录
        :return: 模型回复
        """
        base64_image = self.encode_image(image_path)
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_question
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

        return model_reply


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
image_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/color_image.png"
# reply1 = doubao_client.send_image_query(image_path, "图片里讲了什么?")
# print("追加消息模式 - 第一轮回复:", reply1)
# reply2 = doubao_client.send_image_query(image_path, "还有其他细节吗?")
# print("追加消息模式 - 第二轮回复:", reply2)

# 测试单次调用模式
reply3 = doubao_client.send_image_query(image_path, "这张图片主要颜色是什么?", append_messages=False)
print("单次调用模式 - 回复:", reply3)