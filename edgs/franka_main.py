import sys
import cv2
import numpy as np
import panda_py
project_root = "/home/arlen/arlen/miaa_sim/atomic_tasks"
gsam_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/external/gsam2"
sys.path.insert(0,project_root)
sys.path.insert(0,gsam_path)
from dexterous_grasp.logic_module.understanding_module import IFlytekInterface
from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.logic_module.planning_module import FrankaArmPlanner
from dexterous_grasp.device_module import D435i, Speaker
from dexterous_grasp.logic_module.understanding_module import Dinox
from dexterous_grasp.logic_module.vision_module import Estimation
from dexterous_grasp.logic_module.understanding_module.image_understanding_by_text import GPT4Integration
from dexterous_grasp.config import (request_info, api_key, file_paths,iflytek_config,
                                    ground_sam2_config, file_paths,franka_config,feedback_params)

class EdgsTasks():
    def __init__(self, project_root, robot_type):
        self.logger_manager = LoggerManager(project_root)
        self.ifly_interface = IFlytekInterface(iflytek_config, self.logger_manager)
        self.gpt_interface = GPT4Integration(request_info, self.logger_manager)
        self.task_controller = TaskController(robot_type,franka_config, self.logger_manager)
        self.robot_planner = FrankaArmPlanner()
        self.dinox = Dinox()
        self.estimation2D = Estimation()
        self.gpt_interface = GPT4Integration(request_info)
        self.camera = D435i(self.logger_manager)
        self.speaker = Speaker()

    
    def loop(self):
        print("Listening... Press Ctrl+C to exit")
        self.speaker.play_audio(feedback_params.ready_go)

if __name__ == "__main__":
    robot_type = "franka"
    project_root = ""
    task = EdgsTasks(project_root, robot_type)

    task.loop()
    # T_C_E = franka_config.T_C_E
    # user_input = "帮我拿一个苹果"
    # debug = False

    # Step 1: Voice to Text using IFlytekInterface


# cam.capture_current_info()
# cola_image , color_intrinsics = cam.get_color_info()
# depth_image, depth_intrinsics = cam.get_depth_info()
# cv2.imwrite("cola_image.png", cola_image)
# _, aug_result = gpt_interface.understand_image_by_text(user_input,cola_image)

# mask = dinox.get_mask("cola_image.png", "banana")
# cv2.imwrite("dinox_mask.png", mask)

# P_O_C, R = estimation2D.process_mask_and_transform(mask, cam)

# T_E_B = task_controller.robotic_arm_controller.robot_arm.get_pose()

# initial_angle_gap = task_controller.initial_angle_gap

# q = robot_planner.plan_curobo(P_O_C, R, T_C_E, T_E_B,initial_angle_gap)
# task_controller.robotic_arm_controller.execute_movement_joints(q)
# task_controller.robotic_arm_controller.close_gripper()
# task_controller.robotic_arm_controller.execute_movement_pose(task_controller.start_pose)
# task_controller.robotic_arm_controller.open_gripper()
