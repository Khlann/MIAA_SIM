import os
import cv2
import base64
import requests

from dexterous_grasp.config import proxy_settings, command_token
from dexterous_grasp.logger_module import LoggerValidator


def encode_image(color_image):
    success, encoded_image = cv2.imencode('.jpg', color_image)
    if not success:
        raise ValueError("Failed to encode the image to JPEG format")
    encoded_image_base64 = base64.b64encode(encoded_image).decode('utf-8')
    return encoded_image_base64


class GPT4Integration(LoggerValidator):
    def __init__(self, request_info, logger_manager=None):
        super().__init__(logger_manager)
        os.environ["http_proxy"] = proxy_settings.http
        os.environ["https_proxy"] = proxy_settings.https
        self.request_info = request_info
        self.connection_status = True

    def understand_image_by_text(self, text, color_image):
        self.connection_status = True
        self.logger_manager.logger.info(f"Sending text to GPT-4: {text}")
        encoded_image = encode_image(color_image)
        full_prompt = self.request_info.single_en_prompt.replace(command_token, text)

        payload = {
            "model": self.request_info.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        try:
            # Adding a timeout of 12 seconds for the request
            response = requests.post(self.request_info.api_url, headers=self.request_info.headers, json=payload, timeout=12)
        except requests.exceptions.RequestException as error:
            # This will catch all Request-related errors including ProxyError, Timeout, SSLError, etc.
            self.logger_manager.logger.error(f"Failed to send request to GPT-4: {error}")
            self.connection_status = False
            return self.connection_status, None

        result = response.json()["choices"][0]["message"]["content"]

        self.logger_manager.logger.info(f"Received GPT-4 response: {result}")

        if "None" in result:
            self.logger_manager.logger.warning("Object not recognized by GPT-4")
            return self.connection_status, None
        return self.connection_status, result
