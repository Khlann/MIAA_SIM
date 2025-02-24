
from dexterous_grasp.device_module.cameras import L515, D405, D435i, D435
from dexterous_grasp.device_module.digital_io.microphone import Microphone
from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logic_module.planning_module import RoboticArmPlanner
from dexterous_grasp.logic_module.vision_module import Estimation2D
from dexterous_grasp.logic_module.understanding_module import IFlytekInterface, GPT4Integration
from dexterous_grasp.logic_module.understanding_module import Img2Mask
from dexterous_grasp.logic_module.understanding_module import CLIPImageSimilarity,find_most_similar
from dexterous_grasp.config import (request_info, iflytek_config, ground_sam2_config,camera2base,standard_relative_pose_pairs,end2camera,
                                    dexterous_hand_grasp_pose, grasp_safe_distance, arm_motion_params,
                                    hand_motion_params, hand_device_params, robot_arm_ip_address,
                                    audio_record_params, awake_params, feedback_params,dinox_sam2_clip_config)
from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.utils.common import play_audio_file
from dexterous_grasp.config import planning_module_varant

import cv2
import numpy as np
test_object_list = ["battery", "capsule", "ball", "screwdriver", "red_cloth", "egg", "screw"]
class DexterousGraspTask:

    def __init__(self, logger_manager, upstair=True):
        self.logger_manager = logger_manager
        self.ifly_interface = IFlytekInterface(iflytek_config, self.logger_manager)
        # self.gpt_interface = GPT4Integration(request_info, self.logger_manager)
        # self.grounded_sam2 = GroundedSAM(ground_sam2_config, self.logger_manager)
        self.estimation = Estimation2D(self.logger_manager)
        self.robotic_arm_planner = RoboticArmPlanner(camera2base, dexterous_hand_grasp_pose, grasp_safe_distance,standard_relative_pose_pairs,
                                                     self.logger_manager)
        # self.microphone = Microphone(audio_record_params, awake_params, snowboydecoder, self.logger_manager)
        self.task_controller = TaskController(arm_motion_params, hand_motion_params, hand_device_params,
                                              robot_arm_ip_address, self.logger_manager)
        self.img2mask = Img2Mask(dinox_sam2_clip_config)
        self.clip_similarity = CLIPImageSimilarity()
        # self.realsense_camera = D405(self.logger_manager) if upstair else L515(self.logger_manager)
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

        # Step 7: Robotic Execution
        self.execute_step("# Step 7: Robotic Execution",
                          self.task_controller.execute_task, tpose_sequence)

        self.logger_manager.logger.info("Task completed successfully.")

        play_audio_file(feedback_params.task_completed)

    def process_task1(self):
        task_object_list = ["battery", "capsule", "ball", "screwdriver", "red_cloth", "egg", "screw","can"]
        A_list = ["ball","battery","screwdriver","screw"]
        B_list = ["capsule","red_cloth","egg","can"]

        for obj in task_object_list:
            if obj in A_list:
                obj_type = "A"
            elif obj in B_list:
                obj_type = "B"

            color_image, _ = self.capture_image("# Step 1: Capture RGB-D using Realsense Camera")
            cv2.imwrite("color_image.png", color_image)
            clip_masks,masks = self.img2mask.detect_objects("color_image.png")
            max_clip_mask_index = find_most_similar(clip_masks, obj, self.img2mask, self.clip_similarity)
            mask = masks[max_clip_mask_index]

            for i in range(mask.shape[0]):
                for j in range(mask.shape[1]):
                    if mask[i, j]:
                        color_image[i, j] = [255, 0, 0]

            self.logger_manager.save_image(color_image,"color_image",obj)

            position, z_axis_radian,t = self.execute_step(
                "# Step 5: Optimize the segmentation result using Estimation2D",
                self.estimation.process_mask_and_transform, mask, self.realsense_camera,end2camera)


            tpose_sequence = self.execute_step("# Step 6: Robotic Planning",
                                            self.robotic_arm_planner.plan_path, position, z_axis_radian,t)


            self.execute_step("# Step 7: Robotic Execution",
                            self.task_controller.execute_task, tpose_sequence)

            self.logger_manager.logger.info("Task completed successfully.")

    def process_task2(self):
        task_obj_list = ["battery","plug"]
        for obj in task_obj_list:
            pass
        pass
    def loop(self):
        self.process_task1()#无序分拣
        self.process_task2()#装配


if __name__ == "__main__":
    logger_manager = LoggerManager()
    task = DexterousGraspTask(logger_manager, upstair=False)
    task.loop()
