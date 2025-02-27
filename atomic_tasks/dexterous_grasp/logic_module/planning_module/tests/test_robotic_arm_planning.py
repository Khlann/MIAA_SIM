import unittest
import numpy as np
from dexterous_grasp.config import (
    camera2base,
    dexterous_hand_grasp_pose,
    grasp_safe_distance,
    standard_relative_pose_pairs
)
from dexterous_grasp.logic_module.planning_module import RoboticArmPlanner


class TestDexterousHandPlanning(unittest.TestCase):
    def setUp(self):
        self.robotic_arm_planner = RoboticArmPlanner(camera2base, dexterous_hand_grasp_pose, grasp_safe_distance, standard_relative_pose_pairs)

    def test_hand_strategy_case0(self):
        # target = {
        #     "save_forward_grasp_tpose": [-0.04654987, -0.50640559, 0.22643667, 1.75948829, -0.4119907, 0.36890571],
        #     "save_grasp_tpose": [-0.01104441, -0.50099337, 0.16643667, 1.69533946, -0.59595239, 0.21482544],
        #     "grasp_tpose": [-0.01104441, -0.50099337, 0.10643667, 1.69533946, -0.59595239, 0.21482544],
        # }
        result = self.robotic_arm_planner.plan_path(
            [0.005564116407185793, -0.040016449987888336, 0.8083125352859497],
            37.2916596391342 * np.pi / 180,
            np.array([[ 0.70710678, -0.70710678, 0.       , -0.00257969],
             [ 0.70710678,  0.70710678, 0.      , -0.66057496],
             [ 0.,          0.,          1.,       0.03504637],
             [ 0.,          0.,          0.,          1.        ]])
        )
        print(result)

        # for key, value in result.items():
        #     diff = np.abs(value - target[key])
        #     print(f"{key} diff: {diff}")


if __name__ == '__main__':
    unittest.main()
