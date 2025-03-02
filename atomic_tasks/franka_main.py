import sys
import cv2
import numpy as np
import panda_py
project_root = "/home/arlen/arlen/miaa_sim/atomic_tasks"
gsam_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/external/gsam2"
sys.path.insert(0,project_root)
sys.path.insert(0,gsam_path)

from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.logic_module.planning_module import FrankaArmPlanner
from dexterous_grasp.device_module.cameras import D435i
from dexterous_grasp.logic_module.understanding_module import Dinox
from dexterous_grasp.logic_module.vision_module import Estimation
from dexterous_grasp.logic_module.vision_module import GroundedSAM
from dexterous_grasp.logic_module.understanding_module.image_understanding_by_text import GPT4Integration
from dexterous_grasp.config import franka_config
from dexterous_grasp.config import ground_sam2_config, file_paths

from dexterous_grasp.config import request_info, api_key, file_paths

# Config
# Todo:重新生成一份手眼标定矩阵
T_C_E = franka_config.T_C_E
user_input = "帮我拿一个苹果"
debug = False

# 类初始化
logger_manager = LoggerManager(project_root)
robot_type = "franka"
task_controller = TaskController(robot_type,franka_config, logger_manager)
robot_planner = FrankaArmPlanner()
dinox = Dinox()
# grounded_sam2 = GroundedSAM(ground_sam2_config)
estimation2D = Estimation()
gpt_interface = GPT4Integration(request_info)


# Step1：从相机获取图像
cam = D435i(logger_manager)
cam.capture_current_info()
cola_image , color_intrinsics = cam.get_color_info()
depth_image, depth_intrinsics = cam.get_depth_info()
# todo:在log中保存color和depth的信息
cv2.imwrite("cola_image.png", cola_image)
# user_input = "yellow nailong"

# Step2：Prompt aug
_, aug_result = gpt_interface.understand_image_by_text(user_input,cola_image)

# Step3：Segmentation
# dino 方案
# 在线获取mask
mask = dinox.get_mask("cola_image.png", "banana")
cv2.imwrite("dinox_mask.png", mask)

# 离线获取mask
# mask = cv2.imread("/home/arlen/arlen/miaa_sim/dinox_mask.png")


# gsam 方案
# if debug:
#     mask = cv2.imread("/home/arlen/arlen/miaa_sim/atomic_tasks/external/gsam2/test_mask.png")
# else:
#     grounded_sam2 = GroundedSAM(ground_sam2_config)
#     mask, input_boxe, label, confidence = grounded_sam2.segment(aug_result, cola_image)

# Step4：Estimation
P_O_C, R = estimation2D.process_mask_and_transform(mask, cam)


# 创建旋转矩阵，使末端法兰盘E垂直朝向桌面
# 绕z轴旋转R弧度
# R = np.pi/90

T_E_B = task_controller.robotic_arm_controller.robot_arm.get_pose()

# q策略
q = robot_planner.plan_curobo(P_O_C, R, T_C_E, T_E_B)
task_controller.robotic_arm_controller.execute_movement_joints(q)
# tpose策略
# q = robot_planner.plan_curobo(P_O_C, R, T_C_E, T_E_B)
# tpose = panda_py.fk(q)
# task_controller.robotic_arm_controller.execute_movement_pose(tpose)
task_controller.robotic_arm_controller.close_gripper()
task_controller.robotic_arm_controller.execute_movement_pose(task_controller.start_pose)
task_controller.robotic_arm_controller.open_gripper()
