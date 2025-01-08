from robot.controller import Controller
from config.robot_varant import robot_config

controller = Controller(robot_config)
controller.get_joint_info()
# 目标位置（弧度）
target_positions = [0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5]  # 每个关节的目标位置
controller.control(target_positions)
controller.visualize()
