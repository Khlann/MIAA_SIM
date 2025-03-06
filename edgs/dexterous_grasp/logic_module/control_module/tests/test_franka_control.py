import sys
import os
import numpy as np
import panda_py
project_root = "/home/arlen/arlen/miaa_sim/edgs"
sys.path.insert(0,project_root)

from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logger_module.logger import LoggerManager

from dexterous_grasp.config import franka_config

logger_manager = LoggerManager(project_root)
robot_type = "franka"
task_controller = TaskController(robot_type,franka_config, logger_manager)
j = task_controller.robotic_arm_controller.robot_arm.get_state().theta
print(j)
pose = task_controller.robotic_arm_controller.robot_arm.get_pose()
print(pose)
initial_p = task_controller.robotic_arm_controller.robot_arm.get_pose()
initial_j = panda_py.ik(initial_p)
angle_gap = initial_j[6] 

target_j = initial_j.copy()
target_j[6] = angle_gap + np.pi/4

task_controller.robotic_arm_controller.execute_movement_joints(target_j)
print(target_j)

