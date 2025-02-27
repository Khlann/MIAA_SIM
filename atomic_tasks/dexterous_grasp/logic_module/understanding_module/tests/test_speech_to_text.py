import unittest

from dexterous_grasp.logic_module.understanding_module import IFlytekInterface
from dexterous_grasp.config import iflytek_config


class TestIFlytekInterface(unittest.TestCase):
    def setUp(self):
        self.ifly_interface = IFlytekInterface(iflytek_config)

    def test_transcribe(self):
        language_prompt = self.ifly_interface.voice_to_text()
        print(language_prompt)


if __name__ == '__main__':
    unittest.main()
