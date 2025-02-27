import sys
import cv2
import numpy as np
project_root = "/home/arlen/arlen/miaa_sim/module_based_dexterous_grasp_paper-airs_dex_khl"
sys.path.insert(0,project_root)

from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.logic_module.planning_module import FrankaArmPlanner
from dexterous_grasp.device_module.cameras import D435i
from dexterous_grasp.logic_module.understanding_module import Dinox
from dexterous_grasp.logic_module.vision_module import Estimation
from dexterous_grasp.config import franka_config

T_C_E = np.array([
    [0.01324788, 0.99925666, -0.03620257, 0.05672094],
    [-0.99713529, 0.01589888, 0.07394889, 0.02921566],
    [0.0744695, 0.0351192, 0.9966047, -0.14172613],
    [0., 0., 0., 1.]
])

logger_manager = LoggerManager(project_root)
robot_type = "franka"
task_controller = TaskController(robot_type,franka_config, logger_manager)
robot_planner = FrankaArmPlanner()
dinox = Dinox()
estimation2D = Estimation()
# task_controller.robotic_arm_controller.close_gripper()

# 从相机获取图像
cam = D435i(logger_manager)
cam.capture_current_info()
cola_image , color_intrinsics = cam.get_color_info()
depth_image, depth_intrinsics = cam.get_depth_info()
cv2.imwrite("cola_image.png", cola_image)
user_input = "kiwi"

dinox_mask = dinox.get_mask("cola_image.png", user_input)
# cv2.imshow("dinox_mask", dinox_mask)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# position, z_axis_radian,t = estimation2D.process_mask_and_transform( dinox_mask, cam,T_C_E)
P_O_C = estimation2D.process_mask_and_transform(dinox_mask, cam)

# 创建旋转矩阵，使末端法兰盘E垂直朝向桌面
# 绕z轴旋转R弧度
R = np.pi/90

T_E_B = task_controller.robotic_arm_controller.robot_arm.get_pose()

tpose = robot_planner.plan(P_O_C, R, T_C_E, T_E_B)
task_controller.robotic_arm_controller.execute_movement_pose(tpose)
task_controller.robotic_arm_controller.close_gripper()
task_controller.robotic_arm_controller.execute_movement_pose(task_controller.start_pose)