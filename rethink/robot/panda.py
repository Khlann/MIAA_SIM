import panda_py
from panda_py import libfranka
import time
import numpy as np
class PandaRobot:
    def __init__(self, hostname="172.16.0.2", username="franka", password="franka123"):
        # 机器人参数
        self.hostname = hostname
        self.username = username
        self.password = password

        # 初始化机器人
        self.desk = panda_py.Desk(self.hostname, self.username, self.password)
        self.desk.unlock()
        self.desk.activate_fci()
        self.panda = panda_py.Panda(self.hostname)
        self.gripper = libfranka.Gripper(self.hostname)


    def move_to_joint_position(self, joint):
        """
        移动机械臂到指定的关节位置，并等待到达目标位置
        """
        # 启动机械臂向目标关节位置运动
        self.panda.move_to_joint_position(joint)
        # 设定一个合理的阈值，用于判断是否到达目标位置

    def move_to_pose(self, pose):
        """
        移动机械臂到指定的位姿，并等待到达目标位置
        """
        # 启动机械臂向目标位姿运动
        self.panda.move_to_pose(pose)
        
    
    def get_pose(self):
        """
        获取当前机械臂的位姿
        """
        return self.panda.get_pose()
    
    def calculate_ik(self, pose):
        """
        计算逆运动学
        """
        return panda_py.ik(pose)
    
    def calculate_fk(self, joint):
        """
        计算正运动学
        """
        return panda_py.fk(joint)
    
    def open_gripper(self):
        """
        打开机械臂的夹爪
        """
        self.gripper.open()

    def close_gripper(self):
        """
        关闭机械臂的夹爪
        """
        self.gripper.close()
    
    def control_gripper(self, width, speed=0.2, force=10, epsilon_inner=0.04, epsilon_outer=0.04):
        """
        控制机械臂的夹爪
        """
        self.gripper.move(width, speed, force, epsilon_inner, epsilon_outer)