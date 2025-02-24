import unittest
import cv2
import numpy as np
import os
from dexterous_grasp.logic_module.vision_module.pose_estimation import estimation_2d
from dexterous_grasp.logger_module import LoggerManager
from dexterous_grasp.config import planning_module_varant

class RotationTranslation:
    def __init__(self, rotation, translation):
        self.rotation = rotation
        self.translation = translation

class TestEstimation2D(unittest.TestCase):
    def setUp(self):
        self.logger_manager = LoggerManager()
        self.estimation_2d = estimation_2d.Estimation2D(self.logger_manager)

        # 模拟输入数据
        self.test_mask_path = os.path.expanduser("~/Contest_FInal/contest/assets/mask_8.png")
        self.test_mask = cv2.imread(self.test_mask_path, cv2.IMREAD_GRAYSCALE)
        if self.test_mask is None:
            raise FileNotFoundError(f"Test mask not found at {self.test_mask_path}")

        # 模拟深度图
        self.test_depth_map = np.random.uniform(0.5, 2.0, size=self.test_mask.shape).astype(np.float32)

        # 模拟相机外参
        self.end2camera = RotationTranslation(np.eye(3), np.array([10, 20, 30]))

        # 模拟UR5末端姿态
        planning_module_varant.shot_pose = np.eye(4)

    def test_process_mask_and_transform(self):
        camera = self.estimation_2d  # 假设camera是Estimation2D实例

        position, z_axis_radian, T_base2object = self.estimation_2d.process_mask_and_transform(
            self.test_mask, camera, self.end2camera
        )

        print("Position:", position)
        print("Z-axis radian:", z_axis_radian)
        print("Transformation Matrix (Base to Object):\n", T_base2object)

        # 验证返回值类型和内容
        self.assertIsInstance(position, tuple, "Position should be a tuple.")
        self.assertEqual(len(position), 3, "Position should have three components (x, y, z).")

        self.assertIsInstance(z_axis_radian, float, "Z-axis radian should be a float.")

        self.assertIsInstance(T_base2object, np.ndarray, "Transformation matrix should be a numpy array.")
        self.assertEqual(T_base2object.shape, (4, 4), "Transformation matrix should be 4x4.")
        self.assertTrue(np.allclose(T_base2object[3], [0, 0, 0, 1]), "Last row of the transformation matrix should be [0, 0, 0, 1].")

if __name__ == "__main__":
    unittest.main()



