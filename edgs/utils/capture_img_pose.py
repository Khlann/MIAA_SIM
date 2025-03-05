"""
这个脚本是一个用于流式捕获图像和姿态的工具。它提供了以下功能：
1. 捕获图像：使用相机捕获图像，并将其保存到指定的路径。
2. 捕获姿态：通过调用机器人的API，获取机器人的当前姿态信息。
3. 流式捕获：循环捕获图像和姿态，并将它们保存到指定的路径。
"""

import sys
import cv2
import numpy as np
import panda_py
import json
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
img_save_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/utils/data"
pose_save_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/utils/data/pose.json"

# 类初始化
logger_manager = LoggerManager(project_root)
robot_type = "franka"
task_controller = TaskController(robot_type,franka_config, logger_manager)
cam = D435i(logger_manager)

i = 0
while True:
    # 捕获图像
    cam.capture_current_info(0)
    color_image = cam.color_image
    cv2.namedWindow("color_image", cv2.WINDOW_NORMAL)
    # 调整窗口大小，这里设置为宽 640 高 480，可按需修改
    cv2.resizeWindow("color_image", 640, 480)
    cv2.imshow("color_image", color_image)
    key = cv2.waitKey(1)
    # 检查是否按下 'r' 键
    if key == ord('r'):
        # 保存图像
        img_filename = f"{img_save_path}/image_{i}.png"
        cv2.imwrite(img_filename, color_image)
        print(f"Image saved to {img_filename}")
        # 保存姿态
        pose = task_controller.robotic_arm_controller.robot_arm.get_pose()
        try:
            # 尝试读取现有的 JSON 文件内容
            with open(pose_save_path, 'r') as f:
                poses = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或内容不是有效的 JSON，初始化一个空列表
            poses = []
        # 将新的姿态添加到列表中
        poses.append(pose.tolist())
        # 将更新后的列表以 JSON 格式写回文件
        with open(pose_save_path, 'w') as f:
            json.dump(poses, f, indent=2)
        print(f"Pose saved to {pose_save_path}")
        i += 1
