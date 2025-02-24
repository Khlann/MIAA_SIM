import cv2
import unittest
from dexterous_grasp.logic_module.vision_module import GroundedSAM
from dexterous_grasp.config import ground_sam2_config, file_paths


class TestGroundedSAM2(unittest.TestCase):
    def setUp(self):
        self.grounded_sam2 = GroundedSAM(ground_sam2_config)
        self.test_image_case_0 = cv2.imread(file_paths.understanding_test_image)

    def test_segmentation_case1(self):
        text_prompt = "a gold can with a red bull logo"
        mask, input_boxe, label, confidence = self.grounded_sam2.segment(text_prompt, self.test_image_case_0)

        self.assertIsNotNone(mask, "The output should not be None")
        self.assertIn("gold can", label[0])

    def test_segmentation_case2(self):
        text_prompt = "a cat"
        mask, input_boxe, label, confidence = self.grounded_sam2.segment(text_prompt, self.test_image_case_0)

        self.assertIsNone(mask, "The output should be None")

    def test_segmentation_case3(self):
        text_prompt = "Beverage cans"
        mask, input_boxe, label, confidence = self.grounded_sam2.segment(text_prompt, self.test_image_case_0)

        self.assertIsNotNone(mask, "The output should not be None")


if __name__ == '__main__':
    unittest.main()