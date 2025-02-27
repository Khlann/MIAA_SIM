import sys
import os
import numpy as np
project_root = "/home/arlen/arlen/miaa_sim/module_based_dexterous_grasp_paper-airs_dex_khl"
sys.path.insert(0,project_root)

from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logger_module.logger import LoggerManager

from dexterous_grasp.config import franka_config

logger_manager = LoggerManager(project_root)
robot_type = "franka"
task_controller = TaskController(robot_type,franka_config, logger_manager)
# p = [-2.62117052589383, 0.27274232822552064, 2.8916160119458247, -0.7573939886344107, -0.3653997534360118, 0.8943572264512378, -2.3128942678827378]
# task_controller.robotic_arm_controller.execute_movement_joints(p)

# 创建旋转矩阵，使末端法兰盘E垂直朝向桌面
# 绕z轴旋转R弧度
R = 1.7
P_O_B = np.array([0.4, 0.1, -0.02])

# 创建绕y轴旋转180度（pi弧度）的旋转矩阵
rotation_matrix_y = np.array([
    [-1, 0, 0],
    [0, 1, 0],
    [0, 0, -1]
])

# 创建绕z轴旋转R弧度的旋转矩阵
rotation_matrix_z = np.array([
    [np.cos(R), -np.sin(R), 0],
    [np.sin(R), np.cos(R), 0],
    [0, 0, 1]
])

# 将两个旋转矩阵相乘
rotation_matrix = np.dot(rotation_matrix_y, rotation_matrix_z)
# 构建4x4的变换矩阵
pose_matrix = np.eye(4)
pose_matrix[:3, :3] = rotation_matrix
pose_matrix[:3, 3] = P_O_B

task_controller.robotic_arm_controller.execute_movement_pose(pose_matrix)
