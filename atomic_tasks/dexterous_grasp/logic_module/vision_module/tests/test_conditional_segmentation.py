import cv2
import unittest
import sys
import cv2
project_root = "/home/arlen/arlen/miaa_sim/atomic_tasks"
gsam_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/external/gsam2"
sys.path.insert(0,project_root)
sys.path.insert(0,gsam_path)
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