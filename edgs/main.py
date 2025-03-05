import sys
import cv2
# 下面三个路径自行替换为自己的路径
project_root_path = "/home/arlen/arlen/miaa_sim/edgs"
gsam_path = "/home/arlen/arlen/miaa_sim/edgs/external/gsam2"
snowboy_path = "/home/arlen/arlen/miaa_sim/edgs/external/snowboy"
sys.path.insert(0,project_root_path)
sys.path.insert(0,gsam_path)
sys.path.insert(0,snowboy_path)

from dexterous_grasp.logic_module import IFlytekInterface, Dinox,TaskController, FrankaArmPlanner, Estimation, DoubaoClient
from dexterous_grasp.logger_module import LoggerManager
from dexterous_grasp.device_module import D435i, Speaker, Microphone
from external.snowboy.examples.Python3 import snowboydecoder
from dexterous_grasp.config import (iflytek_config, franka_config, feedback_params, audio_record_params, awake_params,doubao_config,api_token)

class EdgsTasks():
    def __init__(self, project_root_path, robot_type):
        self.logger_manager = LoggerManager(project_root_path)
        self.ifly_interface = IFlytekInterface(iflytek_config, self.logger_manager)
        self.task_controller = TaskController(robot_type,franka_config, self.logger_manager)
        self.robot_planner = FrankaArmPlanner()
        self.dinox = Dinox(api_token)
        self.estimation2D = Estimation()
        self.camera = D435i(self.logger_manager)
        self.speaker = Speaker()
        self.microphone = Microphone(audio_record_params, awake_params, snowboydecoder, self.logger_manager)
        self.doubao_interface = DoubaoClient(doubao_config)

    def process_task(self):
        print("Sucessfully detected wake word")
        
        # Step 1: Voice to Text using IFlytekInterface
        self.speaker.play_audio(iflytek_config.start_recording_audio_path)
        audio_frames = self.microphone.listen() 
        connection, language_prompt = self.ifly_interface.audio_frame2text(b''.join(audio_frames))
        if not connection:
            self.speaker.play_audio(feedback_params.internet_error)
            return None
        if language_prompt is None:
            self.speaker.play_audio(feedback_params.not_clear)
            return None
        self.speaker.play_audio(iflytek_config.stop_recording_audio_path)

        # Step 2: Capture RGB-D using Realsense Camera
        self.camera.capture_current_info()
        color_image, _ = self.camera.get_color_info()
        cv2.imwrite("color_image.png", color_image)
        color_image_path = "color_image.png"
        if color_image is None:
            self.speaker.play_audio(feedback_params.camera_error)
            return None

        # Step 3: Use VLM to understand the text and connect to image
        gpt_result = self.doubao_interface.understand_image_by_text(language_prompt, color_image_path)        
        if gpt_result is None:
            return None
        
        # Step 4: Use Dinox to get mask
        mask = self.dinox.get_mask("color_image.png", gpt_result)
        if mask is None:
            self.speaker.play_audio(feedback_params.not_understand)
            return None
        
        # Step 5: Use Estimation to get 2D pose
        P_O_C, R = self.estimation2D.process_mask_and_transform(mask, self.camera)
        if P_O_C is None:
            return None
        
        # Step 6: Plan robotic arm movement
        T_E_B = self.task_controller.robotic_arm_controller.robot_arm.get_pose()
        initial_angle_gap = self.task_controller.initial_angle_gap
        q_list = self.robot_planner.plan_curobo(P_O_C, R, franka_config.T_C_E, T_E_B,initial_angle_gap)

        # Step 7: Execute movement
        self.task_controller.robotic_arm_controller.execute_movement_joints(q_list)
        self.task_controller.robotic_arm_controller.close_gripper()
        self.task_controller.robotic_arm_controller.execute_movement_pose(self.task_controller.start_pose)
        self.task_controller.robotic_arm_controller.open_gripper()

    def loop(self):
        print("Listening... Press Ctrl+C to exit")
        self.speaker.play_audio(feedback_params.ready_go)
        self.microphone.detector.start(detected_callback=self.process_task, sleep_time=0.03)

if __name__ == "__main__":
    robot_type = "franka"
    # project_root_path = "/home/arlen/arlen/miaa_sim/edgs"
    task = EdgsTasks(project_root_path, robot_type)
    task.loop()
