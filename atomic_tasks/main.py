from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.device_module.cameras import D435i
from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logic_module.planning_module import RoboticArmPlanner
from dexterous_grasp.logic_module.vision_module import Estimation2D
from dexterous_grasp.logic_module.understanding_module import Img2Mask
from dexterous_grasp.config import (camera2base,standard_relative_pose_pairs,
                                    dexterous_hand_grasp_pose, grasp_safe_distance, arm_motion_params,
                                    hand_motion_params, hand_device_params, robot_arm_ip_address, franka_config,realman_config,
                                    dinox_sam2_clip_config)

from dexterous_grasp.config import planning_module_varant

import cv2
import numpy as np
test_object_list = ["battery", "capsule", "ball", "screwdriver", "red_cloth", "egg", "screw"]
class DexterousGraspTask:

    def __init__(self, robot_type, upstair,logger_manager):
        self.logger_manager = logger_manager
        self.estimation = Estimation2D(self.logger_manager)
        self.robotic_arm_planner = RoboticArmPlanner(camera2base, dexterous_hand_grasp_pose, grasp_safe_distance,standard_relative_pose_pairs,
                                                     self.logger_manager)
        self.task_controller = TaskController(robot_type,robot_config, self.logger_manager)
        # self.task_controller = TaskController(arm_motion_params, hand_motion_params, hand_device_params,
        #                                       robot_type = "franka", self.logger_manager)
        self.img2mask = Img2Mask(dinox_sam2_clip_config)
        self.realsense_camera = D435i(self.logger_manager)
        self.K = planning_module_varant.camera_intrinsic_matrix

    def execute_step(self, step_message, function, *args):
        self.logger_manager.logger.info(step_message)
        return function(*args)

    def capture_image(self, step_message):
        self.realsense_camera.capture_current_info()
        cola_image , color_intrinsics = self.execute_step(step_message, self.realsense_camera.get_color_info)
        depth_image, depth_intrinsics = self.execute_step(step_message, self.realsense_camera.get_depth_info)
        return cola_image, depth_image , color_intrinsics, depth_intrinsics
    

    def process_task(self):
        # Step 1: Capture RGB-D using Realsense Camera
        color_image, depth, color_intrinsics, depth_intrinsics = self.capture_image("# Step 2: Capture RGB-D using Realsense Camera")
        print(f"color_instrinsics:{color_intrinsics}")
        print(f"depth_instrinsics:{depth_intrinsics}")
        cv2.imshow("color_image", color_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite("color_image.png", color_image)
        cv2.imwrite("depth.png",depth)
        usr_input = "screwdriver"
        clip_masks,masks = self.img2mask.detect_objects("color_image.png")
        max_clip_mask_index = find_most_similar(clip_masks, usr_input, self.img2mask, self.clip_similarity)
        mask = masks[max_clip_mask_index]
        # 在原图上画出mask
        for i in range(mask.shape[0]):
            for j in range(mask.shape[1]):
                if mask[i, j]:
                    color_image[i, j] = [255, 0, 0]

        cv2.imshow("mask", color_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Step 5: Optimize the segmentation result using Estimation2D
        position, z_axis_radian,t = self.execute_step(
            "# Step 5: Optimize the segmentation result using Estimation2D",
            self.estimation.process_mask_and_transform, mask, self.realsense_camera,end2camera)
        if position is None:
            return None

        print(f"原图像的大小{color_image.shape}")
        # color_image_resized = cv2.resize(color_image, (1280, 720))
        self.execute_step("showing object frame", self.robotic_arm_planner.draw_obj_frame, t, self.K, color_image)


        # Step 6: Robotic Planning
        tpose_sequence = self.execute_step("# Step 6: Robotic Planning",
                                           self.robotic_arm_planner.plan_path, position, z_axis_radian,t)
        if tpose_sequence is None:
            return None

        self.execute_step("# Step 7: Robotic Execution",
                        self.task_controller.execute_task, tpose_sequence)



    def loop(self):
        self.process_task1()#无序分拣

if __name__ == "__main__":
    logger_manager = LoggerManager()
    task = DexterousGraspTask(logger_manager, upstair=False)
    task.loop()
