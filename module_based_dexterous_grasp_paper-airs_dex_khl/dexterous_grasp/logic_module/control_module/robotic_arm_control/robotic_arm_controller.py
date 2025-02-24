import urx
import time
from dexterous_grasp.logger_module.logger import LoggerValidator


class RoboticArmController(LoggerValidator):
    def __init__(self, robot_arm_ip_address, arm_motion_params, logger_manager=None):
        super().__init__(logger_manager)
        self.robot_arm_ip_address = robot_arm_ip_address
        self.build_robot_arm_connection()
        self.default_acc = arm_motion_params.default_acc
        self.default_vel = self.default_acc * 2
        self.default_radius = arm_motion_params.default_radius

    def build_robot_arm_connection(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            status = self.connect_to_robot()
            if status:
                return True
            else:
                self.logger_manager.logger.error(f"Failed to connect to UR5 robot_arm. Retrying... (Attempt {attempt + 1}/{max_attempts})")
        else:
            raise Exception("Failed to connect to UR5 robot_arm after multiple attempts.")

    def connect_to_robot(self):
        try:
            self.robot_arm = urx.Robot(self.robot_arm_ip_address)
            self.logger_manager.logger.info("Connected to UR5 robot_arm successfully.")
            return True
        except Exception as e:
            time.sleep(2)
            return False

    def execute_movement_tposes(self, movement_tposes: list):
        for tpose in movement_tposes:
            self.robot_arm.movel(tpose, acc=self.default_acc, vel=self.default_vel)
        return True

    def execute_smooth_movement_tposes(self, movement_tposes: list):
        self.robot_arm.movels(movement_tposes, acc=self.default_acc, vel=self.default_vel, radius=self.default_radius)
        return True

    def execute_movement_joints(self, movement_command: list):
        self.robot_arm.movej(movement_command, acc=self.default_acc * 2, vel=self.default_vel * 2)
        return True

    def execute_smooth_movement_joints(self, movement_command: list):
        pass
