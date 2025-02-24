# Unit tests for dexterous hand planning
import unittest
import numpy as np
from dexterous_grasp.config import (
    robot_arm_ip_address,
    arm_motion_params,
    hand_motion_params,
    hand_device_params,
    camera2base,
    dexterous_hand_grasp_pose,
    grasp_safe_distance
)

from dexterous_grasp.logic_module.planning_module import RoboticArmPlanner
from dexterous_grasp.logic_module.control_module import TaskController


class TestTaskControl(unittest.TestCase):
    def setUp(self):
        self.robotic_arm_planner = RoboticArmPlanner(camera2base, dexterous_hand_grasp_pose, grasp_safe_distance)
        self.task_controller = TaskController(arm_motion_params, hand_motion_params, hand_device_params,
                                              robot_arm_ip_address)

    def test_task_pipeline_case0(self):
        tposes = self.robotic_arm_planner.plan_path(
            [0.005564116407185793, -0.040016449987888336, 0.8083125352859497], 37.2916596391342 * np.pi / 180)
        print(f"使用 arm_planner 计算得到的 tpose_sequence: {tposes}")
        self.task_controller.execute_task(tposes)
        # self.assertEqual(result, "down")


if __name__ == '__main__':
    unittest.main()
