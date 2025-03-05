# import urx
import panda_py
import time
from dexterous_grasp.logger_module.logger import LoggerValidator
from panda_py import libfranka

class FrankaController(LoggerValidator):
    def __init__(self, franka_config, logger_manager=None):
        super().__init__(logger_manager)
        self.franka_config = franka_config
        self.build_robot_arm_connection()

    def build_robot_arm_connection(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            status = self.connect_to_robot()
            if status:
                return True
            else:
                self.logger_manager.logger.error(f"Failed to connect to Franka robot_arm. Retrying... (Attempt {attempt + 1}/{max_attempts})")
        else:
            raise Exception("Failed to connect to Franka robot_arm after multiple attempts.")

    def connect_to_robot(self):
        try:
            self.desk = panda_py.Desk(self.franka_config.hostname, self.franka_config.username , self.franka_config.password )
            self.desk.unlock()
            self.desk.activate_fci()
            self.robot_arm = panda_py.Panda(self.franka_config.hostname)
            self.gripper = libfranka.Gripper(self.franka_config.hostname)
            self.gripper.move(0.1, 0.2)
            self.logger_manager.logger.info("Connected to Franka robot_arm successfully.")
            return True
        except Exception as e:
            time.sleep(2)
            return False


    def execute_movement_joints(self, joints: list):
        self.robot_arm.move_to_joint_position(joints)
        return True
    
    def execute_movement_pose(self, pose_matrix: list):
        self.robot_arm.move_to_pose(pose_matrix)
        return True

    def close_gripper(self):
        self.gripper.grasp(0.02, 0.2,5,0.06,0.09)

    def open_gripper(self):
        self.gripper.move(0.1, 0.2)

    def move_to_start(self):
        self.robot_arm.move_to_start()

