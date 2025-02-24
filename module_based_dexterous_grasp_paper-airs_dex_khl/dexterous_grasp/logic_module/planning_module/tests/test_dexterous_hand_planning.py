# Unit tests for dexterous hand planning
import unittest
import numpy as np
from dexterous_grasp.config import (
    camera2base,
    dexterous_hand_grasp_pose
)
from dexterous_grasp.logic_module.planning_module import DexterousHandPlanner


class TestDexterousHandPlanning(unittest.TestCase):
    def setUp(self):
        self.dexterous_hand_planner = DexterousHandPlanner(camera2base, dexterous_hand_grasp_pose)

    def test_hand_strategy_case0(self):
        test_origin_radian = 37.2916596391342 * np.pi / 180
        test_target_position_cam = [0.005564116407185793, -0.040016449987888336, 0.8083125352859497]
        result, _ = self.dexterous_hand_planner.get_hand_grasp_strategy(test_origin_radian, test_target_position_cam)
        self.assertEqual(result, "forward")

if __name__ == '__main__':
    unittest.main()
