import time

from snowboy.examples.Python3 import snowboydecoder
from dexterous_grasp.device_module.cameras import L515, D405
from dexterous_grasp.device_module.digital_io.microphone import Microphone
from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logic_module.planning_module import RoboticArmPlanner
from dexterous_grasp.logic_module.vision_module import GroundedSAM, Estimation2D
from dexterous_grasp.logic_module.understanding_module import IFlytekInterface, GPT4Integration
from dexterous_grasp.config import (request_info, iflytek_config, ground_sam2_config, camera2base,
                                    dexterous_hand_grasp_pose, grasp_safe_distance, arm_motion_params,
                                    hand_motion_params, hand_device_params, robot_arm_ip_address,
                                    audio_record_params, awake_params, feedback_params)
from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.utils.common import play_audio_file


class DexterousGraspTask:

    def __init__(self, logger_manager, upstair=True):
        self.logger_manager = logger_manager
        self.ifly_interface = IFlytekInterface(iflytek_config, self.logger_manager)
        self.gpt_interface = GPT4Integration(request_info, self.logger_manager)
        self.grounded_sam2 = GroundedSAM(ground_sam2_config, self.logger_manager)
        self.estimation = Estimation2D(self.logger_manager)
        self.robotic_arm_planner = RoboticArmPlanner(camera2base, dexterous_hand_grasp_pose, grasp_safe_distance,
                                                     self.logger_manager)
        self.microphone = Microphone(audio_record_params, awake_params, snowboydecoder, self.logger_manager)
        self.task_controller = TaskController(arm_motion_params, hand_motion_params, hand_device_params,
                                              robot_arm_ip_address, self.logger_manager)
        self.realsense_camera = D405(self.logger_manager) if upstair else L515(self.logger_manager)

    def execute_step(self, step_message, function, *args):
        self.logger_manager.logger.info(step_message)
        return function(*args)

    def capture_image(self, step_message):
        self.realsense_camera.capture_current_info()
        return self.execute_step(step_message, self.realsense_camera.get_color_info)

    def process_task(self):
        play_audio_file(iflytek_config.start_recording_audio_path)
        # Step 1: Voice to Text using IFlytekInterface
        audio_frames = self.microphone.listen()
        connection, language_prompt = self.execute_step("# Step 1: Voice to Text using IFlytekInterface",
                                            self.ifly_interface.audio_frame2text, b''.join(audio_frames))
        if not connection:
            play_audio_file(feedback_params.internet_error)
            return None

        if language_prompt is None:
            play_audio_file(feedback_params.not_clear)
            return None

        self.logger_manager.create_prompt_folder(language_prompt)
        play_audio_file(iflytek_config.stop_recording_audio_path)

        # Step 2: Capture RGB-D using Realsense Camera
        color_image, _ = self.capture_image("# Step 2: Capture RGB-D using Realsense Camera")
        if color_image is None:
            play_audio_file(feedback_params.photograph_error)
            return None

        # Step 3: Use GPT4Integration to understand the text and connect to image
        connection, gpt_result = self.execute_step("# Step 3: Use GPT4Integration to understand the text and connect to image",
                                       self.gpt_interface.understand_image_by_text, language_prompt, color_image)
        if not connection:
            play_audio_file(feedback_params.internet_error)
            return None
        if gpt_result is None:
            play_audio_file(feedback_params.object_error)
            return None

        # Step 4: Use GroundedSAM for object segmentation based on GPT result
        mask, _, _, _ = self.execute_step(
            "# Step 4: Use GroundedSAM for object segmentation based on GPT result",
            self.grounded_sam2.segment, gpt_result, color_image)
        if mask is None:
            play_audio_file(feedback_params.location_error)
            return None

        # Step 5: Optimize the segmentation result using Estimation2D
        position, z_axis_radian = self.execute_step(
            "# Step 5: Optimize the segmentation result using Estimation2D",
            self.estimation.get_3d_position_and_z_axis_radian, mask, self.realsense_camera)
        if position is None:
            return None

        # Step 6: Robotic Planning
        tpose_sequence = self.execute_step("# Step 6: Robotic Planning",
                                           self.robotic_arm_planner.plan_path, position, z_axis_radian)
        if tpose_sequence is None:
            return None

        # Step 7: Robotic Execution
        self.execute_step("# Step 7: Robotic Execution",
                          self.task_controller.execute_task, tpose_sequence)

        self.logger_manager.logger.info("Task completed successfully.")

        play_audio_file(feedback_params.task_completed)

    def loop(self):
        print("Listening... Press Ctrl+C to exit")
        play_audio_file(feedback_params.ready_go)
        self.microphone.detector.start(detected_callback=self.process_task, sleep_time=0.03)


if __name__ == "__main__":
    logger_manager = LoggerManager()
    task = DexterousGraspTask(logger_manager, upstair=False)
    task.loop()
