import cv2
import unittest
import sys
import cv2
project_root = "/home/arlen/arlen/miaa_sim/atomic_tasks"
sys.path.insert(0,project_root)
from dexterous_grasp.logic_module.understanding_module.image_understanding_by_text import GPT4Integration
from dexterous_grasp.config import request_info, api_key, file_paths


class TestAIFunctions(unittest.TestCase):
    def setUp(self):
        self.gpt_interface = GPT4Integration(request_info)
        self.test_image_case_0 = cv2.imread(file_paths.understanding_test_image)

    def test_text_understanding_case1(self):
        language_prompt = "请帮我拿那个鸭子"
        result = self.gpt_interface.understand_image_by_text(language_prompt, self.test_image_case_0)
        # 判断黄色是否在文字中
        self.assertIn("yellow", result[1], "The output should contain the word 'yellow'")
        print("language_input: ", language_prompt, "gpt_output: ", result)

    def test_text_understanding_case2(self):
        language_prompt = "请帮我拿那个可乐"
        result = self.gpt_interface.understand_image_by_text(language_prompt, self.test_image_case_0)
        self.assertIn("red", result[1], "The output should contain the word 'yellow'")
        print("language_input: ", language_prompt, "gpt_output: ", result)

    def test_text_understanding_case3(self):
        language_prompt = "帮我把那个卷尺拿过来"
        result = self.gpt_interface.understand_image_by_text(language_prompt, self.test_image_case_0)
        self.assertIsNone(result[1], "The output should be None")
        print("language_input: ", language_prompt, "gpt_output: ", result)

    def test_text_understanding_case4(self):
        language_prompt = "能不能递给我那瓶矿泉水"
        result = self.gpt_interface.understand_image_by_text(language_prompt, self.test_image_case_0)
        print("language_input: ", language_prompt, "gpt_output: ", result)

    def test_text_understanding_case5(self):
        language_prompt = "今天天气真好"
        result = self.gpt_interface.understand_image_by_text(language_prompt, self.test_image_case_0)
        self.assertIsNone(result[1], "The output should be None")
        print("language_input: ", language_prompt, "gpt_output: ", result)

    def test_text_understanding_case6(self):
        language_prompt = "请把牙膏给我"
        result = self.gpt_interface.understand_image_by_text(language_prompt, self.test_image_case_0)
        print("language_input: ", language_prompt, "gpt_output: ", result)


if __name__ == '__main__':
    unittest.main()