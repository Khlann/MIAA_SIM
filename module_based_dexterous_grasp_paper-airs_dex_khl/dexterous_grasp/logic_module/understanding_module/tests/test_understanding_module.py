import cv2
import unittest

from dexterous_grasp.logic_module.understanding_module import IFlytekInterface
from dexterous_grasp.logic_module.understanding_module import GPT4Integration
from dexterous_grasp.config import request_info, api_key, file_paths, iflytek_config

class TestUnderstandingModule(unittest.TestCase):
    def setUp(self):
        self.ifly_interface = IFlytekInterface(iflytek_config)
        self.gpt_interface = GPT4Integration(request_info)
        self.test_image_case_0 = cv2.imread(file_paths.understanding_test_image)

    def test_understanding_module(self):
        language_prompt = self.ifly_interface.voice_to_text()
        print("Voice to Text Result: ", language_prompt)

        gpt_result = self.gpt_interface.understand_image_by_text(language_prompt, self.test_image_case_0)
        print("GPT Output: ", gpt_result)

if __name__ == '__main__':
    unittest.main()
